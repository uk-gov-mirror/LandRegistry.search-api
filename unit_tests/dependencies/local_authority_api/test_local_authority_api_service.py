from unittest import TestCase
from unittest.mock import MagicMock

from flask import g
from search_api import main
from search_api.dependencies.local_authority_api.local_authority_api_service import \
    LocalAuthorityService
from search_api.exceptions import ApplicationError
from unit_tests.utilities_tests import super_test_context


class TestLocalAuthorityApiService(TestCase):

    def test_get_latest_organisation_name_success(self):
        with super_test_context(main.app):
            g.requests = MagicMock()
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [{'title': 'new test name',
                                           'migrated': True,
                                           'maintenance': False,
                                           'historic_names': {
                                               'valid_names': ['new test name', 'old test name']
                                           }}]

            g.requests.get.return_value = response

            expected_response = {
                'new test name': 'new test name',
                'old test name': 'new test name'
            }

            response = LocalAuthorityService.get_organisation_title_details()
            self.assertEqual(response, expected_response)

            self.assertEqual(g.requests.get.call_count, 1)

    def test_get_latest_organisation_name_fail(self):
        with super_test_context(main.app):
            response = MagicMock()
            response.status_code = 500

            g.requests = MagicMock()
            g.requests.post.return_value = response

            with self.assertRaises(ApplicationError):
                LocalAuthorityService.get_organisation_title_details()
