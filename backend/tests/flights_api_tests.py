from datetime import date, timedelta

import pytest

import app as app_module
from flights import api as flights_api
from flights import cache, rate_limit, service
from flights.errors import ProviderUnavailableError
from flights.models import FlightCandidate, ProviderResult


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

    def is_configured(self):
        return True

    def search_flexible_dates(self, request):
        if self.error:
            raise self.error
        return ProviderResult(self.name, self.candidates, self.is_live, 1)


def use_provider(monkeypatch, provider):
    monkeypatch.setattr(service, "get_provider", lambda name=None: provider)
    return provider


def future_payload(**overrides):
    earliest = date.today() + timedelta(days=30)
    body = {
        "origin": "YTO",
        "destination": "SFO",
        "earliestDeparture": earliest.isoformat(),
        "latestDeparture": (earliest + timedelta(days=10)).isoformat(),
        "minNights": 5,
        "maxNights": 8,
        "currency": "CAD",
        "directOnly": False,
    }
    body.update(overrides)
    return body


def sample_candidate(body, price=487, nights=7):
    departure = date.fromisoformat(body["earliestDeparture"]) + timedelta(days=2)
    return FlightCandidate(
        origin="YYZ",
        destination="SFO",
        departure_date=departure,
        return_date=departure + timedelta(days=nights),
        total_price=price,
        currency="CAD",
        source="fake-provider",
        airline_code="AC",
        stops=1,
        booking_url="https://www.aviasales.com/search/example",
    )


def test_airport_autocomplete_returns_matches():
    client = app_module.app.test_client()

    response = client.get("/api/flights/airports?q=toronto")

    assert response.status_code == 200
    codes = [entry["code"] for entry in response.get_json()["results"]]
    assert "YYZ" in codes


def test_airport_autocomplete_returns_nothing_for_short_queries():
    client = app_module.app.test_client()

    response = client.get("/api/flights/airports?q=t")

    assert response.get_json() == {"results": []}


def test_flights_health_reports_provider_configuration_without_secrets(monkeypatch):
    monkeypatch.setenv("TRAVELPAYOUTS_API_TOKEN", "super-secret")
    use_provider(monkeypatch, FakeProvider())
    client = app_module.app.test_client()

    response = client.get("/api/flights/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "providerConfigured": True}
    assert "super-secret" not in response.get_data(as_text=True)


def test_search_returns_ranked_results(monkeypatch):
    body = future_payload()
    use_provider(monkeypatch, FakeProvider([sample_candidate(body)]))
    client = app_module.app.test_client()

    response = client.post("/api/flights/search", json=body)

    assert response.status_code == 200
    result = response.get_json()
    assert result["best"]["totalPrice"] == 487
    assert result["freshnessMessage"]
    assert result["isLive"] is False


def test_search_rejects_invalid_input_with_400(monkeypatch):
    use_provider(monkeypatch, FakeProvider())
    client = app_module.app.test_client()

    response = client.post("/api/flights/search", json=future_payload(destination="YTO"))

    assert response.status_code == 400
    assert response.get_json()["field"] == "destination"


def test_search_rejects_a_missing_body(monkeypatch):
    use_provider(monkeypatch, FakeProvider())
    client = app_module.app.test_client()

    response = client.post("/api/flights/search")

    assert response.status_code == 400


def test_search_reports_no_results_with_200(monkeypatch):
    use_provider(monkeypatch, FakeProvider([]))
    client = app_module.app.test_client()

    response = client.post("/api/flights/search", json=future_payload())

    assert response.status_code == 200
    result = response.get_json()
    assert result["candidates"] == []
    assert result["message"] == service.NO_RESULTS_MESSAGE


def test_search_returns_503_when_the_provider_is_unavailable(monkeypatch):
    use_provider(monkeypatch, FakeProvider(error=ProviderUnavailableError()))
    client = app_module.app.test_client()

    response = client.post("/api/flights/search", json=future_payload())

    assert response.status_code == 503
    assert "temporarily unavailable" in response.get_json()["error"]


def test_search_returns_429_once_the_client_limit_is_reached(monkeypatch):
    body = future_payload()
    use_provider(monkeypatch, FakeProvider([sample_candidate(body)]))
    client = app_module.app.test_client()

    for offset in range(rate_limit.PER_MINUTE):
        client.post("/api/flights/search", json=future_payload(minNights=offset % 4))

    response = client.post("/api/flights/search", json=future_payload(maxNights=9))

    assert response.status_code == 429


def test_the_forwarded_client_address_identifies_the_caller():
    assert flights_api.client_id("203.0.113.7, 10.0.0.1", "10.0.0.1") == "203.0.113.7"
    assert flights_api.client_id(None, "10.0.0.1") == "10.0.0.1"
