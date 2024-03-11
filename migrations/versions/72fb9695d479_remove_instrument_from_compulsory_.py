"""remove_instrument_from_compulsory_purchases

Revision ID: 72fb9695d479
Revises: f5bece98f1a1
Create Date: 2018-11-07 13:49:30.192375

"""

# revision identifiers, used by Alembic.
revision = '72fb9695d479'
down_revision = 'f5bece98f1a1'

from alembic import op
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()
    other_id = get_charge_category_id('Other', None, conn)
    category_id = get_charge_category_id('Compulsory purchase order', other_id, conn)
    query = "DELETE FROM charge_categories_instruments " \
            "WHERE category_id = {0};".format(category_id)
    op.execute(query)


def downgrade():
    conn = op.get_bind()
    other_id = get_charge_category_id('Other', None, conn)
    category_id = get_charge_category_id('Compulsory purchase order', other_id, conn)
    res = conn.execute(text("select id from instruments where name ='Order'"))
    results = res.fetchall()
    instrument_id = results[0][0]
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_instruments WHERE category_id = {0} AND " \
            "instruments_id = {1}) THEN " \
            "INSERT INTO charge_categories_instruments (category_id, instruments_id) " \
            "VALUES ({0}, {1}); " \
            "END IF; END $$;".format(category_id, instrument_id)
    op.execute(query)


def get_charge_category_id(category_name, parent_id, conn):
    if parent_id:
        query = "SELECT id FROM charge_categories WHERE name = '{0}' and parent_id = {1};".format(category_name, parent_id)
    else:
        query = "SELECT id FROM charge_categories WHERE name = '{0}' and parent_id is null;".format(category_name)
    res = conn.execute(text(query))
    results = res.fetchall()
    return results[0][0]
