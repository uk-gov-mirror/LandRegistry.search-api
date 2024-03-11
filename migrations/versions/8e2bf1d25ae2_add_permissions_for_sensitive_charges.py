"""Add permissions for sensitive charges

Revision ID: 8e2bf1d25ae2
Revises: 35f70c6783c0
Create Date: 2022-02-08 11:25:52.654276

"""

# revision identifiers, used by Alembic.
revision = '8e2bf1d25ae2'
down_revision = '35f70c6783c0'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.execute("UPDATE charge_categories SET vary_permission = 'Vary Sensitive Charges' WHERE name = 'Pipeline';")
    op.execute("UPDATE charge_categories SET cancel_permission = 'Cancel Sensitive Charges' WHERE name = 'Pipeline';")


def downgrade():
    op.execute("UPDATE charge_categories SET vary_permission = 'Add Sensitive Charges' WHERE name = 'Pipeline';")
    op.execute("UPDATE charge_categories SET cancel_permission = 'Add Sensitive Charges' WHERE name = 'Pipeline';")
