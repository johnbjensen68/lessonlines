import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .base import UUID
from .tag import event_tags
from .standard import event_standards


class Event(Base):
    __tablename__ = "events"

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

    topic = relationship("Topic", back_populates="events")
    tags = relationship("Tag", secondary=event_tags, back_populates="events")
    standards = relationship("CurriculumStandard", secondary=event_standards, back_populates="events")

    __table_args__ = (
        Index("idx_events_topic", "topic_id"),
        Index("idx_events_date", "date_start"),
    )
