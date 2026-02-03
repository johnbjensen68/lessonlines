import uuid
from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .base import UUID


class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    subtitle = Column(String(500))
    color_scheme = Column(String(50), default="blue_green")
    layout = Column(String(20), default="horizontal")
    font = Column(String(50), default="system")
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="timelines")
    events = relationship("TimelineEvent", back_populates="timeline", cascade="all, delete-orphan", order_by="TimelineEvent.position")

    __table_args__ = (
        Index("idx_timelines_user", "user_id"),
    )


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    timeline_id = Column(UUID(), ForeignKey("timelines.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(UUID(), ForeignKey("events.id", ondelete="SET NULL"))
    position = Column(Integer, nullable=False)
    custom_title = Column(String(500))
    custom_description = Column(Text)
    custom_date_display = Column(String(100))
    custom_date_start = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    timeline = relationship("Timeline", back_populates="events")
    event = relationship("Event")

    __table_args__ = (
        UniqueConstraint("timeline_id", "position", name="uq_timeline_position"),
        Index("idx_timeline_events_timeline", "timeline_id"),
    )
