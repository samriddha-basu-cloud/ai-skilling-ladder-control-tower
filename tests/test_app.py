"""Smoke tests for the Flask routes and JSON APIs: every page renders, every API handles good and bad input."""
import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


PAGES = ["/", "/framing", "/exposure", "/matrix", "/ladder", "/interventions", "/operating", "/value",
         "/strategy", "/simulator", "/stress", "/states", "/roadmap", "/kpis", "/navigator", "/ask", "/sources", "/brief"]


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(client, path):
    r = client.get(path)
    assert r.status_code == 200


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_404_page_and_api(client):
    assert client.get("/does-not-exist").status_code == 404
    r = client.get("/api/does-not-exist")
    assert r.status_code == 404
    assert "error" in r.get_json()


def test_old_routes_redirect(client):
    assert client.get("/recommendations").status_code in (301, 302, 308)
    assert client.get("/assumptions").status_code in (301, 302, 308)


def test_api_simulate_valid_and_malformed(client):
    r = client.post("/api/simulate", json={"params": {"completion": 0.8}})
    assert r.status_code == 200
    assert "kpi" in r.get_json()
    r2 = client.post("/api/simulate", data="not json", content_type="application/json")
    assert r2.status_code == 200  # silent=True: falls back to defaults rather than 500ing


def test_api_simulate_rejects_out_of_range_via_clamping(client):
    r = client.post("/api/simulate", json={"params": {"completion": 99, "entrants": -5}})
    body = r.get_json()
    assert 0 < body["params"]["completion"] <= 1
    assert body["params"]["entrants"] >= 1000


def test_api_montecarlo_bounds_runs(client):
    r = client.post("/api/montecarlo", json={"runs": 50})
    assert r.status_code == 200
    assert r.get_json()["runs"] >= 200  # engine floors runs at 200


def test_api_state_known_and_unknown(client):
    assert client.get("/api/state/TN").status_code == 200
    assert client.get("/api/state/ZZ").status_code == 404


def test_api_scenarios_create_and_delete(client):
    r = client.post("/api/scenarios", json={"name": "", "params": {}})
    assert r.status_code == 400
    r2 = client.post("/api/scenarios", json={"name": "Test scenario", "params": {"completion": 0.7}})
    assert r2.status_code == 200
    sid = r2.get_json()["id"]
    r3 = client.delete(f"/api/scenarios/{sid}")
    assert r3.status_code == 200
    r4 = client.delete("/api/scenarios/operating_plan")
    assert r4.status_code == 400  # cannot delete a preset


def test_api_stress_valid_all_and_invalid(client):
    assert client.post("/api/stress", json={"shock": "cost_up"}).status_code == 200
    assert client.post("/api/stress", json={"all": True}).status_code == 200
    assert client.post("/api/stress", json={"shock": "nope"}).status_code == 400
    assert client.post("/api/stress", json={}).status_code == 400


def test_api_ask_requires_question(client):
    r = client.post("/api/ask", json={"q": ""})
    assert r.status_code == 400
    r2 = client.post("/api/ask", json={"q": "What is VACR?"})
    assert r2.status_code == 200
    assert "answer" in r2.get_json()


def test_export_csv_and_json(client):
    assert client.get("/export/scenario.csv").status_code == 200
    assert client.get("/export/scenario.json").status_code == 200


def test_no_hardcoded_secret_key():
    assert flask_app.config["SECRET_KEY"] != "vertex-ai-skill-ladder-3"
    assert len(flask_app.config["SECRET_KEY"]) >= 32
