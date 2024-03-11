"""Update geometry_featurealem table to add composite key.

Revision ID: b7175f5a6811
Revises: e78127b9d712
Create Date: 2017-06-09 08:20:18.536064

"""

# revision identifiers, used by Alembic.
revision = 'b7175f5a6811'
down_revision = 'e78127b9d712'

from alembic import op


def upgrade():
    op.drop_constraint('geometry_feature_pkey', 'geometry_feature')
    op.create_primary_key('geometry_feature_pkey', 'geometry_feature',
                          ['id', 'local_land_charge_id'])

def downgrade():
    op.drop_constraint('geometry_feature_pkey', 'geometry_feature')
    op.create_primary_key('geometry_feature_pkey', 'geometry_feature',
                          ['id'])