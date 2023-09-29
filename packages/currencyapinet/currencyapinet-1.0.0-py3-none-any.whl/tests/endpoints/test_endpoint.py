from unittest import TestCase
from unittest.mock import Mock, patch
from currencyapinet.endpoints.endpoint import Endpoint
import requests

class Test(TestCase):

    def setUp(self):
        self.class_under_test = Endpoint('fakekey', 'fakeendpoint')

    def test_endpoint(self):
        self.assertEqual('JSON', self.class_under_test.param.get('output'))

    def test_endpoint_add_param(self):
        self.class_under_test.add_param('fakeparam', 123)
        self.assertEqual(123, self.class_under_test.param.get('fakeparam'))

    def test_endpoint_ouput(self):
        self.class_under_test.output('xMl')
        self.assertEqual('XML', self.class_under_test.param.get('output'))
        self.assertIsInstance(self.class_under_test.output('xMl'), Endpoint)

    def test_endpoint__isXml(self):
        self.class_under_test.param['output'] = 'xMl'
        self.assertEqual(True, self.class_under_test._isXml())
        
    def test_endpoint__base(self):
        self.class_under_test._base('uSd')
        self.assertEqual('USD', self.class_under_test.param.get('base'))
        
    def test_endpoint__headers_default_json(self):
        expected = {
            'X-Sdk': 'python',
            'Content-Type': 'application/json',
        }
        self.class_under_test._headers()
        self.assertEqual(expected, self.class_under_test._headers())

    def test_endpoint__headers_xml(self):
        self.class_under_test.output('xMl')
        expected = {
            'X-Sdk': 'python',
            'Content-Type': 'application/xml',
        }
        self.class_under_test._headers()
        self.assertEqual(expected, self.class_under_test._headers())

    @patch.object(requests, 'get')
    def test_endpoint_get(self, mock_requests_get):
        mock_data = [{"id": 1}, {"id": 2}]
        response_mock = Mock(return_value=mock_data)
        mock_requests_get.return_value.json = response_mock
        self.assertEqual(
            mock_data, 
            self.class_under_test.get()
        )

    @patch.object(requests, 'get')
    def test_endpoint_get_xml(self, mock_requests_get):
        self.class_under_test.output('xMl')
        mock_data = [{"id": 1}, {"id": 2}]
        mock_requests_get.return_value.text = mock_data
        self.assertEqual(
            mock_data, 
            self.class_under_test.get()
        )

    def test_endpoint__build_url_params(self):
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'JSON'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test.output('xMl')
        self.assertDictEqual(
            {'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        self.class_under_test._base('gbP')
        self.assertDictEqual(
            {'base': 'GBP', 'key': 'fakekey', 'output': 'XML'}, 
            self.class_under_test._build_url_params()
        )
        