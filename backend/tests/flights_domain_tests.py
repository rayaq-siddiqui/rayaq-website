from datetime import date, timedelta

import pytest

from flights import insights, ranking, validation
from flights.errors import FlightSearchError
from flights.models import FlightCandidate


TODAY = date(2026, 9, 1)


def base_payload(**overrides):
    payload = {
        "origin": "YTO",
        "destination": "SFO",
        "earliestDeparture": "2026-09-10",
        "latestDeparture": "2026-09-20",
        "minNights": 5,
        "maxNights": 8,
        "currency": "CAD",
        "directOnly": False,
    }
    payload.update(overrides)
    return payload


def candidate(departure, nights, price, stops=0, airline="AC", duration=400):
    departure_date = date.fromisoformat(departure)
    return FlightCandidate(
        origin="YTO",
        destination="SFO",
        departure_date=departure_date,
        return_date=departure_date + timedelta(days=nights),
        total_price=price,
        currency="CAD",
        source="test",
        airline_code=airline,
        stops=stops,
        duration_minutes=duration,
    )


def test_parse_builds_a_normalized_request():
    request = validation.parse(base_payload(), today=TODAY)

    assert request.origin == "YTO"
    assert request.destination == "SFO"
    assert request.earliest_departure == date(2026, 9, 10)
    assert request.latest_departure == date(2026, 9, 20)
    assert request.min_nights == 5
    assert request.max_nights == 8
    assert request.currency == "CAD"
    assert request.direct_only is False
    assert request.include_nearby is False


def test_parse_reads_the_include_nearby_flag():
    request = validation.parse(base_payload(includeNearby=True), today=TODAY)

    assert request.include_nearby is True


def test_parse_uppercases_codes_and_defaults_currency():
    request = validation.parse(
        base_payload(origin="yyz", destination="sjc", currency=None), today=TODAY
    )

    assert request.origin == "YYZ"
    assert request.destination == "SJC"
    assert request.currency == "CAD"


def test_parse_rejects_identical_origin_and_destination():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(destination="YTO"), today=TODAY)

    assert error.value.field == "destination"


def test_parse_rejects_unknown_airport():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(origin="ZZZ"), today=TODAY)

    assert "ZZZ" in error.value.message


def test_parse_rejects_reversed_departure_window():
    with pytest.raises(FlightSearchError):
        validation.parse(
            base_payload(earliestDeparture="2026-09-20", latestDeparture="2026-09-10"),
            today=TODAY,
        )


def test_parse_rejects_window_starting_in_the_past():
    with pytest.raises(FlightSearchError):
        validation.parse(
            base_payload(earliestDeparture="2026-08-01", latestDeparture="2026-09-15"),
            today=TODAY,
        )


def test_parse_rejects_window_longer_than_the_maximum():
    with pytest.raises(FlightSearchError):
        validation.parse(
            base_payload(earliestDeparture="2026-09-10", latestDeparture="2026-12-10"),
            today=TODAY,
        )


def test_parse_rejects_min_nights_above_max_nights():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(minNights=9, maxNights=4), today=TODAY)

    assert error.value.field == "minNights"


def test_parse_rejects_trip_length_above_the_maximum():
    with pytest.raises(FlightSearchError):
        validation.parse(base_payload(maxNights=45), today=TODAY)


def test_parse_rejects_unsupported_currency():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(currency="EUR"), today=TODAY)

    assert error.value.field == "currency"


def test_parse_rejects_non_dict_payloads():
    with pytest.raises(FlightSearchError):
        validation.parse("not a payload", today=TODAY)


def test_parse_rejects_a_non_string_origin_instead_of_crashing():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(origin=123), today=TODAY)

    assert error.value.field == "origin"


def test_parse_rejects_a_non_string_destination_instead_of_crashing():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(destination=["SFO"]), today=TODAY)

    assert error.value.field == "destination"


def test_parse_rejects_a_non_string_currency_instead_of_crashing():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(currency=42), today=TODAY)

    assert error.value.field == "currency"


def test_parse_rejects_a_whitespace_only_origin():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(origin="   "), today=TODAY)

    assert error.value.field == "origin"


def test_parse_rejects_a_missing_departure_date():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(earliestDeparture=""), today=TODAY)

    assert error.value.field == "earliestDeparture"


def test_parse_rejects_a_malformed_departure_date():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(latestDeparture="20/09/2026"), today=TODAY)

    assert error.value.field == "latestDeparture"
    assert "YYYY-MM-DD" in error.value.message


def test_parse_rejects_negative_trip_length():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(minNights=-1), today=TODAY)

    assert error.value.field == "minNights"
    assert "negative" in error.value.message


def test_parse_rejects_a_non_numeric_trip_length():
    with pytest.raises(FlightSearchError) as error:
        validation.parse(base_payload(maxNights="a few"), today=TODAY)

    assert error.value.field == "maxNights"
    assert "whole number" in error.value.message


def test_filter_keeps_only_candidates_inside_the_window_and_trip_length():
    request = validation.parse(base_payload(), today=TODAY)
    kept = candidate("2026-09-15", 7, 487)
    outside_window = candidate("2026-09-25", 7, 300)
    too_short = candidate("2026-09-15", 2, 250)

    result = ranking.filter_candidates([kept, outside_window, too_short], request)

    assert result == [kept]


def test_filter_drops_connecting_flights_when_direct_only():
    request = validation.parse(base_payload(directOnly=True), today=TODAY)
    direct = candidate("2026-09-15", 7, 700, stops=0)
    connecting = candidate("2026-09-15", 7, 400, stops=1)

    assert ranking.filter_candidates([direct, connecting], request) == [direct]


