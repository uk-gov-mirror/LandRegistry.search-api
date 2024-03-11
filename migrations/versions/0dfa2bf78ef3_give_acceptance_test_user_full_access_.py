"""give acceptance test user full access to stat prov table

Revision ID: 0dfa2bf78ef3
Revises: fbdbb4eb3a5e
Create Date: 2020-05-12 15:02:19.805747

"""

# revision identifiers, used by Alembic.
revision = '0dfa2bf78ef3'
down_revision = 'fbdbb4eb3a5e'

from alembic import op
from flask import current_app


def upgrade():
    op.execute("GRANT DELETE ON statutory_provision TO " + current_app.config.get("ACCTEST_SQL_USERNAME"))
    op.execute("GRANT DELETE ON statutory_provision_id_seq TO " + current_app.config.get("ACCTEST_SQL_USERNAME"))


def downgrade():
    op.execute("REVOKE DELETE ON TABLE statutory_provision FROM " + current_app.config.get('ACCTEST_SQL_USERNAME'))
    op.execute("REVOKE DELETE ON TABLE statutory_provision_id_seq FROM " + current_app.config.get('ACCTEST_SQL_USERNAME'))
