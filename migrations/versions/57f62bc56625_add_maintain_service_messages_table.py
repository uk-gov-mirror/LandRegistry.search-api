"""add maintain service messages table

Revision ID: 57f62bc56625
Revises: 1c659cc52604
Create Date: 2022-11-10 14:11:21.033875

"""

# revision identifiers, used by Alembic.
revision = '57f62bc56625'
down_revision = '1c659cc52604'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    op.create_table(
        'maintain_service_messages',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('message_name', sa.String(), nullable=False),
        sa.Column('message_en', sa.String(), nullable=False),
        sa.Column('message_cy', sa.String(), nullable=False),
        sa.Column('hyperlink_message_en', sa.String(), nullable=True),
        sa.Column('hyperlink_message_cy', sa.String(), nullable=True),
        sa.Column('hyperlink_link_en', sa.String(), nullable=True),
        sa.Column('hyperlink_link_cy', sa.String(), nullable=True)
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON maintain_service_messages TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    op.execute("GRANT ALL ON SEQUENCE maintain_service_messages_id_seq TO {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    # Add permission for acceptance test users
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON maintain_service_messages TO {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))
    op.execute("GRANT ALL ON SEQUENCE maintain_service_messages_id_seq TO {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))


def downgrade():
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE maintain_service_messages_id_seq FROM {};".format(
        current_app.config.get("APP_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON maintain_service_messages FROM {};".format(
        current_app.config.get('APP_SQL_USERNAME')))
    op.execute("REVOKE ALL PRIVILEGES ON SEQUENCE maintain_service_messages_id_seq FROM {};".format(
        current_app.config.get("ACCTEST_SQL_USERNAME")))
    op.execute("REVOKE ALL PRIVILEGES ON maintain_service_messages FROM {};".format(
        current_app.config.get('ACCTEST_SQL_USERNAME')))
    op.drop_table('maintain_service_messages')
