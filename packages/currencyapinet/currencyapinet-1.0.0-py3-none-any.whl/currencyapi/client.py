from currencyapinet.endpoints.rates import Rates

class Client(object):
    def __init__(self, api_key: str):
        self._api_key = api_key

    def rates(self) -> Rates:
        return Rates(self._api_key)
