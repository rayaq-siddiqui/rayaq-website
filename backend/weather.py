import time
from datetime import datetime

import requests

CITIES = [
    {"name": "San Francisco, CA", "lat": 37.7749, "lon": -122.4194},
    {"name": "Cambridge, ON", "lat": 43.3616, "lon": -80.3144},
    {"name": "San Jose, CA", "lat": 37.3382, "lon": -121.8863},
    {"name": "Toronto, ON", "lat": 43.6532, "lon": -79.3832},
]

WEATHER_DESCRIPTIONS = {
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

WEATHER_EMOJIS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌦️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "❄️",
    73: "❄️",
    75: "❄️",
    80: "🌦️",
    81: "🌦️",
    82: "🌦️",
    95: "⛈️",
}
UNKNOWN_EMOJI = "🤷"

_CACHE_TTL_SECONDS = 60 * 60
_cache = {}


def _emoji_for_code(code):
    return WEATHER_EMOJIS.get(code, UNKNOWN_EMOJI)


def _fetch_weather(lat, lon):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "daily": "temperature_2m_max,temperature_2m_min",
            "hourly": "temperature_2m,weathercode",
            "forecast_days": 1,
            "timezone": "auto",
        },
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "current": data["current_weather"],
        "high_c": data["daily"]["temperature_2m_max"][0],
        "low_c": data["daily"]["temperature_2m_min"][0],
        "hourly_times": data["hourly"]["time"],
        "hourly_temps": data["hourly"]["temperature_2m"],
        "hourly_codes": data["hourly"]["weathercode"],
    }


def _format_local_time(iso_time, fmt="%-I:%M %p"):
    return datetime.fromisoformat(iso_time).strftime(fmt)


def _build_hourly(weather):
    return [
        {
            "label": _format_local_time(t, "%-I %p"),
            "temp_c": round(temp),
            "emoji": _emoji_for_code(code),
        }
        for t, temp, code in zip(
            weather["hourly_times"], weather["hourly_temps"], weather["hourly_codes"]
        )
    ]


def get_weather_for_cities():
    results = []
    for city in CITIES:
        cache_key = city["name"]
        cached = _cache.get(cache_key)
        if cached and time.time() - cached["fetched_at"] < _CACHE_TTL_SECONDS:
            weather = cached["weather"]
        else:
            try:
                weather = _fetch_weather(city["lat"], city["lon"])
                _cache[cache_key] = {"weather": weather, "fetched_at": time.time()}
            except (requests.RequestException, KeyError, IndexError):
                weather = None

        if weather:
            code = weather["current"]["weathercode"]
            results.append(
                {
                    "name": city["name"],
                    "local_time": _format_local_time(weather["current"]["time"]),
                    "temperature_c": round(weather["current"]["temperature"]),
                    "high_c": round(weather["high_c"]),
                    "low_c": round(weather["low_c"]),
                    "windspeed_kmh": weather["current"]["windspeed"],
                    "description": WEATHER_DESCRIPTIONS.get(code, "Unknown"),
                    "emoji": _emoji_for_code(code),
                    "hourly": _build_hourly(weather),
                }
            )
        else:
            results.append(
                {
                    "name": city["name"],
                    "local_time": None,
                    "temperature_c": None,
                    "high_c": None,
                    "low_c": None,
                    "windspeed_kmh": None,
                    "description": "Weather unavailable",
                    "emoji": UNKNOWN_EMOJI,
                    "hourly": [],
                }
            )
    return results
