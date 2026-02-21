import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, Date, DateTime, Numeric, ForeignKey, Index, Table, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .base import UUID


class HarvestBatchStatus(str, PyEnum):
    running = "running"
    completed = "completed"
    failed = "failed"


class CandidateStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


candidate_event_tags = Table(
    "candidate_event_tags",
    Base.metadata,
    Column("candidate_event_id", UUID(), ForeignKey("candidate_events.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


candidate_event_standards = Table(
    "candidate_event_standards",
    Base.metadata,
    Column("candidate_event_id", UUID(), ForeignKey("candidate_events.id", ondelete="CASCADE"), primary_key=True),
    Column("standard_id", UUID(), ForeignKey("curriculum_standards.id", ondelete="CASCADE"), primary_key=True),
    Column("alignment_notes", Text),
)


class HarvestBatch(Base):
    __tablename__ = "harvest_batches"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(), ForeignKey("topics.id"), nullable=False)
    source_name = Column(String(255), nullable=False)
    source_url = Column(Text)
    strategy = Column(String(100), nullable=False)
    event_count = Column(Integer, default=0)
    status = Column(String(20), nullable=False, default=HarvestBatchStatus.running.value)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    metadata_json = Column(JSON)

    topic = relationship("Topic")
    candidates = relationship("CandidateEvent", back_populates="harvest_batch")


class CandidateEvent(Base):
    __tablename__ = "candidate_events"

    # Mirror of Event columns
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(), ForeignKey("topics.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date)
    date_display = Column(String(100), nullable=False)
    date_precision = Column(String(20), default="day")
    location = Column(String(255))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    significance = Column(Text)
    source_url = Column(Text)
    source_citation = Column(Text)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Candidate-specific columns
    existing_event_id = Column(UUID(), ForeignKey("events.id"))
    status = Column(String(20), nullable=False, default=CandidateStatus.pending.value)
    source_name = Column(String(255))
    harvest_batch_id = Column(UUID(), ForeignKey("harvest_batches.id"))
    confidence_score = Column(Numeric(3, 2))
    review_notes = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(UUID(), ForeignKey("users.id"))

    topic = relationship("Topic")
    existing_event = relationship("Event")
    harvest_batch = relationship("HarvestBatch", back_populates="candidates")
    reviewer = relationship("User")
    tags = relationship("Tag", secondary=candidate_event_tags)
    standards = relationship("CurriculumStandard", secondary=candidate_event_standards)

    __table_args__ = (
        Index("idx_candidate_events_status", "status"),
        Index("idx_candidate_events_topic", "topic_id"),
        Index("idx_candidate_events_batch", "harvest_batch_id"),
        Index("idx_candidate_events_existing", "existing_event_id"),
    )
