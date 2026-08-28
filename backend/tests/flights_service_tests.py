from datetime import date, datetime, timedelta, timezone

import pytest

from flights import airports, cache, rate_limit, service
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

    def __init__(self, candidates=(), error=None, by_pair=None, errors_by_pair=None):
        self.candidates = tuple(candidates)
        self.error = error
        self.by_pair = by_pair or {}
        self.errors_by_pair = errors_by_pair or {}
        self.calls = 0
        self.requests = []

    def is_configured(self):
        return True

    def search_flexible_dates(self, request):
        self.calls += 1
        self.requests.append(request)
        if self.error:
            raise self.error
        pair_error = self.errors_by_pair.get((request.origin, request.destination))
        if pair_error:
            raise pair_error
        candidates = self.by_pair.get((request.origin, request.destination), self.candidates)
        return ProviderResult(self.name, tuple(candidates), self.is_live, 1)


def use_provider(monkeypatch, provider):
    monkeypatch.setattr(service, "get_provider", lambda name=None: provider)
    return provider


def candidate(departure, nights, price, stops=0, airline="AC", origin="YYZ", destination="SFO"):
    departure_date = date.fromisoformat(departure)
    return FlightCandidate(
        origin=origin,
        destination=destination,
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


def test_price_history_is_absent_without_enough_observed_days(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    assert search()["priceHistory"] is None


def test_price_history_appears_once_enough_days_are_recorded(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))
    for days_ago, price in ((3, 620), (2, 590), (1, 540)):
        cache.record_observations(
            [candidate("2026-09-15", 7, price)], "fake-provider", now=NOW - timedelta(days=days_ago)
        )

    result = search()

    assert result["priceHistory"] == {
        "lowestPrice": 540,
        "currency": "CAD",
        "observedDays": 3,
        "windowDays": cache.PRICE_HISTORY_WINDOW_DAYS,
    }


def test_nearby_airports_are_not_queried_by_default(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search(body=payload(origin="YYZ"))

    assert provider.calls == 1
    assert (provider.requests[0].origin, provider.requests[0].destination) == ("YYZ", "SFO")


def test_include_nearby_also_queries_real_alternate_airports(monkeypatch):
    provider = use_provider(
        monkeypatch,
        FakeProvider(
            by_pair={
                ("YYZ", "SFO"): [candidate("2026-09-15", 7, 487, origin="YYZ")],
                ("YTZ", "SFO"): [candidate("2026-09-16", 7, 610, origin="YTZ")],
                ("YYZ", "OAK"): [candidate("2026-09-17", 7, 399, origin="YYZ", destination="OAK")],
            }
        ),
    )

    result = search(body=payload(origin="YYZ", includeNearby=True))

    pairs = {(r.origin, r.destination) for r in provider.requests}
    assert pairs == {("YYZ", "SFO"), ("YTZ", "SFO"), ("YYZ", "OAK")}
    assert provider.calls == 3
    prices = {c["totalPrice"] for c in result["candidates"]}
    assert prices == {487, 610, 399}


def test_candidates_from_a_different_airport_carry_an_honest_note(monkeypatch):
    use_provider(
        monkeypatch,
        FakeProvider(
            by_pair={
                ("YYZ", "SFO"): [candidate("2026-09-15", 7, 487, origin="YYZ")],
                ("YTZ", "SFO"): [candidate("2026-09-16", 7, 610, origin="YTZ")],
            }
        ),
    )

    result = search(body=payload(origin="YYZ", includeNearby=True))

    notes = {c["origin"]: c["airportNote"] for c in result["candidates"]}
    assert notes["YYZ"] is None
    assert notes["YTZ"] == f"from {airports.label('YTZ')}"


def test_include_nearby_does_not_reuse_an_exact_search_cache_entry(monkeypatch):
    provider = use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))

    search(body=payload(origin="YYZ", includeNearby=False))
    search(body=payload(origin="YYZ", includeNearby=True))

    assert provider.calls == 1 + 3


def test_nearby_fan_out_skips_a_pair_that_would_search_an_airport_against_itself(monkeypatch):
    provider = use_provider(
        monkeypatch,
        FakeProvider(
            by_pair={("YYZ", "YTZ"): [candidate("2026-09-15", 7, 487, origin="YYZ", destination="YTZ")]}
        ),
    )

    result = search(body=payload(origin="YYZ", destination="YTZ", includeNearby=True))

    pairs = {(r.origin, r.destination) for r in provider.requests}
    assert pairs == {("YYZ", "YTZ")}
    assert provider.calls == 1
    prices = {c["totalPrice"] for c in result["candidates"]}
    assert prices == {487}


