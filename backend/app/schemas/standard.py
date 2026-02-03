from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CurriculumFrameworkResponse(BaseModel):
    id: UUID
    code: str
    name: str
    state: Optional[str] = None
    subject: Optional[str] = None
    grade_levels: Optional[str] = None

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


class CurriculumStandardResponse(BaseModel):
    id: UUID
    code: str
    title: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    strand: Optional[str] = None
    framework_code: str

    class Config:
        from_attributes = True
