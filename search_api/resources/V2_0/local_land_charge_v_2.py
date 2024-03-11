import json
from contextlib import contextmanager
from copy import copy

from flask import Blueprint, current_app, g, request
from geoalchemy2.functions import ST_Collect
from geoalchemy2.shape import to_shape
from llc_schema_dto import llc_schema
from search_api import config
from search_api.exceptions import ApplicationError
from search_api.extensions import db
from search_api.models import (GeometryFeature, LocalLandCharge,
                               LocalLandChargeHistory)
from search_api.resources.local_land_charge import (
    get_local_land_charge, get_local_land_charge_history)
from search_api.utilities import model_mappers
from search_api.utilities.charge_id import encode_charge_id
from search_api.utilities.organisation_name import get_latest_organisation_name
from search_api.utilities.sensitive_charge_filter import \
    filter_sensitive_charges
from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid
from sqlalchemy import and_, func
from sqlalchemy.orm import aliased

local_land_charge_V_2 = Blueprint('local_land_charge_V_2', __name__, url_prefix='/v2.0/search')

SORT_BY_FIELD = 'registration-date'

# Register V1 Endpoints
local_land_charge_V_2.add_url_rule('/local_land_charges/<charge_id>',
                                   view_func=get_local_land_charge,
                                   methods=['GET'])

local_land_charge_V_2.add_url_rule('/local_land_charges/<charge_id>/history',
                                   view_func=get_local_land_charge_history,
                                   methods=['GET'])


@contextmanager
def getcursor():  # pragma: no cover
    con = db.engine.raw_connection()
    try:
        yield con.cursor()
    finally:
        con.commit()
        con.close()


@local_land_charge_V_2.route('/local_land_charges/charge_types', methods=['POST'])
def get_charge_types():
    """Post a list of land charges and returns if they are valid IDs and what type the charge is"""
    current_app.logger.info("Checking charge ID validity")

    json_request = request.get_json()
    if "charge_ids" not in json_request or not isinstance(json_request["charge_ids"], list):
        raise ApplicationError("Invalid json", "TYP01", 400)

    results = db.session.query(LocalLandCharge.llc_id,
                               LocalLandCharge.llc_item['charge-type'],
                               LocalLandCharge.llc_item['charge-sub-category']) \
        .filter(LocalLandCharge.llc_id.in_(json_request["charge_ids"])).all()

    output = {
        "invalid_charge_ids": copy(json_request['charge_ids']),
        "valid_charges": []
    }

    for result in results:
        output['valid_charges'].append({
            "local_land_charge": result[0],
            "category": result[1],
            "sub_category": result[2]
        })
        output['invalid_charge_ids'].remove(result[0])

    return json.dumps(output), 200, {'Content-Type': 'application/json'}


@local_land_charge_V_2.route('/local_land_charges/correlations', methods=['POST'])
def get_correlations():
    """Get information to create correlation file for a given set of charge IDs"""
    current_app.logger.info("Getting correlation information")
    json_request = request.get_json()
    if "charge_ids" not in json_request or not isinstance(json_request["charge_ids"], list):
        raise ApplicationError("Invalid json", "COR01", 400)
    alias_llchist = aliased(LocalLandChargeHistory)
    results = db.session.query(LocalLandCharge.llc_id, LocalLandChargeHistory.entry_number,
                               LocalLandCharge.llc_item['originating-authority-charge-identifier'],
                               LocalLandCharge.llc_item['migration-supplier']).select_from(LocalLandChargeHistory) \
        .join(alias_llchist, and_(LocalLandChargeHistory.id == alias_llchist.id,
                                  alias_llchist.entry_number > LocalLandChargeHistory.entry_number), isouter=True) \
        .join(LocalLandCharge, LocalLandChargeHistory.id == LocalLandCharge.id) \
        .filter(alias_llchist.entry_number.is_(None)) \
        .filter(LocalLandCharge.llc_id.in_(json_request["charge_ids"])).all()

    output = {
        "invalid_charge_ids": copy(json_request['charge_ids']),
        "charge_correlations": []
    }

    for result in results:
        output['charge_correlations'].append({
            "originating_authority_charge_identifier": result[2],
            "migration_partner_code": result[3],
            "local_land_charge": result[0],
            "version_id": result[1]
        })
        output['invalid_charge_ids'].remove(result[0])

    return json.dumps(output), 200, {'Content-Type': 'application/json'}


