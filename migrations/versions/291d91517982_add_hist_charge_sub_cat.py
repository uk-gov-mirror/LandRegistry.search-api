"""Add historical versions of sub-categories

Warwick has some old versions of charge sub-cats we already hold.

Revision ID: 291d91517982
Revises: 27d51862106c
Create Date: 2019-07-16 09:06:40.622255

"""

# revision identifiers, used by Alembic.
revision = '291d91517982'
down_revision = '27d51862106c'

from alembic import op
from sqlalchemy.sql import text


def _add_value_to_display_name_valid(display_name_valid_list, value_to_add, row_id):
    display_name_valid_list['valid_display_names'].append(value_to_add)
    # convert the list to a string and escape the single quotes as double quotes.
    to_update = str(display_name_valid_list).replace("'", "\"")
    query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE id = {1}"
             .format(to_update, row_id))
    op.execute(query)


def _remove_value_from_display_name_valid(display_name_valid_list, value_to_remove, row_id):
    display_name_valid_list['valid_display_names']
    if value_to_remove in display_name_valid_list['valid_display_names']:
        display_name_valid_list['valid_display_names'].remove(value_to_remove)
        to_update = str(display_name_valid_list).replace("'", "\"")
        query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE id = {1}"
                 .format(to_update, row_id))
        op.execute(query)
        return 0
    else:
        return -1


def upgrade():
    conn = op.get_bind()
    query = ("SELECT id, name, display_name, display_name_valid FROM public.charge_categories "
             "WHERE parent_id IS NOT NULL "
             "AND display_name in ('Water / drainage / environmental', 'Licence', 'Ancient monuments');")
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("No sub-categories found")
    else:
        for result in results:
            if result[2] == "Ancient monuments":
                _add_value_to_display_name_valid(result[3], "Ancient Monuments", result[0])
            elif result[2] == "Licence":
                _add_value_to_display_name_valid(result[3], "Licences", result[0])
            elif result[2] == "Water / drainage / environmental":
                _add_value_to_display_name_valid(result[3], "Water drainage", result[0])
            else:
                raise Exception("An unexpected display_name was returned. Exiting.")


def downgrade():
    conn = op.get_bind()
    query = ("SELECT id, name, display_name, display_name_valid FROM public.charge_categories "
             "WHERE parent_id IS NOT NULL "
             "AND display_name in ('Water / drainage / environmental', 'Licence', 'Ancient monuments');")
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("No sub-categories found")
    else:
        for result in results:
            if result[2] == "Ancient monuments":
                _remove_value_from_display_name_valid(result[3], "Ancient Monuments", result[0])
            elif result[2] == "Licence":
                _remove_value_from_display_name_valid(result[3], "Licences", result[0])
            elif result[2] == "Water / drainage / environmental":
                _remove_value_from_display_name_valid(result[3], "Water drainage", result[0])
            else:
                raise Exception("An unexpected display_name was returned. Exiting.")
