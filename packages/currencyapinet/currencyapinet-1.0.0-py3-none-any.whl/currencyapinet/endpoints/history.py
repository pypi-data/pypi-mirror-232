from currencyapinet.endpoints.endpoint import Endpoint

HISTORY_ENDPOINT = 'history'

class History(Endpoint):
    def __init__(self, api_key: str):
        super().__init__(api_key, HISTORY_ENDPOINT)
        self._base()

    def base(self, currency: str):
        self._base(currency)
        return self
    
    def date(self, date: str):
        self.add_param('date', date)
        return self

