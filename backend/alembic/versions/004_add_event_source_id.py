"""Add source_id to events

Revision ID: 004_add_event_source_id
Revises: 003_add_is_admin
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '004_add_event_source_id'
down_revision: Union[str, None] = '003_add_is_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('events', sa.Column('source_id', sa.String(100), nullable=True))
    op.create_unique_constraint('uq_events_source_id', 'events', ['source_id'])
    op.create_index('ix_events_source_id', 'events', ['source_id'])


def downgrade() -> None:
    op.drop_index('ix_events_source_id', table_name='events')
    op.drop_constraint('uq_events_source_id', 'events', type_='unique')
    op.drop_column('events', 'source_id')
