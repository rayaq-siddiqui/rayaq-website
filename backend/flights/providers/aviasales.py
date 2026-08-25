import os
from datetime import date, datetime

import requests

from ..errors import ProviderNotConfiguredError, ProviderRateLimitedError, ProviderUnavailableError
from ..models import FlightCandidate, ProviderResult
from .base import FlightSearchProvider

API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
LATEST_URL = "https://api.travelpayouts.com/v2/prices/latest"
BOOKING_HOST = "https://www.aviasales.com"
TIMEOUT_SECONDS = 8
MAX_MONTHS_PER_SEARCH = 3
MAX_TICKETS_PER_MONTH = 1000
MAX_LATEST_TICKETS = 100
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


def _months_in_window(start, end):
    months = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end and len(months) < MAX_MONTHS_PER_SEARCH:
        months.append(cursor.strftime("%Y-%m"))
        cursor = date(cursor.year + (cursor.month // 12), (cursor.month % 12) + 1, 1)
    return months


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            return None


def _stops(ticket):
    legs = [ticket.get("transfers"), ticket.get("return_transfers")]
    known = [leg for leg in legs if isinstance(leg, int)]
    return max(known) if known else None


def _price(ticket, field="price"):
    try:
        return round(float(ticket[field]), 2)
    except (KeyError, TypeError, ValueError):
        return None


def _duration(ticket, field="duration"):
    value = ticket.get(field)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _deep_link(link, marker):
    if not link or not str(link).startswith("/"):
        return None
    url = f"{BOOKING_HOST}{link}"
    if marker:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}marker={marker}"
    return url


def _fallback_link(origin, destination, departure, return_date, marker):
    trip = f"{origin}{departure.strftime('%d%m')}{destination}"
    if return_date:
        trip = f"{trip}{return_date.strftime('%d%m')}"
    url = f"{BOOKING_HOST}/search/{trip}1"
    if marker:
        url = f"{url}?marker={marker}"
    return url


class AviasalesDataProvider(FlightSearchProvider):
    name = "aviasales-data"
    is_live = False
    freshness_message = (
        "Indicative fares recently observed by Aviasales. Prices can change quickly — "
        "verify the current fare before booking."
    )

    def __init__(self, token=None, marker=None):
        self._token = token if token is not None else os.environ.get("TRAVELPAYOUTS_API_TOKEN", "")
        self._marker = marker if marker is not None else os.environ.get("TRAVELPAYOUTS_MARKER", "")

    def is_configured(self):
        return bool(self._token)

    def search_flexible_dates(self, request):
        if not self.is_configured():
            raise ProviderNotConfiguredError()

        candidates = []
        months = _months_in_window(request.earliest_departure, request.latest_departure)
        for month in months:
            candidates.extend(self._tickets_for_month(request, month))
        candidates.extend(self._latest_tickets(request))

        return ProviderResult(
            provider=self.name,
            candidates=tuple(candidates),
            is_live=self.is_live,
            provider_requests=len(months) + 1,
        )

    def _tickets_for_month(self, request, month):
        payload = self._get(
            API_URL,
            {
                "origin": request.origin,
                "destination": request.destination,
                "departure_at": month,
                "currency": request.currency.lower(),
                "sorting": "price",
                "direct": "true" if request.direct_only else "false",
                "one_way": "false",
                "limit": MAX_TICKETS_PER_MONTH,
                "page": 1,
                "token": self._token,
            },
        )
        tickets = payload.get("data") or []
        if not isinstance(tickets, list):
            raise ProviderUnavailableError()
        return [
            candidate
            for candidate in (self._to_candidate(ticket, request) for ticket in tickets)
            if candidate is not None
        ]

    def _latest_tickets(self, request):
        # prices_for_dates is grouped by calendar month, so a lightly-searched route can
        # show only one or two fares per month even though Aviasales has seen more. This
        # endpoint isn't month-bound and its cache outlives the 48-hour window, so it
        # fills in exactly the gap a thin route like Toronto-San Francisco hits.
        payload = self._get(
            LATEST_URL,
            {
                "origin": request.origin,
                "destination": request.destination,
                "currency": request.currency.lower(),
                "limit": MAX_LATEST_TICKETS,
                "page": 1,
                "token": self._token,
            },
        )
        tickets = payload.get("data") or []
        if not isinstance(tickets, list):
            raise ProviderUnavailableError()
        return [
            candidate
            for candidate in (self._to_candidate_from_latest(ticket, request) for ticket in tickets)
            if candidate is not None
        ]

    def _get(self, url, params):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException:
            raise ProviderUnavailableError()

        if response.status_code == 429:
            raise ProviderRateLimitedError()
        if response.status_code >= 400:
            raise ProviderUnavailableError()
        if len(response.content or b"") > MAX_RESPONSE_BYTES:
            raise ProviderUnavailableError()

        try:
            payload = response.json()
        except ValueError:
            raise ProviderUnavailableError()
        if not isinstance(payload, dict) or payload.get("success") is False:
            raise ProviderUnavailableError()
        return payload

    def _to_candidate(self, ticket, request):
        if not isinstance(ticket, dict):
            return None

        departure = _parse_date(ticket.get("departure_at"))
        return_date = _parse_date(ticket.get("return_at"))
        price = _price(ticket)
        if departure is None or price is None:
            return None

        origin = ticket.get("origin_airport") or ticket.get("origin") or request.origin
        destination = (
            ticket.get("destination_airport") or ticket.get("destination") or request.destination
        )
        booking_url = _deep_link(ticket.get("link"), self._marker) or _fallback_link(
            origin, destination, departure, return_date, self._marker
        )

        return FlightCandidate(
            origin=origin,
            destination=destination,
            departure_date=departure,
            return_date=return_date,
            total_price=price,
            currency=request.currency,
            source=self.name,
            airline_code=ticket.get("airline"),
            flight_number=str(ticket["flight_number"]) if ticket.get("flight_number") else None,
            stops=_stops(ticket),
            duration_minutes=_duration(ticket),
            found_at=ticket.get("found_at"),
            booking_url=booking_url,
        )

    def _to_candidate_from_latest(self, ticket, request):
        if not isinstance(ticket, dict):
            return None
        if ticket.get("show_to_affiliates") is False or ticket.get("actual") is False:
            return None

        departure = _parse_date(ticket.get("depart_date"))
        return_date = _parse_date(ticket.get("return_date"))
        price = _price(ticket, "value")
        if departure is None or price is None:
            return None

        origin = ticket.get("origin") or request.origin
        destination = ticket.get("destination") or request.destination
        stops = ticket.get("number_of_changes")

        return FlightCandidate(
            origin=origin,
            destination=destination,
            departure_date=departure,
            return_date=return_date,
            total_price=price,
            currency=request.currency,
            source=self.name,
            stops=stops if isinstance(stops, int) else None,
            duration_minutes=_duration(ticket),
            found_at=ticket.get("found_at"),
            booking_url=_fallback_link(origin, destination, departure, return_date, self._marker),
        )
