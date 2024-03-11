import base64
import json

from flask import Blueprint, current_app, g, request
from geoalchemy2 import shape
from jwt_validation.models import MaintainPrinciple
from search_api.exceptions import ApplicationError
from search_api.extensions import db
from search_api.models import (GeometryFeature, LocalLandCharge,
                               LocalLandChargeHistory)
from search_api.utilities import model_mappers
from search_api.utilities.charge_id import decode_charge_id, is_valid_charge_id
from search_api.utilities.sensitive_charge_filter import \
    filter_sensitive_charges
from shapely.geometry import shape as shapely_shape
from sqlalchemy import func

local_land_charge = Blueprint('local_land_charge', __name__, url_prefix='/search')


@local_land_charge.route('/local_land_charges/<charge_id>', methods=['GET'])
def get_local_land_charge(charge_id):
    """Get local land charge

    Returns local land charge with specified charge_id
    """
    current_app.logger.info("Get local land charge by ID '%s'", charge_id)
    charge_id_param = charge_id.upper()

    if is_valid_charge_id(charge_id_param):
        charge_id_base_10 = decode_charge_id(charge_id_param)
        llc_result = LocalLandCharge.query.get(charge_id_base_10)
    else:
        raise ApplicationError("Invalid Land Charge Number", 422, 422)

    if not llc_result:
        raise ApplicationError("No land charges found.", 404, 404)

    current_app.logger.info("Returning local land charge '%s'", charge_id)

    # returns the original data saved on the database
    original = request.args.get('original')
    if original is None:
        result_dict = model_mappers.map_llc_charge_display_result_to_dictionary_list(llc_result)
    else:
        result_dict = model_mappers.map_llc_result_to_dictionary_list(llc_result)

    if not g.principle.has_all_permissions(['View Sensitive Charges']):
        if (isinstance(g.principle, MaintainPrinciple) and
            g.principle.role == current_app.config['ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS'][0] and
                g.principle.organisation == current_app.config['ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS'][1]):
            current_app.logger.warn("Allowing sensitive charge retrieval for user role %s, organisation %s",
                                    g.principle.role, g.principle.organisation)
        else:
            filtered = filter_sensitive_charges(result_dict)
            if not filtered:
                current_app.logger.info("Land Charge '{}' is sensitive".format(charge_id))
                raise ApplicationError("No land charges found.", 404, 404)

    return json.dumps(result_dict), 200, {'Content-Type': 'application/json'}


@local_land_charge.route('/local_land_charges/', methods=['GET'])
def get_local_land_charges():
    """Get a list of land charges

    Returns all if no parameter is required, otherwise it will return
    those contained in bounding box.
    """
    current_app.logger.info("Get local land charges by geometry search")
    geo_json_extent = request.args.get('boundingBox')
    if geo_json_extent:
        try:
            json_extent = json.loads(base64.b64decode(geo_json_extent).decode())
            extent_shape = shapely_shape(json_extent)

            features = GeometryFeature.query.filter(
                func.ST_Intersects(
                    GeometryFeature.geometry, shape.from_shape(extent_shape, srid=27700)
                )).options(db.joinedload(GeometryFeature.local_land_charge)).all()
            res_set = set()
            for feature in features:
                res_set.add(feature.local_land_charge)
            llc_result = list(res_set)

        except (ValueError, TypeError) as err:
            raise ApplicationError("Unprocessable Entity. {}".format(err), 422, 422)
    else:
        current_app.logger.warning("No bounding box supplied - returning all local land charges")
        llc_result = LocalLandCharge.query.all()

    if not llc_result:
        raise ApplicationError("No land charges found", 404, 404)

    result_dict = model_mappers.map_llc_result_to_dictionary_list(llc_result)

    if result_dict and not g.principle.has_all_permissions(['View Sensitive Charges']):
        result_dict = filter_sensitive_charges(result_dict)

    if not result_dict:
        current_app.logger.info("Land Charges are sensitive")
        raise ApplicationError("No land charges found", 404, 404)

    current_app.logger.info("Returning local land charges")
    return json.dumps(result_dict), 200, {'Content-Type': 'application/json'}


@local_land_charge.route('/local_land_charges/<charge_id>/history', methods=['GET'])
def get_local_land_charge_history(charge_id):
    """Get history of land charge.

    Returns all history for local land charge with charge_id
    """
    current_app.logger.info("Get local land charge history by ID '%s'", charge_id)
    charge_id_param = charge_id.upper()

    if is_valid_charge_id(charge_id_param):
        charge_id_base_10 = decode_charge_id(charge_id_param)
    else:
        raise ApplicationError("Invalid Land Charge Number", 422, 422)

    llc_result = LocalLandCharge.query.get(charge_id_base_10)

    if not llc_result:
        raise ApplicationError("No land charge history found.", 404, 404)

    llc_dict = model_mappers.map_llc_result_to_dictionary_list(llc_result)

    if llc_dict and not g.principle.has_all_permissions(['View Sensitive Charges']):
        filtered = filter_sensitive_charges(llc_dict)
        if not filtered:
            current_app.logger.info("Land Charge '{}' is sensitive".format(charge_id))
            raise ApplicationError("No land charge history found.", 404, 404)

    hist_result = LocalLandChargeHistory.query.filter(LocalLandChargeHistory.id == charge_id_base_10)\
        .order_by(LocalLandChargeHistory.entry_timestamp).all()

    if not hist_result:
        raise ApplicationError("No land charge history found.", 404, 404)

    hist_dict = model_mappers.map_llc_history_result_to_dictionary_list(hist_result)

    current_app.logger.info("Returning local land charge history")
    return json.dumps(hist_dict), 200, {'Content-Type': 'application/json'}
