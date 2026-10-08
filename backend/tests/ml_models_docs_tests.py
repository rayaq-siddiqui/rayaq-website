import os
import re
from datetime import date

from markupsafe import escape

import app as app_module
import ml_models_docs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "frontend", "templates", "ml_models")
TABLE_HEADER = "<th>Component</th><th>Shape/Params</th><th>Meaning</th><th>Source</th>"


def all_urls():
    return ["/ml-models"] + [f"/ml-models/{page['slug']}" for page in ml_models_docs.ready_pages()]


def topic_urls():
    return [f"/ml-models/{page['slug']}" for page in ml_models_docs.ready_pages()]


def test_pins_are_well_formed():
    repos = {
        "pytorch": "https://github.com/pytorch/pytorch",
        "sklearn": "https://github.com/scikit-learn/scikit-learn",
        "xgboost": "https://github.com/dmlc/xgboost",
    }
    assert set(ml_models_docs.PINS) == set(repos)
    for key, pin in ml_models_docs.PINS.items():
        assert pin["repo"] == repos[key]
        assert pin["name"].strip()
        assert re.fullmatch(r"v?\d+\.\d+\.\d+", pin["tag"]), key
        assert re.fullmatch(r"[0-9a-f]{40}", pin["commit"]), key
        assert date.fromisoformat(pin["commit_date"]) <= date.fromisoformat(pin["analyzed_on"])
        assert pin["license"] in {"BSD-3-Clause", "Apache-2.0"}
        assert pin["license_path"]
    assert ml_models_docs.UPSTREAM is ml_models_docs.PINS["pytorch"]


def test_pinned_url_uses_each_pins_commit():
    for key, pin in ml_models_docs.PINS.items():
        base = f"{pin['repo']}/blob/{pin['commit']}/a/b.py"
        assert ml_models_docs.pinned_url(key, "a/b.py") == base
        assert ml_models_docs.pinned_url(key, "a/b.py", 7) == f"{base}#L7"
        assert ml_models_docs.pinned_url(key, "a/b.py", 7, 7) == f"{base}#L7"
        assert ml_models_docs.pinned_url(key, "a/b.py", 7, 12) == f"{base}#L7-L12"
    assert ml_models_docs.sklearn_url("x.py") == ml_models_docs.pinned_url("sklearn", "x.py")
    assert ml_models_docs.xgboost_url("x.cc") == ml_models_docs.pinned_url("xgboost", "x.cc")


def test_every_page_has_a_unique_slug_summary_and_sources():
    slugs = [page["slug"] for page in ml_models_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    for page in ml_models_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]
        for source in page["sources"]:
            key, _, path = source.partition(":")
            assert key in ml_models_docs.PINS, source
            assert path and not path.startswith("/"), source


def test_every_area_is_unique_and_has_pages():
    area_slugs = [area["slug"] for area in ml_models_docs.AREAS]
    assert len(area_slugs) == len(set(area_slugs)) == 12
    for area in ml_models_docs.AREAS:
        assert area["title"].strip() and area["summary"].strip()
        assert any(page["area"] == area["slug"] for page in ml_models_docs.PAGES), area["slug"]


def test_every_page_has_a_known_area_and_level():
    area_slugs = [area["slug"] for area in ml_models_docs.AREAS]
    for page in ml_models_docs.PAGES:
        assert page["area"] in area_slugs, page["slug"]
        assert page["level"] in ml_models_docs.LEVELS, page["slug"]


def test_pages_are_grouped_by_area_in_area_order():
    order = [area["slug"] for area in ml_models_docs.AREAS]
    positions = [order.index(page["area"]) for page in ml_models_docs.PAGES]
    assert positions == sorted(positions)
    grouped = ml_models_docs.pages_by_area()
    assert [group["area"]["slug"] for group in grouped] == order
    assert [page for group in grouped for page in group["pages"]] == ml_models_docs.PAGES


