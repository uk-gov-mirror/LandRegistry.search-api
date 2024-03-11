import base64
import json
import re

from flask import Blueprint, Response, current_app, g
from flask.globals import request
from search_api import config
from search_api.dependencies.index_map_api import (
    search_for_index_map, search_for_index_map_by_title_no)
from search_api.exceptions import ApplicationError
from search_api.utilities.V2_0 import address_response_mapper_v_2

addresses_V_2 = Blueprint('addresses_V_2', __name__, url_prefix='/v2.0/search/addresses')

body = {
    "datasource": "local_authority",
    "search_type": "",
    "query_value": "",
    "response_srid": "EPSG:27700",
    "max_results": 1000
}
postcode_regex_check = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})' \
                       '|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'

uprn_regex_check = r'^[0-9]{1,13}$'
usrn_regex_check = r'^\d+$'


@addresses_V_2.route('/postcode/<postcode>', methods=['GET'])
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
        return search_for_addresses(body)
    else:
        raise ApplicationError("Unprocessable Entity: Postcode is not valid", 422, 422)


@addresses_V_2.route('/uprn/<uprn>', methods=['GET'])
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
        return search_for_addresses(body)
    else:
        raise ApplicationError("Unprocessable Entity: UPRN is not valid", 422, 422)


@addresses_V_2.route('/usrn/<usrn>', methods=['GET'])
def get_addresses_by_usrn(usrn):
    is_base64 = request.args.get('base64')
    postcode = request.args.get('value_2')
    if is_base64 and is_base64.upper() == "TRUE":
        usrn = base64.urlsafe_b64decode(usrn).decode('UTF8')

    current_app.logger.info("Get address by USRN '%s'", usrn)
    usrn = usrn.strip()
    usrn_is_valid = re.match(usrn_regex_check, usrn)

    if usrn_is_valid is not None:
        body["search_type"] = "usrn"
        body["query_value"] = int(usrn)
        if postcode:
            body['query_value_2'] = postcode
        return search_for_addresses(body)
    else:
        raise ApplicationError("Unprocessable Entity: USRN is not valid", 422, 422)


@addresses_V_2.route('/text/<text>', methods=['GET'])
def get_addresses_by_text(text):
    is_base64 = request.args.get('base64')
    if is_base64 and is_base64.upper() == "TRUE":
        text = base64.urlsafe_b64decode(text).decode('UTF8')

    current_app.logger.info("Get address by text '%s'", text)
    text = text.strip()

    body["search_type"] = "text_search"
    body["query_value"] = text

    return search_for_addresses(body)


@addresses_V_2.route('/title/<title>', methods=['GET'])
def get_index_map_by_title(title):
    is_base64 = request.args.get('base64')
    if is_base64 and is_base64.upper() == "TRUE":
        title = base64.urlsafe_b64decode(title).decode('UTF8')

    current_app.logger.info("Get index map by title '{}'".format(title))
    title = title.strip()

    search_results = search_for_index_map_by_title_no(title)

    if search_results.status_code == 200:
        index_map_json = search_results.json()
        index_map = {"type": "FeatureCollection",
                     "features": index_map_json['features']}
    elif search_results.status_code == 404:
        current_app.logger.warning("No index map found for title search")
        raise ApplicationError("No index map found for title search", 404, 404)
    else:
        current_app.logger.exception("Failed to retrieve index map")
        raise ApplicationError(search_results.json(), 500, 500)

    return Response(
        response=json.dumps(index_map),
        status=200,
        mimetype="application/json"
    )


def search_for_addresses(request_body):
    current_app.logger.info("Performing address search")
    search_results = g.requests.post(config.ADDRESS_API_URL + '/v2/addresses/search',
                                     data=json.dumps(request_body, sort_keys=True),
                                     headers={"Content-Type": "application/json", "Accept": "application/json"})
    if search_results.status_code == 400:
        raise ApplicationError(search_results.json(), 400, 400)
    if search_results.status_code != 200:
        raise ApplicationError(search_results.json(), 500, 500)
    if not search_results.json():
        current_app.logger.warning("No addresses found for search")
        raise ApplicationError("No addresses found for search.", 404, 404)

    mapped_resp = address_response_mapper_v_2.map_address_response(search_results.json())

    # If index_map argument set to true, get index map for all the addresses
    if request.args.get('index_map') and request.args.get('index_map').lower() == 'true' and config.INDEX_MAP_API_URL:
        for address in mapped_resp:
            if 'uprn' in address and address['uprn']:
                index_map = None
                try:
                    index_map = search_for_index_map(address['uprn'])
                except Exception:
                    current_app.logger.exception("Failed to retrieve index map")
                if index_map:
                    address['index_map'] = index_map

    current_app.logger.info("Returning address search result")
    return Response(
        response=json.dumps(mapped_resp),
        status=200,
        mimetype="application/json"
    )
