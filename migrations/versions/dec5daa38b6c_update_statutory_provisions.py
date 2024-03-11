"""Create tables for categories and statutory provisions

Revision ID: dec5daa38b6c
Revises: 09ebaab850f1
Create Date: 2018-03-14 15:44:28.124606

"""

# revision identifiers, used by Alembic.
revision = 'dec5daa38b6c'
down_revision = '09ebaab850f1'

import sqlalchemy as sa
from alembic import op
from flask import current_app


def upgrade():
    query = "DELETE FROM statutory_provision;"
    op.execute(query)

    op.add_column('statutory_provision', sa.Column('selectable', sa.Boolean, nullable=False, server_default='t'))

    op.create_table('charge_categories',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('display_name', sa.String(), nullable=False),
                    sa.Column('parent_id', sa.Integer(), sa.ForeignKey('charge_categories.id'), nullable=True),
                    sa.Column('display_order', sa.Integer(), nullable=True),
                    sa.Column('permission', sa.String(), nullable=True)
                    )

    op.create_table('instruments',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('name', sa.String(), nullable=False)
                    )

    op.create_table('charge_categories_stat_provisions',
                    sa.Column('category_id', sa.Integer(), sa.ForeignKey('charge_categories.id'), nullable=False),
                    sa.Column('statutory_provision_id', sa.Integer(), sa.ForeignKey('statutory_provision.id'), nullable=False),
                    )

    op.create_table('charge_categories_instruments',
                    sa.Column('category_id', sa.Integer(), sa.ForeignKey('charge_categories.id'), nullable=False),
                    sa.Column('instruments_id', sa.Integer(), sa.ForeignKey('instruments.id'), nullable=False),
                    )

    op.create_unique_constraint("uq_category_name_parent", "charge_categories", ["name", "parent_id"])
    op.create_unique_constraint("uq_statutory_provision_name", "statutory_provision", ["title"])
    op.create_unique_constraint("uq_instruments_name", "instruments", ["name"])

    op.create_index('ix_charge_categories_name', 'charge_categories', ['name'])

    op.create_primary_key("pk_charge_categories_stat_provisions",
                          "charge_categories_stat_provisions",
                          ["category_id", "statutory_provision_id"])

    op.create_primary_key("pk_charge_categories_instruments",
                          "charge_categories_instruments",
                          ["category_id", "instruments_id"])

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON charge_categories TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON charge_categories_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON instruments TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON instruments_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON charge_categories_stat_provisions TO " + current_app.config.get("APP_SQL_USERNAME"))

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON charge_categories_instruments TO " + current_app.config.get("APP_SQL_USERNAME"))

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON statutory_provision TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_column('statutory_provision', 'selectable')

    op.drop_constraint('uq_category_name_parent', 'charge_categories')
    op.drop_constraint('uq_statutory_provision_name', 'statutory_provision')
    op.drop_constraint('uq_instruments_name', 'instruments')
    op.drop_index('ix_charge_categories_name')
    op.drop_table('charge_categories_instruments')
    op.drop_table('charge_categories_stat_provisions')
    op.drop_table('instruments')
    op.drop_table('charge_categories')
