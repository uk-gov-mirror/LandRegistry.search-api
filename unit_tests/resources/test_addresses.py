import json
import unittest

import mock
from flask import g
from mock import MagicMock, patch
from search_api.main import app
from search_api.resources.addresses import search_for_addresses
from unit_tests.utilities_tests import super_test_context


class TestAddresses(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_postcode(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/postcode/SW1A 1AA", headers={'Content-Type': 'application/json',
                                                                                    'Accept': 'application/json',
                                                                                    'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_postcode_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/postcode/U1cxQSAxQUE=?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'postcode',
                                            'query_value': 'SW1A 1AA', 'response_srid': 'EPSG:27700',
                                            'max_results': 1000}, 'postcode')
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_not_found_with_postcode(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/postcode/XXXX XXX", headers={'Content-Type': 'application/json',
                                                                                    'Accept': 'application/json',
                                                                                    'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 422)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_uprn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/uprn/100023346367", headers={'Content-Type': 'application/json',
                                                                                    'Accept': 'application/json',
                                                                                    'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_uprn_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/uprn/MTAwMDIzMzQ2MzY3?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'uprn',
                                            'query_value': 100023346367, 'response_srid': 'EPSG:27700',
                                            'max_results': 1000}, "uprn")
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_not_found_with_uprn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/uprn/111111111111111111",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 422)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_text(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/text/SW1A", headers={'Content-Type': 'application/json',
                                                                            'Accept': 'application/json',
                                                                            'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.addresses.search_for_addresses')
    def test_get_address_found_with_text_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/search/addresses/text/U1cxQQ==?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'text_search',
                                            'query_value': 'SW1A', 'response_srid': 'EPSG:27700',
                                            'max_results': 1000}, "partial_postcode")
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    def test_get_address_invalid_postcode_in_valid_format(self, mock_validate):
        response = MagicMock()
        response.status_code = 400
        response.json.return_value = "testing"

        with super_test_context(app):
            g.requests.post.return_value = response
            get_response = self.app.get("/search/addresses/postcode/AB1 2CD",
                                        headers={'Content-Type': 'application/json',
                                                 'Accept': 'application/json',
                                                 'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 400)
        self.assertEqual(json.loads(get_response.data.decode())['error_message'], "testing")

    def test_get_address_not_found_with_text(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            mock_response = MagicMock()
            mock_response._content = b'[]'
            mock_response.status_code = 200
            g.requests.post.return_value = mock_response

            try:
                search_for_addresses('foo', 'bar')
            except Exception as ex:
                self.assertEqual(ex.http_code, 404)

    def test_get_address_something_went_wrong(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            mock_response = MagicMock()
            mock_response.status_code = 500
            g.requests.post.return_value = mock_response

            try:
                search_for_addresses('foo', 'bar')
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
