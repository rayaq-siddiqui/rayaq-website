import os
import re
from datetime import date

from markupsafe import escape

import app as app_module
import jj_cloud_docs

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates", "jj_cloud"
)



def all_urls():
    return ["/jj-commit-cloud-poc"] + [f"/jj-commit-cloud-poc/{page['slug']}" for page in jj_cloud_docs.ready_pages()]


def test_pin_is_well_formed():
    assert re.fullmatch(r"[0-9a-f]{40}", jj_cloud_docs.UPSTREAM["commit"])
    date.fromisoformat(jj_cloud_docs.UPSTREAM["commit_date"])
    date.fromisoformat(jj_cloud_docs.UPSTREAM["analyzed_on"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", jj_cloud_docs.UPSTREAM["jj_lib_version"])
    assert jj_cloud_docs.UPSTREAM["repo"] == "https://github.com/jj-vcs/jj-commit-cloud-poc"


def test_every_page_has_a_unique_slug_summary_and_sources():
    slugs = [page["slug"] for page in jj_cloud_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    for page in jj_cloud_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]


def test_every_ready_page_has_a_template():
    for page in jj_cloud_docs.ready_pages():
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


def test_source_url_is_pinned():
    sha = jj_cloud_docs.UPSTREAM["commit"]
    base = f"https://github.com/jj-vcs/jj-commit-cloud-poc/blob/{sha}/server/src/hash_utils.rs"

    assert jj_cloud_docs.source_url("server/src/hash_utils.rs") == base
    assert jj_cloud_docs.source_url("server/src/hash_utils.rs", 3) == f"{base}#L3"
    assert jj_cloud_docs.source_url("server/src/hash_utils.rs", 3, 9) == f"{base}#L3-L9"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["x"], "ready": False},
    ]
    monkeypatch.setattr(jj_cloud_docs, "PAGES", pages)

    assert jj_cloud_docs.find_page("a") is pages[0]
    assert jj_cloud_docs.find_page("b") is None


def test_render_returns_none_for_an_unknown_slug():
    assert jj_cloud_docs.render("missing", lambda *args, **kwargs: "") is None


def test_proto_items_are_unique_identifiers():
    assert len(jj_cloud_docs.PROTO_ITEMS) == len(set(jj_cloud_docs.PROTO_ITEMS))
    for name in jj_cloud_docs.PROTO_ITEMS:
        assert re.fullmatch(r"[A-Z]\w*", name)


def test_jj_lib_url_is_pinned_to_the_crate_version():
    tag = f"v{jj_cloud_docs.UPSTREAM['jj_lib_version']}"
    base = f"https://github.com/jj-vcs/jj/blob/{tag}/lib/src/store.rs"

    assert jj_cloud_docs.jj_lib_url("lib/src/store.rs") == base
    assert jj_cloud_docs.jj_lib_url("lib/src/store.rs", 5, 8) == f"{base}#L5-L8"


def test_every_jj_cloud_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_and_unready_slugs_return_404():
    client = app_module.app.test_client()

    assert client.get("/jj-commit-cloud-poc/not-a-page").status_code == 404
    for page in jj_cloud_docs.PAGES:
        if not page["ready"]:
            assert client.get(f"/jj-commit-cloud-poc/{page['slug']}").status_code == 404


def test_every_upstream_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()
    sha = jj_cloud_docs.UPSTREAM["commit"]

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "jj-commit-cloud-poc/blob/main" not in body, url
        for link in re.findall(r'href="(https://github\.com/jj-vcs/jj-commit-cloud-poc/(?:blob|tree)/[^"]*)"', body):
            assert f"/{sha}" in link, (url, link)
        tag = f"v{jj_cloud_docs.UPSTREAM['jj_lib_version']}"
        for link in re.findall(r'href="(https://github\.com/jj-vcs/jj/(?:blob|tree)/[^"]*)"', body):
            assert re.search(rf"/(?:blob|tree)/{re.escape(tag)}(?:/|$)", link), (url, link)


def test_every_internal_link_resolves():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for link in set(re.findall(r'href="(/jj-commit-cloud-poc[^"#?]*)', body)):
            assert client.get(link).status_code == 200, (url, link)


def test_index_lists_every_page_and_links_to_jj():
    client = app_module.app.test_client()

    body = client.get("/jj-commit-cloud-poc").get_data(as_text=True)

    for page in jj_cloud_docs.PAGES:
        assert str(escape(page["title"])) in body
    for page in jj_cloud_docs.ready_pages():
        assert f'href="/jj-commit-cloud-poc/{page["slug"]}"' in body
    assert 'href="/jj"' in body


def test_pages_show_the_pinned_commit_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert jj_cloud_docs.UPSTREAM["commit"][:12] in body
        assert "Apache-2.0" in body


def test_index_has_the_architecture_diagram():
    client = app_module.app.test_client()

    body = client.get("/jj-commit-cloud-poc").get_data(as_text=True)

    if "<svg" not in body:
        return
    assert 'role="img"' in body
    assert '<title id="cc-arch-title">' in body
    assert '<desc id="cc-arch-desc">' in body


def test_protobufs_page_names_every_proto_item():
    if jj_cloud_docs.find_page("protobufs") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-commit-cloud-poc/protobufs").get_data(as_text=True)

    for name in jj_cloud_docs.PROTO_ITEMS:
        assert re.search(rf"\b{name}\b", body), name
