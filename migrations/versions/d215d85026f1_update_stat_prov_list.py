"""update stat prov list

Revision ID: d215d85026f1
Revises: a68e1274f293
Create Date: 2020-02-27 08:34:11.954164

"""

# revision identifiers, used by Alembic.
revision = 'd215d85026f1'
down_revision = 'a68e1274f293'

import sqlalchemy as sa
from alembic import op

new_stat_prov = 'Town and Country Planning (General Permitted Development) (England) Order 2015 Article 4(1)'
new_instrument = 'Schedule'
stat_prov_display_name = 'Compulsory Purchase (Vesting Declarations) Act 1981 section 3A(4)'
hide_stat_prov = 'Compulsory Purchase(Vesting Declarations) Act 1981 section 3A(4)'

def upgrade():
    query_list =[]
    query_list.append("INSERT INTO statutory_provision (title, selectable, display_title) VALUES ('{0}', {1}, '{2}');"\
            .format(new_stat_prov, True, new_stat_prov))
    query_list.append("INSERT INTO instruments (name) VALUES ('{}');".format(new_instrument))
    query_list.append("UPDATE statutory_provision set selectable = FALSE, display_title = '{0}' where title = '{1}';".format(stat_prov_display_name, hide_stat_prov))
    for query in query_list:
        op.execute(query)

def downgrade():
    query_list =[]
    query_list.append("DELETE from statutory_provision WHERE title = '{}';".format(new_stat_prov))
    query_list.append("DELETE from instruments WHERE name = '{}';".format(new_instrument))
    query_list.append("UPDATE statutory_provision set selectable = TRUE, display_title = '{0}' where title = '{1}';".format(hide_stat_prov, hide_stat_prov))
    for query in query_list:
        op.execute(query)
