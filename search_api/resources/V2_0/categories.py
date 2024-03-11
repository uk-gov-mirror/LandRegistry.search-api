import json

from flask import Blueprint, Response, current_app
from search_api.exceptions import ApplicationError
from search_api.models import ChargeCategory

categories = Blueprint('categories', __name__, url_prefix='/v2.0/search/categories')


@categories.route('/<path:category>', methods=['GET'])
def get_category_latest_name(category):
    current_app.logger.info("Get category for {0}.".format(category))

    category_obj = ChargeCategory.query \
        .filter(ChargeCategory.display_name_valid.contains({'valid_display_names': [category]}))\
        .filter(ChargeCategory.parent_id.is_(None)) \
        .first()

    if category_obj is None:
        raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

    result = {"display-name": category_obj.display_name}

    return Response(response=json.dumps(result), mimetype="application/json")


@categories.route('/<path:category>/sub-categories/<path:sub_category>', methods=['GET'])
def get_sub_category_latest_name(category, sub_category):
    current_app.logger.info("Get category for {0}.".format(category))

    category_obj = ChargeCategory.query \
        .filter(ChargeCategory.display_name_valid.contains({'valid_display_names': [category]}))\
        .filter(ChargeCategory.parent_id.is_(None)) \
        .first()

    if category_obj is None:
        raise ApplicationError("Category '{0}' not found.".format(category), 404, 404)

    sub_category_obj = ChargeCategory.query \
        .filter(ChargeCategory.display_name_valid.contains({'valid_display_names': [sub_category]}))\
        .filter(ChargeCategory.parent_id == category_obj.id) \
        .first()

    if sub_category_obj is None:
        raise ApplicationError("Sub-category '{0}' not found for parent '{1}'".format(sub_category, category),
                               404, 404)

    result = {"display-name": sub_category_obj.display_name}

    return Response(response=json.dumps(result), mimetype="application/json")


@categories.route('/', methods=['GET'])
def get_all_categories():
    current_app.logger.info("Get all categories")

    all_categories = ChargeCategory.query\
        .filter(ChargeCategory.parent_id.is_(None)) \
        .order_by(ChargeCategory.display_order) \
        .all()

    results = []
    for category in all_categories:
        result_json = {
            "add-permission": category.add_permission,
            "vary-permission": category.vary_permission,
            "cancel-permission": category.cancel_permission,
            "add-on-behalf-permission": category.add_on_behalf_permission,
            "display-name": category.display_name,
            "name": category.name,
            "selectable": category.selectable
        }
        results.append(result_json)

    return Response(response=json.dumps(results), mimetype="application/json")
