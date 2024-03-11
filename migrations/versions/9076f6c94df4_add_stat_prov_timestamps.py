"""Add stat prov timestamps

Revision ID: 9076f6c94df4
Revises: 749353252901
Create Date: 2022-07-13 13:18:17.562680

"""

# revision identifiers, used by Alembic.
revision = '9076f6c94df4'
down_revision = '749353252901'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('statutory_provision', sa.Column('created_timestamp', sa.DateTime(), nullable=True))
    op.alter_column('statutory_provision', 'created_timestamp', nullable=True, server_default=sa.func.current_timestamp())


def downgrade():
    op.drop_column('statutory_provision', 'created_timestamp')
