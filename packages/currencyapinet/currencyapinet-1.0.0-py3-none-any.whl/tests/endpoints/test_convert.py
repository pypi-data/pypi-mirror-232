from unittest import TestCase

from currencyapinet.endpoints.convert import Convert

class Test(TestCase):

    def setUp(self):
        self.class_under_test = Convert('fakekey')

    def test_convert_from_currency(self):
        self.class_under_test.from_currency('gBp')
        self.assertEqual('GBP', self.class_under_test.param.get('from'))
        self.assertIsInstance(self.class_under_test.from_currency('uSD'), Convert)

    def test_convert_to_currency(self):
        self.class_under_test.to_currency('gBp')
        self.assertEqual('GBP', self.class_under_test.param.get('to'))
        self.assertIsInstance(self.class_under_test.to_currency('uSD'), Convert)

    def test_convert_amount(self):
        self.class_under_test.amount(10)
        self.assertEqual(10.00, self.class_under_test.param.get('amount'))
        self.assertIsInstance(self.class_under_test.amount(10), Convert)

    def test_history_endpoint_set(self):
        self.assertEqual('convert', self.class_under_test.endpoint)

    def test_convert__build_url_params(self):
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'JSON'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.output('xMl')
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.from_currency('gbP')
        self.class_under_test.to_currency('uSd')
        self.class_under_test.amount(10)
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'XML', 'from': 'GBP', 'to': 'USD', 'amount': 10},
            self.class_under_test._build_url_params()
        )