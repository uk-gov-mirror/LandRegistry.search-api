import json
import unittest

import mock
from flask import g
from mock import MagicMock, patch
from search_api.main import app
from search_api.resources.V2_0.addresses_v_2 import search_for_addresses
from unit_tests.utilities_tests import super_test_context


class TestAddressesV2(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_postcode(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/postcode/SW1A 1AA",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_postcode_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/postcode/U1cxQSAxQUE=?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'postcode',
                                            'query_value': 'SW1A 1AA', 'response_srid': 'EPSG:27700',
                                            'max_results': 1000})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_not_found_with_postcode(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/postcode/XXXX XXX",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 422)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_uprn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/uprn/100023346367",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_uprn_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/uprn/MTAwMDIzMzQ2MzY3?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'uprn',
                                            'query_value': 100023346367, 'response_srid': 'EPSG:27700',
                                            'max_results': 1000})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_not_found_with_uprn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/uprn/11111111111111111111111",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 422)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_usrn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/usrn/100023346367",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_usrn_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/usrn/MTAwMDIzMzQ2MzY3?base64=true&value_2=EX4",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'usrn',
                                            'query_value': 100023346367, 'response_srid': 'EPSG:27700',
                                            'max_results': 1000, 'query_value_2': 'EX4'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_not_found_with_usrn(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/usrn/badusrn",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 422)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_text(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/text/SW1A",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    @mock.patch('search_api.resources.V2_0.addresses_v_2.search_for_addresses')
    def test_get_address_found_with_text_base64(self, mock_get_search, mock_validate):
        mock_get_search.return_value = "Test"
        get_response = self.app.get("/v2.0/search/addresses/text/U1cxQQ==?base64=true",
                                    headers={'Content-Type': 'application/json',
                                             'Accept': 'application/json',
                                             'Authorization': 'Fake JWT'})
        mock_get_search.assert_called_with({'datasource': 'local_authority', 'search_type': 'text_search',
                                            'query_value': 'SW1A', 'response_srid': 'EPSG:27700',
                                            'max_results': 1000})
        self.assertEqual(get_response.status_code, 200)

    @patch('search_api.app.validate')
    def test_get_address_invalid_postcode_in_valid_format(self, mock_validate):
        with super_test_context(app):
            response = MagicMock()
            response.status_code = 400
            response.json.return_value = "testing"
            g.requests.post.return_value = response

            get_response = self.app.get("/v2.0/search/addresses/postcode/AB1 2CD", headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 400)
            self.assertEqual(json.loads(get_response.data.decode())['error_message'], "testing")

    @patch('search_api.app.validate')
    @patch('search_api.utilities.V2_0.address_response_mapper_v_2.map_address_response')
    def test_get_address_index_map(self, mock_mapper, mock_validate):

        with super_test_context(app):
            response_addr = MagicMock()
            response_addr.status_code = 200
            response_addr.json.return_value = [{"uprn": 1234}]
            g.requests.post.return_value = response_addr

            response_index_uprn = MagicMock()
            response_index_uprn.status_code = 200
            response_index_uprn.json.return_value = ["ATITLE"]

            response_index_title = MagicMock()
            response_index_title.status_code = 200
            response_index_title.json.return_value = {"features": [{"not": "arealfeature"}]}

            g.requests.get.side_effect = [response_index_uprn, response_index_title]

            mock_mapper.return_value = [{"uprn": 1234}]

            get_response = self.app.get("/v2.0/search/addresses/postcode/AB1 2CD?index_map=true", headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(json.loads(get_response.data.decode()), [
                {"uprn": 1234, "index_map": {'type': 'FeatureCollection',
                                             'features': [{'not': 'arealfeature'}]}}])

    @patch('search_api.app.validate')
    @patch('search_api.utilities.V2_0.address_response_mapper_v_2.map_address_response')
    def test_get_address_index_map_uprn_fail(self, mock_mapper, mock_validate):
        with super_test_context(app):
            response_addr = MagicMock()
            response_addr.status_code = 200
            response_addr.json.return_value = [{"uprn": 1234}]
            g.requests.post.return_value = response_addr

            response_index_uprn = MagicMock()
            response_index_uprn.status_code = 500
            response_index_uprn.json.return_value = {"a": "fail"}

            g.requests.get.side_effect = [response_index_uprn]

            mock_mapper.return_value = [{"uprn": 1234}]

            get_response = self.app.get("/v2.0/search/addresses/postcode/AB1 2CD?index_map=true", headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(json.loads(get_response.data.decode()), [{'uprn': 1234}])
            g.requests.get.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.utilities.V2_0.address_response_mapper_v_2.map_address_response')
    def test_get_address_index_map_uprn_notfound(self, mock_mapper, mock_validate):
        with super_test_context(app):
            response_addr = MagicMock()
            response_addr.status_code = 200
            response_addr.json.return_value = [{"uprn": 1234}]
            g.requests.post.return_value = response_addr

            response_index_uprn = MagicMock()
            response_index_uprn.status_code = 404

            g.requests.get.side_effect = [response_index_uprn]

            mock_mapper.return_value = [{"uprn": 1234}]

            get_response = self.app.get("/v2.0/search/addresses/postcode/AB1 2CD?index_map=true", headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(json.loads(get_response.data.decode()), [{'uprn': 1234}])

    @patch('search_api.app.validate')
    @patch('search_api.utilities.V2_0.address_response_mapper_v_2.map_address_response')
    def test_get_address_index_map_title_fail(self, mock_mapper, mock_validate):
        with super_test_context(app):
            response_addr = MagicMock()
            response_addr.status_code = 200
            response_addr.json.return_value = [{"uprn": 1234}]
            g.requests.post.return_value = response_addr

            response_index_uprn = MagicMock()
            response_index_uprn.status_code = 200
            response_index_uprn.json.return_value = ["ATITLE"]

            response_index_title = MagicMock()
            response_index_title.status_code = 500
            response_index_title.json.return_value = {"a": "fail"}

            g.requests.get.side_effect = [response_index_uprn, response_index_title]

            mock_mapper.return_value = [{"uprn": 1234}]

            get_response = self.app.get("/v2.0/search/addresses/postcode/AB1 2CD?index_map=true", headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(json.loads(get_response.data.decode()), [{'uprn': 1234}])
            g.requests.get.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.addresses_v_2.search_for_index_map_by_title_no')
    def test_get_index_map_by_title_pass(self, mock_search, mock_validate):
        with super_test_context(app):
            search_results = MagicMock()
            search_results.status_code = 200
            search_results.json.return_value = {"features": 1234}
            mock_search.return_value = search_results
            get_response = self.app.get("/v2.0/search/addresses/title/DN1234",
                                        headers={'Content-Type': 'application/json',
                                                 'Accept': 'application/json',
                                                 'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(json.loads(get_response.data.decode()), {"type": "FeatureCollection",
                                                                      "features": 1234})

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.addresses_v_2.search_for_index_map_by_title_no')
    def test_get_index_map_by_title_fail_404(self, mock_search, mock_validate):
        with super_test_context(app):
            search_results = MagicMock()
            search_results.status_code = 404
            mock_search.return_value = search_results
            get_response = self.app.get("/v2.0/search/addresses/title/DN1234",
                                        headers={'Content-Type': 'application/json',
                                                 'Accept': 'application/json',
                                                 'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 404)
            self.assertEqual(json.loads(get_response.data.decode()).get('error_message'),
                             'No index map found for title search')

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.addresses_v_2.search_for_index_map_by_title_no')
    def test_get_index_map_by_title_fail_500(self, mock_search, mock_validate):
        with super_test_context(app):
            search_results = MagicMock()
            search_results.status_code = 500
            search_results.json.return_value = {'error_message': 'a wrong thing did occur'}
            mock_search.return_value = search_results
            get_response = self.app.get("/v2.0/search/addresses/title/DN1234",
                                        headers={'Content-Type': 'application/json',
                                                 'Accept': 'application/json',
                                                 'Authorization': 'Fake JWT'})
            self.assertEqual(get_response.status_code, 500)
            self.assertEqual(json.loads(get_response.data.decode()).get('error_message'),
                             {'error_message': 'a wrong thing did occur'})

    def test_get_address_not_found_with_text(self):
        with app.test_request_context():
            g.requests = MagicMock()
            g.trace_id = '123'
            mock_response = MagicMock()
            mock_response._content = b'[]'
            mock_response.status_code = 200
            g.requests.post.return_value = mock_response

            try:
                search_for_addresses('foo')
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
                search_for_addresses('foo')
            except Exception as ex:
                self.assertEqual(ex.http_code, 500)
