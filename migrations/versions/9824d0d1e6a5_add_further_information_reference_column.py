"""Setup optional further_information_reference column for authority reference searches

Revision ID: 9824d0d1e6a5
Revises: af832e9dbcea
Create Date: 2017-10-27 10:12:26.902763

"""

# revision identifiers, used by Alembic.
revision = '9824d0d1e6a5'
down_revision = 'af832e9dbcea'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('local_land_charge', sa.Column('further_information_reference', sa.String(), nullable=True))
    op.create_index('ix_local_land_charge_further_information_reference', 'local_land_charge',
                    ['further_information_reference'])


def downgrade():
    op.drop_column('local_land_charge', 'further_information_reference')
