from flask import current_app, g
from search_api.config import LA_API_URL
from search_api.exceptions import ApplicationError


class LocalAuthorityService(object):

    @staticmethod
    def get_organisation_title_details():
        if not hasattr(g, "organisation_title_details") or not g.organisation_title_details:
            g.organisation_title_details = {}
            request_path = "{}/v1.0/organisations".format(LA_API_URL)
            current_app.logger.info("Calling local authority api via this URL: {}".format(request_path))
            response = g.requests.get(request_path)

            if response.status_code == 200:
                current_app.logger.info("Organisations found")
                organisations = response.json()
                for organisation in organisations:
                    org_title = organisation.get('title')
                    org_names = organisation.get('historic_names').get('valid_names')
                    if org_title and org_names:
                        # Given table constraints, this check should always pass but might as well do it just in case,
                        # also every historic name must be unique so we can use them as the keys in this dict
                        for org_name in org_names:
                            g.organisation_title_details[org_name] = org_title
            else:
                current_app.logger.error("Error occurred when getting authorities")
                raise ApplicationError("Error occurred when getting authorities", "ORG1", 500)

        return g.organisation_title_details
