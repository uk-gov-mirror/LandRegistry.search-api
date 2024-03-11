"""modify charge categories

Revision ID: 441441c32014
Revises: 7cba93b9ff46
Create Date: 2018-06-07 10:16:12.182839

"""

# revision identifiers, used by Alembic.
revision = '441441c32014'
down_revision = '7cba93b9ff46'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# Categories to be removed in upgrade
LISTED_BUILDING_CPC = 'Listed building conditional planning consent'

# Categories to be reordered in upgrade
LISTED_BUILDING = 'Listed building'
ENFORCEMENT_NOTICE = 'Enforcement notice'

SMOKE_CO = 'Smoke control order'
SITE_OF_SSI = 'Site of special scientific interest (SSSI)'
LICENSES = 'Licences'
LOCAL_ACTS = 'Local acts'
WATER_DRAINAGE = 'Water / drainage'
UNCOMMON_CHARGES = 'Uncommon charges'

CONSERVATION_AREA = 'Conservation area'
CONDITIONAL_PC = 'Conditional planning consent'
ARTICLE_FOUR_OLD = 'Article 4 / no permitted development'
ARTICLE_FOUR_NEW = 'No permitted development / article 4'
PLANNING_NOTICES_OLD = 'Planning notices'
PLANNING_NOTICES_NEW = 'Planning notice'
PLANNING_AGREEMENT = 'Planning agreement'
TREE_PO = 'Tree preservation order (TPO)'
MODIFICATION = 'Modification / rectification orders'




def upgrade():
    conn = op.get_bind()
    planning_id = get_charge_category_id_by_name('Planning', True, conn)
    listed_building_id = get_charge_category_id_by_name('Listed building', True, conn)
    other_id = get_charge_category_id_by_name('Other', True, conn)

    delete_category(LISTED_BUILDING_CPC, conn)

    update_category_name(ARTICLE_FOUR_OLD, ARTICLE_FOUR_NEW)
    update_category_name(PLANNING_NOTICES_OLD, PLANNING_NOTICES_NEW)

    update_category_display_order(ENFORCEMENT_NOTICE, listed_building_id, 1, conn)
    update_category_display_order(LISTED_BUILDING, listed_building_id, 2, conn)

    update_category_display_order(LICENSES, other_id, 5, conn)
    update_category_display_order(LOCAL_ACTS, other_id, 6, conn)
    update_category_display_order(SITE_OF_SSI, other_id, 7, conn)
    update_category_display_order(SMOKE_CO, other_id, 8, conn)
    update_category_display_order(UNCOMMON_CHARGES, other_id, 9, conn)
    update_category_display_order(WATER_DRAINAGE, other_id, 10, conn)

    update_category_display_order(CONDITIONAL_PC, planning_id, 1, conn)
    update_category_display_order(CONSERVATION_AREA, planning_id, 2, conn)
    update_category_display_order(MODIFICATION, planning_id, 4, conn)
    update_category_display_order(ARTICLE_FOUR_NEW, planning_id, 5, conn)
    update_category_display_order(PLANNING_NOTICES_NEW, planning_id, 7, conn)
    update_category_display_order(TREE_PO, planning_id, 9, conn)


def downgrade():
    conn = op.get_bind()
    planning_id = get_charge_category_id_by_name('Planning', True, conn)
    listed_building_id = get_charge_category_id_by_name('Listed building', True, conn)
    other_id = get_charge_category_id_by_name('Other', True, conn)

    insert_category(LISTED_BUILDING_CPC, LISTED_BUILDING_CPC, planning_id, 8)

    update_category_name(ARTICLE_FOUR_NEW, ARTICLE_FOUR_OLD)
    update_category_name(PLANNING_NOTICES_NEW, PLANNING_NOTICES_OLD)

    update_category_display_order(LISTED_BUILDING, listed_building_id, 1, conn)
    update_category_display_order(ENFORCEMENT_NOTICE, listed_building_id, 2, conn)

    update_category_display_order(SMOKE_CO, other_id, 5, conn)
    update_category_display_order(SITE_OF_SSI, other_id, 6, conn)
    update_category_display_order(LICENSES, other_id, 7, conn)
    update_category_display_order(LOCAL_ACTS, other_id, 8, conn)
    update_category_display_order(WATER_DRAINAGE, other_id, 9, conn)
    update_category_display_order(UNCOMMON_CHARGES, other_id, 10, conn)

    update_category_display_order(CONSERVATION_AREA, planning_id, 1, conn)
    update_category_display_order(CONDITIONAL_PC, planning_id, 2, conn)
    update_category_display_order(ARTICLE_FOUR_OLD, planning_id, 4, conn)
    update_category_display_order(PLANNING_NOTICES_OLD, planning_id, 5, conn)
    update_category_display_order(TREE_PO, planning_id, 7, conn)
    update_category_display_order(MODIFICATION, planning_id, 10, conn)


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


def update_category_name(current_name, new_name):
    op.execute("UPDATE charge_categories "
               "SET name = '{0}', display_name = '{0}' "
               "WHERE name = '{1}'".format(new_name, current_name))


def insert_category(name, display_name, parent_id, display_order):
    op.execute("UPDATE charge_categories "
               "SET display_order = display_order + 1 "
               "WHERE display_order >= {} AND parent_id = {}".format(display_order, parent_id))

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories " \
            "WHERE name = '{}' AND parent_id = {}) THEN ".format(name, parent_id)

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


def update_category_display_order(category, parent_id, new_display_order, conn):
    res = conn.execute(text("SELECT id, display_order "
                       "FROM charge_categories "
                       "WHERE name = '{}' AND parent_id = {}".format(category, parent_id)))

    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to update charge category with name '{}', category not found".format(category))

    category_id = results[0][0]
    old_display_order = results[0][1]

    # Swap display order, put whatever sub-category is currently in the new display order, into the old display order
    op.execute("UPDATE charge_categories "
               "SET display_order = {} "
               "WHERE display_order = {} AND parent_id = {}".format(old_display_order, new_display_order, parent_id))

    # Set old display order to new display order
    op.execute("UPDATE charge_categories "
               "SET display_order = {} "
               "WHERE id = {}".format(new_display_order, category_id))
