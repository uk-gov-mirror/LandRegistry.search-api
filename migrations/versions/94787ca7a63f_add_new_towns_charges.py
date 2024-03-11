"""Add New Towns charges

Revision ID: 94787ca7a63f
Revises: 291d91517982
Create Date: 2019-11-07 16:59:14.775562

"""

import json

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

revision = '94787ca7a63f'
down_revision = '291d91517982'


def upgrade():
    conn = op.get_bind()

    other_id = get_category_id('Other', conn)

    valid_display_names = {"valid_display_names": ["New towns"]}
    query = "INSERT INTO charge_categories(name, display_name, parent_id, display_order, permission, display_name_valid, sensitive) " \
        + "VALUES ('New towns', 'New towns', {}, 12, null, '{}', 'f') RETURNING id;".format(other_id,
                                                                                            json.dumps(valid_display_names))
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to get ID for inserted category")
    new_towns_id = results[0][0]

    stat_prov1_id = get_stat_prov_id('New Towns Act 1981 section 1(5)', conn)
    stat_prov2_id = get_stat_prov_id('New Towns Act 1981 section 12', conn)

    link_category_stat_prov(new_towns_id, stat_prov1_id)
    link_category_stat_prov(new_towns_id, stat_prov2_id)

    order_id = get_instrument_id("Order", conn)
    link_category_instrument(new_towns_id, order_id)


def downgrade():
    conn = op.get_bind()
    new_towns_id = get_category_id('New towns', conn)
    op.execute("DELETE FROM charge_categories_stat_provisions WHERE category_id = {}".format(new_towns_id))
    op.execute("DELETE FROM charge_categories_instruments WHERE category_id = {}".format(new_towns_id))
    op.execute("DELETE FROM charge_categories WHERE name = 'New towns';")


def get_stat_prov_id(stat_prov, conn):
    query = "SELECT id FROM statutory_provision WHERE title = '{}';".format(stat_prov)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve statutory provision {}".format(stat_prov))
    return results[0][0]


def get_category_id(category, conn):
    query = "SELECT id FROM charge_categories WHERE name = '{}';".format(category)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category {}".format(category))
    return results[0][0]


def link_category_stat_prov(category_id, stat_prov_id):
    op.execute("INSERT INTO charge_categories_stat_provisions(category_id, statutory_provision_id) VALUES "
               "({}, {})".format(category_id, stat_prov_id))


def get_instrument_id(instrument, conn):
    query = "SELECT id FROM instruments WHERE name = '{}';".format(instrument)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve instrument {}".format(instrument))
    return results[0][0]


def link_category_instrument(category_id, instruments_id):
    op.execute("INSERT INTO charge_categories_instruments(category_id, instruments_id) VALUES "
               "({}, {})".format(category_id, instruments_id))
