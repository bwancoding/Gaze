"""phase1_data_model_refactor

Revision ID: 2a10363ec8d7
Revises:
Create Date: 2026-03-16 18:57:13.426110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a10363ec8d7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new tables: event_analyses, threads
    op.create_table('event_analyses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('cause_chain', sa.Text(), nullable=True),
        sa.Column('impact_analysis', sa.Text(), nullable=True),
        sa.Column('timeline', sa.Text(), nullable=True),
        sa.Column('stakeholder_perspectives', sa.Text(), nullable=True),
        sa.Column('disputed_claims', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=True),
        sa.Column('quality_score', sa.DECIMAL(3, 2), nullable=True),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
    )

    op.create_table('threads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('user_persona_id', sa.String(36), sa.ForeignKey('user_personas.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), default=False),
        sa.Column('is_locked', sa.Boolean(), default=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('reply_count', sa.Integer(), default=0),
        sa.Column('like_count', sa.Integer(), default=0),
        sa.Column('stakeholder_filter_tag', sa.String(36), sa.ForeignKey('stakeholders.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Add thread_id to comments
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thread_id', sa.String(36), nullable=True))
        batch_op.create_index('ix_comments_thread_id', ['thread_id'], unique=False)
        batch_op.create_foreign_key('fk_comments_thread_id', 'threads', ['thread_id'], ['id'], ondelete='CASCADE')

    # Add new fields to events
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('background', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('cause_chain', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('impact_analysis', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('timeline_data', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('stakeholder_perspectives', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('source_article_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('trending_origin_id', sa.Integer(), sa.ForeignKey('trending_events.id', ondelete='SET NULL'), nullable=True))

    # Add new fields to event_stakeholders
    with op.batch_alter_table('event_stakeholders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('perspective_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('key_concerns', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_ai_generated', sa.Boolean(), nullable=True))

    # Add status to trending_events
    with op.batch_alter_table('trending_events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(20), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('trending_events', schema=None) as batch_op:
        batch_op.drop_column('status')

    with op.batch_alter_table('event_stakeholders', schema=None) as batch_op:
        batch_op.drop_column('is_ai_generated')
        batch_op.drop_column('key_concerns')
        batch_op.drop_column('perspective_summary')

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_column('trending_origin_id')
        batch_op.drop_column('source_article_count')
        batch_op.drop_column('stakeholder_perspectives')
        batch_op.drop_column('timeline_data')
        batch_op.drop_column('impact_analysis')
        batch_op.drop_column('cause_chain')
        batch_op.drop_column('background')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comments_thread_id', type_='foreignkey')
        batch_op.drop_index('ix_comments_thread_id')
        batch_op.drop_column('thread_id')

    op.drop_table('threads')
    op.drop_table('event_analyses')
