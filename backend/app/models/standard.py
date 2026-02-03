import uuid
from sqlalchemy import Column, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .base import UUID


event_standards = Table(
    "event_standards",
    Base.metadata,
    Column("event_id", UUID(), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("standard_id", UUID(), ForeignKey("curriculum_standards.id", ondelete="CASCADE"), primary_key=True),
    Column("alignment_notes", Text),
)


class CurriculumFramework(Base):
    __tablename__ = "curriculum_frameworks"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    state = Column(String(50))
    subject = Column(String(100))
    grade_levels = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    standards = relationship("CurriculumStandard", back_populates="framework")


class CurriculumStandard(Base):
    __tablename__ = "curriculum_standards"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    framework_id = Column(UUID(), ForeignKey("curriculum_frameworks.id"), nullable=False)
    code = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    grade_level = Column(String(20))
    strand = Column(String(255))
    parent_id = Column(UUID(), ForeignKey("curriculum_standards.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    framework = relationship("CurriculumFramework", back_populates="standards")
    parent = relationship("CurriculumStandard", remote_side=[id], backref="children")
    events = relationship("Event", secondary=event_standards, back_populates="standards")
