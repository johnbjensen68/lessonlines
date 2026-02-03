import uuid
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .base import UUID


event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", UUID(), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))

    events = relationship("Event", secondary=event_tags, back_populates="tags")
