"""Add additional threshold columns

Revision ID: 58d2d5c5bf42
Revises: 763bbc0ec902
Create Date: 2021-05-18 16:18:42.247394

"""

# revision identifiers, used by Alembic.
revision = '58d2d5c5bf42'
down_revision = '763bbc0ec902'

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column('organisation_threshold', sa.Column('add_warning', sa.Integer(), nullable=False))
    op.add_column('organisation_threshold', sa.Column('vary_warning', sa.Integer(), nullable=False))
    op.add_column('organisation_threshold', sa.Column('cancel_warning', sa.Integer(), nullable=False))
    op.add_column('organisation_threshold', sa.Column('last_add_warning', sa.Date(), nullable=True))
    op.add_column('organisation_threshold', sa.Column('last_vary_warning', sa.Date(), nullable=True))
    op.add_column('organisation_threshold', sa.Column('last_cancel_warning', sa.Date(), nullable=True))
    op.add_column('organisation_threshold', sa.Column('suspended_until', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('organisation_threshold', 'add_warning')
    op.drop_column('organisation_threshold', 'vary_warning')
    op.drop_column('organisation_threshold', 'cancel_warning')
    op.drop_column('organisation_threshold', 'last_add_warning')
    op.drop_column('organisation_threshold', 'last_vary_warning')
    op.drop_column('organisation_threshold', 'last_cancel_warning')
    op.drop_column('organisation_threshold', 'suspended_until')
