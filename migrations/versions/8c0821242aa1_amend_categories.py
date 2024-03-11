"""Amend categories

Revision ID: 8c0821242aa1
Revises: 3de2b88f738b
Create Date: 2018-05-09 14:20:35.126375

"""

# revision identifiers, used by Alembic.
revision = '8c0821242aa1'
down_revision = '3de2b88f738b'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# Categories to be added in upgrade
MODIFICATION_RECTIFICATION_ORDERS = 'Modification / rectification orders'
RIGHT_TO_BUY = 'Right to buy / right to acquire'
UNCOMMON_CHARGES = 'Uncommon charges'
WATER_DRAINAGE = 'Water / drainage'

# Categories to be removed in upgrade
CHANGE_A_DEVELOPMENT = 'Change a development'
BREACH_OF_CONDITIONS = 'Breach of conditions'
NO_PERMITTED_DEVELOPMENT = 'No permitted development'
REPAIRS_NOTICE = 'Repairs notice'
RE_APPROVAL_OF_GRANT = 'Re-approval of grant'
RE_APPROVAL_UNDER_HMO = 'Re-approval under HMO'


def upgrade():
    conn = op.get_bind()
    planning_id = get_charge_category_id_by_name('Planning', True, conn)
    housing_id = get_charge_category_id_by_name('Housing', True, conn)
    other_id = get_charge_category_id_by_name('Other', True, conn)

    # TODO: Fix display_order so that new categories are at bottom of list
    delete_category(CHANGE_A_DEVELOPMENT, conn)
    delete_category(BREACH_OF_CONDITIONS, conn)
    delete_category(NO_PERMITTED_DEVELOPMENT, conn)
    delete_category(REPAIRS_NOTICE, conn)
    delete_category(RE_APPROVAL_OF_GRANT, conn)
    delete_category(RE_APPROVAL_UNDER_HMO, conn)

    insert_category(MODIFICATION_RECTIFICATION_ORDERS, MODIFICATION_RECTIFICATION_ORDERS, planning_id, 10, None)
    insert_category(RIGHT_TO_BUY, RIGHT_TO_BUY, housing_id, 5, None)
    insert_category(WATER_DRAINAGE, WATER_DRAINAGE, other_id, 9, None)
    insert_category(UNCOMMON_CHARGES, UNCOMMON_CHARGES, other_id, 10, 'Add Uncommon Charges Category')

    update_category_name("Article 4", "Article 4 / no permitted development")
    update_category_name("Highways", "Highways and paths")


def downgrade():
    conn = op.get_bind()
    planning_id = get_charge_category_id_by_name('Planning', True, conn)
    listed_building_id = get_charge_category_id_by_name('Listed building', True, conn)
    housing_id = get_charge_category_id_by_name('Housing', True, conn)

    delete_category(MODIFICATION_RECTIFICATION_ORDERS, conn)
    delete_category(RIGHT_TO_BUY, conn)
    delete_category(UNCOMMON_CHARGES, conn)
    delete_category(WATER_DRAINAGE, conn)

    insert_category(NO_PERMITTED_DEVELOPMENT, NO_PERMITTED_DEVELOPMENT, planning_id, 5, None)
    insert_category(BREACH_OF_CONDITIONS, BREACH_OF_CONDITIONS, planning_id, 1, None)
    insert_category(CHANGE_A_DEVELOPMENT, CHANGE_A_DEVELOPMENT, planning_id, 1, None)
    insert_category(REPAIRS_NOTICE, REPAIRS_NOTICE, listed_building_id, 3, None)
    insert_category(RE_APPROVAL_UNDER_HMO, RE_APPROVAL_UNDER_HMO, housing_id, 6, None)
    insert_category(RE_APPROVAL_OF_GRANT, RE_APPROVAL_OF_GRANT, housing_id, 5, None)

    change_a_development_id = get_charge_category_id_by_name(CHANGE_A_DEVELOPMENT, False, conn)
    link_category_and_stat_prov(change_a_development_id, 'Town and Country Planning Act 1990 section 97', conn)
    link_category_and_instrument(change_a_development_id, 'Order', conn)

    update_category_name("Article 4 / no permitted development", "Article 4")
    update_category_name("Highways and paths", "Highways")


def get_charge_category_id_by_name(category_name, is_parent, conn):
    if is_parent:
        query = "SELECT id FROM charge_categories WHERE name = '{}' AND parent_id IS NULL".format(category_name)
    else:
        query = "SELECT id FROM charge_categories WHERE name = '{}'".format(category_name)

    res = conn.execute(text(query))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category with name '{}'".format(category_name))

    return results[0][0]


def link_category_and_stat_prov(category_id, stat_prov, conn):
    res = conn.execute(text("SELECT id FROM statutory_provision WHERE title = '{}'".format(stat_prov)))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve statutory provision with title '{}'".format(stat_prov))

    stat_prov_id = results[0][0]

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories_stat_provisions " \
            "WHERE category_id = {0} AND statutory_provision_id = {1}) THEN " \
            "INSERT INTO charge_categories_stat_provisions (category_id, statutory_provision_id) " \
            "VALUES ({0}, {1}); END IF; END $$;".format(category_id, stat_prov_id)

    op.execute(query)


def link_category_and_instrument(category_id, instrument, conn):
    res = conn.execute(text("SELECT id FROM instruments WHERE name = '{}'".format(instrument)))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve instrument with name '{}'".format(instrument))

    instrument_id = results[0][0]

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories_instruments " \
            "WHERE category_id = {0} AND instruments_id = {1}) THEN " \
            "INSERT INTO charge_categories_instruments (category_id, instruments_id) " \
            "VALUES ({0}, {1}); END IF; END $$;".format(category_id, instrument_id)

    op.execute(query)


def update_category_name(current_name, new_name):
    op.execute("UPDATE charge_categories "
               "SET name = '{0}', display_name = '{0}' "
               "WHERE name = '{1}'".format(new_name, current_name))


def insert_category(name, display_name, parent_id, display_order, permission):
    op.execute("UPDATE charge_categories "
               "SET display_order = display_order + 1 "
               "WHERE display_order >= {} AND parent_id = {}".format(display_order, parent_id))

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories " \
            "WHERE name = '{}' AND parent_id = {}) THEN ".format(name, parent_id)

    if permission:
        query += "INSERT INTO charge_categories (name, display_name, parent_id, display_order, permission) " \
                 "VALUES ('{}', '{}', {}, {}, '{}')".format(name, display_name, parent_id, display_order, permission)

    else:
        query += "INSERT INTO charge_categories (name, display_name, parent_id, display_order) " \
                 "VALUES ('{}', '{}', {}, {})".format(name, display_name, parent_id, display_order)

    query += "; END IF; END $$"

    op.execute(query)


def delete_category(category, conn):
    res = conn.execute(text("SELECT id, display_order, parent_id "
                       "FROM charge_categories "
                       "WHERE name = '{}'".format(category)))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to delete charge category with name '{}', category not found".format(category))

    category_id = results[0][0]
    display_order = results[0][1]
    parent_id = results[0][2]

    op.execute("UPDATE charge_categories "
               "SET display_order = display_order - 1 "
               "WHERE display_order >= {} AND parent_id = {}".format(display_order, parent_id))

    op.execute("DELETE FROM charge_categories_stat_provisions WHERE category_id = {}".format(category_id))
    op.execute("DELETE FROM charge_categories_instruments WHERE category_id = {}".format(category_id))
    op.execute("DELETE FROM charge_categories WHERE id = {}".format(category_id))
