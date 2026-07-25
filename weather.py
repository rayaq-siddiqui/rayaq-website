import time

import requests

CITIES = [
    {"name": "San Francisco, CA", "lat": 37.7749, "lon": -122.4194},
    {"name": "Cambridge, ON", "lat": 43.3616, "lon": -80.3144},
    {"name": "San Jose, CA", "lat": 37.3382, "lon": -121.8863},
    {"name": "Toronto, ON", "lat": 43.6532, "lon": -79.3832},
]

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

_CACHE_TTL_SECONDS = 600
_cache = {}


def _fetch_current_weather(lat, lon):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
        },
        timeout=5,
    )
    response.raise_for_status()
    return response.json()["current_weather"]


def get_weather_for_cities():
    results = []
    for city in CITIES:
        cache_key = city["name"]
        cached = _cache.get(cache_key)
        if cached and time.time() - cached["fetched_at"] < _CACHE_TTL_SECONDS:
            current = cached["current"]
        else:
            try:
                current = _fetch_current_weather(city["lat"], city["lon"])
                _cache[cache_key] = {"current": current, "fetched_at": time.time()}
            except requests.RequestException:
                current = None

        results.append(
            {
                "name": city["name"],
                "temperature_c": current["temperature"] if current else None,
                "windspeed_kmh": current["windspeed"] if current else None,
                "description": WEATHER_CODES.get(current["weathercode"], "Unknown")
                if current
                else "Unavailable",
            }
        )
    return results
