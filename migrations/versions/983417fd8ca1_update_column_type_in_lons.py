"""Update LONs table to change column type of
    documents_filed and applicant_address from String to JSONB

Revision ID: 983417fd8ca1
Revises: ff564b4e22ba
Create Date: 2017-07-06 12:25:35.446201

"""

# revision identifiers, used by Alembic.
revision = '983417fd8ca1'
down_revision = 'ff564b4e22ba'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.execute('ALTER TABLE light_obstruction_notice \
            ALTER COLUMN documents_filed \
            TYPE JSONB \
            USING (documents_filed::JSONB)')

    op.execute('ALTER TABLE light_obstruction_notice \
            ALTER COLUMN applicant_address \
            TYPE JSONB \
            USING (applicant_address::JSONB)')


def downgrade():

    with op.batch_alter_table('light_obstruction_notice') as batch_op:
        batch_op.alter_column('documents_filed',
                              type_=sa.String())
        batch_op.alter_column('applicant_address',
                              type_=sa.String())
