"""Add cancelled column

Revision ID: 2282351403f3
Revises: 13bccf1c3b47
Create Date: 2017-03-29 13:17:02.127619

"""

# revision identifiers, used by Alembic.
revision = '2282351403f3'
down_revision = '13bccf1c3b47'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('local_land_charge', sa.Column('cancelled', sa.Boolean(), nullable=False))
    op.alter_column('local_land_charge', 'geometry',
                    existing_type=geoalchemy2.types.Geometry(srid=27700),
                    nullable=False)
    op.alter_column('local_land_charge', 'llc_item',
                    existing_type=postgresql.JSONB(),
                    nullable=False)
    op.alter_column('local_land_charge', 'type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)


def downgrade():
    op.alter_column('local_land_charge', 'type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('local_land_charge', 'llc_item',
                    existing_type=postgresql.JSONB(),
                    nullable=True)
    op.alter_column('local_land_charge', 'geometry',
                    existing_type=geoalchemy2.types.Geometry(srid=27700),
                    nullable=True)
    op.drop_column('local_land_charge', 'cancelled')
