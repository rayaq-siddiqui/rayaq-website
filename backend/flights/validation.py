from datetime import date, datetime

from . import airports
from .errors import FlightSearchError
from .models import SUPPORTED_CURRENCIES, SearchRequest

MAX_WINDOW_DAYS = 60
MAX_NIGHTS = 30
DEFAULT_CURRENCY = "CAD"


def _require_code(payload, field, label):
    value = (payload.get(field) or "").strip().upper()
    if not value:
        raise FlightSearchError(f"Choose {label}.", field)
    if not airports.is_known(value):
        raise FlightSearchError(f"We do not know the airport code {value}.", field)
    return value


def _require_date(payload, field, label):
    value = payload.get(field)
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise FlightSearchError(f"Choose {label}.", field)
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise FlightSearchError(f"{label.capitalize()} must be a YYYY-MM-DD date.", field)


def _require_nights(payload, field, label):
    value = payload.get(field)
    try:
        nights = int(value)
    except (TypeError, ValueError):
        raise FlightSearchError(f"{label.capitalize()} must be a whole number of nights.", field)
    if nights < 0:
        raise FlightSearchError(f"{label.capitalize()} cannot be negative.", field)
    if nights > MAX_NIGHTS:
        raise FlightSearchError(f"{label.capitalize()} cannot exceed {MAX_NIGHTS} nights.", field)
    return nights


def parse(payload, today=None):
    if not isinstance(payload, dict):
        raise FlightSearchError("Send a JSON object describing the search.")

    today = today or date.today()

    origin = _require_code(payload, "origin", "where you are flying from")
    destination = _require_code(payload, "destination", "where you are flying to")
    if origin == destination:
        raise FlightSearchError("Origin and destination must be different.", "destination")

    earliest = _require_date(payload, "earliestDeparture", "the earliest departure date")
    latest = _require_date(payload, "latestDeparture", "the latest departure date")
    if latest < earliest:
        raise FlightSearchError(
            "The latest departure date must be on or after the earliest one.", "latestDeparture"
        )
    if earliest < today:
        raise FlightSearchError("The departure window cannot start in the past.", "earliestDeparture")
    if (latest - earliest).days + 1 > MAX_WINDOW_DAYS:
        raise FlightSearchError(
            f"Keep the departure window to {MAX_WINDOW_DAYS} days or fewer.", "latestDeparture"
        )

    min_nights = _require_nights(payload, "minNights", "the minimum trip length")
    max_nights = _require_nights(payload, "maxNights", "the maximum trip length")
    if min_nights > max_nights:
        raise FlightSearchError(
            "The minimum trip length cannot exceed the maximum.", "minNights"
        )

    currency = (payload.get("currency") or DEFAULT_CURRENCY).strip().upper()
    if currency not in SUPPORTED_CURRENCIES:
        raise FlightSearchError(
            f"Currency must be one of {', '.join(SUPPORTED_CURRENCIES)}.", "currency"
        )

    return SearchRequest(
        origin=origin,
        destination=destination,
        earliest_departure=earliest,
        latest_departure=latest,
        min_nights=min_nights,
        max_nights=max_nights,
        currency=currency,
        direct_only=bool(payload.get("directOnly")),
        include_nearby=bool(payload.get("includeNearby")),
    )
