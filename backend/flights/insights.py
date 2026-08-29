from collections import defaultdict

MAX_INSIGHTS = 4
MIN_MEANINGFUL_SAVING = 15


def _money(amount, currency):
    return f"${amount:,.0f} {currency}"


def _long_date(value):
    return value.strftime("%a %b %-d")


def _cheapest_by(candidates, key):
    cheapest = {}
    for candidate in candidates:
        group = key(candidate)
        current = cheapest.get(group)
        if current is None or candidate.total_price < current.total_price:
            cheapest[group] = candidate
    return cheapest


def _cheapest_departure(candidates, currency):
    by_date = _cheapest_by(candidates, lambda c: c.departure_date)
    if len(by_date) < 2:
        return None
    best_date = min(by_date, key=lambda d: by_date[d].total_price)
    best = by_date[best_date]
    return {
        "type": "cheapest_departure",
        "message": (
            f"The cheapest departure in your window is {_long_date(best_date)} "
            f"at {_money(best.total_price, currency)}."
        ),
    }


def _neighbour_saving(candidates, currency):
    by_date = _cheapest_by(candidates, lambda c: c.departure_date)
    if len(by_date) < 2:
        return None
    ordered = sorted(by_date)
    best_date = min(by_date, key=lambda d: by_date[d].total_price)
    best_price = by_date[best_date].total_price

    position = ordered.index(best_date)
    neighbours = [ordered[i] for i in (position - 1, position + 1) if 0 <= i < len(ordered)]
    neighbour = max(neighbours, key=lambda d: by_date[d].total_price)
    saving = by_date[neighbour].total_price - best_price
    if saving < MIN_MEANINGFUL_SAVING:
        return None

    return {
        "type": "date_shift",
        "message": (
            f"Leaving {_long_date(best_date)} instead of {_long_date(neighbour)} "
            f"saves about {_money(saving, currency)}."
        ),
    }


def _best_trip_length(candidates, currency):
    by_nights = _cheapest_by(candidates, lambda c: c.nights)
    if len(by_nights) < 2:
        return None
    best_nights = min(by_nights, key=lambda n: by_nights[n].total_price)
    best_price = by_nights[best_nights].total_price
    runner_up = min(
        (n for n in by_nights if n != best_nights),
        key=lambda n: by_nights[n].total_price,
    )
    if by_nights[runner_up].total_price - best_price < MIN_MEANINGFUL_SAVING:
        return None

    return {
        "type": "trip_length",
        "message": (
            f"{best_nights}-night trips are the cheapest length in this window, "
            f"from {_money(best_price, currency)}."
        ),
    }


def _cheapest_weekday(candidates):
    totals = defaultdict(list)
    for candidate in candidates:
        totals[candidate.departure_date.strftime("%A")].append(candidate.total_price)
    if len(totals) < 3:
        return None
    averages = {day: sum(prices) / len(prices) for day, prices in totals.items()}
    best_day = min(averages, key=averages.get)
    worst_day = max(averages, key=averages.get)
    if averages[worst_day] - averages[best_day] < MIN_MEANINGFUL_SAVING:
        return None

    return {
        "type": "weekday",
        "message": f"{best_day} departures are averaging the lowest prices in this window.",
    }


def build(candidates, request):
    if not candidates:
        return []

    currency = request.currency
    generated = [
        _cheapest_departure(candidates, currency),
        _neighbour_saving(candidates, currency),
        _best_trip_length(candidates, currency),
        _cheapest_weekday(candidates),
    ]
    return [insight for insight in generated if insight][:MAX_INSIGHTS]


def date_prices(candidates):
    by_date = _cheapest_by(candidates, lambda c: c.departure_date)
    return [
        {
            "date": day.isoformat(),
            "label": day.strftime("%b %-d"),
            "weekday": day.strftime("%a"),
            "price": by_date[day].total_price,
        }
        for day in sorted(by_date)
    ]
