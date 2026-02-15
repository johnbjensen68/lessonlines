import uuid

from app.models import CurriculumFramework, CurriculumStandard


class TestGetFrameworks:
    def test_list_frameworks(self, client, sample_framework):
        resp = client.get("/api/standards/frameworks")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["code"] == "APUSH"
        assert data[0]["name"] == "AP US History"

    def test_list_frameworks_empty(self, client):
        resp = client.get("/api/standards/frameworks")
        assert resp.status_code == 200
        assert resp.json() == []


class TestSearchStandards:
    def test_list_standards(self, client, sample_standard):
        resp = client.get("/api/standards")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["code"] == "APUSH.5.1"

    def test_filter_by_framework(self, client, db, sample_standard, sample_framework):
        other_fw = CurriculumFramework(
            id=uuid.uuid4(), code="TEKS", name="Texas TEKS", state="TX"
        )
        db.add(other_fw)
        db.commit()

        other_std = CurriculumStandard(
            id=uuid.uuid4(),
            framework_id=other_fw.id,
            code="TEKS.8.1",
            title="Texas History",
        )
        db.add(other_std)
        db.commit()

        resp = client.get("/api/standards", params={"framework": "APUSH"})
        data = resp.json()
        assert len(data) == 1
        assert data[0]["code"] == "APUSH.5.1"

    def test_search_standards(self, client, sample_standard):
        resp = client.get("/api/standards", params={"q": "Civil War"})
        data = resp.json()
        assert len(data) == 1

        resp = client.get("/api/standards", params={"q": "nothing"})
        assert resp.json() == []

    def test_filter_by_grade(self, client, sample_standard):
        resp = client.get("/api/standards", params={"grade": "11"})
        data = resp.json()
        assert len(data) == 1

        resp = client.get("/api/standards", params={"grade": "5"})
        assert resp.json() == []


class TestGetStandard:
    def test_get_standard_success(self, client, sample_standard):
        resp = client.get(f"/api/standards/{sample_standard.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == "APUSH.5.1"
        assert data["framework_code"] == "APUSH"

    def test_get_standard_not_found(self, client):
        fake_id = uuid.uuid4()
        resp = client.get(f"/api/standards/{fake_id}")
        assert resp.status_code == 404
