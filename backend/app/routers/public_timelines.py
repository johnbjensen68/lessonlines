from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Timeline, TimelineEvent, Event
from ..schemas import PublicTimelineResponse
from .timelines import get_timeline_response

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/timelines/{timeline_id}", response_model=PublicTimelineResponse)
def get_public_timeline(
    timeline_id: UUID,
    db: Session = Depends(get_db),
):
    timeline = db.query(Timeline).filter(
        Timeline.id == timeline_id,
        Timeline.is_public == True,
    ).options(
        joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
    ).first()

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found or not public")

    return get_timeline_response(timeline)
