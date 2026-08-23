from datetime import date, datetime, timedelta, timezone

import pytest

from flights import cache, rate_limit
from flights.models import FlightCandidate, SearchRequest

NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def temp_database(tmp_path, monkeypatch):
    monkeypatch.setenv("FLIGHTS_DB_PATH", str(tmp_path / "flights.db"))
    cache.reset_for_tests()
    rate_limit.reset()
    yield
    cache.reset_for_tests()
    rate_limit.reset()


def build_request():
    return SearchRequest(
        origin="YTO",
        destination="SFO",
        earliest_departure=date(2026, 9, 10),
        latest_departure=date(2026, 9, 20),
        min_nights=5,
        max_nights=8,
        currency="CAD",
        direct_only=False,
    )


def build_candidate(price=487):
    return FlightCandidate(
        origin="YYZ",
        destination="SFO",
        departure_date=date(2026, 9, 15),
        return_date=date(2026, 9, 22),
        total_price=price,
        currency="CAD",
        source="test",
        airline_code="AC",
        stops=1,
    )


def test_cache_key_covers_every_field_that_changes_results():
    request = build_request()

    assert request.cache_key("aviasales-data") == (
        "aviasales-data:YTO:SFO:2026-09-10:2026-09-20:5:8:CAD:any"
    )


def test_reading_a_missing_key_returns_nothing():
    assert cache.read("nothing-here", now=NOW) is None


def test_written_entries_read_back_as_fresh():
    cache.write("key", "test", build_request(), {"candidates": []}, now=NOW)

    entry = cache.read("key", now=NOW + timedelta(minutes=5))

    assert entry["is_fresh"] is True
    assert entry["payload"] == {"candidates": []}
    assert entry["fetched_at"] == NOW


def test_entries_past_their_ttl_read_back_as_stale():
    cache.write("key", "test", build_request(), {"candidates": []}, now=NOW)

    entry = cache.read("key", now=NOW + timedelta(seconds=cache.TTL_SECONDS + 1))

    assert entry["is_fresh"] is False


def test_entries_past_the_stale_grace_period_are_discarded():
    cache.write("key", "test", build_request(), {"candidates": []}, now=NOW)

    later = NOW + timedelta(seconds=cache.STALE_GRACE_SECONDS + 1)

    assert cache.read("key", now=later) is None


def test_writing_the_same_key_twice_replaces_the_entry():
    cache.write("key", "test", build_request(), {"round": 1}, now=NOW)
    cache.write("key", "test", build_request(), {"round": 2}, now=NOW)

    assert cache.read("key", now=NOW)["payload"] == {"round": 2}


def test_observations_are_recorded_for_future_price_history():
    written = cache.record_observations([build_candidate(), build_candidate(510)], "test", now=NOW)

    with cache._connect() as connection:
        rows = connection.execute(
            "SELECT origin, destination, price, provider FROM flight_price_observations ORDER BY price"
        ).fetchall()

    assert written == 2
    assert [row["price"] for row in rows] == [487, 510]
    assert rows[0]["origin"] == "YYZ"
    assert rows[0]["provider"] == "test"


def test_search_events_are_recorded_for_local_analytics():
    cache.record_event("YTO", "SFO", cache_hit=True, result_count=7, now=NOW)

    with cache._connect() as connection:
        row = connection.execute("SELECT * FROM flight_search_events").fetchone()

    assert row["origin"] == "YTO"
    assert row["cache_hit"] == 1
    assert row["result_count"] == 7


def test_prune_removes_entries_beyond_the_stale_grace_period():
    cache.write("key", "test", build_request(), {"candidates": []}, now=NOW)

    cache.prune(now=NOW + timedelta(seconds=cache.STALE_GRACE_SECONDS + 60))

    with cache._connect() as connection:
        remaining = connection.execute("SELECT COUNT(*) AS total FROM flight_search_cache").fetchone()

    assert remaining["total"] == 0
