"""Create table for Light Obstruction Notices.

Revision ID: e78127b9d712
Revises: 4d5c602ef785
Create Date: 2017-06-08 08:18:55.338627

"""

# revision identifiers, used by Alembic.
revision = 'e78127b9d712'
down_revision = '4d5c602ef785'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('lons',
                    sa.Column('local_land_charge_id', sa.BigInteger(), sa.ForeignKey('local_land_charge.id'), nullable=False, primary_key=True),
                    sa.Column('applicant_name', sa.String(), nullable=False),
                    sa.Column('applicant_address', sa.String(), nullable=False),
                    sa.Column('servient_land_interest_description',
                                                                 postgresql.ENUM('Owner', 'Tenant', 'Developer', 'Lender',
                                                                 name='servient_land_interest_description'),
                                                                 nullable=False),
                    sa.Column('structure_position_and_dimension', sa.String(), nullable=False),
                    sa.Column('tribunal_definitive_certificate_date', sa.Date(), nullable=True),
                    sa.Column('documents_filed', sa.String(), nullable=False),
                    sa.Column('tribunal_temporary_certificate_date', sa.Date(), nullable=True),
                    sa.Column('tribunal_temporary_certificate_expiry_date', sa.Date(), nullable=True),
                    sa.Column('notice_expiry_date', sa.Date(), nullable=False))
    op.create_index('ix_lons_local_land_charge_id', 'lons', ['local_land_charge_id'])


def downgrade():
    op.drop_index('ix_lons_local_land_charge_id')
    op.drop_table('lons')
    op.execute('DROP TYPE servient_land_interest_description;')



