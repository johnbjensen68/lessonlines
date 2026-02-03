from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import CurriculumFramework, CurriculumStandard
from ..schemas import CurriculumFrameworkResponse, CurriculumStandardResponse

router = APIRouter(prefix="/api/standards", tags=["standards"])


@router.get("/frameworks", response_model=list[CurriculumFrameworkResponse])
def get_frameworks(db: Session = Depends(get_db)):
    frameworks = db.query(CurriculumFramework).order_by(CurriculumFramework.name).all()
    return frameworks


@router.get("", response_model=list[CurriculumStandardResponse])
def search_standards(
    framework: Optional[str] = Query(None, description="Filter by framework code"),
    grade: Optional[str] = Query(None, description="Filter by grade level"),
    q: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    query = db.query(CurriculumStandard).options(joinedload(CurriculumStandard.framework))

    if framework:
        query = query.join(CurriculumFramework).filter(CurriculumFramework.code == framework)

    if grade:
        query = query.filter(CurriculumStandard.grade_level == grade)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (CurriculumStandard.title.ilike(search_term)) |
            (CurriculumStandard.description.ilike(search_term)) |
            (CurriculumStandard.code.ilike(search_term))
        )

    standards = query.order_by(CurriculumStandard.code).all()

    return [
        {
            "id": s.id,
            "code": s.code,
            "title": s.title,
            "description": s.description,
            "grade_level": s.grade_level,
            "strand": s.strand,
            "framework_code": s.framework.code,
        }
        for s in standards
    ]


@router.get("/{standard_id}", response_model=CurriculumStandardResponse)
def get_standard(standard_id: UUID, db: Session = Depends(get_db)):
    standard = db.query(CurriculumStandard).options(
        joinedload(CurriculumStandard.framework)
    ).filter(CurriculumStandard.id == standard_id).first()

    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")

    return {
        "id": standard.id,
        "code": standard.code,
        "title": standard.title,
        "description": standard.description,
        "grade_level": standard.grade_level,
        "strand": standard.strand,
        "framework_code": standard.framework.code,
    }
