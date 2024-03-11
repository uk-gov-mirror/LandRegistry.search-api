import copy
import unittest

from mock import MagicMock, patch
from search_api.main import app
from search_api.utilities import sensitive_charge_filter


charges = [{"item": {"charge-type": "a category", "charge-sub-category": "a sub category"}},
           {"item": {"charge-type": "a sensitive category", "charge-sub-category": "a sub category"}},
           {"item": {"charge-type": "a category", "charge-sub-category": "a sensitive sub category"}},
           {"item": {"charge-type": "a category", "charge-sub-category": "a sub category"}}]


sensitive_subcat = MagicMock()
sensitive_cat = MagicMock()
sensitive_cat.sub_categories = "A sub category"
sensitive_cat.charge_category = None
sensitive_subcat.charge_category = "A charge category"
sensitive_subcat.display_name_valid = {"valid_display_names": ["a sensitive sub category", "rhubarb"]}
sensitive_cat.display_name_valid = {"valid_display_names": ["a sensitive category", "custard"]}


class TestSensitiveChargeFilter(unittest.TestCase):

    @patch('search_api.utilities.sensitive_charge_filter.ChargeCategory')
    def test_filter_sensitive_charges_no_cats(self, mock_charge_cat):
        mock_charge_cat.query.filter.return_value.all.return_value = []
        result = sensitive_charge_filter.filter_sensitive_charges(charges)
        self.assertEqual(result, charges)

    @patch('search_api.utilities.sensitive_charge_filter.ChargeCategory')
    def test_filter_sensitive_charges_filtered(self, mock_charge_cat):
        with app.app_context():
            mock_charge_cat.query.filter.return_value.all.return_value = [sensitive_cat, sensitive_subcat]
            result = sensitive_charge_filter.filter_sensitive_charges(charges)
            self.assertEqual(result, [charges[0]] + [charges[3]])

    @patch('search_api.utilities.sensitive_charge_filter.ChargeCategory')
    def test_filter_sensitive_charges_filtered_geo(self, mock_charge_cat):
        with app.app_context():
            mock_charge_cat.query.filter.return_value.all.return_value = [sensitive_cat, sensitive_subcat]
            charges_copy1 = copy.deepcopy(charges)
            charges_copy2 = copy.deepcopy(charges)
            result = sensitive_charge_filter.filter_sensitive_charges(charges_copy1, True)
            charges_copy2[1]['item']['geometry'] = {"properties": "sensitive"}
            charges_copy2[1]['geometry'] = {"properties": "sensitive"}
            charges_copy2[2]['item']['geometry'] = {"properties": "sensitive"}
            charges_copy2[2]['geometry'] = {"properties": "sensitive"}
            self.assertEqual(result, charges_copy2)
