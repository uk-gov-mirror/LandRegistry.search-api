"""combine HMO sub-categories

Revision ID: 225329075a5f
Revises: 5b863a675289
Create Date: 2021-02-05 10:25:50.615269

"""

# revision identifiers, used by Alembic.
revision = '225329075a5f'
down_revision = '5b863a675289'

import json

from alembic import op
from sqlalchemy.sql import text

PARENT_CATEGORY = 'Housing / buildings'
INTERIM_CERT = 'Interim certificate under HMO'
HMO_MAIN = 'Occupancy including house in multiple occupation (HMO)'


def upgrade():
    conn = op.get_bind()
    # get IDs of interim and approval categories
    housing_id = get_charge_category_id_by_name(PARENT_CATEGORY, None, conn)
    interim_id = get_charge_category_id_by_name(INTERIM_CERT, housing_id, conn)
    approval_id = get_charge_category_id_by_name(HMO_MAIN, housing_id, conn)

    # Put all valid names for interim into approval
    interim_valid_names = get_valid_names_by_id(interim_id, conn)
    approval_valid_names = get_valid_names_by_id(approval_id, conn)
    all_valid_names = interim_valid_names.get('valid_display_names') + approval_valid_names.get('valid_display_names')
    new_approval_valid_names = {"valid_display_names": all_valid_names}
    # convert the list to a string
    display_name_valid = json.dumps(new_approval_valid_names)
    set_display_name_valid(display_name_valid, approval_id)

    # Remove interim category
    delete_category(interim_id, conn)


def downgrade():
    conn = op.get_bind()
    # get IDs of parent and approval categories
    housing_id = get_charge_category_id_by_name(PARENT_CATEGORY, None, conn)
    approval_id = get_charge_category_id_by_name(HMO_MAIN, housing_id, conn)

    # add interim category
    insert_category(INTERIM_CERT, INTERIM_CERT, housing_id, 2)

    # remove interim from valid list of approval names
    approval_valid_names = get_valid_names_by_id(approval_id, conn)
    if INTERIM_CERT in approval_valid_names.get('valid_display_names'):
        approval_valid_names['valid_display_names'].remove(INTERIM_CERT)
        display_name_valid = json.dumps(approval_valid_names)
        set_display_name_valid(display_name_valid, approval_id)


def get_charge_category_id_by_name(category_name, parent_id, conn):
    if parent_id:
        query = "SELECT id FROM charge_categories WHERE (display_name_valid->'valid_display_names')\
                                ::jsonb ? '{}' AND parent_id = {}".format(category_name, parent_id)
    else:
        query = "SELECT id FROM charge_categories WHERE (display_name_valid->'valid_display_names')\
                        ::jsonb ? '{}' AND parent_id is null;".format(category_name)

    res = conn.execute(text(query))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category with name '{}'".format(category_name))

    return results[0][0]


def get_valid_names_by_id(category_id, conn):
    query = "SELECT display_name_valid FROM charge_categories WHERE id = '{}'".format(category_id)

    res = conn.execute(text(query))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve valid names for charge category with id '{}'".format(category_id))

    return results[0][0]


def set_display_name_valid(display_name_valid, row_id):
    query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE id = {1}"
             .format(display_name_valid, row_id))
    op.execute(query)


def insert_category(name, display_name, parent_id, display_order):
    display_name_valid = json.dumps({"valid_display_names": [display_name]})
    op.execute("UPDATE charge_categories "
               "SET display_order = display_order + 1 "
               "WHERE display_order >= {} AND parent_id = {}".format(display_order, parent_id))

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories " \
            "WHERE name = '{}' AND parent_id = {}) THEN ".format(name, parent_id) \

    query += "INSERT INTO charge_categories (name, display_name, parent_id, display_order, display_name_valid) " \
             "VALUES ('{}', '{}', {}, {}, '{}')".format(name, display_name, parent_id, display_order,
                                                        display_name_valid)

    query += "; END IF; END $$"

    op.execute(query)


def delete_category(category_id, conn):
    res = conn.execute(text("SELECT display_order, parent_id "
                       "FROM charge_categories "
                       "WHERE id = '{}'".format(category_id)))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to delete charge category with id '{}', category not found".format(category_id))

    display_order = results[0][0]
    parent_id = results[0][1]

    op.execute("UPDATE charge_categories "
               "SET display_order = display_order - 1 "
               "WHERE display_order >= {} AND parent_id = {}".format(display_order, parent_id))

    op.execute("DELETE FROM charge_categories_stat_provisions WHERE category_id = {}".format(category_id))
    op.execute("DELETE FROM charge_categories_instruments WHERE category_id = {}".format(category_id))
    op.execute("DELETE FROM charge_categories WHERE id = {}".format(category_id))