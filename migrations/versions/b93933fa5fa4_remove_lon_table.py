"""Remove LON table

Revision ID: b93933fa5fa4
Revises: 9824d0d1e6a5
Create Date: 2017-10-31 13:15:57.501604

"""

# revision identifiers, used by Alembic.
revision = 'b93933fa5fa4'
down_revision = '9824d0d1e6a5'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_index('ix_lons_local_land_charge_id')
    op.drop_table('light_obstruction_notice')
    op.execute('DROP TYPE servient_land_interest_description;')


def downgrade():
    op.create_table('light_obstruction_notice',
                    sa.Column('local_land_charge_id', sa.BigInteger(), sa.ForeignKey('local_land_charge.id'),
                              nullable=False, primary_key=True),
                    sa.Column('applicant_name', sa.String(), nullable=False),
                    sa.Column('applicant_address', sa.String(), nullable=False),
                    sa.Column('servient_land_interest_description',
                              postgresql.ENUM('Owner', 'Tenant', 'Lender',
                                              name='servient_land_interest_description'),
                              nullable=False),
                    sa.Column('structure_position_and_dimension', sa.String(), nullable=False),
                    sa.Column('tribunal_definitive_certificate_date', sa.Date(), nullable=True),
                    sa.Column('documents_filed', sa.String(), nullable=False),
                    sa.Column('tribunal_temporary_certificate_date', sa.Date(), nullable=True),
                    sa.Column('tribunal_temporary_certificate_expiry_date', sa.Date(), nullable=True),
                    sa.Column('notice_expiry_date', sa.Date(), nullable=False))
    op.create_index('ix_lons_local_land_charge_id', 'light_obstruction_notice', ['local_land_charge_id'])