@local_land_charge_V_2.route('/local_land_charges/collect_extents', methods=['POST'])
def get_collect_extents():
    """Create collected extents for a given set of charge IDs"""
    current_app.logger.info("Getting charge information")
    json_request = request.get_json()
    if "charge_ids" not in json_request or not isinstance(json_request["charge_ids"], list):
        raise ApplicationError("Invalid json", "CE01", 400)
    geom_result = db.session.query(
        func.jsonb_agg(LocalLandCharge.llc_id), ST_Collect(GeometryFeature.geometry)). \
        select_from(LocalLandCharge).join(GeometryFeature). \
        filter(LocalLandCharge.llc_id.in_(json_request["charge_ids"])).one_or_none()

    if geom_result and geom_result[0]:
        valid_ids = set(geom_result[0])
    else:
        valid_ids = {}
    if geom_result and geom_result[1]:
        collect_extents = mapping(to_shape(geom_result[1]))
    else:
        collect_extents = None

    output = {
        "invalid_charge_ids": list(set(json_request["charge_ids"]) - valid_ids),
        "collected_extents": collect_extents,
        "valid_charge_ids": list(valid_ids)
    }

    return json.dumps(output), 200, {'Content-Type': 'application/json'}


@local_land_charge_V_2.route('/local_land_charges', methods=['GET'])
def get_local_land_charges():
    """Get a list of land charges"""
    current_app.logger.info("Get local land charges by filter search")

    further_information_reference = request.args.get('furtherInformationReference')
    authority_charge_id = request.args.get('authority_charge_id')
    migrating_authority = request.args.get('migrating_authority')

    if further_information_reference:
        return get_results_for_further_information_reference(further_information_reference)
    elif (authority_charge_id and migrating_authority):
        return get_results_for_originating_authority_charge(authority_charge_id, migrating_authority)
    else:
        raise ApplicationError("Failed to provide a filter.", 400, 400)


@local_land_charge_V_2.route('/local_land_charges', methods=['POST'])
def post_local_land_charges():
    """Get a list of land charges"""
    current_app.logger.info("Get local land charges by geometry search")

    geo_json_extent = request.get_json()
    charge_filter = request.args.get('filter')
    max_results = (int(request.args.get('maxResults')) if request.args.get('maxResults') else 1000)
    filter_sensitive_geometry = request.args.get('filter_sensitive_geometry', False)
    schema_version = request.args.get('schema_version', config.SCHEMA_VERSION)

    if geo_json_extent:
        return get_results_for_boundary(geo_json_extent, charge_filter, max_results, filter_sensitive_geometry,
                                        schema_version=schema_version)
    else:
        raise ApplicationError("Failed to provide a search area.", 400, 400)


@local_land_charge_V_2.route('/local_land_charges/thresholds', methods=['POST'])
def post_local_land_charges_thresholds():
    """Get a list of land charges"""
    current_app.logger.info("Get local land charges by geometry search")

    payload = request.get_json()
    geojson_extent = payload['geojson']
    percentage_threshold = payload['percentage_threshold']
    area_threshold = payload['area_threshold']
    charge_filter = request.args.get('filter')
    max_results = (int(request.args.get('maxResults')) if request.args.get('maxResults') else 1000)
    filter_sensitive_geometry = request.args.get('filter_sensitive_geometry', False)

    if geojson_extent:
        return get_results_for_boundary(geojson_extent, charge_filter, max_results, filter_sensitive_geometry,
                                        percentage_threshold=percentage_threshold, area_threshold=area_threshold,
                                        threshold_search=True)
    else:
        raise ApplicationError("Failed to provide a search area.", 400, 400)


def count_results_for_boundary(geo_extent_shape, cancelled_sql):
    with getcursor() as cur:
        try:
            count_query = ("""SELECT count(DISTINCT llc.id) \
                    FROM geometry_feature as geo \
                    JOIN local_land_charge as llc on geo.local_land_charge_id = llc.id \
                    WHERE ST_DWithin(geo.geometry, ST_GeomFromText('%s', 27700), 0) \
                    AND NOT (ST_Touches(geo.geometry, ST_GeomFromText('%s', 27700)) \
                        AND ST_GeometryType(geo.geometry) IN ('ST_Polygon', 'ST_MultiPolygon')) \
                    %s""" % (geo_extent_shape, geo_extent_shape, cancelled_sql))

            # Execute a query to count the Number of Charges
            cur.execute(count_query)
            result = cur.fetchone()
            return result[0]
        except (ValueError, TypeError) as err:
            raise ApplicationError("Error getting charge count. {}".format(err), 422, 422)


