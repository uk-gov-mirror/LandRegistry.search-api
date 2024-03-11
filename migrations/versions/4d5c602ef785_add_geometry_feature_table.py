"""Add geometry feature table

Revision ID: 4d5c602ef785
Revises: f2818205aa4d
Create Date: 2017-05-24 11:07:28.298985

"""

# revision identifiers, used by Alembic.
revision = '4d5c602ef785'
down_revision = 'f2818205aa4d'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('geometry_feature',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('geometry', geoalchemy2.types.Geometry(srid=27700), nullable=False),
                    sa.Column('local_land_charge_id', sa.BigInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_foreign_key(None, 'geometry_feature', 'local_land_charge', ['local_land_charge_id'], ['id'])
    op.execute("GRANT SELECT ON geometry_feature TO " +
               current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT ON geometry_feature_id_seq TO " +
               current_app.config.get("APP_SQL_USERNAME"))
    op.drop_column('local_land_charge', 'geometry')
    op.drop_column('local_land_charge_history', 'geometry')


def downgrade():
    op.add_column('local_land_charge_history', sa.Column('geometry', geoalchemy2.types.Geometry(srid=27700), autoincrement=False, nullable=True))
    op.add_column('local_land_charge', sa.Column('geometry', geoalchemy2.types.Geometry(srid=27700), autoincrement=False, nullable=True))
    op.create_index('idx_local_land_charge_geometry', 'local_land_charge', ['geometry'], unique=False)
    op.drop_index('idx_geometry_feature_geometry', table_name='geometry_feature')
    op.drop_table('geometry_feature')
