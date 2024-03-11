from flask import current_app
from search_api.models import ChargeCategory
from sqlalchemy.sql.expression import true


def filter_sensitive_charges(charges, filter_geo_only=False):
    # Filter out charges (or optionally just geometry) which have sensitive (sub)category
    sensitive_cats = ChargeCategory.query.filter(ChargeCategory.sensitive == true()).all()
    if not sensitive_cats or not charges:
        return charges
    for_removal = []
    for cat in sensitive_cats:
        for charge in charges:
            charge_type = charge['item'].get('charge-type')
            charge_sub_category = charge['item'].get('charge-sub-category')

            if (not cat.charge_category and charge_type and
                    charge_type in cat.display_name_valid['valid_display_names']) or \
                (cat.charge_category and charge_sub_category and
                    charge_sub_category in cat.display_name_valid['valid_display_names']):
                current_app.logger.info("Filtering sensitive charge")
                if filter_geo_only:
                    charge['item']['geometry'] = {"properties": "sensitive"}
                    charge['geometry'] = {"properties": "sensitive"}
                else:
                    for_removal.append(charge)
    return [charge for charge in charges if charge not in for_removal]