def count_results_for_boundary_thresholds(geo_extent_shape, cancelled_sql):
    """Return the number of charges in the search area.


    When using boundaries, all charges are counted because later in
    the process both non-boundary (AKA non-adjoining) and boundary (AKA adjoining) charges are returned.

    Cancelled charges are never counted, as this is intended to support the search-status-api which will not
    require them.

    :param geo_extent_shape: the extent within which the search should be performed
    :param cancelled_sql: a short sql string to exclude cancelled charges if required
    :return: number of charges contained within the search area
    """
    with getcursor() as cur:
        try:
            count_query = ("""SELECT count(DISTINCT llc.id) \
                    FROM geometry_feature as geo \
                    JOIN local_land_charge as llc on geo.local_land_charge_id = llc.id \
                    WHERE ST_DWithin(geo.geometry, ST_GeomFromText('%s', 27700), 0) \
                    %s""" % (geo_extent_shape, cancelled_sql))

            # Execute a query to count the Number of Charges
            cur.execute(count_query)
            result = cur.fetchone()
            return result[0]
        except (ValueError, TypeError) as err:
            raise ApplicationError("Error getting charge count. {}".format(err), 422, 422)


def get_data_for_boundary(geo_extent_shape, cancelled_sql):
    #  returns the number of rows based on the SQL search with Boundary
    with getcursor() as cur:
        try:
            query = ("""SELECT DISTINCT llc.id, llc.cancelled, llc.further_information_reference, llc.llc_item, \
                    sp.display_title as stat_prov, cc.display_name as charge_type, \
                    scc.display_name as charge_sub_type, llc.llc_item->>'%s', \
                    FALSE as adjoining \
                    FROM geometry_feature as geo \
                    JOIN local_land_charge as llc on geo.local_land_charge_id = llc.id \
                    LEFT OUTER JOIN statutory_provision as sp \
                    ON UPPER(sp.title) = UPPER(llc.llc_item->>'statutory-provision') \
                    JOIN charge_categories as cc ON (cc.display_name_valid->'valid_display_names')::jsonb ? \
                    CAST(llc.llc_item->>'charge-type' AS text) AND cc.parent_id is NULL \
                    LEFT OUTER JOIN charge_categories as scc ON (scc.display_name_valid->'valid_display_names')\
                    ::jsonb ? CAST(llc.llc_item->>'charge-sub-category' AS text) AND scc.parent_id = cc.id \
                    WHERE ST_DWithin(geo.geometry, ST_GeomFromText('%s', 27700), 0) \
                    AND NOT (ST_Touches(geo.geometry, ST_GeomFromText('%s', 27700)) \
                        AND ST_GeometryType(geo.geometry) IN ('ST_Polygon', 'ST_MultiPolygon')) \
                    %s ORDER BY llc.llc_item->>'%s' DESC
                    """ % (SORT_BY_FIELD, geo_extent_shape, geo_extent_shape, cancelled_sql,
                           SORT_BY_FIELD))

            # Execute a query to get the Charges
            cur.execute(query)
            rows = cur.fetchall()
            return rows
        except (ValueError, TypeError) as err:
            raise ApplicationError("Error getting charges. {}".format(err), 422, 422)


