"""Add inspire theme to categories

Revision ID: b5bc2e1a1908
Revises: 8e2bf1d25ae2
Create Date: 2022-03-15 10:27:51.027407

"""

# revision identifiers, used by Alembic.
revision = 'b5bc2e1a1908'
down_revision = '8e2bf1d25ae2'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

INSPIRE_THEMES = [
    ["Planning", "Conditional planning consent", "LU"],
    ["Planning", "Conservation area", "PS"],
    ["Planning", "No permitted development / article 4", "LU"],
    ["Planning", "Planning agreement", "LU"],
    ["Planning", "Tree preservation order (TPO)", "PS"],
    ["Listed building", "Listed building", "PS"],
    ["Other", "Ancient monuments", "PS"],
    ["Other", "Assets of community value", "PS"],
    ["Other", "Local acts", "AM"],
    ["Other", "Protected areas / sites", "PS"],
    ["Other", "Smoke control order", "AM"],
]


def upgrade():
    conn = op.get_bind()
    op.add_column('charge_categories', sa.Column('inspire_theme', sa.String(), nullable=True))
    for theme in INSPIRE_THEMES:
        res = conn.execute(text("SELECT id FROM charge_categories where parent_id is null and display_name_valid -> 'valid_display_names' ? '{}'".format(theme[0])))
        results = res.fetchall()
        if results is None or len(results) == 0:
            raise Exception("Unable to retrieve category with name '{}'".format(theme[0]))
        if theme[1]:
            res = conn.execute(text("SELECT id FROM charge_categories where parent_id = {} AND display_name_valid -> 'valid_display_names' ? '{}'".format(results[0][0], theme[1])))
            results = res.fetchall()
            if results is None or len(results) == 0:
                raise Exception("Unable to retrieve sub_category with name '{}'".format(theme[1]))
        op.execute("UPDATE charge_categories SET inspire_theme = '{}' WHERE id = {}".format(theme[2], results[0][0]))


def downgrade():
    op.drop_column('charge_categories', 'inspire_theme')
