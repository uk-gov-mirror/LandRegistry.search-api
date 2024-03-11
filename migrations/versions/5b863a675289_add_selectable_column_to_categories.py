"""add selectable column to categories

Revision ID: 5b863a675289
Revises: f9d70e6ec06f
Create Date: 2020-06-19 09:51:20.811832

"""

# revision identifiers, used by Alembic.
revision = '5b863a675289'
down_revision = 'f9d70e6ec06f'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.add_column('charge_categories', sa.Column('selectable', sa.Boolean(), server_default="t"))
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON charge_categories TO " +
               current_app.config.get("ACCTEST_SQL_USERNAME"))
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON charge_categories_id_seq TO " +
               current_app.config.get("ACCTEST_SQL_USERNAME"))


def downgrade():
    op.drop_column('charge_categories', 'selectable')
    op.execute("REVOKE ALL PRIVILEGES ON charge_categories FROM " + current_app.config.get("ACCTEST_SQL_USERNAME"))
    op.execute("REVOKE ALL PRIVILEGES ON charge_categories_id_seq FROM " +
               current_app.config.get("ACCTEST_SQL_USERNAME"))
