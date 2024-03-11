"""index entry number

Revision ID: f2818205aa4d
Revises: 92b38a9b2bcb
Create Date: 2017-05-10 14:56:49.535330

"""

# revision identifiers, used by Alembic.
revision = 'f2818205aa4d'
down_revision = '92b38a9b2bcb'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_index(op.f('ix_local_land_charge_history_entry_number'), 'local_land_charge_history', ['entry_number'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_local_land_charge_history_entry_number'), table_name='local_land_charge_history')
