from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional, Any

from .event import TagResponse, StandardBrief, EventResponse


# --- Harvest Batch schemas ---

class HarvestBatchCreate(BaseModel):
    topic_id: UUID
    source_name: str
    source_url: Optional[str] = None
    strategy: str
    metadata_json: Optional[dict[str, Any]] = None


class HarvestBatchUpdate(BaseModel):
    status: Optional[str] = None
    event_count: Optional[int] = None
    metadata_json: Optional[dict[str, Any]] = None


class HarvestBatchResponse(BaseModel):
    id: UUID
    topic_id: UUID
    source_name: str
    source_url: Optional[str] = None
    strategy: str
    event_count: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata_json: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


# --- Candidate Event schemas ---

class CandidateEventCreate(BaseModel):
    topic_id: UUID
    title: str
    description: str
    date_start: date
    date_end: Optional[date] = None
    date_display: str
    date_precision: str = "day"
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    significance: Optional[str] = None
    source_url: Optional[str] = None
    source_citation: Optional[str] = None
    image_url: Optional[str] = None
    existing_event_id: Optional[UUID] = None
    source_name: Optional[str] = None
    harvest_batch_id: Optional[UUID] = None
    confidence_score: Optional[Decimal] = None
    tag_ids: list[UUID] = []
    standard_ids: list[UUID] = []


class CandidateEventUpdate(BaseModel):
    status: str
    review_notes: Optional[str] = None


class CandidateEventResponse(BaseModel):
    id: UUID
    topic_id: UUID
    title: str
    description: str
    date_start: date
    date_end: Optional[date] = None
    date_display: str
    date_precision: str
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    significance: Optional[str] = None
    source_url: Optional[str] = None
    source_citation: Optional[str] = None
    image_url: Optional[str] = None
    existing_event_id: Optional[UUID] = None
    status: str
    source_name: Optional[str] = None
    harvest_batch_id: Optional[UUID] = None
    confidence_score: Optional[Decimal] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[UUID] = None
    created_at: datetime
    tags: list[TagResponse] = []
    standards: list[StandardBrief] = []

    class Config:
        from_attributes = True


class CandidateEventDetail(CandidateEventResponse):
    existing_event: Optional[EventResponse] = None


class CandidateBatchCreate(BaseModel):
    batch_id: Optional[UUID] = None
    candidates: list[CandidateEventCreate]
