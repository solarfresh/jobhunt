"""create joblist tables

Revision ID: fb54aae946ef
Revises: 3dd48620263a
Create Date: 2020-10-10 14:59:59.500046

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import (Sequence, CreateSequence, DropSequence)


# revision identifiers, used by Alembic.
revision = 'fb54aae946ef'
down_revision = '3dd48620263a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'joblist',
        sa.Column('joblist_id', sa.Integer, primary_key=True),
        sa.Column('company_id', sa.BigInteger, nullable=False),
        sa.Column('company_page_link', sa.String),
        sa.Column('indcat_id', sa.Integer),
        sa.Column('indcat_name', sa.String),
        sa.Column('job_area', sa.String),
        sa.Column('job_id', sa.Integer, nullable=False),
        sa.Column('job_page_link', sa.String),
        sa.Column('job_role', sa.Integer),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_id')
    )
    op.create_table(
        'joblist_tmp',
        sa.Column('joblist_tmp_id', sa.Integer, primary_key=True),
        sa.Column('job_id', sa.Integer, nullable=False),
        sa.Column('keyword', sa.String),
        sa.Column('candi_edu', sa.String),
        sa.Column('candi_exp', sa.String),
        sa.Column('job_hot', sa.String),
        sa.Column('job_name', sa.String),
        sa.Column('job_tags', sa.String),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_tmp_id')
    )
    op.create_table(
        'joblist_meta',
        sa.Column('joblist_meta_id', sa.Integer, primary_key=True),
        sa.Column('joblist_id', sa.Integer, nullable=False),
        sa.Column('candi_edu', sa.String),
        sa.Column('candi_exp', sa.String),
        sa.Column('job_hot', sa.String),
        sa.Column('job_name', sa.String),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_meta_id')
    )
    op.create_table(
        'joblist_tag',
        sa.Column('joblist_tag_id', sa.Integer, primary_key=True),
        sa.Column('joblist_id', sa.Integer, nullable=False),
        sa.Column('tag_name', sa.String, nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_tag_id')
    )
    op.create_table(
        'joblist_log',
        sa.Column('joblist_log_id', sa.Integer, primary_key=True),
        sa.Column('joblist_id', sa.Integer, nullable=False),
        sa.Column('is_changed', sa.Integer, nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_log_id')
    )
    op.create_table(
        'joblist_keyword',
        sa.Column('joblist_keyword_id', sa.Integer, primary_key=True),
        sa.Column('joblist_id', sa.Integer, nullable=False),
        sa.Column('keyword_id', sa.Integer, nullable=False),
        sa.Column('create_at', sa.DateTime(), nullable=False),
        sa.Column('update_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('joblist_keyword_id')
    )

    op.execute(CreateSequence(Sequence('joblist_id_seq')))
    op.execute(CreateSequence(Sequence('joblist_tmp_id_seq')))
    op.execute(CreateSequence(Sequence('joblist_meta_id_seq')))
    op.execute(CreateSequence(Sequence('joblist_tag_id_seq')))
    op.execute(CreateSequence(Sequence('joblist_log_id_seq')))
    op.execute(CreateSequence(Sequence('joblist_keyword_id_seq')))


def downgrade():
    op.drop_table('joblist')
    op.drop_table('joblist_tmp')
    op.drop_table('joblist_meta')
    op.drop_table('joblist_tag')
    op.drop_table('joblist_log')
    op.drop_table('joblist_keyword')
    op.execute(DropSequence(Sequence('joblist_id_seq')))
    op.execute(DropSequence(Sequence('joblist_tmp_id_seq')))
    op.execute(DropSequence(Sequence('joblist_meta_id_seq')))
    op.execute(DropSequence(Sequence('joblist_tag_id_seq')))
    op.execute(DropSequence(Sequence('joblist_log_id_seq')))
    op.execute(DropSequence(Sequence('joblist_keyword_id_seq')))
