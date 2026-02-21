import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (
    CandidateEvent,
    CandidateStatus,
    CurriculumFramework,
    CurriculumStandard,
    Event,
    HarvestBatch,
    HarvestBatchStatus,
    Tag,
    Timeline,
    TimelineEvent,
    Topic,
    User,
)
from app.services.auth import create_access_token, get_password_hash

# In-memory SQLite for tests
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create and return a test user."""
    user = User(
        id=uuid.uuid4(),
        email="teacher@example.com",
        hashed_password=get_password_hash("password123"),
        display_name="Test Teacher",
        is_pro=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pro_user(db):
    """Create and return a pro test user."""
    user = User(
        id=uuid.uuid4(),
        email="pro@example.com",
        hashed_password=get_password_hash("password123"),
        display_name="Pro Teacher",
        is_pro=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Return auth headers for the test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pro_auth_headers(pro_user):
    """Return auth headers for the pro user."""
    token = create_access_token(data={"sub": str(pro_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        display_name="Admin User",
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(admin_user):
    """Return auth headers for the admin user."""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user(db):
    """Create a second user for ownership tests."""
    user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        hashed_password=get_password_hash("password123"),
        display_name="Other Teacher",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def other_auth_headers(other_user):
    """Return auth headers for the other user."""
    token = create_access_token(data={"sub": str(other_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_topic(db):
    """Create and return a sample topic."""
    topic = Topic(
        id=uuid.uuid4(),
        slug="civil-war",
        name="Civil War",
        description="The American Civil War (1861-1865)",
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@pytest.fixture
def sample_tag(db):
    """Create and return a sample tag."""
    tag = Tag(id=uuid.uuid4(), name="battle", category="event_type")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@pytest.fixture
def sample_event(db, sample_topic, sample_tag):
    """Create and return a sample event with tag."""
    event = Event(
        id=uuid.uuid4(),
        topic_id=sample_topic.id,
        title="Battle of Gettysburg",
        description="Major battle of the Civil War",
        date_start=date(1863, 7, 1),
        date_end=date(1863, 7, 3),
        date_display="July 1-3, 1863",
        date_precision="day",
        location="Gettysburg, PA",
    )
    event.tags.append(sample_tag)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@pytest.fixture
def sample_framework(db):
    """Create and return a sample curriculum framework."""
    framework = CurriculumFramework(
        id=uuid.uuid4(),
        code="APUSH",
        name="AP US History",
        subject="History",
        grade_levels="11-12",
    )
    db.add(framework)
    db.commit()
    db.refresh(framework)
    return framework


@pytest.fixture
def sample_standard(db, sample_framework):
    """Create and return a sample curriculum standard."""
    standard = CurriculumStandard(
        id=uuid.uuid4(),
        framework_id=sample_framework.id,
        code="APUSH.5.1",
        title="Civil War Causes",
        description="Analyze the causes of the Civil War",
        grade_level="11",
        strand="Period 5",
    )
    db.add(standard)
    db.commit()
    db.refresh(standard)
    return standard


@pytest.fixture
def sample_timeline(db, test_user):
    """Create and return a sample timeline for the test user."""
    timeline = Timeline(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Civil War Timeline",
        subtitle="Key events",
        color_scheme="blue_green",
        layout="horizontal",
        font="system",
    )
    db.add(timeline)
    db.commit()
    db.refresh(timeline)
    return timeline


@pytest.fixture
def sample_harvest_batch(db, sample_topic):
    """Create and return a sample harvest batch."""
    batch = HarvestBatch(
        id=uuid.uuid4(),
        topic_id=sample_topic.id,
        source_name="Wikipedia",
        source_url="https://en.wikipedia.org/wiki/Civil_War",
        strategy="web_scrape",
        status=HarvestBatchStatus.running.value,
        event_count=0,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@pytest.fixture
def sample_candidate(db, sample_topic):
    """Create and return a sample candidate event."""
    candidate = CandidateEvent(
        id=uuid.uuid4(),
        topic_id=sample_topic.id,
        title="Battle of Antietam",
        description="Bloodiest single-day battle in American history",
        date_start=date(1862, 9, 17),
        date_display="September 17, 1862",
        date_precision="day",
        location="Sharpsburg, MD",
        status=CandidateStatus.pending.value,
        source_name="Wikipedia",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
