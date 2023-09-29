from unittest import TestCase

from currencyapinet.endpoints.history import History

class Test(TestCase):

    def setUp(self):
        self.class_under_test = History('fakekey')

    def test_history_base(self):
        self.class_under_test.base('gBp')
        self.assertEqual('GBP', self.class_under_test.param.get('base'))
        self.assertIsInstance(self.class_under_test.base('uSD'), History)    

    def test_history_date(self):
        self.class_under_test.date('2023-01-01')
        self.assertEqual('2023-01-01', self.class_under_test.param.get('date'))
        self.assertIsInstance(self.class_under_test.date('2023-01-01'), History)

    def test_history_endpoint_set(self):
        self.assertEqual('history', self.class_under_test.endpoint)

    def test_history__build_url_params(self):
        self.assertDictEqual(
            {'key': 'fakekey', 'base': 'USD', 'output': 'JSON'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.output('xMl')
        self.assertDictEqual(
            {'key': 'fakekey', 'base': 'USD', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.base('gbP')
        self.assertDictEqual(
            {'key': 'fakekey', 'base': 'GBP', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.date('2023-01-01')
        self.assertDictEqual(
            {'key': 'fakekey', 'base': 'GBP', 'date': '2023-01-01', 'output': 'XML'},
            self.class_under_test._build_url_params()
        )