def test_a_failed_nearby_pair_does_not_discard_the_other_pairs_candidates(monkeypatch):
    provider = use_provider(
        monkeypatch,
        FakeProvider(
            by_pair={
                ("YYZ", "SFO"): [candidate("2026-09-15", 7, 487, origin="YYZ")],
                ("YYZ", "OAK"): [candidate("2026-09-17", 7, 399, origin="YYZ", destination="OAK")],
            },
            errors_by_pair={("YTZ", "SFO"): ProviderUnavailableError()},
        ),
    )

    result = search(body=payload(origin="YYZ", includeNearby=True))

    assert provider.calls == 3
    prices = {c["totalPrice"] for c in result["candidates"]}
    assert prices == {487, 399}


def test_nearby_search_only_fails_when_every_pair_fails(monkeypatch):
    use_provider(
        monkeypatch,
        FakeProvider(
            errors_by_pair={
                ("YYZ", "SFO"): ProviderUnavailableError(),
                ("YTZ", "SFO"): ProviderUnavailableError(),
                ("YYZ", "OAK"): ProviderRateLimitedError(),
            }
        ),
    )

    with pytest.raises(ProviderRateLimitedError):
        search(body=payload(origin="YYZ", includeNearby=True))


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


def test_a_live_search_prunes_cache_entries_past_the_stale_grace_period(monkeypatch):
    use_provider(monkeypatch, FakeProvider([candidate("2026-09-15", 7, 487)]))
    search(body=payload(directOnly=True), now=NOW)

    search(now=NOW + timedelta(seconds=cache.STALE_GRACE_SECONDS + 60))

    with cache._connect() as connection:
        remaining = connection.execute(
            "SELECT COUNT(*) AS total FROM flight_search_cache"
        ).fetchone()["total"]

    assert remaining == 1


def test_health_reports_whether_the_provider_is_configured(monkeypatch):
    use_provider(monkeypatch, FakeProvider())

    assert service.health() == {"status": "ok", "providerConfigured": True}


def test_form_defaults_sit_inside_the_allowed_limits():
    defaults = service.form_defaults(today=TODAY)

    assert defaults["minDate"] == "2026-09-01"
    assert defaults["earliestDeparture"] < defaults["latestDeparture"]
    assert defaults["minNights"] <= defaults["maxNights"]


def test_form_defaults_applies_a_saved_search_from_the_query_string():
    defaults = service.form_defaults(
        today=TODAY,
        query={
            "from": "yyz",
            "to": "sfo",
            "departStart": "2026-09-10",
            "departEnd": "2026-09-20",
            "minNights": "5",
            "maxNights": "12",
            "currency": "usd",
            "direct": "1",
            "nearby": "1",
        },
    )

    assert defaults["origin"] == "YYZ"
    assert defaults["destination"] == "SFO"
    assert defaults["earliestDeparture"] == "2026-09-10"
    assert defaults["latestDeparture"] == "2026-09-20"
    assert defaults["minNights"] == 5
    assert defaults["maxNights"] == 12
    assert defaults["currency"] == "USD"
    assert defaults["directOnly"] is True
    assert defaults["includeNearby"] is True


def test_form_defaults_ignores_unknown_airport_codes_in_the_query_string():
    defaults = service.form_defaults(today=TODAY, query={"from": "ZZZ", "to": "SFO"})

    assert defaults["origin"] == ""
    assert defaults["destination"] == "SFO"


def test_form_defaults_falls_back_on_malformed_query_values():
    defaults = service.form_defaults(
        today=TODAY,
        query={
            "departStart": "not-a-date",
            "minNights": "not-a-number",
            "maxNights": "-5",
            "currency": "XYZ",
        },
    )

    fallback = service.form_defaults(today=TODAY)
    assert defaults["earliestDeparture"] == fallback["earliestDeparture"]
    assert defaults["minNights"] == fallback["minNights"]
    assert defaults["maxNights"] == fallback["maxNights"]
    assert defaults["currency"] == fallback["currency"]


def test_form_defaults_clamps_a_query_window_that_is_too_wide():
    defaults = service.form_defaults(
        today=TODAY,
        query={"departStart": "2026-09-10", "departEnd": "2026-12-25"},
    )

    earliest = date.fromisoformat(defaults["earliestDeparture"])
    latest = date.fromisoformat(defaults["latestDeparture"])
    assert (latest - earliest).days + 1 <= service.validation.MAX_WINDOW_DAYS


def test_page_context_flags_auto_search_only_when_both_places_are_known():
    with_both = service.page_context(today=TODAY, query={"from": "YYZ", "to": "SFO"})
    assert with_both["defaults"]["autoSearch"] is True

    with_one = service.page_context(today=TODAY, query={"from": "YYZ"})
    assert with_one["defaults"]["autoSearch"] is False

    with_none = service.page_context(today=TODAY)
    assert with_none["defaults"]["autoSearch"] is False
