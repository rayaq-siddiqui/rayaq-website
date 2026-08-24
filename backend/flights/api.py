from . import airports, service
from .errors import FlightSearchError, ProviderError, TooManyRequestsError


def page_context(query=None):
    return service.page_context(query=query)


def client_id(forwarded_for, remote_addr):
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return remote_addr


def search_response(payload, client_id=None):
    try:
        return service.search(payload, client_id=client_id), 200
    except FlightSearchError as error:
        return {"error": error.message, "field": error.field}, error.status_code
    except (TooManyRequestsError, ProviderError) as error:
        return {"error": error.message}, error.status_code


def airports_response(query):
    return {"results": airports.search(query)}, 200


def health_response():
    return service.health(), 200
