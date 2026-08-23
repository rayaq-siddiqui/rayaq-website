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
    assert "Building" in body


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


def test_resume_omits_phone_number():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "306" not in body


def test_resume_renders_summary_honors_and_certifications():
    client = app_module.app.test_client()

    body = client.get("/resume").get_data(as_text=True)

    assert "Software Engineer @ Google" in body
    assert "Governor General&#39;s Academic Medal" in body or "Governor General's Academic Medal" in body
    assert "Deep Neural Networks with PyTorch" in body


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


def test_flights_returns_200():
    client = app_module.app.test_client()

    response = client.get("/flights")

    assert response.status_code == 200


def test_flights_renders_the_search_form():
    client = app_module.app.test_client()

    body = client.get("/flights").get_data(as_text=True)

    assert 'id="origin-input"' in body
    assert 'id="destination-input"' in body
    assert 'id="earliest-departure"' in body
    assert 'id="min-nights"' in body
    assert "Direct flights only" in body
    assert "Find cheap flights" in body


def test_flights_offers_popular_route_shortcuts():
    client = app_module.app.test_client()

    body = client.get("/flights").get_data(as_text=True)

    assert 'data-origin="YTO"' in body
    assert 'data-destination="SFO"' in body


def test_flights_discloses_that_prices_are_indicative():
    client = app_module.app.test_client()

    body = client.get("/flights").get_data(as_text=True)

    assert "indicative fares" in body
    assert "Verify the current fare" in body


def test_flights_never_ships_the_provider_token_to_the_browser(monkeypatch):
    monkeypatch.setenv("TRAVELPAYOUTS_API_TOKEN", "super-secret-token")
    client = app_module.app.test_client()

    body = client.get("/flights").get_data(as_text=True)

    assert "super-secret-token" not in body
    assert "TRAVELPAYOUTS" not in body
