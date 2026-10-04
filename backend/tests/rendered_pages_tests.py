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

    assert rendered_pages.get(("jj", "fix"), build) == "<html>page</html>"
    assert rendered_pages.get(("jj", "fix"), build) == "<html>page</html>"
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
    assert rendered_pages.get(("jj", None), lambda: "other") == "jj index"
    assert rendered_pages.get(("jj-dojo", None), lambda: "other") == "dojo index"


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
