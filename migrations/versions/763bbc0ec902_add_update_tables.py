"""Add update tables

Revision ID: 763bbc0ec902
Revises: 225329075a5f
Create Date: 2021-05-11 12:00:48.765485

"""

# revision identifiers, used by Alembic.
revision = '763bbc0ec902'
down_revision = '225329075a5f'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.create_table('organisation_threshold',
    sa.Column('organisation', sa.String(), nullable=False),
    sa.Column('add_threshold', sa.Integer(), nullable=False),
    sa.Column('vary_threshold', sa.Integer(), nullable=False),
    sa.Column('cancel_threshold', sa.Integer(), nullable=False),
    sa.Column('last_add_alert', sa.Date(), nullable=True),
    sa.Column('last_vary_alert', sa.Date(), nullable=True),
    sa.Column('last_cancel_alert', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('organisation'),
    )
    op.create_table('organisation_update',
    sa.Column('_id', sa.BigInteger(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('organisation', sa.String(), nullable=True),
    sa.Column('update_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('_id')
    )
    op.execute("GRANT ALL ON organisation_update TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON organisation_threshold TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON SEQUENCE organisation_update__id_seq TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))

    op.execute("GRANT ALL ON organisation_update TO " + current_app.config.get("ACCTEST_SQL_USERNAME"))
    op.execute("GRANT ALL ON organisation_threshold TO " + current_app.config.get("ACCTEST_SQL_USERNAME"))
    op.execute("GRANT ALL ON SEQUENCE organisation_update__id_seq TO {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))


def downgrade():
    op.drop_table('organisation_update')
    op.drop_table('organisation_threshold')