def get_data_for_non_boundary_thresholds(geo_extent_shape, cancelled_sql, percentage_threshold, area_threshold):
    """Get list of charges contained within the search area and with overlap values matching thresholds


    Takes in a search area and two threshold values. The percentage threshold will be used to determine if a charge
    is part of the search area or only bordering it. For example, if 5 is provided, then charges will be included in
    the results if more than 5% of the charge is covered by the search area, or more than 5% of the search area is
    covered by the charge.

    The area threshold is used similarly. Again if 2 is provided, a charge will be included if the area of overlap
    for the charge and search area is more than 2 square metres.

    If any one of these thresholds is exceeded then the charge will be included in the results. If all 3 values
    fall below the thresholds then the charge will be counted as being bordering the search area and will not
    be returned.

    Cancelled charges are never returned, as this is intended to support the search-status-api which will not
    require them.

    If a charge has zero area it will be automatically counted as being non-boundary as it must be wholly contained
    within the search area to have been found at all, and therefore additional calculations are unnecessary. Also they
    would break due to divide by zero error.

    :param geo_extent_shape: the extent within which the search should be performed
    :param cancelled_sql: a short sql string to exclude cancelled charges if required
    :param percentage_threshold: the minimum percentage of coverage to return a charge
    :param area_threshold: the minimum area in square metres of coverage to return a charge
    :return: list of charges contained within the search area and with overlap values matching thresholds
    """
    #  returns the number of rows based on the SQL search with Boundary
    with getcursor() as cur:
        try:
            search_area = geo_extent_shape.area
            query = ("""SELECT DISTINCT llc.id, llc.cancelled, llc.further_information_reference, llc.llc_item, \
                    sp.display_title as stat_prov, cc.display_name as charge_type, \
                    scc.display_name as charge_sub_type, llc.llc_item->>'%s', \
                    false as adjoining \
                    FROM geometry_feature as geo \
                    JOIN local_land_charge as llc on geo.local_land_charge_id = llc.id \
                    LEFT OUTER JOIN statutory_provision as sp \
                    ON UPPER(sp.title) = UPPER(llc.llc_item->>'statutory-provision') \
                    JOIN charge_categories as cc ON (cc.display_name_valid->'valid_display_names')::jsonb ? \
                    CAST(llc.llc_item->>'charge-type' AS text) AND cc.parent_id is NULL \
                    LEFT OUTER JOIN charge_categories as scc ON (scc.display_name_valid->'valid_display_names')\
                    ::jsonb ? CAST(llc.llc_item->>'charge-sub-category' AS text) AND scc.parent_id = cc.id \
                    WHERE ST_DWithin(geo.geometry, ST_GeomFromText('%s', 27700), 0) \
                    AND ((\
                        ST_Area(geo.geometry) = 0 OR \
                        ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) >= %d \
                        OR \
                        (ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) / %d) * 100 >= %d \
                        OR \
                        (ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) / \
                        ST_Area(geo.geometry)) * 100 >= %d\
                    ) \
                    AND NOT (ST_Touches(geo.geometry, ST_GeomFromText('%s', 27700)) \
                        AND ST_GeometryType(geo.geometry) IN ('ST_Polygon', 'ST_MultiPolygon'))) \
                    %s \
                    ORDER BY llc.llc_item->>'%s' DESC
                    """ % (SORT_BY_FIELD, geo_extent_shape, geo_extent_shape, area_threshold, geo_extent_shape,
                           search_area, percentage_threshold, geo_extent_shape, percentage_threshold, geo_extent_shape,
                           cancelled_sql, SORT_BY_FIELD))

            # Execute a query to get the Charges
            cur.execute(query)
            rows = cur.fetchall()
            return rows
        except (ValueError, TypeError) as err:
            raise ApplicationError("Error getting charges. {}".format(err), 422, 422)


