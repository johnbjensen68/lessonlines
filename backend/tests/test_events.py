import uuid
from datetime import date

from app.models import Event, Tag, Topic


class TestGetTopics:
    def test_list_topics(self, client, sample_topic):
        resp = client.get("/api/topics")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["slug"] == "civil-war"
        assert data[0]["name"] == "Civil War"

    def test_list_topics_empty(self, client):
        resp = client.get("/api/topics")
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetTags:
    def test_list_tags(self, client, sample_tag):
        resp = client.get("/api/tags")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "battle"

    def test_filter_tags_by_category(self, client, db, sample_tag):
        other_tag = Tag(id=uuid.uuid4(), name="president", category="person")
        db.add(other_tag)
        db.commit()

        resp = client.get("/api/tags", params={"category": "person"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "president"

    def test_filter_tags_no_match(self, client, sample_tag):
        resp = client.get("/api/tags", params={"category": "nonexistent"})
        assert resp.json() == []


class TestSearchEvents:
    def test_list_all_events(self, client, sample_event):
        resp = client.get("/api/events")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Battle of Gettysburg"

    def test_filter_by_topic(self, client, db, sample_event, sample_topic):
        other_topic = Topic(id=uuid.uuid4(), slug="revolution", name="American Revolution")
        db.add(other_topic)
        db.commit()

        resp = client.get("/api/events", params={"topic": "civil-war"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Battle of Gettysburg"

        resp = client.get("/api/events", params={"topic": "revolution"})
        assert resp.json() == []

    def test_search_by_keyword(self, client, sample_event):
        resp = client.get("/api/events", params={"q": "Gettysburg"})
        data = resp.json()
        assert len(data) == 1

        resp = client.get("/api/events", params={"q": "nothing"})
        assert resp.json() == []

    def test_search_case_insensitive(self, client, sample_event):
        resp = client.get("/api/events", params={"q": "gettysburg"})
        assert len(resp.json()) == 1

    def test_filter_by_tag(self, client, sample_event):
        resp = client.get("/api/events", params={"tag": "battle"})
        data = resp.json()
        assert len(data) == 1

        resp = client.get("/api/events", params={"tag": "politics"})
        assert resp.json() == []

    def test_events_include_tags(self, client, sample_event):
        resp = client.get("/api/events")
        data = resp.json()
        assert len(data[0]["tags"]) == 1
        assert data[0]["tags"][0]["name"] == "battle"


class TestGetEvent:
    def test_get_event_success(self, client, sample_event):
        resp = client.get(f"/api/events/{sample_event.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Battle of Gettysburg"
        assert data["date_display"] == "July 1-3, 1863"
        assert data["location"] == "Gettysburg, PA"

    def test_get_event_not_found(self, client):
        fake_id = uuid.uuid4()
        resp = client.get(f"/api/events/{fake_id}")
        assert resp.status_code == 404
