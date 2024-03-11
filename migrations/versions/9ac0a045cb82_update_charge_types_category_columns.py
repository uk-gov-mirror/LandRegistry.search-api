""" Update charge types and category columns

Revision ID: 9ac0a045cb82
Revises: 4b4479b49a95
Create Date: 2018-12-19 09:28:25.361632

"""

# revision identifiers, used by Alembic.
revision = '9ac0a045cb82'
down_revision = '4b4479b49a95'

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

charge_dict = {
    "Housing": "Housing / buildings",
    "Approval under house in multiple occupation (HMO)": "Occupancy including house in multiple occupation (HMO)",
    "Notice of works or repairs": "Works, repairs or authority action",
    "Compulsory purchase order": "Compulsory purchase or acquisition",
    "Water / drainage": "Water / drainage / environmental"
}


def upgrade():
    op.add_column('charge_categories', sa.Column('display_name_valid', postgresql.JSONB()))
    update_display_name_valid()
    query = "UPDATE charge_categories SET display_name = 'Light obstruction notice' WHERE name = 'Light obstruction notice';"
    op.execute(query)
    update_order()


def downgrade():
    op.drop_column('charge_categories', 'display_name_valid')
    for charge_name in charge_dict:
        query = "UPDATE charge_categories SET display_name = '%s' WHERE name = '%s';" % (charge_name, charge_name)
        op.execute(query)
    query = "UPDATE charge_categories SET display_name = 'Light obstruction notice (LON)' WHERE name = 'Light obstruction notice';"
    op.execute(query)
    update_order()


# Loop through current charge_categories table and add the existing charges to the JSON field in the Database
def update_display_name_valid():
    conn = op.get_bind()
    query = "SELECT name, display_name FROM charge_categories;"
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Charge Categories")

    for result in results:
        charge_name = result[0]
        updated_charge_name = charge_dict.get(result[0])   # None if not listed in the dict

        # Compare the name & display_name, as there are some charge categories that are already different,
        # so we need to save both versions in the JSON field for validation
        if updated_charge_name is None:
            if result[0] != result[1]:
                valid_charges = '"%s","%s"' % (result[0], result[1])
            else:
                valid_charges = '"%s"' % (result[1])
        else:
            if result[0] != result[1]:
                valid_charges = '"%s","%s","%s"' % (result[0], result[1], updated_charge_name)
            else:
                valid_charges = '"%s","%s"' % (result[1], updated_charge_name)

            query = ("UPDATE charge_categories SET display_name = '%s' WHERE name = '%s';" %
                     (updated_charge_name, charge_name))
            op.execute(query)

        display_name_current = '{"valid_display_names":[%s]}' % (valid_charges)
        query = ("UPDATE charge_categories SET display_name_valid = '{0}' WHERE name = '{1}';".
                 format(display_name_current, charge_name))
        op.execute(query)


def update_order():
    query = """
        UPDATE public.charge_categories a
        SET display_order =
            (SELECT position from
                (SELECT b.display_name, row_number() over(order by display_name) as position
                    FROM public.charge_categories b
                    WHERE b.parent_id = a.parent_id) result
                WHERE a.display_name = result.display_name)
        WHERE a.parent_id is not null;"""
    op.execute(query)