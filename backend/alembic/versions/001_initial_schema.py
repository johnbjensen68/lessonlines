"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Curriculum frameworks table
    op.create_table(
        'curriculum_frameworks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('state', sa.String(50), nullable=True),
        sa.Column('subject', sa.String(100), nullable=True),
        sa.Column('grade_levels', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('is_pro', sa.Boolean(), nullable=True, default=False),
        sa.Column('pro_purchased_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Curriculum standards table
    op.create_table(
        'curriculum_standards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('framework_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('grade_level', sa.String(20), nullable=True),
        sa.Column('strand', sa.String(255), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['framework_id'], ['curriculum_frameworks.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['curriculum_standards.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date_start', sa.Date(), nullable=False),
        sa.Column('date_end', sa.Date(), nullable=True),
        sa.Column('date_display', sa.String(100), nullable=False),
        sa.Column('date_precision', sa.String(20), nullable=True, default='day'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('significance', sa.Text(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_citation', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_events_topic', 'events', ['topic_id'])
    op.create_index('idx_events_date', 'events', ['date_start'])

    # Timelines table
    op.create_table(
        'timelines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('color_scheme', sa.String(50), nullable=True, default='blue_green'),
        sa.Column('layout', sa.String(20), nullable=True, default='horizontal'),
        sa.Column('font', sa.String(50), nullable=True, default='system'),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_timelines_user', 'timelines', ['user_id'])

    # Event tags junction table
    op.create_table(
        'event_tags',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'tag_id')
    )

    # Event standards junction table
    op.create_table(
        'event_standards',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('standard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alignment_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['standard_id'], ['curriculum_standards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'standard_id')
    )

    # Timeline events table
    op.create_table(
        'timeline_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timeline_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('custom_title', sa.String(500), nullable=True),
        sa.Column('custom_description', sa.Text(), nullable=True),
        sa.Column('custom_date_display', sa.String(100), nullable=True),
        sa.Column('custom_date_start', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['timeline_id'], ['timelines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('timeline_id', 'position', name='uq_timeline_position')
    )
    op.create_index('idx_timeline_events_timeline', 'timeline_events', ['timeline_id'])


def downgrade() -> None:
    op.drop_table('timeline_events')
    op.drop_table('event_standards')
    op.drop_table('event_tags')
    op.drop_table('timelines')
    op.drop_table('events')
    op.drop_table('curriculum_standards')
    op.drop_table('users')
    op.drop_table('curriculum_frameworks')
    op.drop_table('tags')
    op.drop_table('topics')
