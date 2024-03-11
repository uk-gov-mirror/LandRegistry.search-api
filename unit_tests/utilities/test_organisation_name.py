from unittest import TestCase
from unittest.mock import patch

from search_api import main
from search_api.utilities.organisation_name import get_latest_organisation_name
from unit_tests.utilities_tests import super_test_context


class TestOrganisationName(TestCase):

    @patch('search_api.utilities.organisation_name.LocalAuthorityService')
    def test_get_latest_organisation_name_exists(self, mock_la_service):
        with super_test_context(main.app):
            mock_la_service.get_organisation_title_details.return_value = {
                'new test org': 'new test org',
                'old test org': 'new test org'
            }
            response = get_latest_organisation_name('old test org')
            self.assertEqual(response, 'new test org')

    @patch('search_api.utilities.organisation_name.LocalAuthorityService')
    def test_get_latest_organisation_name_no_exists(self, mock_la_service):
        with super_test_context(main.app):
            mock_la_service.get_organisation_title_details.return_value = {
                'new test org': 'new test org',
                'old test org': 'new test org'
            }
            response = get_latest_organisation_name('bunk test org')
            self.assertEqual(response, 'bunk test org')
