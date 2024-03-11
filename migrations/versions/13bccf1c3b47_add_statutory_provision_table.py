"""Add Statutory Provision table

Revision ID: 13bccf1c3b47
Revises: 7efb0a3f9a39
Create Date: 2017-03-16 11:54:06.135132

"""

# revision identifiers, used by Alembic.
revision = '13bccf1c3b47'
down_revision = '7efb0a3f9a39'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.create_table('statutory_provision',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('title', sa.String(), nullable=False))
    op.execute("GRANT SELECT, INSERT ON statutory_provision TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON statutory_provision_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('statutory_provision')