def test_filter_drops_one_way_and_non_positive_prices():
    request = validation.parse(base_payload(), today=TODAY)
    one_way = FlightCandidate(
        origin="YTO",
        destination="SFO",
        departure_date=date(2026, 9, 15),
        return_date=None,
        total_price=300,
        currency="CAD",
        source="test",
    )
    free = candidate("2026-09-15", 7, 0)

    assert ranking.filter_candidates([one_way, free], request) == []


def test_a_candidate_without_a_return_date_has_no_nights():
    one_way = FlightCandidate(
        origin="YTO",
        destination="SFO",
        departure_date=date(2026, 9, 15),
        return_date=None,
        total_price=300,
        currency="CAD",
        source="test",
    )

    assert one_way.nights is None


def test_dedupe_key_prefers_the_provider_id_when_one_is_supplied():
    with_id = FlightCandidate(
        origin="YTO",
        destination="SFO",
        departure_date=date(2026, 9, 15),
        return_date=date(2026, 9, 22),
        total_price=487,
        currency="CAD",
        source="test",
        raw_provider_id="ticket-abc123",
    )

    assert with_id.dedupe_key == "ticket-abc123"


def test_dedupe_removes_identical_candidates():
    first = candidate("2026-09-15", 7, 487)
    duplicate = candidate("2026-09-15", 7, 487)
    other = candidate("2026-09-16", 7, 487)

    assert ranking.dedupe([first, duplicate, other]) == [first, other]


def test_dedupe_collapses_the_same_fare_seen_with_and_without_an_airline_code():
    from_prices_for_dates = candidate("2026-09-15", 7, 487, airline="AC")
    from_prices_latest = candidate("2026-09-15", 7, 487, airline=None)

    assert ranking.dedupe([from_prices_for_dates, from_prices_latest]) == [from_prices_for_dates]


def test_rank_sorts_by_price_then_stops_then_duration():
    cheap_connecting = candidate("2026-09-15", 7, 400, stops=1)
    same_price_direct = candidate("2026-09-16", 7, 400, stops=0)
    expensive = candidate("2026-09-17", 7, 900, stops=0)

    ordered = ranking.rank([expensive, cheap_connecting, same_price_direct])

    assert ordered == [same_price_direct, cheap_connecting, expensive]


def test_prepare_filters_dedupes_ranks_and_limits():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [
        candidate("2026-09-16", 7, 620),
        candidate("2026-09-15", 7, 487),
        candidate("2026-09-15", 7, 487),
        candidate("2026-09-25", 7, 100),
    ]

    result = ranking.prepare(candidates, request, limit=2)

    assert [c.total_price for c in result] == [487, 620]


def test_insights_report_the_cheapest_departure_and_date_shift():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [candidate("2026-09-15", 7, 487), candidate("2026-09-16", 7, 569)]

    messages = " ".join(item["message"] for item in insights.build(candidates, request))

    assert "cheapest departure" in messages
    assert "$82" in messages


def test_insights_report_the_cheapest_trip_length():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [
        candidate("2026-09-15", 5, 620),
        candidate("2026-09-15", 7, 487),
        candidate("2026-09-16", 6, 540),
    ]

    types = [item["type"] for item in insights.build(candidates, request)]

    assert "trip_length" in types


def test_insights_stay_silent_on_a_trip_length_difference_too_small_to_act_on():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [
        candidate("2026-09-15", 5, 490),
        candidate("2026-09-15", 7, 487),
    ]

    types = [item["type"] for item in insights.build(candidates, request)]

    assert "trip_length" not in types


def test_insights_report_the_cheapest_weekday():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [
        candidate("2026-09-14", 7, 700),  # Monday
        candidate("2026-09-15", 7, 480),  # Tuesday
        candidate("2026-09-16", 7, 500),  # Wednesday
    ]

    messages = " ".join(item["message"] for item in insights.build(candidates, request))
    types = [item["type"] for item in insights.build(candidates, request)]

    assert "weekday" in types
    assert "Tuesday departures are averaging the lowest prices" in messages


def test_insights_stay_silent_on_a_weekday_split_too_small_to_act_on():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [
        candidate("2026-09-14", 7, 490),  # Monday
        candidate("2026-09-15", 7, 480),  # Tuesday
        candidate("2026-09-16", 7, 487),  # Wednesday
    ]

    types = [item["type"] for item in insights.build(candidates, request)]

    assert "weekday" not in types


def test_insights_stay_silent_on_trivial_differences():
    request = validation.parse(base_payload(), today=TODAY)
    candidates = [candidate("2026-09-15", 7, 487), candidate("2026-09-16", 7, 489)]

    types = [item["type"] for item in insights.build(candidates, request)]

    assert "date_shift" not in types


def test_insights_are_empty_without_candidates():
    request = validation.parse(base_payload(), today=TODAY)

    assert insights.build([], request) == []


def test_date_prices_report_the_cheapest_price_per_departure_day():
    candidates = [
        candidate("2026-09-15", 7, 487),
        candidate("2026-09-15", 6, 610),
        candidate("2026-09-16", 7, 569),
    ]

    assert insights.date_prices(candidates) == [
        {"date": "2026-09-15", "label": "Sep 15", "weekday": "Tue", "price": 487},
        {"date": "2026-09-16", "label": "Sep 16", "weekday": "Wed", "price": 569},
    ]
