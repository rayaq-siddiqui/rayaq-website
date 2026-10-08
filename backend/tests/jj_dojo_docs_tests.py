import os
import re
from datetime import date

import app as app_module
import jj_dojo_docs

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates", "jj_dojo"
)



def all_urls():
    return ["/jj-dojo"] + [f"/jj-dojo/{page['slug']}" for page in jj_dojo_docs.ready_pages()]


def test_pin_is_well_formed():
    assert re.fullmatch(r"[0-9a-f]{40}", jj_dojo_docs.UPSTREAM["commit"])
    date.fromisoformat(jj_dojo_docs.UPSTREAM["commit_date"])
    date.fromisoformat(jj_dojo_docs.UPSTREAM["analyzed_on"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", jj_dojo_docs.UPSTREAM["version"])
    assert jj_dojo_docs.UPSTREAM["repo"] == "https://github.com/jj-vcs/jj-dojo"


def test_every_page_has_a_unique_slug_summary_and_sources():
    slugs = [page["slug"] for page in jj_dojo_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    for page in jj_dojo_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]


def test_every_ready_page_has_a_template():
    for page in jj_dojo_docs.ready_pages():
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


def test_source_url_is_pinned():
    sha = jj_dojo_docs.UPSTREAM["commit"]
    base = f"https://github.com/jj-vcs/jj-dojo/blob/{sha}/src/extension.ts"

    assert jj_dojo_docs.source_url("src/extension.ts") == base
    assert jj_dojo_docs.source_url("src/extension.ts", 3) == f"{base}#L3"
    assert jj_dojo_docs.source_url("src/extension.ts", 3, 9) == f"{base}#L3-L9"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["x"], "ready": False},
    ]
    monkeypatch.setattr(jj_dojo_docs, "PAGES", pages)

    assert jj_dojo_docs.find_page("a") is pages[0]
    assert jj_dojo_docs.find_page("b") is None


def test_render_returns_none_for_an_unknown_slug():
    assert jj_dojo_docs.render("missing", lambda *args, **kwargs: "") is None


def test_protocol_types_are_unique_identifiers():
    assert len(jj_dojo_docs.PROTOCOL_TYPES) == len(set(jj_dojo_docs.PROTOCOL_TYPES))
    for name in jj_dojo_docs.PROTOCOL_TYPES:
        assert re.fullmatch(r"[A-Z]\w*", name)


def test_every_jj_dojo_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_and_unready_slugs_return_404():
    client = app_module.app.test_client()

    assert client.get("/jj-dojo/not-a-page").status_code == 404
    for page in jj_dojo_docs.PAGES:
        if not page["ready"]:
            assert client.get(f"/jj-dojo/{page['slug']}").status_code == 404


def test_every_upstream_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()
    sha = jj_dojo_docs.UPSTREAM["commit"]

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "jj-dojo/blob/main" not in body, url
        for link in re.findall(r'href="(https://github\.com/jj-vcs/jj-dojo/(?:blob|tree)/[^"]*)"', body):
            assert f"/{sha}" in link, (url, link)


def test_every_internal_link_resolves():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for link in set(re.findall(r'href="(/jj-dojo[^"#?]*)', body)):
            assert client.get(link).status_code == 200, (url, link)


def test_index_lists_every_page_and_links_to_jj():
    client = app_module.app.test_client()

    body = client.get("/jj-dojo").get_data(as_text=True)

    for page in jj_dojo_docs.PAGES:
        assert page["title"] in body
    for page in jj_dojo_docs.ready_pages():
        assert f'href="/jj-dojo/{page["slug"]}"' in body
    assert 'href="/jj"' in body


def test_pages_show_the_pinned_commit_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert jj_dojo_docs.UPSTREAM["commit"][:12] in body
        assert "Apache-2.0" in body


def test_graph_protocol_names_every_protocol_type():
    if jj_dojo_docs.find_page("graph-protocol") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/graph-protocol").get_data(as_text=True)

    for name in jj_dojo_docs.PROTOCOL_TYPES:
        assert re.search(rf"\b{name}\b", body), name


def test_graph_layout_covers_every_required_section_with_diagrams():
    if jj_dojo_docs.find_page("graph-layout") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/graph-layout").get_data(as_text=True)

    for anchor in ["input", "pipeline", "lanes", "drawing", "ranges", "focus-mode", "worked-example", "invariants"]:
        assert f'<h2 id="{anchor}">' in body, anchor
    assert body.count('<svg viewBox') >= 2
    assert "preprocess_test.ts" in body


def test_graph_webview_covers_every_required_section_with_diagrams():
    if jj_dojo_docs.find_page("graph-webview") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/graph-webview").get_data(as_text=True)

    for anchor in ["shell", "rows", "top-bar", "search", "drag-and-drop", "context-menus", "resize", "safe-html", "styles"]:
        assert f'<h2 id="{anchor}">' in body, anchor
    assert body.count('<svg viewBox') >= 2
    for name in ["search_box_state", "search_highlighter", "safeHTML", "JjResizeController", "isNoopInsert"]:
        assert name in body, name


def test_icon_theme_covers_lookup_parsing_model_and_caching():
    if jj_dojo_docs.find_page("icon-theme") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/icon-theme").get_data(as_text=True)

    for anchor in ["locate", "parse", "model", "service", "caching", "tests", "gaps"]:
        assert f'<h2 id="{anchor}">' in body, anchor
    for name in ["IconTheme", "IconThemeDocument", "IconDefinition", "ThemeFont", "FileIcon", "FileFont", "jsonc-parser"]:
        assert name in body, name


def test_utils_covers_every_helper():
    if jj_dojo_docs.find_page("utils") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/utils").get_data(as_text=True)

    for anchor in ["hashmap", "hashset", "check", "dispose", "time", "gaps"]:
        assert f'<h2 id="{anchor}">' in body, anchor


def test_build_and_test_covers_bazel_tests_and_ci():
    if jj_dojo_docs.find_page("build-and-test") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj-dojo/build-and-test").get_data(as_text=True)

    for anchor in ["module", "targets", "deps", "rules", "testing", "ci", "gaps"]:
        assert f'<h2 id="{anchor}">' in body, anchor
    for name in ["//:extension", "//:vsix", "jasmine_test", "installVscode", "addlicense"]:
        assert name in body, name
