from datetime import date, datetime, timedelta, timezone

import pytest

from flights import cache, rate_limit, service
from flights.errors import (
    FlightSearchError,
    ProviderRateLimitedError,
    ProviderUnavailableError,
    TooManyRequestsError,
)
from flights.models import FlightCandidate, ProviderResult

TODAY = date(2026, 9, 1)
NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("FLIGHTS_DB_PATH", str(tmp_path / "flights.db"))
    cache.reset_for_tests()
    rate_limit.reset()
    yield
    cache.reset_for_tests()
    rate_limit.reset()


class FakeProvider:
    name = "fake-provider"
    is_live = False
    freshness_message = "Indicative fares."

    def __init__(self, candidates=(), error=None):
        self.candidates = tuple(candidates)
        self.error = error
        self.calls = 0

    def is_configured(self):
        return True

    def search_flexible_dates(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return ProviderResult(self.name, self.candidates, self.is_live, 1)


def use_provider(monkeypatch, provider):
    monkeypatch.setattr(service, "get_provider", lambda name=None: provider)
    return provider


def candidate(departure, nights, price, stops=0, airline="AC"):
    departure_date = date.fromisoformat(departure)
    return FlightCandidate(
        origin="YYZ",
        destination="SFO",
        departure_date=departure_date,
        return_date=departure_date + timedelta(days=nights),
        total_price=price,
        currency="CAD",
        source="fake-provider",
        airline_code=airline,
        stops=stops,
        duration_minutes=700,
        booking_url="https://www.aviasales.com/search/example",
    )


def payload(**overrides):
    body = {
        "origin": "YTO",
        "destination": "SFO",
        "earliestDeparture": "2026-09-10",
        "latestDeparture": "2026-09-20",
        "minNights": 5,
        "maxNights": 8,
        "currency": "CAD",
        "directOnly": False,
    }
    body.update(overrides)
    return body


def search(**kwargs):
    kwargs.setdefault("today", TODAY)
    kwargs.setdefault("now", NOW)
    return service.search(kwargs.pop("body", payload()), **kwargs)


def test_search_returns_ranked_candidates_with_a_best_deal(monkeypatch):
    use_provider(
        monkeypatch,
        FakeProvider([candidate("2026-09-16", 7, 612), candidate("2026-09-15", 7, 487)]),
    )

    result = search()

    assert result["provider"] == "fake-provider"
    assert result["isLive"] is False
    assert result["best"]["totalPrice"] == 487
    assert [c["totalPrice"] for c in result["candidates"]] == [487, 612]
    assert result["message"] is None
    assert result["metadata"]["cacheHit"] is False


def test_search_describes_the_route_in_human_readable_terms(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    places = search()["places"]

    assert places["origin"]["label"] == "Toronto"
    assert places["destination"]["label"] == "San Francisco (SFO)"


def test_search_drops_candidates_outside_the_requested_criteria(monkeypatch):
    use_provider(
        monkeypatch,
        FakeProvider(
            [
                candidate("2026-09-15", 7, 487),
                candidate("2026-09-28", 7, 120),
                candidate("2026-09-15", 2, 130),
            ]
        ),
    )

    assert len(search()["candidates"]) == 1


def test_search_returns_a_plain_message_when_nothing_matches(monkeypatch):
    use_provider(monkeypatch, FakeProvider([]))

    result = search()

    assert result["candidates"] == []
    assert result["best"] is None
    assert result["message"] == service.NO_RESULTS_MESSAGE
    assert result["insights"] == []


def test_search_includes_flexible_date_prices_and_insights(monkeypatch):
    use_provider(
        monkeypatch,
        FakeProvider([candidate("2026-09-15", 7, 487), candidate("2026-09-16", 7, 612)]),
    )

    result = search()

    assert [entry["price"] for entry in result["datePrices"]] == [487, 612]
    assert result["insights"]


def test_a_repeat_search_is_served_from_cache(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search()
    result = search(now=NOW + timedelta(minutes=5))

    assert provider.calls == 1
    assert result["metadata"]["cacheHit"] is True
    assert result["best"]["totalPrice"] == 487


def test_an_expired_cache_entry_triggers_a_fresh_provider_call(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search()
    search(now=NOW + timedelta(seconds=cache.TTL_SECONDS + 60))

    assert provider.calls == 2


def test_differing_criteria_do_not_share_a_cache_entry(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search()
    search(body=payload(directOnly=True))

    assert provider.calls == 2


def test_a_provider_outage_falls_back_to_the_stale_cache(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))
    search()

    provider.error = ProviderUnavailableError()
    result = search(now=NOW + timedelta(seconds=cache.TTL_SECONDS + 60))

    assert result["metadata"]["stale"] is True
    assert result["message"] == service.STALE_MESSAGE
    assert result["best"]["totalPrice"] == 487


def test_a_provider_outage_without_a_cache_surfaces_the_error(monkeypatch):
    use_provider(monkeypatch, FakeProvider(error=ProviderUnavailableError()))

    with pytest.raises(ProviderUnavailableError):
        search()


def test_provider_rate_limiting_surfaces_a_friendly_error(monkeypatch):
    use_provider(monkeypatch, FakeProvider(error=ProviderRateLimitedError()))

    with pytest.raises(ProviderRateLimitedError) as error:
        search()

    assert "busy" in error.value.message


def test_invalid_input_is_rejected_before_the_provider_is_called(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    with pytest.raises(FlightSearchError):
        search(body=payload(destination="YTO"))

    assert provider.calls == 0


def test_searches_are_rate_limited_per_client(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    for _ in range(rate_limit.PER_MINUTE):
        search(client_id="1.2.3.4")

    with pytest.raises(TooManyRequestsError):
        search(client_id="1.2.3.4")


def test_search_records_observations_and_an_event(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search()

    with cache._connect() as connection:
        observations = connection.execute(
            "SELECT COUNT(*) AS total FROM flight_price_observations"
        ).fetchone()["total"]
        events = connection.execute(
            "SELECT COUNT(*) AS total FROM flight_search_events"
        ).fetchone()["total"]

    assert observations == 1
    assert events == 1


def test_health_reports_whether_the_provider_is_configured(monkeypatch):
    use_provider(monkeypatch, FakeProvider())

    assert service.health() == {"status": "ok", "providerConfigured": True}


def test_form_defaults_sit_inside_the_allowed_limits():
    defaults = service.form_defaults(today=TODAY)

    assert defaults["minDate"] == "2026-09-01"
    assert defaults["earliestDeparture"] < defaults["latestDeparture"]
    assert defaults["minNights"] <= defaults["maxNights"]
