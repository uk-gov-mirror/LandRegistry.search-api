"""Tree preservation order (TPO) and statutory provision mapping updated

Revision ID: 7cba93b9ff46
Revises: 3de2b88f738b
Create Date: 2018-05-10 09:02:45.447660

"""

# revision identifiers, used by Alembic.
revision = '7cba93b9ff46'
down_revision = '8c0821242aa1'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()
    tpo_id = get_charge_category_id('Tree preservation order (TPO)', conn)
    insert_into_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 198', conn)
    insert_into_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 201', conn)
    insert_into_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 202', conn)


def downgrade():
    conn = op.get_bind()
    tpo_id = get_charge_category_id('Tree preservation order (TPO)', conn)
    delete_from_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 198', conn)
    delete_from_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 201', conn)
    delete_from_charge_categories_stat_provisions(tpo_id, 'Town and Country Planning Act 1990 section 202', conn)


def insert_into_charge_categories_stat_provisions(category_id, statutory_provision, conn):
    res = conn.execute(text("SELECT id from statutory_provision WHERE title = '{0}';".format(statutory_provision)))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Statutory provision " + statutory_provision + " doesn't exist to insert")
    stat_prov_id = results[0][0]

    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_stat_provisions WHERE category_id = {0} " \
            "AND statutory_provision_id = {1}) THEN " \
            "INSERT INTO charge_categories_stat_provisions (category_id, statutory_provision_id) " \
            "VALUES ({0}, {1}); " \
            "END IF; END $$;".format(category_id, stat_prov_id)
    conn.execute(text(query))


def delete_from_charge_categories_stat_provisions(category_id, statutory_provision, conn):
    query = "SELECT id FROM statutory_provision WHERE title = '{0}';".format(statutory_provision)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Statutory provision" + statutory_provision + " doesn't exist to delete")
    stat_prov_id = results[0][0]

    query = "DELETE FROM charge_categories_stat_provisions WHERE category_id = {0} AND " \
            "statutory_provision_id = {1};".format(category_id, stat_prov_id)
    conn.execute(text(query))


def get_charge_category_id(category_name, conn):
    query = "SELECT id FROM charge_categories WHERE name = '{0}';".format(category_name)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception(category_name + " does not exist in the DB to be linked")
    return results[0][0]
