import pytest

from flights import rate_limit
from flights.errors import TooManyRequestsError


@pytest.fixture(autouse=True)
def clean_limiter():
    rate_limit.reset()
    yield
    rate_limit.reset()


def test_rate_limiting_allows_the_configured_burst():
    for offset in range(rate_limit.PER_MINUTE):
        rate_limit.check("1.2.3.4", now=1000 + offset)


def test_rate_limiting_rejects_the_next_request_in_the_same_minute():
    for offset in range(rate_limit.PER_MINUTE):
        rate_limit.check("1.2.3.4", now=1000 + offset)

    with pytest.raises(TooManyRequestsError):
        rate_limit.check("1.2.3.4", now=1000 + rate_limit.PER_MINUTE)


def test_rate_limiting_forgets_requests_once_the_minute_passes():
    for offset in range(rate_limit.PER_MINUTE):
        rate_limit.check("1.2.3.4", now=1000 + offset)

    rate_limit.check("1.2.3.4", now=1000 + 61)


def test_rate_limiting_is_per_client():
    for offset in range(rate_limit.PER_MINUTE):
        rate_limit.check("1.2.3.4", now=1000 + offset)

    rate_limit.check("5.6.7.8", now=1000)


def test_rate_limiting_caps_the_hourly_total():
    stamp = 1000
    for _ in range(rate_limit.PER_HOUR // rate_limit.PER_MINUTE):
        for offset in range(rate_limit.PER_MINUTE):
            rate_limit.check("1.2.3.4", now=stamp + offset)
        stamp += 61

    with pytest.raises(TooManyRequestsError):
        rate_limit.check("1.2.3.4", now=stamp)
