import uuid
from datetime import date


class TestCandidateEventCRUD:
    """Test candidate event CRUD operations."""

    def test_create_candidate_new_event(self, client, admin_auth_headers, sample_topic):
        """Create a new candidate event (no existing_event_id)."""
        response = client.post(
            "/api/admin/candidates",
            json={
                "topic_id": str(sample_topic.id),
                "title": "First Battle of Bull Run",
                "description": "First major battle of the Civil War",
                "date_start": "1861-07-21",
                "date_display": "July 21, 1861",
                "date_precision": "day",
                "location": "Manassas, VA",
                "source_name": "Wikipedia",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "First Battle of Bull Run"
        assert data["status"] == "pending"
        assert data["existing_event_id"] is None

    def test_create_candidate_proposed_change(self, client, admin_auth_headers, sample_topic, sample_event):
        """Create a candidate as a proposed change to an existing event."""
        response = client.post(
            "/api/admin/candidates",
            json={
                "topic_id": str(sample_topic.id),
                "title": "Battle of Gettysburg (Updated)",
                "description": "Updated description of the major battle",
                "date_start": "1863-07-01",
                "date_display": "July 1-3, 1863",
                "date_precision": "day",
                "existing_event_id": str(sample_event.id),
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["existing_event_id"] == str(sample_event.id)

    def test_create_candidate_with_tags_and_standards(
        self, client, admin_auth_headers, sample_topic, sample_tag, sample_standard
    ):
        """Create a candidate with tag and standard associations."""
        response = client.post(
            "/api/admin/candidates",
            json={
                "topic_id": str(sample_topic.id),
                "title": "Fort Sumter Attack",
                "description": "Opening engagement of the Civil War",
                "date_start": "1861-04-12",
                "date_display": "April 12, 1861",
                "tag_ids": [str(sample_tag.id)],
                "standard_ids": [str(sample_standard.id)],
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "battle"
        assert len(data["standards"]) == 1
        assert data["standards"][0]["code"] == "APUSH.5.1"

    def test_create_candidate_requires_auth(self, client, sample_topic):
        """Creating a candidate without auth should fail."""
        response = client.post(
            "/api/admin/candidates",
            json={
                "topic_id": str(sample_topic.id),
                "title": "Test",
                "description": "Test",
                "date_start": "1861-01-01",
                "date_display": "1861",
            },
        )
        assert response.status_code == 401

    def test_non_admin_gets_403(self, client, auth_headers, sample_topic):
        """Non-admin user gets 403 on admin endpoints."""
        response = client.get("/api/admin/candidates", headers=auth_headers)
        assert response.status_code == 403

    def test_list_candidates_default_pending(self, client, admin_auth_headers, sample_candidate):
        """List candidates defaults to pending status filter."""
        response = client.get("/api/admin/candidates", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(c["status"] == "pending" for c in data)

    def test_list_candidates_filter_by_topic(self, client, admin_auth_headers, sample_candidate, sample_topic):
        """Filter candidates by topic slug."""
        response = client.get(
            f"/api/admin/candidates?topic={sample_topic.slug}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_candidates_filter_by_keyword(self, client, admin_auth_headers, sample_candidate):
        """Filter candidates by keyword search."""
        response = client.get(
            "/api/admin/candidates?q=Antietam",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Antietam" in data[0]["title"]

    def test_list_candidates_filter_has_existing_event(
        self, client, admin_auth_headers, sample_topic, sample_event, db
    ):
        """Filter candidates by whether they have an existing event."""
        from app.models import CandidateEvent, CandidateStatus

        # Create a candidate with existing_event_id
        candidate = CandidateEvent(
            id=uuid.uuid4(),
            topic_id=sample_topic.id,
            title="Proposed Change",
            description="A proposed change",
            date_start=date(1863, 7, 1),
            date_display="July 1, 1863",
            existing_event_id=sample_event.id,
            status=CandidateStatus.pending.value,
        )
        db.add(candidate)
        db.commit()

        response = client.get(
            "/api/admin/candidates?has_existing_event=true",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(c["existing_event_id"] is not None for c in data)

    def test_list_candidates_pagination(self, client, admin_auth_headers, sample_topic, db):
        """Test limit and offset pagination."""
        from app.models import CandidateEvent, CandidateStatus

        for i in range(5):
            db.add(CandidateEvent(
                id=uuid.uuid4(),
                topic_id=sample_topic.id,
                title=f"Event {i}",
                description=f"Description {i}",
                date_start=date(1861, 1, 1),
                date_display="1861",
                status=CandidateStatus.pending.value,
            ))
        db.commit()

        response = client.get(
            "/api/admin/candidates?limit=2&offset=0",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

        response2 = client.get(
            "/api/admin/candidates?limit=2&offset=2",
            headers=admin_auth_headers,
        )
        assert response2.status_code == 200
        assert len(response2.json()) == 2

    def test_get_candidate_detail(self, client, admin_auth_headers, sample_candidate):
        """Get a single candidate by ID."""
        response = client.get(
            f"/api/admin/candidates/{sample_candidate.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Battle of Antietam"
        assert data["existing_event"] is None

    def test_get_candidate_detail_with_existing_event(
        self, client, admin_auth_headers, sample_topic, sample_event, db
    ):
        """Get candidate detail includes existing event for comparison."""
        from app.models import CandidateEvent, CandidateStatus

        candidate = CandidateEvent(
            id=uuid.uuid4(),
            topic_id=sample_topic.id,
            title="Updated Gettysburg",
            description="Updated description",
            date_start=date(1863, 7, 1),
            date_display="July 1-3, 1863",
            existing_event_id=sample_event.id,
            status=CandidateStatus.pending.value,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        response = client.get(
            f"/api/admin/candidates/{candidate.id}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["existing_event"] is not None
        assert data["existing_event"]["title"] == "Battle of Gettysburg"

    def test_get_candidate_not_found(self, client, admin_auth_headers):
        """Get non-existent candidate returns 404."""
        response = client.get(
            f"/api/admin/candidates/{uuid.uuid4()}",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_approve_candidate(self, client, admin_auth_headers, sample_candidate):
        """Approve a candidate sets review metadata."""
        response = client.patch(
            f"/api/admin/candidates/{sample_candidate.id}",
            json={"status": "approved", "review_notes": "Looks good"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["review_notes"] == "Looks good"
        assert data["reviewed_at"] is not None
        assert data["reviewed_by"] is not None

    def test_reject_candidate(self, client, admin_auth_headers, sample_candidate):
        """Reject a candidate sets review metadata."""
        response = client.patch(
            f"/api/admin/candidates/{sample_candidate.id}",
            json={"status": "rejected", "review_notes": "Inaccurate dates"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["review_notes"] == "Inaccurate dates"


class TestPromoteCandidate:
    """Test candidate promotion to events."""

    def test_promote_new_event(self, client, admin_auth_headers, sample_candidate):
        """Promoting a candidate with no existing_event_id creates a new event."""
        response = client.post(
            f"/api/admin/candidates/{sample_candidate.id}/promote",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Battle of Antietam"
        assert data["description"] == "Bloodiest single-day battle in American history"

        # Verify the new event appears in public events
        events_response = client.get("/api/events")
        event_titles = [e["title"] for e in events_response.json()]
        assert "Battle of Antietam" in event_titles

        # Verify candidate status is now approved
        candidate_response = client.get(
            f"/api/admin/candidates/{sample_candidate.id}",
            headers=admin_auth_headers,
        )
        assert candidate_response.json()["status"] == "approved"

    def test_promote_as_update(self, client, admin_auth_headers, sample_topic, sample_event, db):
        """Promoting a candidate with existing_event_id updates the existing event."""
        from app.models import CandidateEvent, CandidateStatus

        candidate = CandidateEvent(
            id=uuid.uuid4(),
            topic_id=sample_topic.id,
            title="Battle of Gettysburg (Revised)",
            description="Revised description of the major battle",
            date_start=date(1863, 7, 1),
            date_display="July 1-3, 1863",
            date_precision="day",
            existing_event_id=sample_event.id,
            status=CandidateStatus.pending.value,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        response = client.post(
            f"/api/admin/candidates/{candidate.id}/promote",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_event.id)
        assert data["title"] == "Battle of Gettysburg (Revised)"
        assert data["description"] == "Revised description of the major battle"

    def test_promote_already_approved(self, client, admin_auth_headers, sample_candidate, db):
        """Promoting an already-approved candidate returns 400."""
        sample_candidate.status = "approved"
        db.commit()

        response = client.post(
            f"/api/admin/candidates/{sample_candidate.id}/promote",
            headers=admin_auth_headers,
        )
        assert response.status_code == 400

    def test_promote_not_found(self, client, admin_auth_headers):
        """Promoting a non-existent candidate returns 404."""
        response = client.post(
            f"/api/admin/candidates/{uuid.uuid4()}/promote",
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    def test_promote_requires_admin(self, client, auth_headers, sample_candidate):
        """Non-admin user cannot promote candidates."""
        response = client.post(
            f"/api/admin/candidates/{sample_candidate.id}/promote",
            headers=auth_headers,
        )
        assert response.status_code == 403


class TestCandidateBatchCreate:
    """Test bulk candidate creation."""

    def test_batch_create(self, client, admin_auth_headers, sample_topic, sample_harvest_batch):
        """Bulk create candidates with batch ID."""
        response = client.post(
            "/api/admin/candidates/batch",
            json={
                "batch_id": str(sample_harvest_batch.id),
                "candidates": [
                    {
                        "topic_id": str(sample_topic.id),
                        "title": "Event A",
                        "description": "Description A",
                        "date_start": "1861-04-12",
                        "date_display": "April 12, 1861",
                    },
                    {
                        "topic_id": str(sample_topic.id),
                        "title": "Event B",
                        "description": "Description B",
                        "date_start": "1861-07-21",
                        "date_display": "July 21, 1861",
                    },
                ],
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 2
        assert all(c["harvest_batch_id"] == str(sample_harvest_batch.id) for c in data)

        # Verify batch event_count was updated
        batch_response = client.get("/api/admin/harvest-batches", headers=admin_auth_headers)
        batches = batch_response.json()
        batch = next(b for b in batches if b["id"] == str(sample_harvest_batch.id))
        assert batch["event_count"] == 2


class TestHarvestBatchCRUD:
    """Test harvest batch CRUD operations."""

    def test_create_harvest_batch(self, client, admin_auth_headers, sample_topic):
        """Create a new harvest batch."""
        response = client.post(
            "/api/admin/harvest-batches",
            json={
                "topic_id": str(sample_topic.id),
                "source_name": "Wikipedia",
                "strategy": "web_scrape",
                "source_url": "https://en.wikipedia.org",
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source_name"] == "Wikipedia"
        assert data["status"] == "running"
        assert data["event_count"] == 0

    def test_list_harvest_batches(self, client, admin_auth_headers, sample_harvest_batch):
        """List harvest batches."""
        response = client.get("/api/admin/harvest-batches", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_harvest_batches_filter_by_status(self, client, admin_auth_headers, sample_harvest_batch):
        """Filter harvest batches by status."""
        response = client.get(
            "/api/admin/harvest-batches?status=running",
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(b["status"] == "running" for b in data)

    def test_update_harvest_batch_completed(self, client, admin_auth_headers, sample_harvest_batch):
        """Update batch to completed sets completed_at."""
        response = client.patch(
            f"/api/admin/harvest-batches/{sample_harvest_batch.id}",
            json={"status": "completed"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_update_harvest_batch_not_found(self, client, admin_auth_headers):
        """Update non-existent batch returns 404."""
        response = client.patch(
            f"/api/admin/harvest-batches/{uuid.uuid4()}",
            json={"status": "completed"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404


class TestCandidateIsolation:
    """Test that candidates do NOT appear in /api/events."""

    def test_candidates_not_in_events_list(self, client, sample_candidate):
        """Candidate events must not appear in the public events endpoint."""
        response = client.get("/api/events")
        assert response.status_code == 200
        data = response.json()
        candidate_ids = [str(sample_candidate.id)]
        event_ids = [e["id"] for e in data]
        for cid in candidate_ids:
            assert cid not in event_ids

    def test_candidate_not_accessible_via_events_endpoint(self, client, sample_candidate):
        """Candidate event should not be accessible via /api/events/{id}."""
        response = client.get(f"/api/events/{sample_candidate.id}")
        assert response.status_code == 404
