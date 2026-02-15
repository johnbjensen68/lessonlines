import uuid

import pytest


class TestPdfExport:
    def test_export_pro_user(self, client, pro_auth_headers, db, pro_user):
        # Create a timeline for the pro user
        from app.models import Timeline
        timeline = Timeline(
            id=uuid.uuid4(),
            user_id=pro_user.id,
            title="Pro Timeline",
        )
        db.add(timeline)
        db.commit()

        resp = client.post(
            f"/api/timelines/{timeline.id}/export/pdf",
            headers=pro_auth_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "Pro Timeline" in resp.headers.get("content-disposition", "")

    def test_export_non_pro_denied(self, client, auth_headers, sample_timeline):
        resp = client.post(
            f"/api/timelines/{sample_timeline.id}/export/pdf",
            headers=auth_headers,
        )
        assert resp.status_code == 403
        assert "pro feature" in resp.json()["detail"].lower()

    def test_export_unauthenticated(self, client, sample_timeline):
        resp = client.post(f"/api/timelines/{sample_timeline.id}/export/pdf")
        assert resp.status_code == 401

    def test_export_timeline_not_found(self, client, pro_auth_headers):
        resp = client.post(
            f"/api/timelines/{uuid.uuid4()}/export/pdf",
            headers=pro_auth_headers,
        )
        assert resp.status_code == 404
