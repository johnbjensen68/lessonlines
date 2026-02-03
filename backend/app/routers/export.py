import io
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from ..database import get_db
from ..models import User, Timeline, TimelineEvent, Event
from ..services.auth import get_current_user

router = APIRouter(prefix="/api/timelines", tags=["export"])


COLOR_SCHEMES = {
    "blue_green": {"primary": colors.HexColor("#3498db"), "secondary": colors.HexColor("#2ecc71")},
    "red_orange": {"primary": colors.HexColor("#e74c3c"), "secondary": colors.HexColor("#f39c12")},
    "purple_blue": {"primary": colors.HexColor("#9b59b6"), "secondary": colors.HexColor("#3498db")},
    "dark": {"primary": colors.HexColor("#34495e"), "secondary": colors.HexColor("#34495e")},
}


def generate_timeline_pdf(timeline: Timeline) -> io.BytesIO:
    """Generate a PDF for the given timeline."""
    buffer = io.BytesIO()

    # Use landscape for horizontal timelines
    page_size = landscape(letter) if timeline.layout == "horizontal" else letter
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Get color scheme
    scheme = COLOR_SCHEMES.get(timeline.color_scheme, COLOR_SCHEMES["blue_green"])

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=6,
        textColor=scheme["primary"],
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        spaceAfter=24,
        textColor=colors.gray,
    )
    event_title_style = ParagraphStyle(
        "EventTitle",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=scheme["primary"],
        spaceAfter=4,
    )
    event_date_style = ParagraphStyle(
        "EventDate",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.gray,
        spaceAfter=4,
    )
    event_desc_style = ParagraphStyle(
        "EventDesc",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=12,
    )

    # Build content
    story = []

    # Title and subtitle
    story.append(Paragraph(timeline.title, title_style))
    if timeline.subtitle:
        story.append(Paragraph(timeline.subtitle, subtitle_style))
    else:
        story.append(Spacer(1, 12))

    # Sort events by position
    sorted_events = sorted(timeline.events, key=lambda e: e.position)

    # Events
    for idx, te in enumerate(sorted_events):
        # Get event details
        if te.event:
            title = te.event.title
            description = te.event.description
            date_display = te.event.date_display
            location = te.event.location
        else:
            title = te.custom_title or "Custom Event"
            description = te.custom_description or ""
            date_display = te.custom_date_display or ""
            location = None

        # Event number marker
        marker_text = f"<b>{idx + 1}.</b> "
        story.append(Paragraph(marker_text + title, event_title_style))

        # Date and location
        date_location = date_display
        if location:
            date_location += f" | {location}"
        story.append(Paragraph(date_location, event_date_style))

        # Description
        story.append(Paragraph(description, event_desc_style))

        # Add spacing between events
        story.append(Spacer(1, 8))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@router.post("/{timeline_id}/export/pdf")
def export_timeline_pdf(
    timeline_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export a timeline as PDF. Requires pro subscription."""
    # Check if user is pro
    if not current_user.is_pro:
        raise HTTPException(
            status_code=403,
            detail="PDF export is a pro feature. Please upgrade to access this feature.",
        )

    # Get timeline with events
    timeline = (
        db.query(Timeline)
        .filter(Timeline.id == timeline_id, Timeline.user_id == current_user.id)
        .options(
            joinedload(Timeline.events).joinedload(TimelineEvent.event).joinedload(Event.tags)
        )
        .first()
    )

    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    # Generate PDF
    pdf_buffer = generate_timeline_pdf(timeline)

    # Create safe filename
    safe_title = "".join(c for c in timeline.title if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title or 'timeline'}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
