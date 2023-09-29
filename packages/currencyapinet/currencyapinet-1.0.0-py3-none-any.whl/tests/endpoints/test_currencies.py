from unittest import TestCase

from currencyapinet.endpoints.currencies import Currencies

class Test(TestCase):

    def setUp(self):
        self.class_under_test = Currencies('fakekey')

    def test_currencies_endpoint_set(self):
        self.assertEqual('currencies', self.class_under_test.endpoint)

    def test_currencies__build_url_params(self):
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'JSON'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.output('xMl')
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )