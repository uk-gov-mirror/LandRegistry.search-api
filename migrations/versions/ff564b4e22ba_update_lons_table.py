"""Update lons table: rename, remove type, update enum.

Revision ID: ff564b4e22ba
Revises: b7175f5a6811
Create Date: 2017-06-23 09:24:17.423380

"""

# revision identifiers, used by Alembic.
revision = 'ff564b4e22ba'
down_revision = 'b7175f5a6811'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


def upgrade():
    op.drop_column('lons', 'servient_land_interest_description')

    op.execute("DROP TYPE servient_land_interest_description")
    servient_land_interest_description = postgresql.ENUM('Owner', 'Tenant', 'Lender',
                                                         name='servient_land_interest_description')
    servient_land_interest_description.create(op.get_bind())
    with op.batch_alter_table('lons') as batch_op:
        batch_op.drop_column('notice_expiry_date')
        batch_op.add_column(sa.Column('servient_land_interest_description',
                                      sa.Enum('Owner', 'Tenant', 'Lender',
                                              name='servient_land_interest_description'), nullable=False))

    op.rename_table('lons', 'light_obstruction_notice')


def downgrade():
    op.drop_column('light_obstruction_notice', 'servient_land_interest_description')

    op.execute("DROP TYPE servient_land_interest_description")
    servient_land_interest_description = postgresql.ENUM('Owner', 'Tenant', 'Developer', 'Lender',
                                                         name='servient_land_interest_description')
    servient_land_interest_description.create(op.get_bind())

    op.rename_table('light_obstruction_notice', 'lons')
    with op.batch_alter_table('lons') as batch_op:
        batch_op.add_column(sa.Column('servient_land_interest_description',
                                      sa.Enum('Owner', 'Tenant', 'Developer', 'Lender',
                                              name='servient_land_interest_description'), nullable=False))
        batch_op.add_column(sa.Column('notice_expiry_date', sa.Date(), nullable=False))