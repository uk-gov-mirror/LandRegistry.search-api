"""Modify celery result table

Revision ID: d3c6b3a21f31
Revises: 57f62bc56625
Create Date: 2023-08-23 16:17:22.305708

"""

# revision identifiers, used by Alembic.
revision = 'd3c6b3a21f31'
down_revision = '57f62bc56625'

import json
import pickle
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text


def upgrade():
    op.add_column('celery_taskmeta', sa.Column('result_json', postgresql.JSONB()))
    conn = op.get_bind()
    res = conn.execute(text("select id, result from celery_taskmeta;"))
    results = res.fetchall()
    for row in results:
        result_dict = pickle.loads(row[1].tobytes() if row[1] else "{}")
        conn.execute(text("UPDATE celery_taskmeta SET result_json = :result_json WHERE id = :row_id;"),
                     {"result_json": json.dumps(result_dict), "row_id": row[0]})
    op.drop_column('celery_taskmeta', 'result')
    op.alter_column('celery_taskmeta', 'result_json', new_column_name='result')


def downgrade():
    op.add_column('celery_taskmeta', sa.Column('result_bin', sa.LargeBinary()))
    conn = op.get_bind()
    res = conn.execute(text("SELECT id, result FROM celery_taskmeta;"))
    results = res.fetchall()
    for row in results:
        result_dict = row[1] if row[1] else {}
        conn.execute(text("UPDATE celery_taskmeta SET result_bin = :result_bin WHERE id = :row_id;"),
                     {"result_bin": pickle.dumps(result_dict), "row_id": row[0]})
    op.drop_column('celery_taskmeta', 'result')
    op.alter_column('celery_taskmeta', 'result_bin', new_column_name='result')
