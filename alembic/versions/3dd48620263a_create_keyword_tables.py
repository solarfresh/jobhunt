"""create keyword tables

Revision ID: 3dd48620263a
Revises: 
Create Date: 2020-10-09 22:13:59.607194

"""
from alembic import op
import sqlalchemy as sa


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
        sa.PrimaryKeyConstraint('keyword_id')
    )
    op.create_table(
        'kw_search_relation',
        sa.Column('kw_search_relation_id', sa.Integer, primary_key=True),
        sa.Column('keyword_id', sa.Integer, nullable=False),
        sa.Column('searched_keyword_id', sa.Integer),
        sa.PrimaryKeyConstraint('kw_search_relation_id')
    )


def downgrade():
    op.drop_table('keyword')
    op.drop_table('kw_search_relation')
