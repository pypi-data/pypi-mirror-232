from unittest.mock import Mock, patch
from unittest import TestCase
from currencyapinet.endpoints.rates import Rates
import requests

class Test(TestCase):

    def setUp(self):
        self.class_under_test = Rates('fakekey')

    def test_rates_base(self):
        self.class_under_test.base('gBp')
        self.assertEqual('GBP', self.class_under_test.param.get('base'))
        self.assertIsInstance(self.class_under_test.base('uSD'), Rates)

    def test_rates_endpoint_set(self):
        self.assertEqual('rates', self.class_under_test.endpoint)

    @patch.object(requests, 'get')
    def test_rates_get(self, mock_requests_get):
        mock_data = [{"id": 1}, {"id": 2}]
        response_mock = Mock(return_value=mock_data)
        mock_requests_get.return_value.json = response_mock
        self.assertEqual(
            mock_data, 
            self.class_under_test.get()
        )

    @patch.object(requests, 'get')
    def test_rates_get_xml(self, mock_requests_get):
        self.class_under_test.output('xMl')
        mock_data = [{"id": 1}, {"id": 2}]
        mock_requests_get.return_value.text = mock_data
        self.assertEqual(
            mock_data, 
            self.class_under_test.get()
        )

    def test_rates__build_url_params(self):
        self.assertDictEqual(
            {'base': 'USD', 'key': 'fakekey', 'output': 'JSON'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.output('xMl')
        self.assertDictEqual(
            {'base': 'USD', 'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.base('gbP')
        self.assertDictEqual(
            {'base': 'GBP', 'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )