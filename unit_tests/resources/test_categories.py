from unittest.mock import MagicMock

from flask import url_for
from flask_testing import TestCase
from mock import patch
from search_api import main


class TestCategories(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_all_categories(self, mock_categories, mock_validate):
        mock_category = MagicMock()
        mock_category.name = "abc"
        mock_category.display_name = "Display"
        mock_category.add_permission = "test add permission"
        mock_category.vary_permission = "test vary permission"
        mock_category.cancel_permission = "test cancel permission"
        mock_category.add_on_behalf_permission = "test add on behalf permission"
        mock_category.selectable = True

        mock_categories.query \
            .filter.return_value \
            .order_by.return_value \
            .all.return_value = [mock_category]

        response = self.client.get(url_for('categories.get_all_categories'),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual(1, len(response.json))
        self.assertEqual("abc", response.json[0]['name'])
        self.assertEqual("Display", response.json[0]['display-name'])
        self.assertEqual("test add permission", response.json[0]['add-permission'])
        self.assertEqual("test vary permission", response.json[0]['vary-permission'])
        self.assertEqual("test cancel permission", response.json[0]['cancel-permission'])
        self.assertEqual("test add on behalf permission", response.json[0]['add-on-behalf-permission'])
        mock_validate.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_category(self, mock_categories, mock_validate):

        mock_category = MagicMock()
        mock_category.display_name = "display"

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = mock_category

        response = self.client.get(url_for('categories.get_category_latest_name', category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual("display", response.json["display-name"])
        mock_validate.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_category_404(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.return_value = None

        response = self.client.get(url_for('categories.get_category_latest_name', category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)
        mock_validate.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_sub_category_parent_does_not_exist(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [None, None]

        response = self.client.get(url_for('categories.get_sub_category_latest_name', category="Planning",
                                           sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(1, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_sub_category_does_not_exist(self, mock_categories, mock_validate):

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [MagicMock(), None]

        response = self.client.get(url_for('categories.get_sub_category_latest_name', category="Planning",
                                           sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 404)

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()

    @patch('search_api.app.validate')
    @patch('search_api.resources.V2_0.categories.ChargeCategory')
    def test_get_sub_category_successful(self, mock_categories, mock_validate):

        mock_parent = MagicMock()
        mock_parent.id = 1
        mock_parent.display_name = "parent display name"

        mock_sub_category = MagicMock()
        mock_sub_category.display_name = "child display name"

        mock_categories.query.filter.return_value.filter.return_value.first.side_effect = [mock_parent,
                                                                                           mock_sub_category]

        response = self.client.get(url_for('categories.get_sub_category_latest_name', category="Planning",
                                           sub_category="abc"),
                                   headers={'Authorization': 'Fake JWT', 'Content-Type': 'application/json'})

        self.assertStatus(response, 200)
        self.assertEqual("child display name", response.json["display-name"])

        mock_categories.query.filter.return_value.filter.return_value.first.assert_called()
        self.assertEqual(2, mock_categories.query.filter.return_value.filter.return_value.first.call_count)
        mock_validate.assert_called()
