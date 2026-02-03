from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import User, Timeline, TimelineEvent, Event
from ..schemas import (
    TimelineCreate,
    TimelineUpdate,
    TimelineResponse,
    TimelineEventCreate,
    TimelineEventResponse,
    ReorderRequest,
)
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/timelines", tags=["timelines"])


def get_timeline_response(timeline: Timeline) -> dict:
    """Convert timeline to response format with event details."""
    events = []
    for te in timeline.events:
        event_data = {
            "id": te.id,
            "timeline_id": te.timeline_id,
            "event_id": te.event_id,
            "position": te.position,
            "custom_title": te.custom_title,
            "custom_description": te.custom_description,
            "custom_date_display": te.custom_date_display,
            "custom_date_start": te.custom_date_start,
            "event": None,
        }
        if te.event:
            event_data["event"] = {
                "id": te.event.id,
                "title": te.event.title,
                "description": te.event.description,
                "date_display": te.event.date_display,
                "location": te.event.location,
                "tags": [{"id": t.id, "name": t.name, "category": t.category} for t in te.event.tags],
            }
        events.append(event_data)

    return {
        "id": timeline.id,
        "user_id": timeline.user_id,
        "title": timeline.title,
        "subtitle": timeline.subtitle,
        "color_scheme": timeline.color_scheme,
        "layout": timeline.layout,
        "font": timeline.font,
        "is_public": timeline.is_public,
        "created_at": timeline.created_at,
        "updated_at": timeline.updated_at,
        "events": events,
    }


@router.get("", response_model=list[TimelineResponse])
def get_user_timelines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timelines = db.query(Timeline).filter(
        Timeline.user_id == current_user.id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).order_by(Timeline.updated_at.desc()).all()

    return [get_timeline_response(t) for t in timelines]


@router.post("", response_model=TimelineResponse)
def create_timeline(
    data: TimelineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = Timeline(
        user_id=current_user.id,
        title=data.title,
        subtitle=data.subtitle,
        color_scheme=data.color_scheme or "blue_green",
        layout=data.layout or "horizontal",
        font=data.font or "system",
    )
    db.add(timeline)
    db.commit()
    db.refresh(timeline)

    return get_timeline_response(timeline)


@router.get("/{timeline_id}", response_model=TimelineResponse)
def get_timeline(
    timeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    return get_timeline_response(timeline)


@router.put("/{timeline_id}", response_model=TimelineResponse)
def update_timeline(
    timeline_id: UUID,
    data: TimelineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    if data.title is not None:
        timeline.title = data.title
    if data.subtitle is not None:
        timeline.subtitle = data.subtitle
    if data.color_scheme is not None:
        timeline.color_scheme = data.color_scheme
    if data.layout is not None:
        timeline.layout = data.layout
    if data.font is not None:
        timeline.font = data.font

    db.commit()
    db.refresh(timeline)

    # Reload with relationships
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    return get_timeline_response(timeline)


@router.delete("/{timeline_id}")
def delete_timeline(
    timeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    db.delete(timeline)
    db.commit()

    return {"status": "deleted"}


@router.post("/{timeline_id}/events", response_model=TimelineResponse)
def add_event_to_timeline(
    timeline_id: UUID,
    data: TimelineEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    # Get the next position
    max_position = db.query(TimelineEvent).filter(
        TimelineEvent.timeline_id == timeline_id
    ).count()

    timeline_event = TimelineEvent(
        timeline_id=timeline_id,
        event_id=data.event_id,
        position=max_position,
        custom_title=data.custom_title,
        custom_description=data.custom_description,
        custom_date_display=data.custom_date_display,
        custom_date_start=data.custom_date_start,
    )
    db.add(timeline_event)
    db.commit()

    # Reload timeline with relationships
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    return get_timeline_response(timeline)


@router.delete("/{timeline_id}/events/{position}", response_model=TimelineResponse)
def remove_event_from_timeline(
    timeline_id: UUID,
    position: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    timeline_event = db.query(TimelineEvent).filter(
        TimelineEvent.timeline_id == timeline_id,
        TimelineEvent.position == position
    ).first()

    if not timeline_event:
        raise HTTPException(status_code=404, detail="Event not found at this position")

    db.delete(timeline_event)

    # Reorder remaining events
    remaining_events = db.query(TimelineEvent).filter(
        TimelineEvent.timeline_id == timeline_id,
        TimelineEvent.position > position
    ).order_by(TimelineEvent.position).all()

    for event in remaining_events:
        event.position -= 1

    db.commit()

    # Reload timeline with relationships
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    return get_timeline_response(timeline)


@router.put("/{timeline_id}/events/reorder", response_model=TimelineResponse)
def reorder_timeline_events(
    timeline_id: UUID,
    data: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.user_id == current_user.id
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    # Update positions based on the order in the request
    for new_position, event_id in enumerate(data.positions):
        timeline_event = db.query(TimelineEvent).filter(
            TimelineEvent.timeline_id == timeline_id,
            TimelineEvent.id == event_id
        ).first()
        if timeline_event:
            timeline_event.position = new_position

    db.commit()

    # Reload timeline with relationships
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    return get_timeline_response(timeline)
