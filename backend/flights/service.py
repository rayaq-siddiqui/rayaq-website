import json
import logging
import time
from datetime import date, datetime, timedelta, timezone

from . import airports, cache, insights, ranking, rate_limit, validation
from .errors import ProviderError
from .providers import get_provider

MAX_CANDIDATES = 10
NO_RESULTS_MESSAGE = "No recently observed fares were available for this search."
STALE_MESSAGE = (
    "Showing previously observed prices because the flight-data service is "
    "temporarily unavailable."
)

POPULAR_ROUTES = (
    {"origin": "YTO", "destination": "SFO", "label": "Toronto → San Francisco"},
    {"origin": "SFO", "destination": "YTO", "label": "San Francisco → Toronto"},
    {"origin": "YTO", "destination": "SJC", "label": "Toronto → San Jose"},
    {"origin": "YTO", "destination": "LHR", "label": "Toronto → London"},
)

logger = logging.getLogger("flights")


def form_defaults(today=None):
    today = today or date.today()
    return {
        "earliestDeparture": (today + timedelta(days=30)).isoformat(),
        "latestDeparture": (today + timedelta(days=44)).isoformat(),
        "minNights": 5,
        "maxNights": 8,
        "currency": validation.DEFAULT_CURRENCY,
        "directOnly": False,
        "maxWindowDays": validation.MAX_WINDOW_DAYS,
        "maxNightsAllowed": validation.MAX_NIGHTS,
        "minDate": today.isoformat(),
    }


def health():
    provider = get_provider()
    return {"status": "ok", "providerConfigured": provider.is_configured()}


def _place(code):
    entry = airports.find(code)
    if entry is None:
        return {"code": code, "label": code, "city": code, "country": None}
    return {
        "code": entry["code"],
        "label": airports.label(code),
        "city": entry["city"],
        "country": entry["country"],
    }


def _build_payload(request, provider, candidates, searched_at):
    top = candidates[:MAX_CANDIDATES]
    return {
        "provider": provider.name,
        "searchedAt": searched_at.isoformat(),
        "isLive": provider.is_live,
        "freshnessMessage": provider.freshness_message,
        "request": request.to_api(),
        "places": {
            "origin": _place(request.origin),
            "destination": _place(request.destination),
        },
        "best": top[0].to_api() if top else None,
        "candidates": [candidate.to_api() for candidate in top],
        "datePrices": insights.date_prices(candidates),
        "insights": insights.build(candidates, request),
        "message": None if top else NO_RESULTS_MESSAGE,
    }


def _with_metadata(payload, cache_hit, provider_requests, stale=False):
    result = dict(payload)
    result["metadata"] = {
        "cacheHit": cache_hit,
        "providerRequests": provider_requests,
        "stale": stale,
    }
    if stale:
        result["message"] = STALE_MESSAGE
    return result


def _log(request, cache_hit, provider_requests, result_count, duration_ms, status):
    logger.info(
        json.dumps(
            {
                "event": "flight_search",
                "origin": request.origin,
                "destination": request.destination,
                "cacheHit": cache_hit,
                "provider": get_provider().name,
                "providerRequests": provider_requests,
                "resultCount": result_count,
                "durationMs": duration_ms,
                "status": status,
            }
        )
    )


def search(payload, client_id=None, today=None, now=None):
    started = time.perf_counter()
    rate_limit.check(client_id)
    request = validation.parse(payload, today=today)

    provider = get_provider()
    cache_key = request.cache_key(provider.name)
    cached = cache.read(cache_key, now=now)

    def finish(result, cache_hit, provider_requests, status):
        count = len(result["candidates"])
        duration_ms = round((time.perf_counter() - started) * 1000)
        cache.record_event(request.origin, request.destination, cache_hit, count, now=now)
        _log(request, cache_hit, provider_requests, count, duration_ms, status)
        return result

    if cached and cached["is_fresh"]:
        return finish(_with_metadata(cached["payload"], True, 0), True, 0, "cache")

    try:
        provider_result = provider.search_flexible_dates(request)
    except ProviderError:
        if cached:
            return finish(_with_metadata(cached["payload"], True, 0, stale=True), True, 0, "stale")
        raise

    searched_at = now or datetime.now(timezone.utc)
    candidates = ranking.prepare(provider_result.candidates, request)
    result = _build_payload(request, provider, candidates, searched_at)

    cache.write(cache_key, provider.name, request, result, now=now)
    cache.record_observations(candidates[:MAX_CANDIDATES], provider.name, now=now)

    return finish(
        _with_metadata(result, False, provider_result.provider_requests),
        False,
        provider_result.provider_requests,
        "live",
    )
