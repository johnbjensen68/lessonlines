from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from .event import EventListResponse


class TimelineSettings(BaseModel):
    color_scheme: Optional[str] = None
    layout: Optional[str] = None
    font: Optional[str] = None


class TimelineEventCreate(BaseModel):
    event_id: Optional[UUID] = None
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    custom_date_display: Optional[str] = None
    custom_date_start: Optional[date] = None


class TimelineEventResponse(BaseModel):
    id: UUID
    timeline_id: UUID
    event_id: Optional[UUID] = None
    position: int
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    custom_date_display: Optional[str] = None
    custom_date_start: Optional[date] = None
    event: Optional[EventListResponse] = None

    class Config:
        from_attributes = True


class TimelineCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    color_scheme: Optional[str] = "blue_green"
    layout: Optional[str] = "horizontal"
    font: Optional[str] = "system"


class TimelineUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    color_scheme: Optional[str] = None
    layout: Optional[str] = None
    font: Optional[str] = None


class TimelineResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    subtitle: Optional[str] = None
    color_scheme: str
    layout: str
    font: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    events: list[TimelineEventResponse] = []

    class Config:
        from_attributes = True


class ReorderRequest(BaseModel):
    positions: list[UUID]
