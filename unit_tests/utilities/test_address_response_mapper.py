import json
import unittest

from search_api.main import app
from search_api.utilities import address_response_mapper
from unit_tests.data import (test_address_response_data,
                             test_address_response_data_different_roads,
                             test_address_response_data_different_towns,
                             test_address_response_filtered_data)

response_address_filtered_data_json = json.dumps(test_address_response_filtered_data.response_address_filtered_data,
                                                 sort_keys=True)


class TestAddressResponseMapper(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_address_response_mapper(self):
        filtered_result = json.dumps(address_response_mapper.map_address_response
                                     (test_address_response_data.response_address_data, ''), sort_keys=True)
        self.assertEqual(filtered_result, response_address_filtered_data_json)

    def test_is_street_search_same_roads_same_town(self):
        is_street_search = address_response_mapper.is_street_search(test_address_response_data.response_address_data)
        self.assertEqual(is_street_search, True)

    def test_is_street_search_same_town_different_roads(self):
        test_address_response_data_different_roads.response_address_data_different_roads[0]['street_description'] \
            = 'something'
        is_street_search = address_response_mapper.\
            is_street_search(test_address_response_data_different_roads.response_address_data_different_roads)
        self.assertEqual(is_street_search, False)

    def test_is_street_search_same_roads_different_town(self):
        test_address_response_data_different_towns.response_address_data_different_towns[0]['town_name'] = 'something'
        is_street_search = address_response_mapper.\
            is_street_search(test_address_response_data_different_towns.response_address_data_different_towns)
        self.assertEqual(is_street_search, False)
