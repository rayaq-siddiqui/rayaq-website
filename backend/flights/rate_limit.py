import threading
import time
from collections import defaultdict, deque

from .errors import TooManyRequestsError

PER_MINUTE = 10
PER_HOUR = 100

_lock = threading.Lock()
_hits = defaultdict(deque)


def reset():
    with _lock:
        _hits.clear()


def check(client_id, now=None):
    if not client_id:
        return
    now = now if now is not None else time.time()

    with _lock:
        hits = _hits[client_id]
        while hits and now - hits[0] > 3600:
            hits.popleft()

        recent = sum(1 for hit in hits if now - hit <= 60)
        if recent >= PER_MINUTE or len(hits) >= PER_HOUR:
            raise TooManyRequestsError()

        hits.append(now)
