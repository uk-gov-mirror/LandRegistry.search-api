"""Update mapping

Revision ID: f35534934918
Revises: 7cba93b9ff46
Create Date: 2018-06-20 13:24:58.734372

"""

# revision identifiers, used by Alembic.
revision = 'f35534934918'
down_revision = '441441c32014'

from alembic import op
from sqlalchemy.sql import text

NEW_STAT_PROV = {
    'Environmental Permitting (England and Wales) Regulations 2010, regulation 15': 't',
    'Flood and Water Management Act 2010, schedule 1 (Effect of Designation), paragraph 5(1)': 't'
}

WATER_STAT_PROV = [
    'Environmental Permitting (England and Wales) Regulations 2010, regulation 15',
    'Flood and Water Management Act 2010, schedule 1 (Effect of Designation), paragraph 5(1)',
    'Land Drainage Act 1991 section 18(8)',
    'Water Industry Act 1991 section 82'
]

TREE_STAT_PROV = [
    'Town and Country Planning Act 1990 section 201'
]

BUY_STAT_PROV = [
    'Housing Act 1985 section 156A'
]

INSTRUMENTS = [
    'Notice',
    'Deed',
    'Order'
]


def upgrade():
    conn = op.get_bind()
    other_id = get_charge_category_id('Other', None, conn)
    planning_id = get_charge_category_id('Planning', None, conn)
    housing_id = get_charge_category_id('Housing', None, conn)

    clear_instrument_mapping('Ancient monuments', other_id, conn)
    rename_category('Licences', 'Licence', other_id)
    add_instrument('Licence')
    load_stat_prov(NEW_STAT_PROV)
    load_stat_prov_mapping('Water / drainage', other_id, WATER_STAT_PROV, conn)
    clear_stat_prov_mapping('Tree preservation order (TPO)', planning_id, TREE_STAT_PROV, conn)
    load_stat_prov_mapping('Right to buy / right to acquire', housing_id,  BUY_STAT_PROV, conn)


def downgrade():
    conn = op.get_bind()
    other_id = get_charge_category_id('Other', None, conn)
    planning_id = get_charge_category_id('Planning', None, conn)
    housing_id = get_charge_category_id('Housing', None, conn)

    load_instrument_mapping(INSTRUMENTS, 'Ancient monuments', other_id, conn)
    rename_category('Licence', 'Licences', other_id)
    delete_instrument('Licence')
    clear_stat_prov_mapping('Water / drainage', other_id, WATER_STAT_PROV, conn)
    clear_stat_prov(NEW_STAT_PROV)
    load_stat_prov_mapping('Tree preservation order (TPO)', planning_id, TREE_STAT_PROV, conn)
    clear_stat_prov_mapping('Right to buy / right to acquire', housing_id,  BUY_STAT_PROV, conn)


def get_charge_category_id(category_name, parent_id, conn):
    if parent_id:
        query = "SELECT id FROM charge_categories WHERE name = '{0}' and parent_id = {1};".format(category_name, parent_id)
    else:
        query = "SELECT id FROM charge_categories WHERE name = '{0}' and parent_id is null;".format(category_name)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception(category_name + " does not exist in the DB")
    return results[0][0]


def get_stat_prov_id(title, conn):
    query = "SELECT id from statutory_provision WHERE title = '{0}' ".format(title)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception(title + 'does not exist in the DB')
    return results[0][0]


def load_instrument_mapping(inst, category, parent_id, conn):
    category_id = get_charge_category_id(category, parent_id, conn)
    for instrument in inst:
        res = conn.execute(text("select id from instruments where name ='{0}'".format(instrument)))
        results = res.fetchall()
        if results is None or len(results) == 0:
            raise Exception("Instrument '{}' does not exits in the DB to be linked".format(instrument))
        instrument_id = results[0][0]
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_instruments WHERE category_id = {0} AND " \
                "instruments_id = {1}) THEN " \
                "INSERT INTO charge_categories_instruments (category_id, instruments_id) " \
                "VALUES ({0}, {1}); " \
                "END IF; END $$;".format(category_id, instrument_id)
        op.execute(query)


def clear_instrument_mapping(category, parent_id, conn):
    category_id = get_charge_category_id(category, parent_id, conn)
    query = "DELETE FROM charge_categories_instruments " \
            "WHERE category_id = {0};".format(category_id)
    op.execute(query)


def rename_category(old_name, new_name, parent_id):
    query = "UPDATE charge_categories SET name = '{0}', display_name = '{0}' " \
            "WHERE name = '{1}' AND parent_id = {2};".format(new_name, old_name, parent_id)
    op.execute(query)


def add_instrument(instrument_name):
    query = "INSERT INTO instruments (name) VALUES ('{0}');".format(instrument_name)
    op.execute(query)


def delete_instrument(instrument_name):
    query = "DELETE FROM instruments WHERE name = '{0}';".format(instrument_name)
    op.execute(query)


def load_stat_prov(statutory_provisions):
    for title, exclude in statutory_provisions.items():
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM statutory_provision WHERE title = '{0}') " \
                "THEN INSERT INTO statutory_provision " \
                "(title, selectable) VALUES ('{0}', '{1}'); END IF; END $$;".format(title.replace("\'", "\'\'"),
                                                                                    exclude)
        op.execute(query)


def clear_stat_prov(statutory_provisions):
    for title, exclude in statutory_provisions.items():
        query = "DELETE FROM statutory_provision WHERE title = '{0}'".format(title)
        op.execute(query)


def load_stat_prov_mapping(cat_name, parent_id, stat_prov_list, conn):
    cat_id = get_charge_category_id(cat_name, parent_id, conn)
    for stat_prov in stat_prov_list:
        stat_prov_id = get_stat_prov_id(stat_prov, conn)
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_stat_provisions WHERE category_id = {0}" \
                "AND statutory_provision_id = {1})" \
                "THEN INSERT INTO charge_categories_stat_provisions (category_id, statutory_provision_id)" \
                "VALUES ({0}, {1});" \
                "END IF; END $$;".format(cat_id, stat_prov_id)
        op.execute(query)


def clear_stat_prov_mapping(cat_name, parent_id, stat_prov_list, conn):
    cat_id = get_charge_category_id(cat_name, parent_id, conn)
    for stat_prov in stat_prov_list:
        stat_prov_id = get_stat_prov_id(stat_prov, conn)
        query = "DELETE FROM charge_categories_stat_provisions WHERE category_id = '{0}'" \
                "AND statutory_provision_id = '{1}'".format(cat_id, stat_prov_id)
        op.execute(query)


