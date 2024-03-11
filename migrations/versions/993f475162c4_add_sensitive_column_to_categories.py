"""Add sensitive column to categories

Revision ID: 993f475162c4
Revises: 168edc31ffcd
Create Date: 2019-04-23 14:57:38.783346

"""

# revision identifiers, used by Alembic.
revision = '993f475162c4'
down_revision = '168edc31ffcd'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('charge_categories', sa.Column('sensitive', sa.Boolean(), server_default="f"))
    query = "UPDATE charge_categories SET sensitive = 't' WHERE name = 'Pipeline';"
    op.execute(query)


def downgrade():
    op.drop_column('charge_categories', 'sensitive')
