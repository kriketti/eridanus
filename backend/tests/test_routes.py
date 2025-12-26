import eridanus.activities.pushups.blueprint as pushups_blueprint
import eridanus.activities.jump_rope.blueprint as jump_rope_blueprint
import eridanus.dashboard.blueprint as dashboard_blueprint


def test_home_redirects(client):
    response = client.get("/")
    assert response.status_code in (301, 302)


def test_dashboard_route_ok(client, monkeypatch):
    class FakeDashboardService:
        def home_stats(self, username):
            return {"ok": True}

    monkeypatch.setattr(dashboard_blueprint, "DashboardService", FakeDashboardService)
    response = client.get("/dashboard/")
    assert response.status_code == 200


def test_pushups_list_ok(client, monkeypatch):
    monkeypatch.setattr(pushups_blueprint.service, "fetch_all", lambda username: [])
    response = client.get("/activities/pushups/")
    assert response.status_code == 200


def test_jump_rope_list_ok(client, monkeypatch):
    monkeypatch.setattr(jump_rope_blueprint.service, "fetch_all", lambda username: [])
    response = client.get("/activities/jump_rope/")
    assert response.status_code == 200
