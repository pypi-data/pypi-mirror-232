import requests

API_VERSION = 'v1'
BASE_URL = 'https://currencyapi.net/api/' + API_VERSION + '/'
DEFAULT_BASE = 'USD'
DEFAULT_OUTPUT = 'JSON'
XML_OUTPUT = 'XML'

class Endpoint(object):
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key.lower()
        self.endpoint = endpoint.lower()
        self.param = {}
        self.param['output'] = DEFAULT_OUTPUT.upper()

    def add_param(self, name, value):
        self.param[name] = value

    def _base(self, currency: str = DEFAULT_BASE):
        self.add_param('base', currency.upper())

    def output(self, output):
        self.param['output'] = output.upper()
        return self

    def _isXml(self):
        return self.param.get('output').upper() == XML_OUTPUT

    def _headers(self):
        if self._isXml():
            content_type = 'application/xml'
        else:
            content_type = 'application/json'

        headers = {}
        headers['X-Sdk'] = 'python'
        headers['Content-Type'] = content_type
        return headers
    
    def _build_url_params(self):
        params = {'key': self.api_key}
        params.update(self.param)
        return params

    def get(self):
        url = BASE_URL + self.endpoint
        r = requests.get(url, params=self._build_url_params(), headers=self._headers())

        if self._isXml():
            return r.text
        else:
            return r.json()
