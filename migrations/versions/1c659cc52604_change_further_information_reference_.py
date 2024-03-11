"""Change further_information_reference indexing

Revision ID: 1c659cc52604
Revises: 7d321428b3de
Create Date: 2022-10-11 14:12:57.091400

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = '1c659cc52604'
down_revision = '7d321428b3de'


def upgrade():
   op.create_index('ix_local_land_charge_further_information_reference_lower', 'local_land_charge',
                    [sa.text('lower(further_information_reference)')])

def downgrade():
   op.drop_index('ix_local_land_charge_further_information_reference_lower')
