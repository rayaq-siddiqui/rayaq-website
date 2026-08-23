import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "airports.json")
MAX_RESULTS = 8

_airports = None
_by_code = None


def _load():
    global _airports, _by_code
    if _airports is None:
        with open(DATA_PATH, encoding="utf-8") as handle:
            _airports = json.load(handle)
        _by_code = {entry["code"]: entry for entry in _airports}
    return _airports


def all_airports():
    return list(_load())


def find(code):
    _load()
    return _by_code.get((code or "").strip().upper())


def is_known(code):
    return find(code) is not None


def _match_rank(entry, query):
    code = entry["code"]
    city = entry["city"].lower()
    name = entry["name"].lower()
    country = entry["country"].lower()

    if code.lower() == query:
        return 0
    if city == query:
        return 1
    if city.startswith(query):
        return 2
    if code.lower().startswith(query):
        return 3
    if name.startswith(query):
        return 4
    if query in name or query in city:
        return 5
    if query in country:
        return 6
    return None


def search(query, limit=MAX_RESULTS):
    query = (query or "").strip().lower()
    if len(query) < 2:
        return []

    scored = []
    for entry in _load():
        rank = _match_rank(entry, query)
        if rank is not None:
            scored.append((rank, 0 if entry["type"] == "city" else 1, entry["city"], entry))

    scored.sort(key=lambda row: row[:3])
    return [row[3] for row in scored[:limit]]


def label(code):
    entry = find(code)
    if entry is None:
        return code
    if entry["type"] == "city":
        return entry["city"]
    return f"{entry['city']} ({entry['code']})"
