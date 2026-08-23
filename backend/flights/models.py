from dataclasses import dataclass, replace
from datetime import date
from typing import Optional

SUPPORTED_CURRENCIES = ("CAD", "USD")
CURRENCY_SYMBOLS = {"CAD": "$", "USD": "$"}


@dataclass(frozen=True)
class SearchRequest:
    origin: str
    destination: str
    earliest_departure: date
    latest_departure: date
    min_nights: int
    max_nights: int
    currency: str
    direct_only: bool

    def cache_key(self, provider):
        return ":".join(
            [
                provider,
                self.origin,
                self.destination,
                self.earliest_departure.isoformat(),
                self.latest_departure.isoformat(),
                str(self.min_nights),
                str(self.max_nights),
                self.currency,
                "direct" if self.direct_only else "any",
            ]
        )

    def to_api(self):
        return {
            "origin": self.origin,
            "destination": self.destination,
            "earliestDeparture": self.earliest_departure.isoformat(),
            "latestDeparture": self.latest_departure.isoformat(),
            "minNights": self.min_nights,
            "maxNights": self.max_nights,
            "currency": self.currency,
            "directOnly": self.direct_only,
        }


@dataclass(frozen=True)
class FlightCandidate:
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date]
    total_price: float
    currency: str
    source: str
    airline_code: Optional[str] = None
    flight_number: Optional[str] = None
    stops: Optional[int] = None
    duration_minutes: Optional[int] = None
    found_at: Optional[str] = None
    booking_url: Optional[str] = None
    raw_provider_id: Optional[str] = None

    @property
    def nights(self):
        if self.return_date is None:
            return None
        return (self.return_date - self.departure_date).days

    @property
    def dedupe_key(self):
        if self.raw_provider_id:
            return self.raw_provider_id
        return (
            self.origin,
            self.destination,
            self.departure_date,
            self.return_date,
            self.airline_code,
            round(self.total_price, 2),
        )

    def with_booking_url(self, url):
        return replace(self, booking_url=url)

    def to_api(self):
        return {
            "origin": self.origin,
            "destination": self.destination,
            "departureDate": self.departure_date.isoformat(),
            "returnDate": self.return_date.isoformat() if self.return_date else None,
            "nights": self.nights,
            "totalPrice": self.total_price,
            "currency": self.currency,
            "airlineCode": self.airline_code,
            "flightNumber": self.flight_number,
            "stops": self.stops,
            "durationMinutes": self.duration_minutes,
            "source": self.source,
            "foundAt": self.found_at,
            "bookingUrl": self.booking_url,
        }


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    candidates: tuple
    is_live: bool
    provider_requests: int = 0