def test_prerequisites_are_real_pages_without_cycles():
    by_slug = {page["slug"]: page for page in ml_models_docs.PAGES}
    for page in ml_models_docs.PAGES:
        for prerequisite in page["prerequisites"]:
            assert prerequisite in by_slug, (page["slug"], prerequisite)
            assert prerequisite != page["slug"]

    state = {}

    def visit(slug, trail):
        if state.get(slug) == "done":
            return
        assert state.get(slug) != "visiting", " -> ".join(trail + [slug])
        state[slug] = "visiting"
        for prerequisite in by_slug[slug]["prerequisites"]:
            visit(prerequisite, trail + [slug])
        state[slug] = "done"

    for slug in by_slug:
        visit(slug, [])


def test_registry_matches_the_spec_inventory():
    with open(os.path.join(ROOT, "specs", "ml-models.md")) as handle:
        spec = handle.read()
    rows = re.findall(r"^\| `([a-z-]+)` \| [^|]+ \| (intro|core|advanced) \|", spec, re.M)
    assert [(page["slug"], page["level"]) for page in ml_models_docs.PAGES] == rows


def test_every_ready_page_has_a_template():
    for page in ml_models_docs.ready_pages():
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


def test_source_url_is_pinned():
    sha = ml_models_docs.UPSTREAM["commit"]
    base = f"https://github.com/pytorch/pytorch/blob/{sha}/torch/nn/modules/linear.py"

    assert ml_models_docs.source_url("torch/nn/modules/linear.py") == base
    assert ml_models_docs.source_url("torch/nn/modules/linear.py", 3) == f"{base}#L3"
    assert ml_models_docs.source_url("torch/nn/modules/linear.py", 3, 9) == f"{base}#L3-L9"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["pytorch:torch/x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["pytorch:torch/x"], "ready": False},
    ]
    monkeypatch.setattr(ml_models_docs, "PAGES", pages)

    assert ml_models_docs.find_page("a") is pages[0]
    assert ml_models_docs.find_page("b") is None


def test_render_returns_none_for_an_unknown_slug():
    assert ml_models_docs.render("missing", lambda *args, **kwargs: "") is None


def test_every_ml_models_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_and_unready_slugs_return_404():
    client = app_module.app.test_client()

    assert client.get("/ml-models/not-a-page").status_code == 404
    for page in ml_models_docs.PAGES:
        if not page["ready"]:
            assert client.get(f"/ml-models/{page['slug']}").status_code == 404


def test_every_upstream_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "/blob/main" not in body, url
        assert "/tree/main" not in body, url
        for pin in ml_models_docs.PINS.values():
            pattern = rf'href="({re.escape(pin["repo"])}/(?:blob|tree)/[^"]*)"'
            for link in re.findall(pattern, body):
                assert re.search(rf"/(?:blob|tree)/{pin['commit']}(?:/|$)", link), (url, link)


def test_every_internal_link_resolves():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for link in set(re.findall(r'href="(/ml-models[^"#?]*)', body)):
            assert client.get(link).status_code == 200, (url, link)


def test_index_lists_every_page():
    client = app_module.app.test_client()

    body = client.get("/ml-models").get_data(as_text=True)

    for page in ml_models_docs.PAGES:
        assert str(escape(page["title"])) in body
    for page in ml_models_docs.ready_pages():
        assert f'href="/ml-models/{page["slug"]}"' in body


def test_index_has_the_map_diagram_and_vocabulary_table():
    client = app_module.app.test_client()

    body = client.get("/ml-models").get_data(as_text=True)

    assert 'role="img"' in body
    assert '<title id="ml-map-title">' in body
    assert '<desc id="ml-map-desc">' in body
    assert TABLE_HEADER in body


def test_pages_show_the_pinned_release_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert ml_models_docs.UPSTREAM["tag"] in body
        assert ml_models_docs.UPSTREAM["commit"][:12] in body
        assert "BSD-3-Clause" in body


