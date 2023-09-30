from currencyapinet.endpoints.endpoint import Endpoint

TIMEFRAME_ENDPOINT = 'timeframe'

class Timeframe(Endpoint):
    def __init__(self, api_key: str):
        super().__init__(api_key, TIMEFRAME_ENDPOINT)
        self._base()

    def base(self, currency: str):
        self._base(currency)
        return self
    
    def start_date(self, start_date: str):
        self.add_param('start_date', start_date)
        return self
    
    def end_date(self, end_date: str):
        self.add_param('end_date', end_date)
        return self

