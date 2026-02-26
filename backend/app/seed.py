"""
Database seeding script for LessonLines.
Run with: python -m app.seed
"""
from pathlib import Path
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import (
    Topic,
    Tag,
    CurriculumFramework,
    CurriculumStandard,
)
from .services.import_events import import_all_event_files

EVENT_DATA_DIR = Path(__file__).parent.parent.parent / "event-data"


def seed_tags(db: Session) -> None:
    tags_data = [
        {"name": "military", "category": "theme"},
        {"name": "political", "category": "theme"},
        {"name": "social", "category": "theme"},
        {"name": "economic", "category": "theme"},
        {"name": "diplomatic", "category": "theme"},
        {"name": "cultural", "category": "theme"},
        {"name": "battle", "category": "type"},
        {"name": "treaty", "category": "type"},
        {"name": "declaration", "category": "type"},
        {"name": "legislation", "category": "type"},
        {"name": "assassination", "category": "type"},
    ]
    for data in tags_data:
        if not db.query(Tag).filter_by(name=data["name"]).first():
            db.add(Tag(**data))
    db.flush()


def seed_frameworks(db: Session) -> dict[str, CurriculumFramework]:
    frameworks_data = [
        {
            "code": "CCSS",
            "name": "Common Core State Standards",
            "state": None,
            "subject": "English Language Arts & Literacy in History/Social Studies",
            "grade_levels": "6-12",
        },
        {
            "code": "AP_USH",
            "name": "AP US History",
            "state": None,
            "subject": "History",
            "grade_levels": "9-12",
        },
        {
            "code": "TEKS",
            "name": "Texas Essential Knowledge and Skills",
            "state": "TX",
            "subject": "Social Studies",
            "grade_levels": "K-12",
        },
    ]

    frameworks = {}
    for data in frameworks_data:
        framework = db.query(CurriculumFramework).filter_by(code=data["code"]).first()
        if not framework:
            framework = CurriculumFramework(**data)
            db.add(framework)
            db.flush()
        frameworks[data["code"]] = framework
    return frameworks


def seed_standards(db: Session, frameworks: dict[str, CurriculumFramework]) -> None:
    standards_data = [
        # Common Core
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.6-8.1",
            "title": "Cite specific textual evidence",
            "description": "Cite specific textual evidence to support analysis of primary and secondary sources.",
            "grade_level": "6-8",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.6-8.2",
            "title": "Determine central ideas",
            "description": "Determine the central ideas or information of a primary or secondary source.",
            "grade_level": "6-8",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.9-10.3",
            "title": "Analyze key events",
            "description": "Analyze in detail a series of events described in a text; determine whether earlier events caused later ones.",
            "grade_level": "9-10",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.11-12.7",
            "title": "Integrate multiple sources",
            "description": "Integrate and evaluate multiple sources of information presented in diverse formats.",
            "grade_level": "11-12",
            "strand": "Reading",
        },
        # AP US History
        {
            "framework": "AP_USH",
            "code": "AP.USH.5.1",
            "title": "Slavery and Sectional Conflict",
            "description": "Explain the causes of the Civil War including the expansion of slavery.",
            "grade_level": "HS",
            "strand": "Period 5",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.5.2",
            "title": "The Civil War",
            "description": "Explain how the Civil War was fought and the consequences of the war.",
            "grade_level": "HS",
            "strand": "Period 5",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.3.1",
            "title": "Colonial Independence",
            "description": "Explain the causes of the American Revolution.",
            "grade_level": "HS",
            "strand": "Period 3",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.7.1",
            "title": "World War II",
            "description": "Explain the causes and consequences of American involvement in World War II.",
            "grade_level": "HS",
            "strand": "Period 7",
        },
        # Texas TEKS
        {
            "framework": "TEKS",
            "code": "TEKS.8.1.A",
            "title": "Identify major causes of Civil War",
            "description": "Identify the major eras and events in U.S. history through 1877, including the Civil War.",
            "grade_level": "8",
            "strand": "History",
        },
        {
            "framework": "TEKS",
            "code": "TEKS.8.4.C",
            "title": "Explain American Revolution causes",
            "description": "Explain the issues surrounding important events of the American Revolution.",
            "grade_level": "8",
            "strand": "History",
        },
        {
            "framework": "TEKS",
            "code": "TEKS.US.7.A",
            "title": "WWII causes and effects",
            "description": "Identify reasons for U.S. involvement in World War II.",
            "grade_level": "HS",
            "strand": "History",
        },
    ]

    for data in standards_data:
        framework = frameworks[data.pop("framework")]
        if not db.query(CurriculumStandard).filter_by(code=data["code"]).first():
            db.add(CurriculumStandard(framework_id=framework.id, **data))
    db.flush()


def run_seed():
    """Main seeding function."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Topic).count() > 0:
            print("Database already seeded. Skipping...")
            return

        print("Seeding tags...")
        seed_tags(db)

        print("Seeding curriculum frameworks...")
        frameworks = seed_frameworks(db)

        print("Seeding curriculum standards...")
        seed_standards(db, frameworks)

        print(f"Importing events from {EVENT_DATA_DIR}...")
        results = import_all_event_files(db, EVENT_DATA_DIR)
        for r in results:
            print(f"  {r['topic']}: {r['inserted']} inserted, {r['updated']} updated")

        db.commit()
        print("Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
