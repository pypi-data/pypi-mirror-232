from currencyapinet import Currency
from currencyapinet.endpoints.rates import Rates
from currencyapinet.endpoints.history import History
from currencyapinet.endpoints.timeframe import Timeframe
from currencyapinet.endpoints.convert import Convert
from currencyapinet.endpoints.currencies import Currencies
from unittest import TestCase

class Test(TestCase):
    def test_rates_method(self):
        class_under_test = Currency('fakeKey')
        self.assertIsInstance(class_under_test.rates(), Rates)

    def test_history_method(self):
        class_under_test = Currency('fakeKey')
        self.assertIsInstance(class_under_test.history(), History)

    def test_timeframe_method(self):
        class_under_test = Currency('fakeKey')
        self.assertIsInstance(class_under_test.timeframe(), Timeframe)

    def test_convert_method(self):
        class_under_test = Currency('fakeKey')
        self.assertIsInstance(class_under_test.convert(), Convert)

    def test_currencies_method(self):
        class_under_test = Currency('fakeKey')
        self.assertIsInstance(class_under_test.currencies(), Currencies)