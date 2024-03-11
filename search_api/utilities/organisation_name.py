from flask import current_app
from search_api.dependencies.local_authority_api.local_authority_api_service import \
    LocalAuthorityService


def get_latest_organisation_name(organisation):
    organisation_title_details = LocalAuthorityService.get_organisation_title_details()
    latest_name = organisation_title_details.get(organisation)
    if latest_name:
        current_app.logger.info("Organisation latest name {} found for {}".format(latest_name, organisation))
        return latest_name
    else:
        current_app.logger.info("Organisation not found for {}, using supplied name".format(organisation))
        return organisation
