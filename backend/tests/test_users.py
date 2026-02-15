class TestGetCurrentUser:
    def test_get_me_authenticated(self, client, auth_headers, test_user):
        resp = client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "teacher@example.com"
        assert data["display_name"] == "Test Teacher"
        assert data["is_pro"] is False

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/users/me")
        assert resp.status_code == 401
