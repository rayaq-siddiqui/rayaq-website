import re
from pathlib import Path

import app as app_module
import resume_data

PHONE_NUMBER = re.compile(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")

PROJECT_LINKS = [
    "/leetcode",
    "/ml-models",
    "/jj",
    "/jj-dojo",
    "/jj-vfs-poc",
    "/jj-commit-cloud-poc",
    "/weather",
]


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

    assert "306" not in re.sub(r"\?v=\d+", "", body)
    assert "tel:" not in body
    assert not PHONE_NUMBER.search(body)


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


def test_weather_uses_the_shared_light_and_dark_theme(monkeypatch):
    monkeypatch.setattr(
        app_module, "get_weather_for_cities", lambda: [fake_city()]
    )
    client = app_module.app.test_client()

    body = client.get("/weather").get_data(as_text=True)

    assert '<body class="site">' in body


def test_weather_styles_use_theme_tokens():
    css = (Path(app_module.app.static_folder) / "style.css").read_text()
    weather_rules = css[css.index(".subheader {"):css.index(".back-link {")]

    assert "#" not in weather_rules


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



def test_leetcode_returns_200():
    client = app_module.app.test_client()

    response = client.get("/leetcode")

    assert response.status_code == 200
    assert "LeetCode patterns" in response.get_data(as_text=True)


def test_leetcode_unknown_page_returns_404():
    client = app_module.app.test_client()

    assert client.get("/leetcode/not-a-page").status_code == 404


def projects_section(body):
    return body[body.index('id="projects"'):]


def test_home_has_about_then_projects_sections():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert body.count("<h1") == 1
    assert "About me</h2>" in body
    assert "Fun projects</h2>" in body
    assert body.index('id="about"') < body.index('id="projects"')


def test_home_links_every_project_section_in_order():
    client = app_module.app.test_client()

    projects = projects_section(client.get("/").get_data(as_text=True))

    positions = [projects.index(f'href="{link}"') for link in PROJECT_LINKS]
    assert positions == sorted(positions)


def test_home_project_links_all_resolve():
    client = app_module.app.test_client()

    for link in PROJECT_LINKS:
        if link == "/weather":
            continue
        assert client.get(link).status_code == 200, link


def test_home_renders_resume_from_resume_data():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert resume_data.HEADLINE in body
    assert resume_data.SUMMARY.replace("'", "&#39;") in body
    assert resume_data.EDUCATION["school"] in body
    for job in resume_data.EXPERIENCES:
        assert job["role"] in body
    for project in resume_data.PROJECTS:
        assert project["name"] in body
    for skill in resume_data.SKILLS["Languages"]:
        assert skill in body
    assert body.index('id="about"') < body.index("Experience</h3>") < body.index('id="projects"')


def test_home_drops_the_coming_soon_card():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert "Coming soon" not in body
    assert "feature-card" not in body


def test_home_omits_phone_number():
    client = app_module.app.test_client()

    body = client.get("/").get_data(as_text=True)

    assert "306" not in re.sub(r"\?v=\d+", "", body)
    assert "tel:" not in body
    assert not PHONE_NUMBER.search(body)


def test_resume_and_home_share_the_resume_markup():
    client = app_module.app.test_client()

    home = client.get("/").get_data(as_text=True)
    resume = client.get("/resume").get_data(as_text=True)

    for page in (home, resume):
        assert "Kids Caring for Kids Cancer Drive" in page
        assert "Deep Learning Specialization" in page
    assert "Experience</h2>" in resume
    assert "Experience</h3>" in home
