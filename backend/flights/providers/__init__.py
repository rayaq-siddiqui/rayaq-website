from .aviasales import AviasalesDataProvider
from .base import FlightSearchProvider

DEFAULT_PROVIDER = AviasalesDataProvider.name
_REGISTRY = {AviasalesDataProvider.name: AviasalesDataProvider}

_instances = {}


def get_provider(name=None):
    name = name or DEFAULT_PROVIDER
    if name not in _instances:
        _instances[name] = _REGISTRY[name]()
    return _instances[name]


def reset_providers():
    _instances.clear()


__all__ = ["AviasalesDataProvider", "FlightSearchProvider", "get_provider", "reset_providers"]
