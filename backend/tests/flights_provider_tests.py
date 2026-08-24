import json
import os
from datetime import date

import pytest
import requests

from flights.errors import (
    ProviderNotConfiguredError,
    ProviderRateLimitedError,
    ProviderUnavailableError,
)
from flights.models import SearchRequest
from flights.providers import aviasales, get_provider, reset_providers

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "aviasales_prices_for_dates.json")
LATEST_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "aviasales_prices_latest.json")


def fixture_payload():
    with open(FIXTURE_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def latest_fixture_payload():
    with open(LATEST_FIXTURE_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def build_request(**overrides):
    fields = {
        "origin": "YTO",
        "destination": "SFO",
        "earliest_departure": date(2026, 9, 10),
        "latest_departure": date(2026, 9, 20),
        "min_nights": 5,
        "max_nights": 8,
        "currency": "CAD",
        "direct_only": False,
    }
    fields.update(overrides)
    return SearchRequest(**fields)


class FakeResponse:
    def __init__(self, payload=None, status_code=200, body=None):
        self._payload = payload
        self.status_code = status_code
        self.content = body if body is not None else json.dumps(payload or {}).encode()

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


def patch_get(monkeypatch, response, calls=None):
    def fake_get(url, params=None, timeout=None):
        if calls is not None:
            calls.append({"url": url, "params": params, "timeout": timeout})
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(aviasales.requests, "get", fake_get)


def patch_get_by_url(monkeypatch, responses, calls=None):
    def fake_get(url, params=None, timeout=None):
        if calls is not None:
            calls.append({"url": url, "params": params, "timeout": timeout})
        return responses[url]

    monkeypatch.setattr(aviasales.requests, "get", fake_get)


def test_provider_reports_when_no_token_is_configured():
    assert aviasales.AviasalesDataProvider(token="").is_configured() is False
    assert aviasales.AviasalesDataProvider(token="secret").is_configured() is True


def test_search_without_a_token_raises_not_configured():
    provider = aviasales.AviasalesDataProvider(token="")

    with pytest.raises(ProviderNotConfiguredError):
        provider.search_flexible_dates(build_request())


def test_fixture_normalizes_into_flight_candidates(monkeypatch):
    patch_get(monkeypatch, FakeResponse(fixture_payload()))
    provider = aviasales.AviasalesDataProvider(token="secret", marker="")

    result = provider.search_flexible_dates(build_request())

    assert result.provider == "aviasales-data"
    assert result.is_live is False
    assert len(result.candidates) == 3

    best = result.candidates[0]
    assert best.origin == "YYZ"
    assert best.destination == "SFO"
    assert best.departure_date == date(2026, 9, 15)
    assert best.return_date == date(2026, 9, 22)
    assert best.total_price == 487.0
    assert best.currency == "CAD"
    assert best.airline_code == "AC"
    assert best.flight_number == "759"
    assert best.stops == 1
    assert best.duration_minutes == 745
    assert best.nights == 7
    assert best.booking_url == "https://www.aviasales.com/search/YYZ1509SFO22091?t=abc123"


def test_tickets_without_a_usable_price_are_dropped(monkeypatch):
    patch_get(monkeypatch, FakeResponse(fixture_payload()))
    provider = aviasales.AviasalesDataProvider(token="secret")

    prices = [c.total_price for c in provider.search_flexible_dates(build_request()).candidates]

    assert None not in prices
    assert 199 in prices


def test_numeric_flight_numbers_normalize_to_strings(monkeypatch):
    patch_get(monkeypatch, FakeResponse(fixture_payload()))
    provider = aviasales.AviasalesDataProvider(token="secret")

    candidates = provider.search_flexible_dates(build_request()).candidates

    assert candidates[1].flight_number == "512"


def test_missing_links_fall_back_to_a_route_search_url(monkeypatch):
    patch_get(monkeypatch, FakeResponse(fixture_payload()))
    provider = aviasales.AviasalesDataProvider(token="secret", marker="")

    candidates = provider.search_flexible_dates(build_request()).candidates

    assert candidates[1].booking_url == "https://www.aviasales.com/search/YYZ1609SFO23091"


def test_the_affiliate_marker_is_appended_when_configured(monkeypatch):
    patch_get(monkeypatch, FakeResponse(fixture_payload()))
    provider = aviasales.AviasalesDataProvider(token="secret", marker="12345")

    candidates = provider.search_flexible_dates(build_request()).candidates

    assert candidates[0].booking_url.endswith("&marker=12345")
    assert candidates[1].booking_url.endswith("?marker=12345")


def test_one_upstream_request_is_made_per_month_in_the_window(monkeypatch):
    calls = []
    patch_get(monkeypatch, FakeResponse({"success": True, "data": []}), calls)
    provider = aviasales.AviasalesDataProvider(token="secret")

    result = provider.search_flexible_dates(
        build_request(earliest_departure=date(2026, 9, 25), latest_departure=date(2026, 10, 5))
    )

    month_calls = [call for call in calls if call["url"] == aviasales.API_URL]
    latest_calls = [call for call in calls if call["url"] == aviasales.LATEST_URL]

    assert [call["params"]["departure_at"] for call in month_calls] == ["2026-09", "2026-10"]
    assert len(latest_calls) == 1
    assert result.provider_requests == 3


def test_the_latest_prices_endpoint_is_also_queried_once_per_search(monkeypatch):
    calls = []
    patch_get(monkeypatch, FakeResponse({"success": True, "data": []}), calls)
    provider = aviasales.AviasalesDataProvider(token="secret")

    provider.search_flexible_dates(build_request())

    latest_calls = [call for call in calls if call["url"] == aviasales.LATEST_URL]
    assert len(latest_calls) == 1
    assert latest_calls[0]["params"]["origin"] == "YTO"
    assert latest_calls[0]["params"]["destination"] == "SFO"
    assert latest_calls[0]["params"]["currency"] == "cad"


def test_latest_prices_fill_in_a_route_the_month_endpoint_has_thin_data_for(monkeypatch):
    patch_get_by_url(
        monkeypatch,
        {
            aviasales.API_URL: FakeResponse({"success": True, "data": []}),
            aviasales.LATEST_URL: FakeResponse(latest_fixture_payload()),
        },
    )
    provider = aviasales.AviasalesDataProvider(token="secret", marker="")

    candidates = provider.search_flexible_dates(build_request()).candidates

    assert len(candidates) == 2
    best = candidates[0]
    assert best.origin == "YTO"
    assert best.destination == "SFO"
    assert best.departure_date == date(2026, 10, 9)
    assert best.return_date == date(2026, 10, 12)
    assert best.total_price == 594.0
    assert best.stops == 1
    assert best.duration_minutes == 1030
    assert best.found_at == "2026-08-18T20:58:17"
    assert best.booking_url == "https://www.aviasales.com/search/YTO0910SFO12101"


def test_latest_prices_hidden_from_affiliates_or_marked_stale_are_dropped(monkeypatch):
    patch_get_by_url(
        monkeypatch,
        {
            aviasales.API_URL: FakeResponse({"success": True, "data": []}),
            aviasales.LATEST_URL: FakeResponse(latest_fixture_payload()),
        },
    )
    provider = aviasales.AviasalesDataProvider(token="secret")

    prices = [c.total_price for c in provider.search_flexible_dates(build_request()).candidates]

    assert 410 not in prices
    assert 399 not in prices
    assert None not in prices


def test_direct_only_searches_ask_the_provider_for_direct_flights(monkeypatch):
    calls = []
    patch_get(monkeypatch, FakeResponse({"success": True, "data": []}), calls)
    provider = aviasales.AviasalesDataProvider(token="secret")

    provider.search_flexible_dates(build_request(direct_only=True))

    assert calls[0]["params"]["direct"] == "true"
    assert calls[0]["params"]["currency"] == "cad"
    assert calls[0]["params"]["one_way"] == "false"
    assert calls[0]["timeout"] == aviasales.TIMEOUT_SECONDS


def test_rate_limited_responses_raise_a_rate_limit_error(monkeypatch):
    patch_get(monkeypatch, FakeResponse({}, status_code=429))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderRateLimitedError):
        provider.search_flexible_dates(build_request())


def test_error_responses_raise_provider_unavailable(monkeypatch):
    patch_get(monkeypatch, FakeResponse({}, status_code=500))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderUnavailableError):
        provider.search_flexible_dates(build_request())


