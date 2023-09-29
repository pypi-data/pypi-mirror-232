from currencyapinet.endpoints.endpoint import Endpoint

CURRENCIES_ENDPOINT = 'currencies'

class Currencies(Endpoint):
    def __init__(self, api_key: str):
        super().__init__(api_key, CURRENCIES_ENDPOINT)

