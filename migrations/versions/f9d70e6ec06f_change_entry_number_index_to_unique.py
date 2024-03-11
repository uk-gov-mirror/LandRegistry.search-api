"""Change entry number index to unique

Revision ID: f9d70e6ec06f
Revises: 4324861ea4a5
Create Date: 2020-06-09 16:06:21.059139

"""

# revision identifiers, used by Alembic.
revision = 'f9d70e6ec06f'
down_revision = '4324861ea4a5'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.drop_index(op.f('ix_local_land_charge_history_entry_number'), table_name='local_land_charge_history')
    op.create_index(op.f('ix_local_land_charge_history_entry_number'), 'local_land_charge_history', ['entry_number'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_local_land_charge_history_entry_number'), table_name='local_land_charge_history')
    op.create_index(op.f('ix_local_land_charge_history_entry_number'), 'local_land_charge_history', ['entry_number'], unique=False)
