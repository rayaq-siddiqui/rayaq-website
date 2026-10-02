import os
import re
from datetime import date

import app as app_module
import jj_docs

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates", "jj")
SOURCE_LINK = re.compile(r'href="(https://github\.com/jj-vcs/jj/[^"]*)"')


def all_urls():
    return ["/jj"] + [f"/jj/{page['slug']}" for page in jj_docs.ready_pages()]


def test_pin_is_well_formed():
    assert re.fullmatch(r"[0-9a-f]{40}", jj_docs.UPSTREAM["commit"])
    date.fromisoformat(jj_docs.UPSTREAM["commit_date"])
    date.fromisoformat(jj_docs.UPSTREAM["analyzed_on"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", jj_docs.UPSTREAM["version"])
    assert jj_docs.UPSTREAM["repo"] == "https://github.com/jj-vcs/jj"


def test_every_page_has_a_unique_slug_summary_and_sources():
    slugs = [page["slug"] for page in jj_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    for page in jj_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]


def test_every_ready_page_has_a_template():
    for page in jj_docs.ready_pages():
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


def test_source_url_is_pinned():
    sha = jj_docs.UPSTREAM["commit"]
    base = f"https://github.com/jj-vcs/jj/blob/{sha}/lib/src/fix.rs"

    assert jj_docs.source_url("lib/src/fix.rs") == base
    assert jj_docs.source_url("lib/src/fix.rs", 10) == f"{base}#L10"
    assert jj_docs.source_url("lib/src/fix.rs", 10, 10) == f"{base}#L10"
    assert jj_docs.source_url("lib/src/fix.rs", 10, 20) == f"{base}#L10-L20"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["x"], "ready": False},
    ]
    monkeypatch.setattr(jj_docs, "PAGES", pages)

    assert jj_docs.find_page("a") is pages[0]
    assert jj_docs.find_page("b") is None
    assert jj_docs.find_page("missing") is None


def test_table_of_contents_reads_h2_and_h3_with_ids():
    html = '<h1>T</h1><h2 id="one">One <code>x</code></h2><h3 id="two" class="c">Two</h3><h2>No id</h2>'

    assert jj_docs.table_of_contents(html) == [
        {"level": 2, "id": "one", "text": "One x"},
        {"level": 3, "id": "two", "text": "Two"},
    ]


def test_render_returns_none_for_an_unknown_slug():
    assert jj_docs.render("does-not-exist", lambda *args, **kwargs: "") is None


def test_proto_messages_cover_seven_files():
    assert len(jj_docs.PROTO_MESSAGES) == 7
    assert all(names for names in jj_docs.PROTO_MESSAGES.values())


def test_every_jj_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_jj_slug_returns_404():
    client = app_module.app.test_client()

    assert client.get("/jj/not-a-page").status_code == 404


def test_every_source_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()
    sha = jj_docs.UPSTREAM["commit"]

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "blob/main" not in body, url
        for link in SOURCE_LINK.findall(body):
            if "/blob/" in link or "/tree/" in link:
                assert f"/{sha}/" in link or link.endswith(f"/{sha}"), (url, link)


def test_index_lists_every_page_and_links_ready_ones():
    client = app_module.app.test_client()

    body = client.get("/jj").get_data(as_text=True)

    for page in jj_docs.PAGES:
        assert page["title"] in body
    for page in jj_docs.ready_pages():
        assert f'href="/jj/{page["slug"]}"' in body


def test_pages_show_the_pinned_commit_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert jj_docs.UPSTREAM["commit"][:12] in body
        assert "Apache-2.0" in body
