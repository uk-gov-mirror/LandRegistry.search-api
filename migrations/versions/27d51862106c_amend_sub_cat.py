"""Amend the sub category 
No permitted development / article 4 to add Article 4 / no permitted development
as a valid version to the display_name_valid column for the sub category

Revision ID: 27d51862106c
Revises: 993f475162c4
Create Date: 2019-05-23 07:42:22.131254

"""

# revision identifiers, used by Alembic.
revision = '27d51862106c'
down_revision = '993f475162c4'

import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

updated_charge = 'Article 4 / no permitted development'

def upgrade():
    conn = op.get_bind()
    query = "SELECT display_name_valid FROM charge_categories WHERE display_name = 'No permitted development / article 4' AND parent_id IS NOT NULL;"
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Charge Category: No permitted development / article 4")
    else:
        for result in results:
            for element in result:
                display_name_current = element.get('valid_display_names')
                display_name_current.append(updated_charge)
                valid_display_names = '{{"valid_display_names":{0}}}'.format(display_name_current)
                valid_display_names = valid_display_names.replace("'", "\"")
                query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE name = 'No permitted development / article 4';".
                         format(valid_display_names))
                op.execute(query)


def downgrade():
    conn = op.get_bind()
    query = "SELECT display_name_valid FROM charge_categories WHERE display_name = 'No permitted development / article 4' AND parent_id IS NOT NULL;"
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Charge Category: No permitted development / article 4")
    else:
        for result in results:
            for element in result:
                display_name_current = element.get('valid_display_names')
                display_name_current.remove(updated_charge)
                valid_display_names = '{{"valid_display_names":{0}}}'.format(display_name_current)
                valid_display_names = valid_display_names.replace("'", "\"")
                query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE name = 'No permitted development / article 4';".
                        format(valid_display_names))
                op.execute(query)
