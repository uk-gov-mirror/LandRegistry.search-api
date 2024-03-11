"""Add celery tables

Revision ID: 7d321428b3de
Revises: 9076f6c94df4
Create Date: 2022-05-05 13:12:52.383386

"""

# revision identifiers, used by Alembic.
revision = '7d321428b3de'
down_revision = '9076f6c94df4'

import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.schema import CreateSequence, DropSequence, Sequence


def upgrade():
    op.execute(CreateSequence(Sequence('task_id_sequence')))
    op.create_table('celery_taskmeta',
                    sa.Column('id', sa.Integer(), sa.Sequence("task_id_sequence"),
                              primary_key=True, autoincrement=True),
                    sa.Column('task_id', sa.String(length=155), unique=True),
                    sa.Column('status', sa.String(length=50)),
                    sa.Column('result', sa.LargeBinary()),
                    sa.Column('date_done', sa.DateTime()),
                    sa.Column('traceback', sa.Text()),
                    sa.Column('name', sa.String(length=155)),
                    sa.Column('args', sa.LargeBinary()),
                    sa.Column('kwargs', sa.LargeBinary()),
                    sa.Column('worker', sa.String(length=155)),
                    sa.Column('retries', sa.Integer()),
                    sa.Column('queue', sa.String(length=155))
                    )

    op.execute(CreateSequence(Sequence('taskset_id_sequence')))
    op.create_table('celery_tasksetmeta',
                    sa.Column('id', sa.Integer(), sa.Sequence("taskset_id_sequence"),
                              primary_key=True, autoincrement=True),
                    sa.Column('taskset_id', sa.String(length=155), unique=True),
                    sa.Column('result', sa.LargeBinary()),
                    sa.Column('date_done', sa.DateTime())
                    )

    op.execute("GRANT ALL ON celery_taskmeta TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON task_id_sequence TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON celery_tasksetmeta TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT ALL ON taskset_id_sequence TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.execute(DropSequence(Sequence('task_id_sequence')))
    op.execute(DropSequence(Sequence('taskset_id_sequence')))
    op.drop_table('celery_taskmeta')
    op.drop_table('celery_tasksetmeta')
