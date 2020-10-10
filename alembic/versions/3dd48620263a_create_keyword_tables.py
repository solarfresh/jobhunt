"""create keyword tables

Revision ID: 3dd48620263a
Revises: 
Create Date: 2020-10-09 22:13:59.607194

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.schema import (Sequence, CreateSequence, DropSequence)

# revision identifiers, used by Alembic.
revision = '3dd48620263a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'keyword',
        sa.Column('keyword_id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('keyword', sa.String(32), nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('keyword_id')
    )
    op.create_table(
        'kw_search_relation',
        sa.Column('kw_search_relation_id', sa.Integer, primary_key=True),
        sa.Column('keyword_id', sa.Integer, nullable=False),
        sa.Column('searched_keyword_id', sa.Integer),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('kw_search_relation_id')
    )
    op.execute(CreateSequence(Sequence('kw_id_seq')))
    op.execute(CreateSequence(Sequence('kw_search_relation_id_seq')))


def downgrade():
    op.drop_table('keyword')
    op.drop_table('kw_search_relation')
    op.execute(DropSequence(Sequence('kw_id_seq')))
    op.execute(DropSequence(Sequence('kw_search_relation_id_seq')))
