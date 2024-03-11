"""Update inspire categories

Revision ID: 749353252901
Revises: b5bc2e1a1908
Create Date: 2022-04-06 10:18:41.632901

"""

# revision identifiers, used by Alembic.
revision = '749353252901'
down_revision = 'b5bc2e1a1908'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

INSPIRE_THEMES = [
    ["Planning", "Tree preservation order (TPO)", "LU", "PS"],
    ["Other", "Compulsory purchase order", "LU", None],
]

def upgrade():
    conn = op.get_bind()
    for theme in INSPIRE_THEMES:
        res = conn.execute(text("SELECT id FROM charge_categories where display_name_valid -> 'valid_display_names' ? '{}'".format(theme[0])))
        results = res.fetchall()
        if results is None or len(results) == 0:
            raise Exception("Unable to retrieve category with name '{}'".format(theme[0]))
        if theme[1]:
            res = conn.execute(text("SELECT id FROM charge_categories where parent_id = {} AND display_name_valid -> 'valid_display_names' ? '{}'".format(results[0][0], theme[1])))
            results = res.fetchall()
            if results is None or len(results) == 0:
                raise Exception("Unable to retrieve sub_category with name '{}'".format(theme[1]))
        if theme[2]:
            op.execute("UPDATE charge_categories SET inspire_theme = '{}' WHERE id = {}".format(theme[2], results[0][0]))
        else:
            op.execute("UPDATE charge_categories SET inspire_theme = null WHERE id = {}".format(results[0][0]))


def downgrade():
    conn = op.get_bind()
    for theme in INSPIRE_THEMES:
        res = conn.execute(text("SELECT id FROM charge_categories where display_name_valid -> 'valid_display_names' ? '{}'".format(theme[0])))
        results = res.fetchall()
        if results is None or len(results) == 0:
            raise Exception("Unable to retrieve category with name '{}'".format(theme[0]))
        if theme[1]:
            res = conn.execute(text("SELECT id FROM charge_categories where parent_id = {} AND display_name_valid -> 'valid_display_names' ? '{}'".format(results[0][0], theme[1])))
            results = res.fetchall()
            if results is None or len(results) == 0:
                raise Exception("Unable to retrieve sub_category with name '{}'".format(theme[1]))
        if theme[3]:
            op.execute("UPDATE charge_categories SET inspire_theme = '{}' WHERE id = {}".format(theme[3], results[0][0]))
        else:
            op.execute("UPDATE charge_categories SET inspire_theme = null WHERE id = {}".format(results[0][0]))
