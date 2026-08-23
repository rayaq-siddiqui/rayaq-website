import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "var", "flights.db")
TTL_SECONDS = 45 * 60
STALE_GRACE_SECONDS = 24 * 60 * 60

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS flight_search_cache (
        cache_key TEXT PRIMARY KEY,
        provider TEXT NOT NULL,
        request_json TEXT NOT NULL,
        response_json TEXT NOT NULL,
        fetched_at TEXT NOT NULL,
        expires_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS flight_price_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        return_date TEXT,
        price REAL NOT NULL,
        currency TEXT NOT NULL,
        airline_code TEXT,
        stops INTEGER,
        provider TEXT NOT NULL,
        observed_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS flight_search_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT,
        destination TEXT,
        searched_at TEXT NOT NULL,
        cache_hit INTEGER NOT NULL,
        result_count INTEGER NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS flight_observations_route ON flight_price_observations (origin, destination, departure_date)",
)

_initialized = set()


def db_path():
    return os.environ.get("FLIGHTS_DB_PATH") or DEFAULT_DB_PATH


def _connect():
    path = db_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    if path not in _initialized:
        connection.execute("PRAGMA journal_mode=WAL")
        for statement in SCHEMA:
            connection.execute(statement)
        connection.commit()
        _initialized.add(path)
    return connection


def reset_for_tests():
    _initialized.clear()


def _now(now=None):
    return now or datetime.now(timezone.utc)


def _iso(value):
    return value.astimezone(timezone.utc).isoformat()


def _parse(value):
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def read(cache_key, now=None):
    now = _now(now)
    try:
        with _connect() as connection:
            row = connection.execute(
                "SELECT response_json, fetched_at, expires_at FROM flight_search_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
    except sqlite3.Error:
        return None

    if row is None:
        return None

    try:
        payload = json.loads(row["response_json"])
        fetched_at = _parse(row["fetched_at"])
        expires_at = _parse(row["expires_at"])
    except (ValueError, TypeError):
        return None

    if now - fetched_at > timedelta(seconds=STALE_GRACE_SECONDS):
        return None

    return {"payload": payload, "fetched_at": fetched_at, "is_fresh": now < expires_at}


def write(cache_key, provider, request, payload, now=None, ttl_seconds=TTL_SECONDS):
    now = _now(now)
    try:
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO flight_search_cache
                    (cache_key, provider, request_json, response_json, fetched_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    response_json = excluded.response_json,
                    fetched_at = excluded.fetched_at,
                    expires_at = excluded.expires_at
                """,
                (
                    cache_key,
                    provider,
                    json.dumps(request.to_api()),
                    json.dumps(payload),
                    _iso(now),
                    _iso(now + timedelta(seconds=ttl_seconds)),
                ),
            )
    except sqlite3.Error:
        return False
    return True


def record_observations(candidates, provider, now=None):
    if not candidates:
        return 0
    now = _now(now)
    rows = [
        (
            candidate.origin,
            candidate.destination,
            candidate.departure_date.isoformat(),
            candidate.return_date.isoformat() if candidate.return_date else None,
            candidate.total_price,
            candidate.currency,
            candidate.airline_code,
            candidate.stops,
            provider,
            _iso(now),
        )
        for candidate in candidates
    ]
    try:
        with _connect() as connection:
            connection.executemany(
                """
                INSERT INTO flight_price_observations
                    (origin, destination, departure_date, return_date, price, currency,
                     airline_code, stops, provider, observed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
    except sqlite3.Error:
        return 0
    return len(rows)


def record_event(origin, destination, cache_hit, result_count, now=None):
    try:
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO flight_search_events
                    (origin, destination, searched_at, cache_hit, result_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (origin, destination, _iso(_now(now)), 1 if cache_hit else 0, result_count),
            )
    except sqlite3.Error:
        return False
    return True


def prune(now=None):
    cutoff = _iso(_now(now) - timedelta(seconds=STALE_GRACE_SECONDS))
    try:
        with _connect() as connection:
            connection.execute("DELETE FROM flight_search_cache WHERE fetched_at < ?", (cutoff,))
    except sqlite3.Error:
        return False
    return True
