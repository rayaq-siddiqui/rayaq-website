class FlightSearchProvider:
    name = "unset"
    is_live = False
    freshness_message = "Indicative fares based on recently observed prices."

    def is_configured(self):
        raise NotImplementedError

    def search_flexible_dates(self, request):
        raise NotImplementedError
