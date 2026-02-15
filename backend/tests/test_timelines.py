import uuid

import pytest


class TestCreateTimeline:
    def test_create_success(self, client, auth_headers):
        resp = client.post("/api/timelines", json={
            "title": "My Timeline",
            "subtitle": "A test timeline",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "My Timeline"
        assert data["subtitle"] == "A test timeline"
        assert data["color_scheme"] == "blue_green"
        assert data["layout"] == "horizontal"
        assert data["events"] == []

    def test_create_unauthenticated(self, client):
        resp = client.post("/api/timelines", json={"title": "Nope"})
        assert resp.status_code == 401


class TestListTimelines:
    def test_list_own_timelines(self, client, auth_headers, sample_timeline):
        resp = client.get("/api/timelines", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Civil War Timeline"

    def test_list_empty(self, client, auth_headers):
        resp = client.get("/api/timelines", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/timelines")
        assert resp.status_code == 401

    def test_cannot_see_other_users_timelines(self, client, other_auth_headers, sample_timeline):
        resp = client.get("/api/timelines", headers=other_auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetTimeline:
    def test_get_own_timeline(self, client, auth_headers, sample_timeline):
        resp = client.get(f"/api/timelines/{sample_timeline.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Civil War Timeline"

    def test_get_other_users_timeline(self, client, other_auth_headers, sample_timeline):
        resp = client.get(f"/api/timelines/{sample_timeline.id}", headers=other_auth_headers)
        assert resp.status_code == 404

    def test_get_nonexistent_timeline(self, client, auth_headers):
        resp = client.get(f"/api/timelines/{uuid.uuid4()}", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateTimeline:
    def test_update_success(self, client, auth_headers, sample_timeline):
        resp = client.put(f"/api/timelines/{sample_timeline.id}", json={
            "title": "Updated Title",
            "color_scheme": "dark",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Title"
        assert data["color_scheme"] == "dark"
        # Unchanged fields preserved
        assert data["layout"] == "horizontal"

    def test_update_other_users_timeline(self, client, other_auth_headers, sample_timeline):
        resp = client.put(f"/api/timelines/{sample_timeline.id}", json={
            "title": "Hacked",
        }, headers=other_auth_headers)
        assert resp.status_code == 404


class TestDeleteTimeline:
    def test_delete_success(self, client, auth_headers, sample_timeline):
        resp = client.delete(f"/api/timelines/{sample_timeline.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

        # Confirm it's gone
        resp = client.get(f"/api/timelines/{sample_timeline.id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_other_users_timeline(self, client, other_auth_headers, sample_timeline):
        resp = client.delete(f"/api/timelines/{sample_timeline.id}", headers=other_auth_headers)
        assert resp.status_code == 404


class TestTimelineEvents:
    def test_add_curated_event(self, client, auth_headers, sample_timeline, sample_event):
        resp = client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "event_id": str(sample_event.id),
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["events"]) == 1
        assert data["events"][0]["event_id"] == str(sample_event.id)
        assert data["events"][0]["position"] == 0

    def test_add_custom_event(self, client, auth_headers, sample_timeline):
        resp = client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "custom_title": "My Custom Event",
            "custom_description": "Something happened",
            "custom_date_display": "1865",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["events"]) == 1
        assert data["events"][0]["event_id"] is None
        assert data["events"][0]["custom_title"] == "My Custom Event"

    def test_remove_event(self, client, auth_headers, sample_timeline, sample_event):
        # Add an event first
        client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "event_id": str(sample_event.id),
        }, headers=auth_headers)

        # Remove it
        resp = client.delete(
            f"/api/timelines/{sample_timeline.id}/events/0",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["events"]) == 0

    @pytest.mark.xfail(
        reason="SQLite checks unique constraints per-row; works with PostgreSQL deferred constraints"
    )
    def test_reorder_events(self, client, auth_headers, sample_timeline, sample_event):
        # Add three events
        client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "custom_title": "First",
            "custom_date_display": "1861",
        }, headers=auth_headers)
        client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "custom_title": "Second",
            "custom_date_display": "1862",
        }, headers=auth_headers)
        resp3 = client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "custom_title": "Third",
            "custom_date_display": "1863",
        }, headers=auth_headers)

        events = resp3.json()["events"]
        first_id = events[0]["id"]
        second_id = events[1]["id"]
        third_id = events[2]["id"]

        # Reorder: reverse order (3, 2, 1)
        resp = client.put(f"/api/timelines/{sample_timeline.id}/events/reorder", json={
            "positions": [third_id, second_id, first_id],
        }, headers=auth_headers)
        assert resp.status_code == 200
        reordered = resp.json()["events"]
        assert reordered[0]["id"] == third_id
        assert reordered[1]["id"] == second_id
        assert reordered[2]["id"] == first_id

    def test_add_event_to_other_users_timeline(self, client, other_auth_headers, sample_timeline):
        resp = client.post(f"/api/timelines/{sample_timeline.id}/events", json={
            "custom_title": "Hacked",
        }, headers=other_auth_headers)
        assert resp.status_code == 404
