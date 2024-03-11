from unittest.mock import MagicMock

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_api import main
from unit_tests.utilities_tests import super_test_context

CHARGE_ID = 'LLC-6521'
INVALID_CHARGE_ID = 'some_invalid_charge_id'
LOCAL_LAND_CHARGES_HISTORY_ROUTE = 'local_land_charge.get_local_land_charge_history'


class TestLocalLandChargeHistory(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.decode_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandChargeHistory')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_history_with_valid_charge_id(
            self, llc_query_mock, llchist_query_mock, decode_charge_id_mock, is_valid_charge_id_mock,
            model_mappers_mock, mock_validate):
        """Valid ID test

        Should pass the given charge id to the charge id service to decode it, then use it to query the charge ids,
        and pass the charge ids to the mapper.
        """
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            decode_charge_id_mock.return_value = CHARGE_ID
            llchist_query_mock.query.filter.return_value.order_by.return_value.all.return_value = CHARGE_ID
            llc_query_mock.query.get.return_value = CHARGE_ID
            model_mappers_mock.map_llc_history_result_to_dictionary_list.return_value = CHARGE_ID

            response = self.client.get(url_for(LOCAL_LAND_CHARGES_HISTORY_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})

            decode_charge_id_mock.assert_called_with(CHARGE_ID)
            llchist_query_mock.query.filter.assert_called()
            model_mappers_mock.map_llc_history_result_to_dictionary_list.assert_called_with(CHARGE_ID)

            self.assertIn(CHARGE_ID, response.data.decode())
            self.assertStatus(response, 200)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    def test_get_land_charge_history_with_invalid_charge_id(self, is_valid_charge_id_mock, mock_validate):
        """Should throw an ApplicationError returning a status of 422 if the given charge id is invalid"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = False
            response = self.client.get(url_for(LOCAL_LAND_CHARGES_HISTORY_ROUTE,
                                               charge_id=INVALID_CHARGE_ID), headers={'Authorization': 'Fake JWT'})

            self.assertIn('Invalid Land Charge Number', response.data.decode())
            self.assertStatus(response, 422)

    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.filter_sensitive_charges')
    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandChargeHistory')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_history_with_no_history(self, llc_query_mock, llchist_query_mock,
                                                     is_valid_charge_id_mock, mock_validate, mock_filter,
                                                     mock_mapper):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            llchist_query_mock.query.filter.return_value.order_by.return_value.all.return_value = None
            llc_query_mock.query.get.return_value = CHARGE_ID
            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False
            mock_filter.return_value = CHARGE_ID
            mock_mapper.map_llc_result_to_dictionary_list.return_value = CHARGE_ID

            response = self.client.get(url_for(LOCAL_LAND_CHARGES_HISTORY_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
            self.assertIn('No land charge history found.', response.data.decode())
            self.assertStatus(response, 404)

    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.filter_sensitive_charges')
    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_history_filtered_charge(self, llc_query_mock,
                                                     is_valid_charge_id_mock, mock_validate, mock_filter,
                                                     mock_mapper):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            llc_query_mock.query.get.return_value = CHARGE_ID
            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False
            mock_filter.return_value = []
            mock_mapper.map_llc_result_to_dictionary_list.return_value = CHARGE_ID

            response = self.client.get(url_for(LOCAL_LAND_CHARGES_HISTORY_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
            self.assertIn('No land charge history found.', response.data.decode())
            self.assertStatus(response, 404)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_history_with_no_charge(self, llc_query_mock, is_valid_charge_id_mock, mock_validate):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            llc_query_mock.query.get.return_value = None

            response = self.client.get(url_for(LOCAL_LAND_CHARGES_HISTORY_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
            self.assertIn('No land charge history found.', response.data.decode())
            self.assertStatus(response, 404)
