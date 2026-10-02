import requests

import weather


def make_weather(temp=20.0, code=1, high=25.0, low=15.0):
    return {
        "current": {
            "time": "2026-07-24T15:30",
            "temperature": temp,
            "windspeed": 10.0,
            "weathercode": code,
        },
        "high_c": high,
        "low_c": low,
        "hourly_times": ["2026-07-24T00:00", "2026-07-24T01:00"],
        "hourly_temps": [18.4, 17.6],
        "hourly_codes": [0, 61],
    }


def test_emoji_for_known_code():
    assert weather._emoji_for_code(0) == "☀️"


def test_emoji_for_unknown_code():
    assert weather._emoji_for_code(999) == weather.UNKNOWN_EMOJI


def test_format_local_time_default():
    assert weather._format_local_time("2026-07-24T15:30") == "3:30 PM"


def test_format_local_time_custom_format():
    assert weather._format_local_time("2026-07-24T09:00", "%-I %p") == "9 AM"


def test_build_hourly_rounds_temps_and_maps_emoji():
    hourly = weather._build_hourly(make_weather())
    assert hourly == [
        {"label": "12 AM", "temp_c": 18, "emoji": "☀️"},
        {"label": "1 AM", "temp_c": 18, "emoji": "🌧️"},
    ]


def test_get_weather_for_cities_returns_all_cities(monkeypatch):
    weather._cache.clear()
    monkeypatch.setattr(weather, "_fetch_weather", lambda lat, lon: make_weather())

    results = weather.get_weather_for_cities()

    assert [city["name"] for city in results] == [c["name"] for c in weather.CITIES]
    assert results[0]["temperature_c"] == 20
    assert results[0]["high_c"] == 25
    assert results[0]["low_c"] == 15
    assert results[0]["description"] == "Mainly clear"
    assert len(results[0]["hourly"]) == 2


def test_get_weather_for_cities_uses_cache_within_ttl(monkeypatch):
    weather._cache.clear()
    call_count = {"n": 0}

    def fake_fetch(lat, lon):
        call_count["n"] += 1
        return make_weather()

    monkeypatch.setattr(weather, "_fetch_weather", fake_fetch)

    weather.get_weather_for_cities()
    weather.get_weather_for_cities()

    assert call_count["n"] == len(weather.CITIES)


def test_weather_is_cached_for_three_hours(monkeypatch):
    weather._cache.clear()
    call_count = {"n": 0}
    now = {"t": 1_000_000.0}

    def fake_fetch(lat, lon):
        call_count["n"] += 1
        return make_weather()

    monkeypatch.setattr(weather, "_fetch_weather", fake_fetch)
    monkeypatch.setattr(weather.time, "time", lambda: now["t"])

    weather.get_weather_for_cities()
    now["t"] += 3 * 60 * 60 - 1
    weather.get_weather_for_cities()
    assert call_count["n"] == len(weather.CITIES)

    now["t"] += 1
    weather.get_weather_for_cities()
    assert call_count["n"] == len(weather.CITIES) * 2


def test_get_weather_for_cities_refetches_after_ttl_expires(monkeypatch):
    weather._cache.clear()
    call_count = {"n": 0}

    def fake_fetch(lat, lon):
        call_count["n"] += 1
        return make_weather()

    monkeypatch.setattr(weather, "_fetch_weather", fake_fetch)
    monkeypatch.setattr(weather, "_CACHE_TTL_SECONDS", 0)

    weather.get_weather_for_cities()
    weather.get_weather_for_cities()

    assert call_count["n"] == len(weather.CITIES) * 2


def test_get_weather_for_cities_handles_fetch_failure(monkeypatch):
    weather._cache.clear()

    def failing_fetch(lat, lon):
        raise requests.RequestException("boom")

    monkeypatch.setattr(weather, "_fetch_weather", failing_fetch)

    results = weather.get_weather_for_cities()

    assert all(city["temperature_c"] is None for city in results)
    assert all(city["description"] == "Weather unavailable" for city in results)
    assert all(city["emoji"] == weather.UNKNOWN_EMOJI for city in results)