def get_data_for_boundary_thresholds(geo_extent_shape, cancelled_sql, percentage_threshold, area_threshold):
    """Get list of charges contained within the search area and with overlap values matching thresholds


    Takes in a search area and two threshold values. The percentage threshold will be used to determine if a charge
    is part of the search area or only bordering it. For example, if 5 is provided, then charges will be classed as in
    the "boundary" if less than 5% of the charge is covered by the search area, and less than 5% of the search area is
    covered by the charge.

    The area threshold is used similarly. Again if 2 is provided, a charge will be in the "boundary" if the area of
    overlap for the charge and search area is less than 2 square metres.

    As this function returns charges in the "boundary" area, all 3 of the above criteria must be met for a charge to
    be counted as being in the "boundary" and therefore returned.

    If ALL of these thresholds ARE NOT exceeded but the charge is within the search area, then the charge will be
    included in the results. The charge will be counted as being bordering the search area and will be returned.

    Cancelled charges are never returned, as this is intended to support the search-status-api which will not
    require them.

    If a charge has zero area it will be automatically counted as being non-boundary as it must be wholly contained
    within the search area to have been found at all, and therefore additional calculations are unnecessary. Also they
    would break due to divide by zero error.

    :param geo_extent_shape: the extent within which the search should be performed
    :param cancelled_sql: a short sql string to exclude cancelled charges if required
    :param percentage_threshold: the minimum percentage of coverage to return a charge
    :param area_threshold: the minimum area in square metres of coverage to return a charge
    :return: list of charges contained within the search area and with overlap values matching thresholds
    """
    #  returns the number of rows based on the SQL search with Boundary
    with getcursor() as cur:
        try:
            search_area = geo_extent_shape.area
            query = ("""SELECT DISTINCT llc.id, llc.cancelled, llc.further_information_reference, llc.llc_item, \
                    sp.display_title as stat_prov, cc.display_name as charge_type, \
                    scc.display_name as charge_sub_type, llc.llc_item->>'%s', \
                    true as adjoining \
                    FROM geometry_feature as geo \
                    JOIN local_land_charge as llc on geo.local_land_charge_id = llc.id \
                    LEFT OUTER JOIN statutory_provision as sp \
                    ON UPPER(sp.title) = UPPER(llc.llc_item->>'statutory-provision') \
                    JOIN charge_categories as cc ON (cc.display_name_valid->'valid_display_names')::jsonb ? \
                    CAST(llc.llc_item->>'charge-type' AS text) AND cc.parent_id is NULL \
                    LEFT OUTER JOIN charge_categories as scc ON (scc.display_name_valid->'valid_display_names')\
                    ::jsonb ? CAST(llc.llc_item->>'charge-sub-category' AS text) AND scc.parent_id = cc.id \
                    WHERE ST_DWithin(geo.geometry, ST_GeomFromText('%s', 27700), 0) \
                    AND ((\
                        ST_Area(geo.geometry) > 0 AND \
                        ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) < %d \
                        AND \
                        (ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) / %d) * 100 < %d \
                        AND \
                        (ST_Area(ST_Intersection(geo.geometry, ST_GeomFromText('%s', 27700))) / \
                        ST_Area(geo.geometry)) * 100 < %d\
                    ) \
                    OR (ST_Touches(geo.geometry, ST_GeomFromText('%s', 27700)) \
                        AND ST_GeometryType(geo.geometry) IN ('ST_Polygon', 'ST_MultiPolygon'))) \
                    %s \
                    ORDER BY llc.llc_item->>'%s' DESC
                    """ % (SORT_BY_FIELD, geo_extent_shape, geo_extent_shape, area_threshold, geo_extent_shape,
                           search_area, percentage_threshold, geo_extent_shape, percentage_threshold, geo_extent_shape,
                           cancelled_sql, SORT_BY_FIELD))

            # Execute a query to get the Charges
            cur.execute(query)
            rows = cur.fetchall()
            return rows
        except (ValueError, TypeError) as err:
            raise ApplicationError("Error getting charges. {}".format(err), 422, 422)


