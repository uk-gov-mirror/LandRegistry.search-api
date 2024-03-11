"""Initial DB setup

Revision ID: 7efb0a3f9a39
Revises: None
Create Date: 2017-03-01 09:30:31.519855

"""

# revision identifiers, used by Alembic.
revision = '7efb0a3f9a39'
down_revision = None

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('local_land_charge',
                    sa.Column('id', sa.BigInteger(), primary_key=True),
                    sa.Column('geometry', geoalchemy2.types.Geometry(srid=27700)),
                    sa.Column('type', sa.String()),
                    sa.Column('llc_item', postgresql.JSONB()))
    op.create_index('ix_local_land_charge_id', 'local_land_charge', ['id'])
    op.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_index('ix_local_land_charge_id')
    op.drop_table('local_land_charge')
