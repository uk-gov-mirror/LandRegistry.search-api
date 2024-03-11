import base64
import json
import re

from flask import Blueprint, Response, current_app, g, request
from search_api import config
from search_api.exceptions import ApplicationError
from search_api.utilities import address_response_mapper

addresses = Blueprint('addresses', __name__, url_prefix='/search/addresses')

body = {
    "datasource": "local_authority",
    "search_type": "",
    "query_value": "",
    "response_srid": "EPSG:27700",
    "max_results": 1000
}
postcode_regex_check = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})' \
                       '|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'

partial_postcode_regex_check = '^(([gG][iI][rR] {0,}0[aA]{2})|((([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)' \
                               '|(([a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|([a-pr-uwyzA-PR-UWYZ]' \
                               '[a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y])))( {0,}[0-9]' \
                               '[abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2})?))$'

uprn_regex_check = r'^[0-9]{1,13}$'


@addresses.route('/postcode/<postcode>', methods=['GET'])
def get_addresses_by_postcode(postcode):
    is_base64 = request.args.get('base64')
    if is_base64 and is_base64.upper() == "TRUE":
        postcode = base64.urlsafe_b64decode(postcode).decode('UTF8')

    current_app.logger.info("Get address by postcode '%s'", postcode)
    postcode = postcode.strip()
    postcode_is_valid = re.match(postcode_regex_check, postcode)

    if postcode_is_valid is not None:
        body["search_type"] = "postcode"
        body["query_value"] = postcode
        return search_for_addresses(body, "postcode")
    else:
        raise ApplicationError("Unprocessable Entity: Postcode is not valid", 422, 422)


@addresses.route('/uprn/<uprn>', methods=['GET'])
def get_addresses_by_uprn(uprn):
    is_base64 = request.args.get('base64')
    if is_base64 and is_base64.upper() == "TRUE":
        uprn = base64.urlsafe_b64decode(uprn).decode('UTF8')

    current_app.logger.info("Get address by UPRN '%s'", uprn)
    uprn = uprn.strip()
    uprn_is_valid = re.match(uprn_regex_check, uprn)

    if uprn_is_valid is not None:
        body["search_type"] = "uprn"
        body["query_value"] = int(uprn)
        return search_for_addresses(body, "uprn")
    else:
        raise ApplicationError("Unprocessable Entity: UPRN is not valid", 422, 422)


@addresses.route('/text/<text>', methods=['GET'])
def get_addresses_by_text(text):
    is_base64 = request.args.get('base64')
    if is_base64 and is_base64.upper() == "TRUE":
        text = base64.urlsafe_b64decode(text).decode('UTF8')

    current_app.logger.info("Get address by text '%s'", text)
    text = text.strip()

    body["search_type"] = "text_search"
    body["query_value"] = text
    search_type = "text"

    is_partial_postcode = re.match(partial_postcode_regex_check, text)
    if is_partial_postcode is not None:
        search_type = "partial_postcode"

    return search_for_addresses(body, search_type)


def search_for_addresses(request_body, search_type):
    current_app.logger.info("Performing '%s' address search", search_type)
    search_results = g.requests.post(config.ADDRESS_API_URL + '/v1/addresses/search',
                                     data=json.dumps(request_body, sort_keys=True),
                                     headers={"Content-Type": "application/json", "Accept": "application/json"})

    if search_results.status_code == 400:
        raise ApplicationError(search_results.json(), 400, 400)
    if search_results.status_code != 200:
        raise ApplicationError(search_results.json(), 500, 500)
    if not search_results.json():
        current_app.logger.warning("No addresses found for search")
        raise ApplicationError("No addresses found for search.", 404, 404)

    current_app.logger.info("Returning address search result")
    return Response(
        response=json.dumps(address_response_mapper.map_address_response(search_results.json(), search_type)),
        status=200,
        mimetype="application/json"
    )
