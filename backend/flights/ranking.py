def matches_request(candidate, request):
    if candidate.total_price is None or candidate.total_price <= 0:
        return False
    if candidate.return_date is None:
        return False
    if not request.earliest_departure <= candidate.departure_date <= request.latest_departure:
        return False
    nights = candidate.nights
    if nights is None or not request.min_nights <= nights <= request.max_nights:
        return False
    if request.direct_only and (candidate.stops is None or candidate.stops > 0):
        return False
    return True


def filter_candidates(candidates, request):
    return [candidate for candidate in candidates if matches_request(candidate, request)]


def dedupe(candidates):
    seen = set()
    unique = []
    for candidate in candidates:
        key = candidate.dedupe_key
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def score(candidate):
    return (
        candidate.total_price,
        candidate.stops if candidate.stops is not None else 9,
        candidate.duration_minutes if candidate.duration_minutes is not None else 10**6,
    )


def rank(candidates, limit=None):
    ordered = sorted(candidates, key=score)
    return ordered[:limit] if limit else ordered


def prepare(candidates, request, limit=None):
    return rank(dedupe(filter_candidates(candidates, request)), limit)