def get_results_for_boundary(boundary, charge_filter, max_results, filter_sensitive_geometry,
                             percentage_threshold=0, area_threshold=0, threshold_search=False,
                             schema_version=config.SCHEMA_VERSION):
    """Returns the results of land charges contained in a extent

    :param boundary: Extent to search for land charges within
    :param charge_filter: String indicating whether to filter out cancelled charges
    :param max_results: Max number of land charges to be returned.  Defaults to 1000
    :param filter_sensitive_geometry: Boolean to indicate whether to return sensitive charges or not
    :param percentage_threshold: The largest percentage of overlap for a charge to be considered adjoining
    :param area_threshold: The largest area (in square metres) of overlap for a charge to be considered adjoining
    :param threshold_search: Will be True if performing a new style search where adjoining charges are determined by
    defined overlap thresholds
    :return: Json representation of the results
    """
    try:
        extent_shape = make_valid(shape(boundary))
        geo_extent_shape = unary_union(extent_shape)

        cancelled_sql = ""
        if charge_filter:
            cancelled_sql = "AND llc.cancelled is not True"

        # Execute the call to count the Number of Charges
        if threshold_search:
            count = count_results_for_boundary_thresholds(geo_extent_shape, cancelled_sql)
        else:
            count = count_results_for_boundary(geo_extent_shape, cancelled_sql)

        if int(count) > max_results:
            current_app.logger.info("Search-area: {0}, "
                                    "Number-of-charges: {1}, "
                                    "Normal-limit: {2}, "
                                    "Too many charges returned"
                                    .format(boundary, count, max_results))
            raise ApplicationError("Too many charges, search a smaller area", 507, 507)

        if threshold_search:
            non_boundary_rows = get_data_for_non_boundary_thresholds(geo_extent_shape, cancelled_sql,
                                                                     percentage_threshold, area_threshold)
            boundary_rows = get_data_for_boundary_thresholds(geo_extent_shape, cancelled_sql, percentage_threshold,
                                                             area_threshold)
            rows = non_boundary_rows + boundary_rows
        else:
            rows = get_data_for_boundary(geo_extent_shape, cancelled_sql)

        llc_result = []
        for row in rows:
            # check if the charge is already in the list, which will happen if there are multiple geometries for
            # a charge. If so, only include one entry and make sure it is not adjoinining if multiple options
            skip_input = False
            for i, obj in enumerate(llc_result):
                if obj["id"] == row[0]:
                    # if id already exists in list, check if existing is adjoining and new is not, in either
                    # case can stop looping as we should only see the ID in llc_result once
                    if obj["adjoining"] is True and row[8] is False:
                        # in this case remove existing to be replaced with new, otherwise skip input for this loop
                        del llc_result[i]
                    else:
                        skip_input = True
                    continue

            if not skip_input:
                llc_item = row[3]  # llc_item JSON object
                if row[4]:
                    llc_item['statutory-provision'] = row[4]  # Latest Stat Prov
                if row[5]:
                    llc_item['charge-type'] = row[5]  # Latest Charge Type
                if row[6]:
                    llc_item['charge-sub-category'] = row[6]  # Latest Sub Charge Category

                # get latest organisation name
                if llc_item.get('originating-authority'):
                    llc_item['originating-authority'] = \
                        get_latest_organisation_name(llc_item['originating-authority'])
                if llc_item.get('migrating-authority'):
                    llc_item['migrating-authority'] = \
                        get_latest_organisation_name(llc_item['migrating-authority'])

                llc_dict = {
                    "id": row[0],
                    "display-id": encode_charge_id(row[0]),
                    "geometry": llc_item['geometry'],
                    "type": llc_item['charge-type'],
                    "charge-sub-category": llc_item.get('charge-sub-category'),
                    "item": llc_schema.convert(llc_item, schema_version),
                    "cancelled": row[1],
                    "adjoining": row[8]
                }

                llc_result.append(llc_dict)

        if not threshold_search:
            # Do not filter out sensitive charges for threshold searches, as these types of searches currently will
            # only be used for DIP API. If in future this is changed to be used for regular searches as well, then
            # this block of code will need new logic.
            if llc_result and (not g.principle.has_all_permissions(['View Sensitive Charges']) or
                               filter_sensitive_geometry):
                llc_result = filter_sensitive_charges(llc_result, filter_sensitive_geometry)

        if llc_result and len(llc_result) > 0:
            current_app.logger.info("Returning local land charges")
            return json.dumps(llc_result), 200, {'Content-Type': 'application/json'}
        else:
            raise ApplicationError("No land charges found", 404, 404)
    except (ValueError, TypeError) as err:
        raise ApplicationError("Unprocessable Entity. {}".format(err), 422, 422)


def get_results_for_further_information_reference(further_information_reference):
    """Returns the results of land charges which match a given further information reference

    :param further_information_reference: Authority reference to search by
    :return: Json representation of the results
    """
    features = LocalLandCharge.query \
        .filter(
            func.lower(LocalLandCharge.further_information_reference) == func.lower(further_information_reference)
        ).order_by(LocalLandCharge.llc_item[SORT_BY_FIELD].desc()) \
        .all()

    if features and len(features) > 0:
        current_app.logger.info("Returning local land charges")
        result_dict = model_mappers.map_llc_result_to_dictionary_list(features)
        if not g.principle.has_all_permissions(['View Sensitive Charges']):
            result_dict = filter_sensitive_charges(result_dict)
        if not result_dict:
            raise ApplicationError("No land charges found", 404, 404)
        return json.dumps(result_dict), 200, {'Content-Type': 'application/json'}
    else:
        raise ApplicationError("No land charges found", 404, 404)


def get_results_for_originating_authority_charge(authority_charge_id, migrating_authority):
    """Returns the results of land charges which match a given originating authority charge identifier

    :param originating_authority_charge_identifier: originating authority charge identifier to search by
    :return: Json representation of the results
    """

    features = LocalLandCharge.query \
        .filter(
            LocalLandCharge.llc_item["originating-authority-charge-identifier"].astext == authority_charge_id,
            LocalLandCharge.llc_item["migrating-authority"].astext == migrating_authority
        ).order_by(LocalLandCharge.llc_item[SORT_BY_FIELD].desc()) \
        .all()

    if features and len(features) > 0:
        current_app.logger.info("Returning local land charges by originating authority & migrating authority")
        result_dict = model_mappers.map_llc_result_to_dictionary_list(features)
        if not g.principle.has_all_permissions(['View Sensitive Charges']):
            result_dict = filter_sensitive_charges(result_dict)
        if not result_dict:
            raise ApplicationError("No land charges found", 404, 404)
        return json.dumps(result_dict), 200, {'Content-Type': 'application/json'}
    else:
        raise ApplicationError("No land charges found", 404, 404)
