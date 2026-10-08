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


def test_home_links_to_resume_page():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert '/resume' in body


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


def test_assembly_page_is_gone():
    client = app_module.app.test_client()

    assert client.get("/assembly-agents").status_code == 404


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


def test_leetcode_returns_200():
    client = app_module.app.test_client()

    response = client.get("/leetcode")

    assert response.status_code == 200
    assert "LeetCode patterns" in response.get_data(as_text=True)


def test_leetcode_unknown_page_returns_404():
    client = app_module.app.test_client()

    assert client.get("/leetcode/not-a-page").status_code == 404


def test_home_links_to_leetcode_between_ml_models_and_jj_dojo():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert body.index('href="/ml-models"') < body.index('href="/leetcode"') < body.index('href="/jj-dojo"')
