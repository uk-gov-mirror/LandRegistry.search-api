"""Add pipeline category

Revision ID: 168edc31ffcd
Revises: 9ac0a045cb82
Create Date: 2019-04-11 12:27:47.540041

"""

# revision identifiers, used by Alembic.
revision = '168edc31ffcd'
down_revision = '9ac0a045cb82'

import sqlalchemy as sa
from alembic import op


def upgrade():

    query = "DO $$ BEGIN IF NOT EXISTS " \
            "(SELECT FROM charge_categories " \
            "WHERE name = 'Pipeline') THEN " \
            "UPDATE charge_categories SET display_order = (display_order + 1) " \
            "WHERE parent_id = (SELECT id FROM charge_categories WHERE name = 'Other') " \
            "AND display_order >= 7; " \
            "INSERT INTO charge_categories(name, display_name, parent_id, display_order, "\
            "permission, display_name_valid) " \
            "VALUES('Pipeline', 'Pipeline', (SELECT id FROM charge_categories WHERE name = 'Other'), 7, "\
            "'Add Sensitive Charges', '{\"valid_display_names\": [\"Pipeline\"]}');" \
            "END IF; END $$"
    op.execute(query)


def downgrade():
    query = "DO $$ BEGIN IF EXISTS " \
            "(SELECT FROM charge_categories " \
            "WHERE name = 'Pipeline') THEN " \
            "DELETE FROM charge_categories WHERE name = 'Pipeline'; " \
            "UPDATE charge_categories SET display_order = (display_order - 1) " \
            "WHERE parent_id = (SELECT id FROM charge_categories WHERE name = 'Other') " \
            "AND display_order > 7; " \
            "END IF; END $$"
    op.execute(query)
