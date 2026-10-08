import app as app_module


def fake_city():
    return {
        "name": "Testville, TS",
        "local_time": "3:30 PM",
        "temperature_c": 20,
        "high_c": 25,
        "low_c": 15,
        "windspeed_kmh": 10.0,
        "description": "Mainly clear",
        "emoji": "🌤️",
        "hourly": [{"label": "12 AM", "temp_c": 18, "emoji": "☀️"}],
    }


def fake_showcase():
    return {
        "name": "Assembly",
        "tagline": "A multi-agent software delivery orchestrator.",
        "repo_url": "https://github.com/rayaq-siddiqui/assembly-agents",
        "playbook_url": "https://github.com/rayaq-siddiqui/assembly-agents/blob/main/docs/DAILY_AGENT.md",
        "summary_paragraphs": ["It coordinates specialized agents."],
        "highlights": [{"title": "Spec-first", "detail": "Specs before code."}],
        "status": {
            "current_milestone": "M0",
            "current_milestone_title": "Design and benchmark setup",
            "runs_to_date": 7,
            "cycles_last_run": 14,
            "tests_passing": 99,
            "verification": "pytest 99 passed",
        },
        "in_progress_headline": "The type layer is finished",
        "in_progress_paragraphs": ["Fourteen cycles landed."],
        "milestones": [{"id": "M0", "title": "Design and benchmark setup", "state": "active"}],
        "milestones_completed": 0,
        "milestones_total": 8,
        "recent_work": [
            {
                "sha": "8fe571a",
                "title": "Contract tests",
                "detail": "Every artifact type round-trips.",
                "url": "https://github.com/rayaq-siddiqui/assembly-agents/commit/8fe571a",
            }
        ],
        "next_up": ["Define the policy rule set"],
        "updated_at": "2026-08-02",
    }


def test_home_returns_200():
    client = app_module.app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_home_links_to_weather_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/weather' in body


def test_home_links_to_resume_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/resume' in body


def test_home_links_to_assembly_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/assembly-agents' in body
    assert "Building" not in body
    assert body.index("/assembly-agents") > body.index("/resume")


def test_resume_returns_200():
    client = app_module.app.test_client()

    response = client.get("/resume")

    assert response.status_code == 200


def test_resume_renders_experience_and_education():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "University of Waterloo" in body
    assert "Google" in body
    assert "d-Matrix" in body
    assert "IBM" in body
    assert "BlackBerry Limited" in body
    assert "RBC" in body
    assert "Polar" in body
    assert "CloudMesh" in body
    assert "Text Recognition Glasses" in body


def test_resume_omits_phone_number():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "306" not in body


def test_resume_renders_summary_honors_and_certifications():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "Software Engineer @ Google" in body
    assert "Governor General&#39;s Academic Medal" in body or "Governor General's Academic Medal" in body
    assert "Deep Learning Specialization" in body


def test_resume_renders_leadership():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "Leadership" in body
    assert "Kids Caring for Kids Cancer Drive" in body


def test_resume_keeps_career_planning_private():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    for private in ("L3", "L4", "promotion", "DeepMind", "Seeking"):
        assert private not in body


def test_weather_returns_200(monkeypatch):
    monkeypatch.setattr(
        app_module, "get_weather_for_cities", lambda: [fake_city()]
    )
    client = app_module.app.test_client()

    response = client.get("/weather")

    assert response.status_code == 200


def test_weather_renders_city_data(monkeypatch):
    monkeypatch.setattr(
        app_module, "get_weather_for_cities", lambda: [fake_city()]
    )
    client = app_module.app.test_client()

    body = client.get("/weather").get_data(as_text=True)

    assert "Testville, TS" in body
    assert "20&deg;C" in body
    assert "Mainly clear" in body


def test_weather_includes_date_header(monkeypatch):
    monkeypatch.setattr(
        app_module, "get_weather_for_cities", lambda: [fake_city()]
    )
    client = app_module.app.test_client()

    body = client.get("/weather").get_data(as_text=True)

    assert "Current Weather for" in body


def test_assembly_agents_returns_200(monkeypatch):
    monkeypatch.setattr(app_module, "get_showcase", fake_showcase)
    client = app_module.app.test_client()

    response = client.get("/assembly-agents")

    assert response.status_code == 200


def test_assembly_agents_renders_status_and_progress(monkeypatch):
    monkeypatch.setattr(app_module, "get_showcase", fake_showcase)
    client = app_module.app.test_client()

    body = client.get("/assembly-agents").get_data(as_text=True)

    assert "Currently building" in body
    assert "The type layer is finished" in body
    assert "Fourteen cycles landed." in body
    assert "Design and benchmark setup" in body
    assert "99" in body


def test_assembly_agents_links_recent_work_to_commits(monkeypatch):
    monkeypatch.setattr(app_module, "get_showcase", fake_showcase)
    client = app_module.app.test_client()

    body = client.get("/assembly-agents").get_data(as_text=True)

    assert "assembly-agents/commit/8fe571a" in body


def test_assembly_agents_degrades_when_showcase_is_unavailable(monkeypatch):
    monkeypatch.setattr(app_module, "get_showcase", lambda: None)
    client = app_module.app.test_client()

    response = client.get("/assembly-agents")

    assert response.status_code == 200
    assert "temporarily unavailable" in response.get_data(as_text=True)


def test_assembly_agents_renders_the_real_committed_showcase():
    client = app_module.app.test_client()

    body = client.get("/assembly-agents").get_data(as_text=True)

    assert "Assembly" in body
    assert "temporarily unavailable" not in body


def test_health_returns_200_ok():
    client = app_module.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_pages_link_static_assets_with_a_version():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert "/static/style.css?v=" in body


def test_static_assets_are_cacheable_for_a_year():
    client = app_module.app.test_client()

    response = client.get("/static/style.css")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "public, max-age=31536000"


def test_flights_pages_are_gone():
    client = app_module.app.test_client()

    assert client.get("/flights").status_code == 404
    assert client.get("/api/flights/health").status_code == 404


def test_jj_returns_200():
    client = app_module.app.test_client()

    response = client.get("/jj")

    assert response.status_code == 200
    assert "jj architecture" in response.get_data(as_text=True)


def test_home_links_to_jj_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert 'href="/jj"' in body


def test_jj_dojo_returns_200():
    client = app_module.app.test_client()

    response = client.get("/jj-dojo")

    assert response.status_code == 200
    assert "jj-dojo architecture" in response.get_data(as_text=True)


def test_home_links_to_jj_dojo_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert 'href="/jj-dojo"' in body


def test_jj_vfs_returns_200():
    client = app_module.app.test_client()

    response = client.get("/jj-vfs-poc")

    assert response.status_code == 200
    assert "jj-vfs-poc architecture" in response.get_data(as_text=True)


def test_home_links_to_jj_vfs_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert 'href="/jj-vfs-poc"' in body


def test_jj_cloud_returns_200():
    client = app_module.app.test_client()

    response = client.get("/jj-commit-cloud-poc")

    assert response.status_code == 200
    assert "Commit Cloud architecture" in response.get_data(as_text=True)


def test_home_links_to_jj_cloud_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert 'href="/jj-commit-cloud-poc"' in body


def test_ml_models_returns_200():
    client = app_module.app.test_client()

    response = client.get("/ml-models")

    assert response.status_code == 200
    assert "ML model architectures" in response.get_data(as_text=True)


def test_home_links_to_ml_models_between_jj_and_jj_dojo():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert body.index('href="/jj"') < body.index('href="/ml-models"') < body.index('href="/jj-dojo"')
