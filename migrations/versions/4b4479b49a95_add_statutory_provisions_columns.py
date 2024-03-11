"""Add extra columns to the Statutory Provisions

Revision ID: 4b4479b49a95
Revises: 72fb9695d479
Create Date: 2018-11-13 10:26:48.407471

"""

# revision identifiers, used by Alembic.
revision = '4b4479b49a95'
down_revision = '72fb9695d479'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.add_column('statutory_provision', sa.Column('display_title', sa.String(), nullable=True))

    query = "UPDATE statutory_provision SET display_title = title;"
    op.execute(query)


def downgrade():
    op.drop_column('statutory_provision', 'display_title')