def test_ready_topic_pages_have_diagrams_tables_and_a_snippet():
    client = app_module.app.test_client()

    for url in topic_urls():
        body = client.get(url).get_data(as_text=True)
        svgs = re.findall(r"<svg\b.*?</svg>", body, re.S)
        assert len(svgs) >= 2, url
        for svg in svgs:
            assert 'role="img"' in svg, url
            assert "<title" in svg and "<desc" in svg, url
        assert TABLE_HEADER in body, url
        assert "<pre><code" in body, url


def test_pages_load_nothing_from_other_origins():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert not re.search(r'<script[^>]*\bsrc="(?:https?:)?//', body), url
        assert not re.search(r'<link[^>]*\bhref="(?:https?:)?//', body), url
        assert not re.search(r'<img[^>]*\bsrc="(?:https?:)?//', body), url


def test_torch_is_never_a_server_dependency():
    for name in ["requirements.txt", "requirements-dev.txt"]:
        with open(os.path.join(ROOT, "backend", name)) as handle:
            lines = [line.split("#")[0].strip().lower() for line in handle]
        assert not any(re.match(r"torch\b", line) for line in lines), name


def test_upcoming_model_slugs_are_registered_pages():
    slugs = {page["slug"] for page in ml_models_docs.PAGES}

    for tier in ml_models_docs.UPCOMING_MODELS:
        for model in tier["models"]:
            assert model["name"].strip() and model["idea"].strip() and model["paper"].strip()
            if model.get("slug"):
                assert model["slug"] in slugs, model["name"]
            if model.get("url"):
                assert model["url"].startswith("https://arxiv.org/abs/"), model["name"]

def test_index_lists_every_upcoming_model():
    client = app_module.app.test_client()

    body = client.get("/ml-models").get_data(as_text=True)

    assert 'id="upcoming"' in body
    for tier in ml_models_docs.UPCOMING_MODELS:
        assert str(escape(tier["tier"])) in body
        for model in tier["models"]:
            assert str(escape(model["name"])) in body

def test_attention_weights_rows_are_distributions():
    for causal in [False, True]:
        result = ml_models_docs.attention_weights(ml_models_docs.ATTENTION_EXAMPLE, causal=causal)
        for row in result["weights"]:
            assert abs(sum(row) - 1) < 1e-9
            assert all(weight >= 0 for weight in row)


def test_attention_weights_match_the_worked_example():
    full = ml_models_docs.attention_weights(ml_models_docs.ATTENTION_EXAMPLE)
    causal = ml_models_docs.attention_weights(ml_models_docs.ATTENTION_EXAMPLE, causal=True)

    assert [round(w, 2) for w in full["weights"][2]] == [0.04, 0.73, 0.18, 0.04]
    assert [round(x, 2) for x in full["outputs"][2]] == [0.22, 0.91]
    assert causal["weights"][0] == [1.0, 0.0, 0.0, 0.0]
    for i, row in enumerate(causal["weights"]):
        assert all(weight == 0 for weight in row[i + 1:])
        assert all(score is None for score in causal["scores"][i][i + 1:])


def test_unscaled_attention_is_sharper():
    scaled = ml_models_docs.attention_weights(ml_models_docs.ATTENTION_EXAMPLE)
    unscaled = ml_models_docs.attention_weights(ml_models_docs.ATTENTION_EXAMPLE, scaled=False)

    assert max(unscaled["weights"][2]) > max(scaled["weights"][2])


def test_param_count_matches_nn_transformer_defaults():
    count = ml_models_docs.transformer_param_count(512, 6, 6, 2048)

    assert count["attention"] == 1_050_624
    assert count["feed_forward"] == 2_099_712
    assert count["encoder_layer"] == 3_152_384
    assert count["decoder_layer"] == 4_204_032
    assert count["total"] == 44_140_544

def test_transformer_page_has_its_interactive_pieces_and_fallbacks():
    client = app_module.app.test_client()

    body = client.get("/ml-models/transformer").get_data(as_text=True)

    assert "data-ml-attention" in body
    assert "data-ml-attention-static" in body
    assert "data-ml-params" in body
    assert "44,140,544" in body
    assert 'id="references"' in body
    assert "arxiv.org/abs/1706.03762" in body
