from currencyapinet.endpoints.endpoint import Endpoint

RATES_ENDPOINT = 'rates'

class Rates(Endpoint):
    def __init__(self, api_key: str):
        super().__init__(api_key, RATES_ENDPOINT)
        self._base()

    def base(self, currency: str):
        self._base(currency)
        return self

