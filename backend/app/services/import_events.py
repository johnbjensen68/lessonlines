"""
Import events from JSON files into the database.
Events are identified by their source_id slug for upsert logic.
"""
import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from ..models import CurriculumStandard, Event, Tag, Topic


def import_events_from_file(db: Session, file_path: Path) -> dict:
    """
    Import events from a single JSON file.
    - Inserts events not yet in the DB (matched by source_id).
    - Updates existing events in place.
    - Leaves DB events absent from the file untouched.
    Returns a summary dict.
    """
    with open(file_path) as f:
        data = json.load(f)

    topic_data = data["topic"]
    topic = db.query(Topic).filter_by(slug=topic_data["slug"]).first()
    if not topic:
        topic = Topic(
            slug=topic_data["slug"],
            name=topic_data["name"],
            description=topic_data.get("description"),
        )
        db.add(topic)
        db.flush()

    inserted = 0
    updated = 0

    for raw in data["events"]:
        source_id = raw["id"]
        date_start = date.fromisoformat(raw["date_start"])
        date_end = date.fromisoformat(raw["date_end"]) if raw.get("date_end") else None

        tags = _resolve_tags(db, raw.get("tags", []))
        standards = _resolve_standards(db, raw.get("standards", []))

        existing = db.query(Event).filter_by(source_id=source_id).first()
        if existing:
            _apply_fields(existing, raw, topic.id, date_start, date_end)
            existing.tags = tags
            existing.standards = standards
            updated += 1
        else:
            event = Event(
                source_id=source_id,
                topic_id=topic.id,
                title=raw["title"],
                description=raw["description"],
                date_start=date_start,
                date_end=date_end,
                date_display=raw["date_display"],
                date_precision=raw.get("date_precision", "day"),
                location=raw.get("location"),
                significance=raw.get("significance"),
                source_url=raw.get("source_url"),
                source_citation=raw.get("source_citation"),
                image_url=raw.get("image_url"),
            )
            event.tags = tags
            event.standards = standards
            db.add(event)
            inserted += 1

    db.flush()
    return {"topic": topic_data["slug"], "inserted": inserted, "updated": updated}


def import_all_event_files(db: Session, data_dir: Path) -> list[dict]:
    """Import all *.json files from data_dir, sorted by filename."""
    results = []
    for file_path in sorted(data_dir.glob("*.json")):
        result = import_events_from_file(db, file_path)
        results.append(result)
    return results


# ── helpers ──────────────────────────────────────────────────────────────────

def _apply_fields(event: Event, raw: dict, topic_id, date_start, date_end) -> None:
    event.topic_id = topic_id
    event.title = raw["title"]
    event.description = raw["description"]
    event.date_start = date_start
    event.date_end = date_end
    event.date_display = raw["date_display"]
    event.date_precision = raw.get("date_precision", "day")
    event.location = raw.get("location")
    event.significance = raw.get("significance")
    event.source_url = raw.get("source_url")
    event.source_citation = raw.get("source_citation")
    event.image_url = raw.get("image_url")


def _resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    tags = []
    for name in names:
        tag = db.query(Tag).filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def _resolve_standards(db: Session, codes: list[str]) -> list[CurriculumStandard]:
    standards = []
    for code in codes:
        standard = db.query(CurriculumStandard).filter_by(code=code).first()
        if standard:
            standards.append(standard)
    return standards
