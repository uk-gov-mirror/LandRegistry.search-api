"""Update LLC History Table to include Item Changes, Entry Timestamp and Geometry Field

Revision ID: 92b38a9b2bcb
Revises: 37d3726feb0a
Create Date: 2017-04-27 10:10:43.249964

"""

# revision identifiers, used by Alembic.
revision = '92b38a9b2bcb'
down_revision = '37d3726feb0a'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('local_land_charge_history', sa.Column('item_changes', postgresql.JSONB()))
    op.add_column('local_land_charge_history', sa.Column('entry_timestamp', sa.DateTime(), nullable=False))
    op.add_column('local_land_charge_history', sa.Column('geometry',
                                                         geoalchemy2.types.Geometry(srid=27700), nullable=False))


def downgrade():
    op.drop_column('local_land_charge_history', 'item_changes')
    op.drop_column('local_land_charge_history', 'entry_timestamp')
    op.drop_column('local_land_charge_history', 'geometry')