def test_network_failures_raise_provider_unavailable(monkeypatch):
    patch_get(monkeypatch, requests.RequestException("boom"))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderUnavailableError):
        provider.search_flexible_dates(build_request())


def test_unparseable_bodies_raise_provider_unavailable(monkeypatch):
    patch_get(monkeypatch, FakeResponse(None, body=b"<html>nope</html>"))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderUnavailableError):
        provider.search_flexible_dates(build_request())


def test_unsuccessful_payloads_raise_provider_unavailable(monkeypatch):
    patch_get(monkeypatch, FakeResponse({"success": False}))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderUnavailableError):
        provider.search_flexible_dates(build_request())


def test_oversized_payloads_are_refused(monkeypatch):
    oversized = b"x" * (aviasales.MAX_RESPONSE_BYTES + 1)
    patch_get(monkeypatch, FakeResponse({"success": True, "data": []}, body=oversized))
    provider = aviasales.AviasalesDataProvider(token="secret")

    with pytest.raises(ProviderUnavailableError):
        provider.search_flexible_dates(build_request())


def test_the_registry_returns_the_aviasales_provider(monkeypatch):
    monkeypatch.setenv("TRAVELPAYOUTS_API_TOKEN", "secret")
    reset_providers()

    provider = get_provider()

    assert provider.name == "aviasales-data"
    assert provider is get_provider()
    reset_providers()
