"""add protected sites sub-category

Revision ID: 3e8d3521b816
Revises: f14dd341e520
Create Date: 2019-11-27 09:56:37.826969

"""

# revision identifiers, used by Alembic.
revision = '3e8d3521b816'
down_revision = 'f14dd341e520'

import json

from alembic import op
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()

    ssi_name = "Site of special scientific interest (SSSI)"
    pas_name = "Protected areas / sites"

    other_id = get_category_id("Other", conn)
    ssi_id = get_category_id(ssi_name, conn)

    # update name and display_name
    valid_display_names = {"valid_display_names": [ssi_name, pas_name]}
    query = ("UPDATE charge_categories "
             "SET name = '{}', "
             "display_name = '{}', "
             "display_name_valid = '{}' "
             "WHERE id = '{}' "
             "AND parent_id = {};".format(pas_name, pas_name, json.dumps(valid_display_names), ssi_id, other_id))
    op.execute(query)

    # Clear all current stat provs and add new ones
    op.execute("DELETE FROM charge_categories_stat_provisions WHERE category_id = {}".format(ssi_id))

    stat_prov1_id = get_stat_prov_id('Conservation (Natural Habitats, &c) Regulations 1994 regulation 22 paragraph 4',
                                     conn)
    stat_prov2_id = get_stat_prov_id('Countryside and Rights of Way Act 2000 schedule 9 paragraph 28(9)', conn)
    stat_prov3_id = get_stat_prov_id('Countryside and Rights of Way Act 2000 section 16', conn)
    stat_prov4_id = get_stat_prov_id('Wildlife and Countryside Act 1981 section 28(9)', conn)
    stat_prov5_id = get_stat_prov_id('Wildlife and Countryside Act 1981 section 28C(6)', conn)

    link_category_stat_prov(ssi_id, stat_prov1_id)
    link_category_stat_prov(ssi_id, stat_prov2_id)
    link_category_stat_prov(ssi_id, stat_prov3_id)
    link_category_stat_prov(ssi_id, stat_prov4_id)
    link_category_stat_prov(ssi_id, stat_prov5_id)

    # Unlink instrument
    op.execute("DELETE FROM charge_categories_instruments WHERE category_id = {}".format(ssi_id))


def downgrade():
    conn = op.get_bind()

    ssi_name = "Site of special scientific interest (SSSI)"
    pas_name = "Protected areas / sites"

    other_id = get_category_id("Other", conn)
    pas_id = get_category_id(pas_name, conn)

    # update name and display_name
    valid_display_names = {"valid_display_names": [ssi_name]}
    query = ("UPDATE charge_categories "
             "SET name = '{}', "
             "display_name = '{}', "
             "display_name_valid = '{}' "
             "WHERE id = '{}' "
             "AND parent_id = {};".format(ssi_name, ssi_name, json.dumps(valid_display_names), pas_id, other_id))
    op.execute(query)

    # Clear all current stat provs and add new one
    op.execute("DELETE FROM charge_categories_stat_provisions WHERE category_id = {}".format(pas_id))

    stat_prov1_id = get_stat_prov_id('Wildlife and Countryside Act 1981 section 28(9)', conn)

    link_category_stat_prov(pas_id, stat_prov1_id)

    # Link instrument
    notice_id = get_instrument_id("Notice", conn)
    link_category_instrument(pas_id, notice_id)


def get_category_id(category, conn):
    query = "SELECT id FROM charge_categories WHERE name = '{}';".format(category)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category {}".format(category))
    return results[0][0]


def get_stat_prov_id(stat_prov, conn):
    query = "SELECT id FROM statutory_provision WHERE title = '{}';".format(stat_prov)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve statutory provision {}".format(stat_prov))
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
