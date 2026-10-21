import os
import re
from datetime import date

from markupsafe import escape

import app as app_module
import rml_docs

TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates", "rml"
)

DECODER_ANCHORS = [
    "config", "weights", "forward-pass", "attention-kv-cache", "rope", "moe", "families",
]


def all_urls():
    return ["/rml"] + [f"/rml/{page['slug']}" for page in rml_docs.ready_pages()]


def test_pin_is_well_formed():
    assert re.fullmatch(r"[0-9a-f]{40}", rml_docs.UPSTREAM["commit"])
    date.fromisoformat(rml_docs.UPSTREAM["commit_date"])
    date.fromisoformat(rml_docs.UPSTREAM["analyzed_on"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", rml_docs.UPSTREAM["version"])
    assert rml_docs.UPSTREAM["license"] == "Apache-2.0"
    assert rml_docs.UPSTREAM["repo"] == "https://github.com/rayaq-siddiqui/rml"


def test_every_page_has_a_unique_slug_title_summary_and_sources():
    slugs = [page["slug"] for page in rml_docs.PAGES]
    titles = [page["title"] for page in rml_docs.PAGES]
    summaries = [page["summary"] for page in rml_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    assert len(titles) == len(set(titles))
    assert len(summaries) == len(set(summaries))
    for page in rml_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]
        assert page["group"] in rml_docs.GROUPS


def test_pages_are_in_group_order():
    positions = [rml_docs.GROUPS.index(page["group"]) for page in rml_docs.PAGES]
    assert positions == sorted(positions)


def test_every_ready_page_has_a_template():
    for page in rml_docs.ready_pages():
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


def test_source_and_tree_urls_are_pinned():
    sha = rml_docs.UPSTREAM["commit"]
    base = f"https://github.com/rayaq-siddiqui/rml/blob/{sha}/rml/core/tensor.h"

    assert rml_docs.source_url("rml/core/tensor.h") == base
    assert rml_docs.source_url("rml/core/tensor.h", 3) == f"{base}#L3"
    assert rml_docs.source_url("rml/core/tensor.h", 3, 9) == f"{base}#L3-L9"
    assert rml_docs.tree_url("rml/core") == f"https://github.com/rayaq-siddiqui/rml/tree/{sha}/rml/core"
    assert rml_docs.tree_url() == f"https://github.com/rayaq-siddiqui/rml/tree/{sha}"


def test_ml_models_link_only_links_ready_pages(monkeypatch):
    monkeypatch.setattr(rml_docs.ml_models_docs, "find_page", lambda slug: {"slug": slug} if slug == "a" else None)

    assert str(rml_docs.ml_models_link("a", "A")) == '<a href="/ml-models/a">A</a>'
    assert str(rml_docs.ml_models_link("b", "B<")) == "B&lt;"


def test_page_link_only_links_ready_pages(monkeypatch):
    monkeypatch.setattr(rml_docs, "find_page", lambda slug: {"slug": slug} if slug == "a" else None)

    assert str(rml_docs.page_link("a", "A")) == '<a href="/rml/a">A</a>'
    assert str(rml_docs.page_link("a", "A", "#x")) == '<a href="/rml/a#x">A</a>'
    assert str(rml_docs.page_link("b", "B<")) == "B&lt;"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["x"], "ready": False},
    ]
    monkeypatch.setattr(rml_docs, "PAGES", pages)

    assert rml_docs.find_page("a") is pages[0]
    assert rml_docs.find_page("b") is None


def test_render_returns_none_for_an_unknown_slug():
    assert rml_docs.render("missing", lambda *args, **kwargs: "") is None


def test_every_module_and_example_is_claimed_by_a_page():
    for module in rml_docs.MODULES:
        assert rml_docs.pages_for(module), module
    sources = [source for page in rml_docs.PAGES for source in page["sources"]]
    for example in rml_docs.EXAMPLES:
        assert any(
            source == "examples" or source == f"examples/{example}" for source in sources
        ), example


def test_modules_and_examples_are_unique():
    assert len(rml_docs.EXAMPLES) == len(set(rml_docs.EXAMPLES))
    for module, stems in rml_docs.MODULES.items():
        assert module.startswith("rml/")
        assert len(stems) == len(set(stems)), module


def test_every_rml_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_and_unready_slugs_return_404():
    client = app_module.app.test_client()

    assert client.get("/rml/not-a-page").status_code == 404
    for page in rml_docs.PAGES:
        if not page["ready"]:
            assert client.get(f"/rml/{page['slug']}").status_code == 404


def test_every_upstream_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()
    sha = rml_docs.UPSTREAM["commit"]

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "rml/blob/main" not in body, url
        links = re.findall(r'href="(https://github\.com/rayaq-siddiqui/rml[^"]*)"', body)
        assert links, url
        for link in links:
            assert re.match(
                rf"https://github\.com/rayaq-siddiqui/rml/(?:blob|tree)/{sha}(?:/|#|$)", link
            ), (url, link)


def test_every_internal_link_resolves():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for link in set(re.findall(r'href="(/(?:rml|ml-models)[^"#?]*)', body)):
            assert client.get(link).status_code == 200, (url, link)


def test_index_lists_every_page():
    client = app_module.app.test_client()

    body = client.get("/rml").get_data(as_text=True)

    for page in rml_docs.PAGES:
        assert str(escape(page["title"])) in body
    for page in rml_docs.ready_pages():
        assert f'href="/rml/{page["slug"]}"' in body


def test_index_diagram_is_accessible():
    client = app_module.app.test_client()

    body = client.get("/rml").get_data(as_text=True)

    svg = body[body.index("<svg"):body.index("</svg>")]
    assert 'role="img"' in svg
    assert "<title" in svg
    assert "<desc" in svg


def test_pages_show_the_pinned_commit_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert rml_docs.UPSTREAM["commit"][:12] in body
        assert "Apache-2.0" in body


def test_decoder_page_has_its_sections_and_diagrams():
    if rml_docs.find_page("decoder") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/rml/decoder").get_data(as_text=True)

    positions = [body.index(f'<h2 id="{anchor}"') for anchor in DECODER_ANCHORS]
    assert positions == sorted(positions)
    assert body.count("<svg viewBox") >= 2


def test_inference_stack_leads_the_section():
    assert rml_docs.GROUPS[0] == "Inference stack"
    assert rml_docs.PAGES[0]["slug"] == "stack"


def test_stack_page_has_its_layer_diagram():
    if rml_docs.find_page("stack") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/rml/stack").get_data(as_text=True)

    assert "<svg viewBox" in body
