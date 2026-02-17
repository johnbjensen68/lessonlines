from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class TopicResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: UUID
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class StandardBrief(BaseModel):
    id: UUID
    code: str
    title: str
    framework_code: str
    grade_level: Optional[str] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    id: UUID
    title: str
    description: str
    date_display: str
    location: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: UUID
    topic_id: UUID
    title: str
    description: str
    date_start: date
    date_end: Optional[date] = None
    date_display: str
    date_precision: str
    location: Optional[str] = None
    significance: Optional[str] = None
    source_url: Optional[str] = None
    source_citation: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[TagResponse] = []
    standards: list[StandardBrief] = []
    created_at: datetime

    class Config:
        from_attributes = True
