"""adding_LLC_reference_to_database

Revision ID: a68e1274f293
Revises: 3e8d3521b816
Create Date: 2020-02-12 11:32:12.012021

"""

# revision identifiers, used by Alembic.
revision = 'a68e1274f293'
down_revision = '3e8d3521b816'

import sqlalchemy as sa
from alembic import op
from search_api.utilities.charge_id import encode_charge_id
from sqlalchemy.sql import text


def upgrade():
    conn = op.get_bind()
    op.add_column('local_land_charge',
                  sa.Column('llc_id', sa.String()))
    op.create_index('ix_local_land_charge_llc_id', 'local_land_charge', ['llc_id'])
    query = 'SELECT MAX(id) FROM local_land_charge'
    max_id = conn.execute(text(query)).first()[0]
    if max_id:
        for id in range(1, max_id + 1):
            query = "UPDATE local_land_charge SET llc_id = '{}' WHERE id = '{}'".format(encode_charge_id(id), id)
            conn.execute(text(query))
        

def downgrade():
    op.drop_index('ix_local_land_charge_llc_id')
    op.drop_column('local_land_charge', 'llc_id')
