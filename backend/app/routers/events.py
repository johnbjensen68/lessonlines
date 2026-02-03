from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Topic, Event, Tag, CurriculumStandard
from ..schemas import TopicResponse, EventListResponse, EventResponse, TagResponse

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/topics", response_model=list[TopicResponse])
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).order_by(Topic.name).all()
    return topics


@router.get("/tags", response_model=list[TagResponse])
def get_tags(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    return query.order_by(Tag.name).all()


@router.get("/events", response_model=list[EventListResponse])
def search_events(
    topic: Optional[str] = Query(None, description="Filter by topic slug"),
    q: Optional[str] = Query(None, description="Search query"),
    standard: Optional[UUID] = Query(None, description="Filter by standard ID"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    grade: Optional[str] = Query(None, description="Filter by grade level"),
    db: Session = Depends(get_db)
):
    query = db.query(Event).options(joinedload(Event.tags))

    if topic:
        topic_obj = db.query(Topic).filter(Topic.slug == topic).first()
        if topic_obj:
            query = query.filter(Event.topic_id == topic_obj.id)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (Event.title.ilike(search_term)) | (Event.description.ilike(search_term))
        )

    if standard:
        query = query.join(Event.standards).filter(CurriculumStandard.id == standard)

    if tag:
        query = query.join(Event.tags).filter(Tag.name == tag)

    if grade:
        query = query.join(Event.standards).filter(CurriculumStandard.grade_level == grade)

    events = query.order_by(Event.date_start).all()
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    event = db.query(Event).options(
        joinedload(Event.tags),
        joinedload(Event.standards).joinedload(CurriculumStandard.framework)
    ).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Transform standards to include framework_code
    response_data = {
        "id": event.id,
        "topic_id": event.topic_id,
        "title": event.title,
        "description": event.description,
        "date_start": event.date_start,
        "date_end": event.date_end,
        "date_display": event.date_display,
        "date_precision": event.date_precision,
        "location": event.location,
        "significance": event.significance,
        "source_url": event.source_url,
        "source_citation": event.source_citation,
        "image_url": event.image_url,
        "tags": event.tags,
        "standards": [
            {
                "id": s.id,
                "code": s.code,
                "title": s.title,
                "framework_code": s.framework.code,
                "grade_level": s.grade_level,
            }
            for s in event.standards
        ],
        "created_at": event.created_at,
    }

    return response_data
