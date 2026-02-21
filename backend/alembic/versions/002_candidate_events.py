"""Candidate events and harvest batches

Revision ID: 002_candidate_events
Revises: 001_initial
Create Date: 2026-02-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_candidate_events'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Harvest batches table
    op.create_table(
        'harvest_batches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('topic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_name', sa.String(255), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('strategy', sa.String(100), nullable=False),
        sa.Column('event_count', sa.Integer(), nullable=True, default=0),
        sa.Column('status', sa.String(20), nullable=False, default='running'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Candidate events table
    op.create_table(
        'candidate_events',
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
        sa.Column('existing_event_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('source_name', sa.String(255), nullable=True),
        sa.Column('harvest_batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id']),
        sa.ForeignKeyConstraint(['existing_event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['harvest_batch_id'], ['harvest_batches.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_candidate_events_status', 'candidate_events', ['status'])
    op.create_index('idx_candidate_events_topic', 'candidate_events', ['topic_id'])
    op.create_index('idx_candidate_events_batch', 'candidate_events', ['harvest_batch_id'])
    op.create_index('idx_candidate_events_existing', 'candidate_events', ['existing_event_id'])

    # Candidate event tags junction table
    op.create_table(
        'candidate_event_tags',
        sa.Column('candidate_event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_event_id'], ['candidate_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('candidate_event_id', 'tag_id')
    )

    # Candidate event standards junction table
    op.create_table(
        'candidate_event_standards',
        sa.Column('candidate_event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('standard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alignment_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_event_id'], ['candidate_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['standard_id'], ['curriculum_standards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('candidate_event_id', 'standard_id')
    )


def downgrade() -> None:
    op.drop_table('candidate_event_standards')
    op.drop_table('candidate_event_tags')
    op.drop_index('idx_candidate_events_existing', 'candidate_events')
    op.drop_index('idx_candidate_events_batch', 'candidate_events')
    op.drop_index('idx_candidate_events_topic', 'candidate_events')
    op.drop_index('idx_candidate_events_status', 'candidate_events')
    op.drop_table('candidate_events')
    op.drop_table('harvest_batches')
