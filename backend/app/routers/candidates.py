from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import (
    CandidateEvent,
    CandidateStatus,
    HarvestBatch,
    HarvestBatchStatus,
    Tag,
    CurriculumStandard,
    Topic,
    User,
)
from ..schemas import (
    CandidateEventCreate,
    CandidateEventUpdate,
    CandidateEventResponse,
    CandidateEventDetail,
    CandidateBatchCreate,
    HarvestBatchCreate,
    HarvestBatchUpdate,
    HarvestBatchResponse,
)
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


# --- Candidate Event endpoints ---

@router.get("/candidates", response_model=list[CandidateEventResponse])
def list_candidates(
    status: Optional[str] = Query("pending", description="Filter by status"),
    topic: Optional[str] = Query(None, description="Filter by topic slug"),
    source_name: Optional[str] = Query(None, description="Filter by source name"),
    harvest_batch_id: Optional[UUID] = Query(None, description="Filter by harvest batch"),
    has_existing_event: Optional[bool] = Query(None, description="Filter proposed changes"),
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(CandidateEvent).options(
        joinedload(CandidateEvent.tags),
        joinedload(CandidateEvent.standards),
    )

    if status:
        query = query.filter(CandidateEvent.status == status)

    if topic:
        topic_obj = db.query(Topic).filter(Topic.slug == topic).first()
        if topic_obj:
            query = query.filter(CandidateEvent.topic_id == topic_obj.id)

    if source_name:
        query = query.filter(CandidateEvent.source_name == source_name)

    if harvest_batch_id:
        query = query.filter(CandidateEvent.harvest_batch_id == harvest_batch_id)

    if has_existing_event is True:
        query = query.filter(CandidateEvent.existing_event_id.isnot(None))
    elif has_existing_event is False:
        query = query.filter(CandidateEvent.existing_event_id.is_(None))

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (CandidateEvent.title.ilike(search_term)) | (CandidateEvent.description.ilike(search_term))
        )

    candidates = query.order_by(CandidateEvent.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for c in candidates:
        results.append(_candidate_to_response(c, db))
    return results


@router.get("/candidates/{candidate_id}", response_model=CandidateEventDetail)
def get_candidate(
    candidate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = db.query(CandidateEvent).options(
        joinedload(CandidateEvent.tags),
        joinedload(CandidateEvent.standards),
        joinedload(CandidateEvent.existing_event),
    ).filter(CandidateEvent.id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate event not found")

    response = _candidate_to_response(c=candidate, db=db)

    # Build existing_event detail if present
    existing_event = None
    if candidate.existing_event:
        ev = candidate.existing_event
        existing_event = {
            "id": ev.id,
            "topic_id": ev.topic_id,
            "title": ev.title,
            "description": ev.description,
            "date_start": ev.date_start,
            "date_end": ev.date_end,
            "date_display": ev.date_display,
            "date_precision": ev.date_precision,
            "location": ev.location,
            "significance": ev.significance,
            "source_url": ev.source_url,
            "source_citation": ev.source_citation,
            "image_url": ev.image_url,
            "tags": ev.tags if hasattr(ev, 'tags') else [],
            "standards": [],
            "created_at": ev.created_at,
        }
    response["existing_event"] = existing_event

    return response


@router.post("/candidates", response_model=CandidateEventResponse, status_code=201)
def create_candidate(
    data: CandidateEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = _create_candidate_from_data(data, db)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return _candidate_to_response(candidate, db)


@router.post("/candidates/batch", response_model=list[CandidateEventResponse], status_code=201)
def create_candidates_batch(
    data: CandidateBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidates = []
    for item in data.candidates:
        if data.batch_id and not item.harvest_batch_id:
            item.harvest_batch_id = data.batch_id
        candidate = _create_candidate_from_data(item, db)
        db.add(candidate)
        candidates.append(candidate)

    db.commit()

    # Update harvest batch event_count if batch_id provided
    if data.batch_id:
        batch = db.query(HarvestBatch).filter(HarvestBatch.id == data.batch_id).first()
        if batch:
            batch.event_count = (batch.event_count or 0) + len(candidates)
            db.commit()

    for c in candidates:
        db.refresh(c)

    return [_candidate_to_response(c, db) for c in candidates]


@router.patch("/candidates/{candidate_id}", response_model=CandidateEventResponse)
def review_candidate(
    candidate_id: UUID,
    data: CandidateEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidate = db.query(CandidateEvent).filter(CandidateEvent.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate event not found")

    candidate.status = data.status
    if data.review_notes is not None:
        candidate.review_notes = data.review_notes
    candidate.reviewed_at = datetime.now(timezone.utc)
    candidate.reviewed_by = current_user.id

    db.commit()
    db.refresh(candidate)
    return _candidate_to_response(candidate, db)


# --- Harvest Batch endpoints ---

@router.get("/harvest-batches", response_model=list[HarvestBatchResponse])
def list_harvest_batches(
    topic: Optional[str] = Query(None, description="Filter by topic slug"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(HarvestBatch)

    if topic:
        topic_obj = db.query(Topic).filter(Topic.slug == topic).first()
        if topic_obj:
            query = query.filter(HarvestBatch.topic_id == topic_obj.id)

    if status:
        query = query.filter(HarvestBatch.status == status)

    return query.order_by(HarvestBatch.started_at.desc()).offset(offset).limit(limit).all()


@router.post("/harvest-batches", response_model=HarvestBatchResponse, status_code=201)
def create_harvest_batch(
    data: HarvestBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    batch = HarvestBatch(
        topic_id=data.topic_id,
        source_name=data.source_name,
        source_url=data.source_url,
        strategy=data.strategy,
        status=HarvestBatchStatus.running.value,
        event_count=0,
        metadata_json=data.metadata_json,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.patch("/harvest-batches/{batch_id}", response_model=HarvestBatchResponse)
def update_harvest_batch(
    batch_id: UUID,
    data: HarvestBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    batch = db.query(HarvestBatch).filter(HarvestBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Harvest batch not found")

    if data.status is not None:
        batch.status = data.status
        if data.status in (HarvestBatchStatus.completed.value, HarvestBatchStatus.failed.value):
            batch.completed_at = datetime.now(timezone.utc)

    if data.event_count is not None:
        batch.event_count = data.event_count

    if data.metadata_json is not None:
        batch.metadata_json = data.metadata_json

    db.commit()
    db.refresh(batch)
    return batch


# --- Helpers ---

def _create_candidate_from_data(data: CandidateEventCreate, db: Session) -> CandidateEvent:
    candidate = CandidateEvent(
        topic_id=data.topic_id,
        title=data.title,
        description=data.description,
        date_start=data.date_start,
        date_end=data.date_end,
        date_display=data.date_display,
        date_precision=data.date_precision,
        location=data.location,
        latitude=data.latitude,
        longitude=data.longitude,
        significance=data.significance,
        source_url=data.source_url,
        source_citation=data.source_citation,
        image_url=data.image_url,
        existing_event_id=data.existing_event_id,
        source_name=data.source_name,
        harvest_batch_id=data.harvest_batch_id,
        confidence_score=data.confidence_score,
        status=CandidateStatus.pending.value,
    )

    if data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        candidate.tags = tags

    if data.standard_ids:
        standards = db.query(CurriculumStandard).filter(CurriculumStandard.id.in_(data.standard_ids)).all()
        candidate.standards = standards

    return candidate


def _candidate_to_response(c: CandidateEvent, db: Session) -> dict:
    standards_data = []
    for s in c.standards:
        framework = s.framework
        standards_data.append({
            "id": s.id,
            "code": s.code,
            "title": s.title,
            "framework_code": framework.code if framework else "",
            "grade_level": s.grade_level,
        })

    return {
        "id": c.id,
        "topic_id": c.topic_id,
        "title": c.title,
        "description": c.description,
        "date_start": c.date_start,
        "date_end": c.date_end,
        "date_display": c.date_display,
        "date_precision": c.date_precision,
        "location": c.location,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "significance": c.significance,
        "source_url": c.source_url,
        "source_citation": c.source_citation,
        "image_url": c.image_url,
        "existing_event_id": c.existing_event_id,
        "status": c.status,
        "source_name": c.source_name,
        "harvest_batch_id": c.harvest_batch_id,
        "confidence_score": c.confidence_score,
        "review_notes": c.review_notes,
        "reviewed_at": c.reviewed_at,
        "reviewed_by": c.reviewed_by,
        "created_at": c.created_at,
        "tags": c.tags,
        "standards": standards_data,
    }
