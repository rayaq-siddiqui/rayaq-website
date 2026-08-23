class FlightSearchError(Exception):
    status_code = 400

    def __init__(self, message, field=None):
        super().__init__(message)
        self.message = message
        self.field = field


class TooManyRequestsError(Exception):
    status_code = 429

    def __init__(self, message="Too many searches. Give it a minute and try again."):
        super().__init__(message)
        self.message = message


class ProviderError(Exception):
    status_code = 503

    def __init__(self, message="Flight data is temporarily unavailable. Try again shortly."):
        super().__init__(message)
        self.message = message


class ProviderUnavailableError(ProviderError):
    pass


class ProviderRateLimitedError(ProviderError):
    def __init__(self, message="The flight-data service is busy. Try again in a moment."):
        super().__init__(message)


class ProviderNotConfiguredError(ProviderUnavailableError):
    def __init__(self, message="Flight search is not configured on this server yet."):
        super().__init__(message)
