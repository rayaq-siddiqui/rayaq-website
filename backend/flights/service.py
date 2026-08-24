import json
import logging
import time
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

from . import airports, cache, insights, ranking, rate_limit, validation
from .errors import ProviderError
from .models import SUPPORTED_CURRENCIES
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


def page_context(today=None):
    return {
        "defaults": form_defaults(today),
        "popular_routes": POPULAR_ROUTES,
        "currencies": SUPPORTED_CURRENCIES,
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


def _search_pairs(request):
    pairs = [(request.origin, request.destination)]
    if not request.include_nearby:
        return pairs
    for alt in airports.nearby(request.origin):
        pairs.append((alt["code"], request.destination))
    for alt in airports.nearby(request.destination):
        pairs.append((request.origin, alt["code"]))
    return pairs


def _airport_note(candidate, request):
    parts = []
    if candidate.origin != request.origin:
        parts.append(f"from {airports.label(candidate.origin)}")
    if candidate.destination != request.destination:
        parts.append(f"to {airports.label(candidate.destination)}")
    return " ".join(parts) if parts else None


def _candidate_api(candidate, request):
    data = candidate.to_api()
    data["airportNote"] = _airport_note(candidate, request)
    return data


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
        "best": _candidate_api(top[0], request) if top else None,
        "candidates": [_candidate_api(candidate, request) for candidate in top],
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
        raw_candidates = []
        provider_requests = 0
        for origin, destination in _search_pairs(request):
            sub_request = replace(request, origin=origin, destination=destination)
            provider_result = provider.search_flexible_dates(sub_request)
            raw_candidates.extend(provider_result.candidates)
            provider_requests += provider_result.provider_requests
    except ProviderError:
        if cached:
            return finish(_with_metadata(cached["payload"], True, 0, stale=True), True, 0, "stale")
        raise

    searched_at = now or datetime.now(timezone.utc)
    candidates = ranking.prepare(raw_candidates, request)
    result = _build_payload(request, provider, candidates, searched_at)

    cache.write(cache_key, provider.name, request, result, now=now)
    cache.record_observations(candidates[:MAX_CANDIDATES], provider.name, now=now)
    cache.prune(now=now)

    return finish(
        _with_metadata(result, False, provider_requests),
        False,
        provider_requests,
        "live",
    )
