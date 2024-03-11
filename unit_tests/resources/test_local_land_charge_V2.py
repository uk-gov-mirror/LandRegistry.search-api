import json
from unittest.mock import MagicMock

from flask import g, url_for
from flask_testing import TestCase
from mock import patch
from search_api import main
from search_api.exceptions import ApplicationError
from search_api.resources.V2_0.local_land_charge_v_2 import (
    count_results_for_boundary, get_data_for_boundary,
    get_results_for_boundary, get_results_for_originating_authority_charge)
from unit_tests.utilities_tests import super_test_context

CHARGE_ID = 'LLC-6521'
INVALID_CHARGE_ID = 'some_invalid_charge_id'

GET_LOCAL_LAND_CHARGES_ROUTE = 'local_land_charge_V_2.get_local_land_charges'
POST_LOCAL_LAND_CHARGES_ROUTE = 'local_land_charge_V_2.post_local_land_charges'

BASE64_GEO = "eyJjb29yZGluYXRlcyI6WzQ0ODY4MS41Mzc1MDAwMDAwMywyNzk2NTkuMTEyNV0sInR5cGUiOiJQb2ludCJ9"

BOUNDARY_DATA = '{"coordinates":[448681.53750000003,279659.1125],"type":"Point"}'
MULTIPLE_EXTENTS_DATA = '{"type": "geometrycollection", "geometries": \
    [{"coordinates": [ \
        [[290000, 910000], [290100, 910000], [290100, 910100], [290000, 910100], [290000, 910000]] \
    ], "type": "Polygon", "crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}}, \
    {"coordinates": [ \
        [[290001, 910001], [290101, 910001], [290101, 910101], [290001, 910101], [290001, 910001]] \
    ], "type": "Polygon", "crs": {"properties": {"name": "EPSG:27700"}, "type": "name"}}]}'


