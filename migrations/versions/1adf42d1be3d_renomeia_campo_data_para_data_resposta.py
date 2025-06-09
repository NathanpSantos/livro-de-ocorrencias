"""Renomeia campo data para data_resposta

Revision ID: 1adf42d1be3d
Revises: a836883d7859
Create Date: 2025-06-08 21:34:25.779164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1adf42d1be3d'
down_revision = 'a836883d7859'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('historico', schema=None) as batch_op:
        batch_op.alter_column('data', new_column_name='data_resposta')


    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('historico', schema=None) as batch_op:
        batch_op.alter_column('data_resposta', new_column_name='data')


    # ### end Alembic commands ###
