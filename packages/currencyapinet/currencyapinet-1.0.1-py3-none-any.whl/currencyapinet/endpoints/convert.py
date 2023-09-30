from currencyapinet.endpoints.endpoint import Endpoint

CONVERT_ENDPOINT = 'convert'

class Convert(Endpoint):
    def __init__(self, api_key: str):
        super().__init__(api_key, CONVERT_ENDPOINT)
    
    def from_currency(self, currency: str):
        self.add_param('from', currency.upper())
        return self
    
    def to_currency(self, currency: str):
        self.add_param('to', currency.upper())
        return self
    
    def amount(self, amount: float):
        self.add_param('amount', amount)
        return self

