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


def test_home_returns_200():
    client = app_module.app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_home_links_to_weather_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/weather' in body


def test_home_does_not_link_to_resume_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/resume' not in body


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


def test_health_returns_200_ok():
    client = app_module.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
