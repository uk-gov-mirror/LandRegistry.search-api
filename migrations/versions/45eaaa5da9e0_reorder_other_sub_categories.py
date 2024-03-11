"""Reorder Other sub-categories

Revision ID: 45eaaa5da9e0
Revises: 94787ca7a63f
Create Date: 2019-11-08 13:39:54.388646

"""

# revision identifiers, used by Alembic.
revision = '45eaaa5da9e0'
down_revision = '94787ca7a63f'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()
    other_id = get_category_id("Other", conn)
    new_towns_id = get_category_id("New towns", conn)
    pipeline_order = get_category_display_order("Pipeline", conn)
    op.execute("UPDATE charge_categories SET display_order = display_order + 1 "
               "WHERE parent_id = {} AND display_order >= {}".format(other_id, pipeline_order))
    op.execute("UPDATE charge_categories SET display_order = {} WHERE id = {}".format(pipeline_order, new_towns_id))
    

def downgrade():
    conn = op.get_bind()
    other_id = get_category_id("Other", conn)
    new_towns_id = get_category_id("New towns", conn)
    pipeline_order = get_category_display_order("Pipeline", conn)
    op.execute("UPDATE charge_categories SET display_order = display_order - 1 "
               "WHERE parent_id = {} AND display_order >= {}".format(other_id, pipeline_order))
    op.execute("UPDATE charge_categories SET display_order = 12 WHERE id = {}".format(new_towns_id))


def get_category_id(category, conn):
    query = "SELECT id FROM charge_categories WHERE name = '{}';".format(category)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category {}".format(category))
    return results[0][0]


def get_category_display_order(category, conn):
    query = "SELECT display_order FROM charge_categories WHERE name = '{}';".format(category)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Unable to retrieve charge category display order {}".format(category))
    return results[0][0]
