"""add stat prov
Revision ID: a724301e7136
Revises: d215d85026f1
Create Date: 2020-03-16 09:31:24.646197
"""
# revision identifiers, used by Alembic.
revision = 'a724301e7136'
down_revision = 'd215d85026f1'

import sqlalchemy as sa
from alembic import op

stat_prov = 'Compulsory Purchase (Vesting Declarations) Act 1981 section 3A(4)'

def upgrade():
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM statutory_provision WHERE title = '{0}') THEN INSERT INTO statutory_provision " \
                "(title, selectable, display_title) VALUES ('{0}', {1}, '{0}'); END IF; END $$;".format(stat_prov, True)
    op.execute(query)

def downgrade():
    op.execute("DELETE from statutory_provision WHERE title = '{}';".format(stat_prov))
