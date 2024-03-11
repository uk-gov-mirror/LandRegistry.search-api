"""Add new stat provs

Revision ID: fbdbb4eb3a5e
Revises: a724301e7136
Create Date: 2020-04-27 13:41:44.033855

"""

# revision identifiers, used by Alembic.
revision = 'fbdbb4eb3a5e'
down_revision = 'a724301e7136'

import sqlalchemy as sa
from alembic import op

stat_provs = ['Water Industry Act 1991 section 185',
              'Environmental Permitting (England and Wales) Regulations 2016 regulation 15']

def upgrade():
    for stat_prov in stat_provs:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM statutory_provision WHERE title = '{0}') THEN INSERT INTO statutory_provision " \
                    "(title, selectable, display_title) VALUES ('{0}', {1}, '{0}'); END IF; END $$;".format(stat_prov, True)
        op.execute(query)

def downgrade():
    for stat_prov in stat_provs:
        op.execute("DELETE from statutory_provision WHERE title = '{}';".format(stat_prov))
