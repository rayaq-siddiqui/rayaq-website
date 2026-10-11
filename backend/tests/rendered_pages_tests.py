import pytest

import app as app_module
import jj_docs
import rendered_pages


@pytest.fixture(autouse=True)
def empty_cache():
    rendered_pages.clear()
    yield
    rendered_pages.clear()


def test_builds_once_and_reuses_the_result():
    calls = []

    def build():
        calls.append(1)
        return "<html>page</html>"

    assert rendered_pages.get(("jj", "fix"), build) == b"<html>page</html>"
    assert rendered_pages.get(("jj", "fix"), build) == b"<html>page</html>"
    assert len(calls) == 1


def test_does_not_cache_missing_pages():
    calls = []

    def build():
        calls.append(1)
        return None

    assert rendered_pages.get(("jj", "not-a-page"), build) is None
    assert rendered_pages.get(("jj", "not-a-page"), build) is None
    assert len(calls) == 2
    assert rendered_pages._pages == {}


def test_keys_are_independent():
    rendered_pages.get(("jj", None), lambda: "jj index")
    rendered_pages.get(("jj-dojo", None), lambda: "dojo index")
    assert rendered_pages.get(("jj", None), lambda: "other") == b"jj index"
    assert rendered_pages.get(("jj-dojo", None), lambda: "other") == b"dojo index"


def test_keeps_pages_as_utf8_bytes():
    html = rendered_pages.get(("jj", "fix"), lambda: "<p>a → b · ✓</p>")
    assert html == "<p>a → b · ✓</p>".encode("utf-8")
    assert rendered_pages._pages[("jj", "fix")] is html


def test_cached_response_matches_a_fresh_render():
    with app_module.app.test_request_context():
        fresh = jj_docs.render("fix", app_module.render_template).encode("utf-8")
    client = app_module.app.test_client()
    first = client.get("/jj/fix")
    second = client.get("/jj/fix")
    assert first.data == second.data == fresh
    assert first.headers["Content-Type"] == "text/html; charset=utf-8"
    assert first.headers["Content-Length"] == str(len(fresh))


def test_jj_route_renders_each_page_once(monkeypatch):
    real_render = jj_docs.render
    calls = []

    def counting_render(slug, render_template):
        calls.append(slug)
        return real_render(slug, render_template)

    monkeypatch.setattr(jj_docs, "render", counting_render)
    client = app_module.app.test_client()
    first = client.get("/jj/fix")
    second = client.get("/jj/fix")

    assert first.status_code == second.status_code == 200
    assert first.data == second.data
    assert calls == ["fix"]


def test_unknown_slugs_still_404_on_every_request():
    client = app_module.app.test_client()
    assert client.get("/jj/not-a-page").status_code == 404
    assert client.get("/jj/not-a-page").status_code == 404
    assert rendered_pages._pages == {}
