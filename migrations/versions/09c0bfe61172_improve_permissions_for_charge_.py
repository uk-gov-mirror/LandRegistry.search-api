"""Improve permissions for charge categories

Revision ID: 09c0bfe61172
Revises: 58d2d5c5bf42
Create Date: 2021-10-06 10:37:45.441706

"""

# revision identifiers, used by Alembic.
revision = '09c0bfe61172'
down_revision = '58d2d5c5bf42'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('charge_categories', sa.Column('vary_cancel_permission', sa.String(), nullable=True))
    op.execute("UPDATE charge_categories SET vary_cancel_permission = 'Add Sensitive Charges' WHERE name = 'Pipeline';")
    op.execute("UPDATE charge_categories SET vary_cancel_permission = 'Vary LON' WHERE name = 'Light obstruction notice';")


def downgrade():
    op.drop_column('charge_categories', 'vary_cancel_permission')
