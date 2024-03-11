"""Adjust permissions for categories again

Revision ID: 35f70c6783c0
Revises: 09c0bfe61172
Create Date: 2021-12-14 15:49:59.869746

"""

# revision identifiers, used by Alembic.
revision = '35f70c6783c0'
down_revision = '09c0bfe61172'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('charge_categories', sa.Column('cancel_permission', sa.String(), nullable=False, server_default='Cancel LLC'))
    op.execute("UPDATE charge_categories SET cancel_permission = 'Add Sensitive Charges' WHERE name = 'Pipeline';")
    op.execute("UPDATE charge_categories SET cancel_permission = 'Cancel LON' WHERE name = 'Light obstruction notice';")

    op.alter_column('charge_categories', 'vary_cancel_permission', nullable=True, new_column_name='vary_permission', server_default='Vary LLC')
    op.execute("UPDATE charge_categories SET vary_permission = 'Vary LLC' WHERE vary_permission IS null;")
    op.alter_column('charge_categories', 'vary_permission', nullable=False)

    op.alter_column('charge_categories', 'permission', nullable=True, new_column_name='add_permission', server_default='Add LLC')
    op.execute("UPDATE charge_categories SET add_permission = 'Add LLC' WHERE add_permission IS null;")
    op.alter_column('charge_categories', 'add_permission', nullable=False)

    op.add_column('charge_categories', sa.Column('add_on_behalf_permission', sa.String(), nullable=False, server_default='Add LLC On Behalf'))
    op.execute("UPDATE charge_categories SET add_on_behalf_permission = 'Add Sensitive Charges On Behalf' WHERE name = 'Pipeline';")
    op.execute("UPDATE charge_categories SET add_on_behalf_permission = 'NONE' WHERE name = 'Light obstruction notice';")
    op.execute("UPDATE charge_categories SET add_on_behalf_permission = 'Add Uncommon Charges On Behalf' WHERE name = 'Uncommon charges';")


def downgrade():
    op.drop_column('charge_categories', 'cancel_permission')

    op.alter_column('charge_categories', 'vary_permission', nullable=True, new_column_name='vary_cancel_permission', server_default=None)
    op.execute("UPDATE charge_categories SET vary_cancel_permission = null WHERE vary_cancel_permission = 'Vary LLC';")

    op.alter_column('charge_categories', 'add_permission', nullable=True, new_column_name='permission', server_default=None)
    op.execute("UPDATE charge_categories SET permission = null WHERE permission = 'Add LLC';")

    op.drop_column('charge_categories', 'add_on_behalf_permission')