class TestLocalLandCharge(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_api.app.validate')
    def test_get_land_charges_no_bounding_box(self, mock_validate):
        """Should return a 400 status when request does not contain a bounding box"""
        response = self.client.post(url_for(POST_LOCAL_LAND_CHARGES_ROUTE), headers={'Authorization': 'Fake JWT'},
                                    json={})
        self.assertIn('Failed to provide a search area.', response.data.decode())
        self.assertStatus(response, 400)

    @patch('search_api.resources.V2_0.local_land_charge_v_2.filter_sensitive_charges')
    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.model_mappers')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.LocalLandCharge')
    def test_get_land_charges_by_further_info_ref(self, mock_llc_query, model_mappers_mock, mock_validate,
                                                  mock_filter):
        """Should return a 200 status and response should contain charge ids returned by query"""
        with super_test_context(main.app):
            mock_charge = MagicMock()
            mock_charge.display_id = CHARGE_ID
            mock_charge.llc_item = {
                'registration-date': '2017-01-01'
            }

            mock_principle = MagicMock()
            mock_validate.return_value.principle = mock_principle
            mock_principle.has_all_permissions.return_value = False
            mock_filter.return_value = [{"woo": CHARGE_ID}]

            mock_llc_query.query.filter.return_value.order_by.return_value.all.return_value = [mock_charge]

            model_mappers_mock.map_llc_result_to_dictionary_list.return_value = [{"woo": CHARGE_ID}]

            response = self.client.get(url_for(GET_LOCAL_LAND_CHARGES_ROUTE, furtherInformationReference="KD-1337"),
                                       headers={'Authorization': 'Fake JWT'})

            model_mappers_mock.map_llc_result_to_dictionary_list.assert_called_with([mock_charge])

            self.assertIn(CHARGE_ID, response.data.decode())
            self.assertStatus(response, 200)

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.LocalLandCharge')
    def test_get_land_charges_by_further_incfo_ref_no_results(self, mock_llc_query, mock_validate):
        """Should return a 200 status and response should contain charge ids returned by query"""
        mock_llc_query.query.filter.return_value.order_by.return_value.all.return_value = []

        response = self.client.get(url_for(GET_LOCAL_LAND_CHARGES_ROUTE, furtherInformationReference="KD-1337"),
                                   headers={'Authorization': 'Fake JWT'})

        self.assertIn('No land charges found', response.data.decode())
        self.assertStatus(response, 404)

    @patch('search_api.resources.V2_0.local_land_charge_v_2.getcursor')
    def test_count_results_for_boundary_with_result(self, mock_cursor):
        """Should return results """

        mock_cursor.return_value.__enter__.return_value.fetchone.return_value = ['one']
        response = count_results_for_boundary('geo_extent_shape', 'cancelled_sql')
        self.assertEqual(response, 'one')

    @patch('search_api.resources.V2_0.local_land_charge_v_2.getcursor')
    def test_get_data_for_boundary_with_results(self, mock_cursor):
        """Should return results """

        mock_cursor.return_value.__enter__.return_value.fetchall.return_value = {'one', 'two', 'three', 'four'}
        response = get_data_for_boundary('geo_extent_shape', 'cancelled_sql')
        self.assertEqual(response, {'one', 'two', 'three', 'four'})

    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_latest_organisation_name')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.count_results_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_data_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.shape')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.unary_union')
    def test_get_results_for_boundary_too_many_charges(self, mock_unary_union, mock_asShape,
                                                       mock_data, mock_count, mock_org_name):
        with main.app.app_context():
            """Should return a Too many charges """
            mock_count.return_value = 1500
            mock_data.return_value = {'one'}

            with self.assertRaises(ApplicationError):
                response = get_results_for_boundary('boundary', True, 1000, False)
                self.assertRaises('Too many charges, search a smaller area', 507)
                self.assertStatus(response, 507)

            expected_string = "Search-area: {0}, Number-of-charges: {1}, Normal-limit: {2}, Too many charges returned"\
                .format('boundary', 1500, 1000)
            main.app.logger.info.assert_called_with(expected_string)

    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_latest_organisation_name')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.count_results_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_data_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.shape')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.unary_union')
    def test_get_results_for_boundary_no_charges(self, mock_unary_union, mock_asShape,
                                                 mock_data, mock_count, mock_org_name):
        """Should return no results """
        mock_count.return_value = 0
        mock_data.return_value = {}

        with self.assertRaises(ApplicationError):
            response = get_results_for_boundary('boundary', True, 1000, False)
            self.assertRaises('No land charges found', 404)
            self.assertStatus(response, 404)

    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_latest_organisation_name')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.filter_sensitive_charges')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.count_results_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.get_data_for_boundary')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.shape')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.unary_union')
    def test_get_results_for_boundaries(self, mock_unary_union, mock_asShape, mock_data, mock_count,
                                        mock_filter, mock_org_name):
        """Should return a single result """
        with super_test_context(main.app):
            g.principle = MagicMock()
            g.principle.has_all_permissions.return_value = False

            mock_count.return_value = 1

            mock_org_name.return_value = "test organisation"

            mock_llc_item = {
                'statutory-provision': 'old stat prov',
                'charge-type': 'old charge type',
                'charge-sub-category': 'old sub category',
                'registration-date': '2019-01-16',
                'expiry-date': '2020-01-01',
                'originating-authority': 'Test OA',
                'further-information-reference': 'AB1212',
                'author': {'organisation': 'HMLR', 'full-name': 'HMLR'},
                'local-land-charge': 32,
                'charge-geographic-description': 'Varying as LR user',
                'schema-version': '11.0',
                'geometry': {'type': 'FeatureCollection',
                             'features': [{'properties': {'id': 410},
                                          'geometry': {'coordinates': [294300, 21054], 'type': 'Point'},
                                           'type': 'Feature',
                                           'crs': {'properties': {'name': 'urn:ogc:def:crs:EPSG::27700'},
                                                   'type': 'name1'}}]}
            }

            mock_data.return_value = [(1, False, 'further information', mock_llc_item,
                                       'new stat prov', 'new charge type', 'new charge sub type', 'item', False)]
            mock_filter.return_value = [{"item": mock_llc_item}]

            response = get_results_for_boundary('boundary', True, 1000, False)
            updated_object = json.loads(response[0])[0]['item']

            self.assertEqual(len(response), 3)
            self.assertEqual(response[1], 200)
            self.assertEqual(mock_data.return_value[0][3], updated_object)

    @patch('search_api.resources.V2_0.local_land_charge_v_2.LocalLandCharge')
    def test_get_result_originating_authority_not_found(self, mock_llc):

        mock_llc.query.filter.return_value.order_by.return_value.all.return_value = []

        with self.assertRaises(ApplicationError) as exc:
            get_results_for_originating_authority_charge("an ID", "an Authority")

        self.assertEqual(exc.exception.message, "No land charges found")

    @patch('search_api.resources.V2_0.local_land_charge_v_2.filter_sensitive_charges')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.model_mappers')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.LocalLandCharge')
    def test_get_result_originating_authority_all_filtered(self, mock_llc, mock_mappers, mock_filter):

        with super_test_context(main.app):
            mock_llc.query.filter.return_value.order_by.return_value.all.return_value = [1]
            mock_mappers.map_llc_result_to_dictionary_list.return_value = [1]
            g.principle = MagicMock()
            g.principle.has_all_permissions.return_value = False
            mock_filter.return_value = []

            with self.assertRaises(ApplicationError) as exc:
                get_results_for_originating_authority_charge("an ID", "an Authority")

            self.assertEqual(exc.exception.message, "No land charges found")

    @patch('search_api.resources.V2_0.local_land_charge_v_2.filter_sensitive_charges')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.model_mappers')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.LocalLandCharge')
    def test_get_result_originating_authority_some_filtered(self, mock_llc, mock_mappers, mock_filter):

        with super_test_context(main.app):
            mock_llc.query.filter.return_value.order_by.return_value.all.return_value = [1, 2, 3]
            mock_mappers.map_llc_result_to_dictionary_list.return_value = [1, 2, 3]
            g.principle = MagicMock()
            g.principle.has_all_permissions.return_value = False
            mock_filter.return_value = [1, 3]

            result = get_results_for_originating_authority_charge("an ID", "an Authority")

            self.assertEqual(result[0], '[1, 3]')

    @patch('search_api.app.validate')
    def test_get_correlations_invalid(self, mock_validate):
        response = self.client.post(url_for("local_land_charge_V_2.get_correlations"),
                                    headers={'Authorization': 'Fake JWT'}, json={})
        self.assertIn('Invalid json', response.data.decode())
        self.assertStatus(response, 400)

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.db')
    def test_get_correlations_ok(self, mock_db, mock_validate):
        mock_db.session.query.return_value.select_from.return_value.join.return_value.join.return_value. \
            filter.return_value.filter.return_value.all.return_value = [
                ["LLC-1", 1, "oaci1", "mpc1"],
                ["LLC-2", 2, "oaci2", "mpc2"],
                ["LLC-3", 3, "oaci3", "mpc3"]
            ]

        response = self.client.post(url_for("local_land_charge_V_2.get_correlations"),
                                    headers={'Authorization': 'Fake JWT'},
                                    json={"charge_ids": ["LLC-1", "LLC-2", "LLC-3", "LLC-4"]})

        self.assertEqual(json.loads(response.data.decode()),
                         {
                             "invalid_charge_ids": ["LLC-4"],
                             "charge_correlations": [
                                 {
                                     "originating_authority_charge_identifier": "oaci1",
                                     "migration_partner_code": "mpc1",
                                     "local_land_charge": "LLC-1",
                                     "version_id": 1
                                 }, {
                                     "originating_authority_charge_identifier": "oaci2",
                                     "migration_partner_code": "mpc2",
                                     "local_land_charge": "LLC-2",
                                     "version_id": 2
                                 }, {
                                     "originating_authority_charge_identifier": "oaci3",
                                     "migration_partner_code": "mpc3",
                                     "local_land_charge": "LLC-3",
                                     "version_id": 3
                                 }
                             ]
        })

    @patch('search_api.app.validate')
    def test_get_charge_types_invalid(self, mock_validate):
        response = self.client.post(url_for("local_land_charge_V_2.get_charge_types"),
                                    headers={'Authorization': 'Fake JWT'}, json={})
        self.assertIn('Invalid json', response.data.decode())
        self.assertStatus(response, 400)

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.db')
    def test_get_charge_types_ok(self, mock_db, mock_validate):
        mock_db.session.query.return_value.filter.return_value.all.return_value = [
            ["LLC-1", "Planning", "Conditional planning consent"],
            ["LLC-2", "Light obstruction notice", None],
            ["LLC-3", "Financial", None]
        ]

        response = self.client.post(url_for("local_land_charge_V_2.get_charge_types"),
                                    headers={'Authorization': 'Fake JWT'},
                                    json={"charge_ids": ["LLC-1", "LLC-2", "LLC-3", "LLC-4"]})

        self.assertEqual(json.loads(response.data.decode()),
                         {
                             "invalid_charge_ids": ["LLC-4"],
                             "valid_charges": [
                                 {
                                     "local_land_charge": "LLC-1",
                                     "category": "Planning",
                                     "sub_category": "Conditional planning consent"
                                 }, {
                                     "local_land_charge": "LLC-2",
                                     "category": "Light obstruction notice",
                                     "sub_category": None
                                 }, {
                                     "local_land_charge": "LLC-3",
                                     "category": "Financial",
                                     "sub_category": None
                                 }
                             ]
        })

    @patch('search_api.resources.V2_0.local_land_charge_v_2.mapping')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.to_shape')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.db')
    @patch('search_api.app.validate')
    def test_get_get_collect_extents(self, mock_validate, mock_db, mock_to_shape, mock_mapping):

        with super_test_context(main.app):
            mock_mapping.return_value = {"some": "geojson"}
            mock_to_shape.return_value = "ashape"

            mock_db.session.query.return_value.select_from.return_value.join.return_value.filter.return_value. \
                one_or_none.return_value = [["LLC-1"], "somegeometry"]

            response = self.client.post(url_for('local_land_charge_V_2.get_collect_extents'),
                                        headers={'Authorization': 'Fake JWT'},
                                        json={"charge_ids": ["LLC-1", "LLC-2"]})

            self.assertEqual(response.json, {
                "invalid_charge_ids": ["LLC-2"],
                "collected_extents": {"some": "geojson"},
                "valid_charge_ids": ["LLC-1"]
            })

    @patch('search_api.resources.V2_0.local_land_charge_v_2.mapping')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.to_shape')
    @patch('search_api.resources.V2_0.local_land_charge_v_2.db')
    @patch('search_api.app.validate')
    def test_get_get_collect_extents_no_geom(self, mock_validate, mock_db, mock_to_shape, mock_mapping):

        with super_test_context(main.app):
            mock_mapping.return_value = {"some": "geojson"}
            mock_to_shape.return_value = "ashape"

            mock_db.session.query.return_value.select_from.return_value.join.return_value.filter.return_value. \
                one_or_none.return_value = [["LLC-1"], None]

            response = self.client.post(url_for('local_land_charge_V_2.get_collect_extents'),
                                        headers={'Authorization': 'Fake JWT'},
                                        json={"charge_ids": ["LLC-1", "LLC-2"]})

            self.assertEqual(response.json, {
                "invalid_charge_ids": ["LLC-2"],
                "collected_extents": None,
                "valid_charge_ids": ["LLC-1"]
            })

    @patch('search_api.app.validate')
    def test_get_get_collect_extents_no_charges(self, mock_validate):

        with super_test_context(main.app):

            response = self.client.post(url_for('local_land_charge_V_2.get_collect_extents'),
                                        headers={'Authorization': 'Fake JWT'},
                                        json={"rhubarb": ["LLC-1", "LLC-2"]})

            self.assertEqual(response.json, {'error_code': 'CE01', 'error_message': 'Invalid json'})
