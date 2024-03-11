from unittest.mock import MagicMock

from flask import url_for
from flask_testing import TestCase
from jwt_validation.exceptions import ValidationFailure
from jwt_validation.models import MaintainClientPrinciple
from mock import patch
from search_api import main
from search_api.config import ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS
from unit_tests.utilities_tests import super_test_context

CHARGE_ID = 'LLC-6521'
INVALID_CHARGE_ID = 'some_invalid_charge_id'

LOCAL_LAND_CHARGES_ROUTE = 'local_land_charge.get_local_land_charges'
LOCAL_LAND_CHARGE_ROUTE = 'local_land_charge.get_local_land_charge'

BASE64_GEO = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"


class TestLocalLandCharge(TestCase):

    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    @patch('search_api.resources.local_land_charge.GeometryFeature')
    @patch('search_api.resources.local_land_charge.db')
    def test_get_land_charges_geo_results(self, mock_db, mock_geo_feature, mock_llc_query, model_mappers_mock,
                                          mock_validate):
        """Should return a 200 status and response should contain charge ids returned by query"""
        with super_test_context(main.app):
            mock_charge = MagicMock()
            mock_charge.local_land_charge = CHARGE_ID
            mock_geo_feature.query.filter.return_value.options.return_value.all.return_value = [mock_charge]

            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = True

            model_mappers_mock.map_llc_result_to_dictionary_list.return_value = [{"woo": CHARGE_ID}]
            response = self.client.get(url_for(LOCAL_LAND_CHARGES_ROUTE, boundingBox=BASE64_GEO),
                                       headers={'Authorization': 'Fake JWT'})

            model_mappers_mock.map_llc_result_to_dictionary_list.assert_called_with([CHARGE_ID])

            self.assertIn(CHARGE_ID, response.data.decode())
            self.assertStatus(response, 200)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charges_results(self, mock_llc_query, model_mappers_mock, mock_validate):
        """Should return a 200 status and response should contain charge ids returned by query"""
        mock_llc_query.query.all.return_value = [CHARGE_ID]

        model_mappers_mock.map_llc_result_to_dictionary_list.return_value = [{"woo": CHARGE_ID}]

        response = self.client.get(url_for(LOCAL_LAND_CHARGES_ROUTE), headers={'Authorization': 'Fake JWT'})

        model_mappers_mock.map_llc_result_to_dictionary_list.assert_called_with([CHARGE_ID])

        self.assertIn(CHARGE_ID, response.data.decode())
        self.assertStatus(response, 200)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charges_no_results_exception(self, mock_llc_query, mock_validate):
        """Should throw an ApplicationError returning a 404 status if no charge ids where found"""
        mock_llc_query.query.all.return_value = None

        response = self.client.get(url_for(LOCAL_LAND_CHARGES_ROUTE), headers={'Authorization': 'Fake JWT'})

        self.assertIn('No land charges found', response.data.decode())
        self.assertStatus(response, 404)

    @patch('search_api.resources.local_land_charge.filter_sensitive_charges')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charges_all_filtered_exception(self, mock_llc_query, mock_validate, model_mappers_mock,
                                                     mock_sensitive_filter):
        """Should throw an ApplicationError returning a 404 status if no charge ids where found"""
        with super_test_context(main.app):
            mock_llc_query.query.all.return_value = [CHARGE_ID]

            model_mappers_mock.map_llc_result_to_dictionary_list.return_value = [{"woo": CHARGE_ID}]

            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False

            mock_sensitive_filter.return_value = []

            response = self.client.get(url_for(LOCAL_LAND_CHARGES_ROUTE), headers={'Authorization': 'Fake JWT'})

            self.assertIn('No land charges found', response.data.decode())
            self.assertStatus(response, 404)

    @patch('search_api.app.validate')
    def test_get_land_charges_failed_decode_exception(self, mock_validate):
        """Should throw an ApplicationError returning a 404 status if no charge ids where found"""
        response = self.client.get(url_for(LOCAL_LAND_CHARGES_ROUTE, boundingBox="fkoefkoe"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertIn('Unprocessable Entity.', response.data.decode())
        self.assertStatus(response, 422)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.decode_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_with_valid_charge_id(
            self, llc_query_mock, decode_charge_id_mock, is_valid_charge_id_mock, model_mappers_mock, mock_validate):
        """Valid ID test

        Should pass the given charge id to the charge id service to decode it, then use it to query the charge ids,
        and pass the charge ids to the mapper.
        """
        is_valid_charge_id_mock.return_value = True
        decode_charge_id_mock.return_value = CHARGE_ID
        llc_query_mock.query.get.return_value = CHARGE_ID
        model_mappers_mock.map_llc_charge_display_result_to_dictionary_list.return_value = CHARGE_ID

        response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                           charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})

        decode_charge_id_mock.assert_called_with(CHARGE_ID)
        llc_query_mock.query.get.assert_called_with(CHARGE_ID)
        model_mappers_mock.map_llc_charge_display_result_to_dictionary_list.assert_called_with(CHARGE_ID)

        self.assertIn(CHARGE_ID, response.data.decode())
        self.assertStatus(response, 200)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    def test_get_land_charge_with_invalid_charge_id(self, is_valid_charge_id_mock, mock_validate):
        """Should throw an ApplicationError returning a status of 422 if the given charge id is invalid"""
        is_valid_charge_id_mock.return_value = False
        response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                           charge_id=INVALID_CHARGE_ID), headers={'Authorization': 'Fake JWT'})

        self.assertIn('Invalid Land Charge Number', response.data.decode())
        self.assertStatus(response, 422)

    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_with_no_results_returned(self, llc_query_mock, is_valid_charge_id_mock, mock_validate):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        is_valid_charge_id_mock.return_value = True
        llc_query_mock.query.get.return_value = None

        response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                           charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
        self.assertIn('No land charges found.', response.data.decode())
        self.assertStatus(response, 404)

    @patch('search_api.resources.local_land_charge.filter_sensitive_charges')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_with_result_filtered_out(self, llc_query_mock, is_valid_charge_id_mock, mock_validate,
                                                      model_mappers_mock, mock_sensitive_filter):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            llc_query_mock.query.get.return_value = CHARGE_ID
            model_mappers_mock.map_llc_charge_display_result_to_dictionary_list.return_value = CHARGE_ID

            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False

            mock_sensitive_filter.return_value = []

            response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
            self.assertIn('No land charges found.', response.data.decode())
            self.assertStatus(response, 404)

    def test_get_no_token(self):
        """Should return 401 with no auth token"""
        response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                           charge_id=CHARGE_ID))
        self.assertStatus(response, 401)

    @patch('search_api.app.validate')
    def test_get_invalid(self, mock_validate):
        """Should return 401 with invalid token"""
        mock_validate.side_effect = ValidationFailure("There was a failure")
        response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                           charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
        self.assertStatus(response, 401)

    @patch('search_api.resources.local_land_charge.filter_sensitive_charges')
    @patch('search_api.resources.local_land_charge.model_mappers')
    @patch('search_api.app.validate')
    @patch('search_api.resources.local_land_charge.is_valid_charge_id')
    @patch('search_api.resources.local_land_charge.LocalLandCharge')
    def test_get_land_charge_user_allowed_user_no_filter(self, llc_query_mock, is_valid_charge_id_mock, mock_validate,
                                                         model_mappers_mock, mock_sensitive_filter):
        """Should throw an ApplicationError returning a status of 404 if no charges with the given id where found"""
        with super_test_context(main.app):
            is_valid_charge_id_mock.return_value = True
            llc_query_mock.query.get.return_value = CHARGE_ID
            model_mappers_mock.map_llc_charge_display_result_to_dictionary_list.return_value = CHARGE_ID

            mock_principle = MagicMock(spec=MaintainClientPrinciple)
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False
            mock_principle.role = ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS[0]
            mock_principle.organisation = ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS[1]

            mock_sensitive_filter.return_value = []

            response = self.client.get(url_for(LOCAL_LAND_CHARGE_ROUTE,
                                               charge_id=CHARGE_ID), headers={'Authorization': 'Fake JWT'})
            self.assertIn(CHARGE_ID, response.data.decode())
            self.assertStatus(response, 200)

            mock_sensitive_filter.assert_not_called()
