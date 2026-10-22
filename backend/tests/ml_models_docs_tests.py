import os
import math
import random
import re
from datetime import date

import pytest
from markupsafe import escape

import app as app_module
import ml_models_docs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "frontend", "templates", "ml_models")
TABLE_HEADER = "<th>Component</th><th>Shape/Params</th><th>Meaning</th><th>Source</th>"
TERM_TABLE_HEADER = "<th>Term</th><th>Shape/Params</th><th>Meaning</th><th>Source</th>"
FORMAT_SECTIONS = [
    "problem",
    "intuition",
    "mechanics",
    "worked-example",
    "implementation",
    "tradeoffs",
    "connections",
    "references",
]
FORMAT_EXEMPT = set()


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


def test_learning_path_matches_the_spec():
    slugs = {page["slug"] for page in ml_models_docs.PAGES}
    with open(os.path.join(ROOT, "specs", "ml-models.md")) as handle:
        spec = handle.read()
    section = spec[spec.index("### 4.3"):spec.index("## 5.")]
    rows = re.findall(r"^\| (\d) \| [^|]+ \| ([^|]+) \|$", section, re.M)

    assert len(rows) == len(ml_models_docs.LEARNING_PATH) == 7
    for (number, cell), step in zip(rows, ml_models_docs.LEARNING_PATH):
        assert re.findall(r"`([a-z-]+)`", cell) == step["slugs"], number
        assert step["title"].strip()
        assert set(step["slugs"]) <= slugs


def test_connections_list_prerequisites_and_what_follows():
    result = ml_models_docs.connections("chain-rule")

    assert [page["slug"] for page in result["prerequisites"]] == [
        "derivatives-and-gradients",
        "matrix-multiplication",
    ]
    assert "backpropagation" in [page["slug"] for page in result["leads_to"]]
    assert ml_models_docs.connections("tensors-and-shapes")["prerequisites"] == []


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


def test_index_groups_every_page_by_area_with_its_level():
    client = app_module.app.test_client()

    body = client.get("/ml-models").get_data(as_text=True)

    positions = [body.index(f'<h3 id="area-{area["slug"]}">{escape(area["title"])}</h3>') for area in ml_models_docs.AREAS]
    assert positions == sorted(positions)
    for group in ml_models_docs.pages_by_area():
        start = body.index(f'id="area-{group["area"]["slug"]}"')
        end = body.index("</section>", start)
        section = body[start:end]
        for page in group["pages"]:
            title = str(escape(page["title"]))
            assert title in section, page["slug"]
            after = section[section.index(title):]
            assert f'<span class="jj-badge">{page["level"]}</span>' in after.split("</li>")[0], page["slug"]


def test_index_shows_the_learning_path_in_order():
    client = app_module.app.test_client()

    body = client.get("/ml-models").get_data(as_text=True)
    path = body[body.index('<h2 id="learning-path">'):body.index('<h2 id="map">')]

    cursor = 0
    for step in ml_models_docs.learning_path():
        cursor = path.index(str(escape(step["title"])), cursor)
        for page in step["pages"]:
            if page["ready"]:
                marker = f'<a href="/ml-models/{page["slug"]}">{escape(page["title"])}</a>'
            else:
                marker = f'<span class="jj-nav-pending">{escape(page["title"])}</span>'
            cursor = path.index(marker, cursor)


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
        for key, pin in ml_models_docs.PINS.items():
            assert f"{pin['name']} {pin['tag']}" in body, (url, key)
            assert pin["commit"][:12] in body, (url, key)
            assert ml_models_docs.pinned_url(key, pin["license_path"]) in body, (url, key)
            assert pin["license"] in body, (url, key)


def test_nav_groups_every_page_under_its_area():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        nav = body[body.index('<nav class="jj-nav"'):body.index("</nav>")]
        positions = [nav.index(f"<summary>{escape(area['title'])}</summary>") for area in ml_models_docs.AREAS]
        assert positions == sorted(positions), url
        for page in ml_models_docs.PAGES:
            title = str(escape(page["title"]))
            area_index = [area["slug"] for area in ml_models_docs.AREAS].index(page["area"])
            following = positions[area_index + 1] if area_index + 1 < len(positions) else len(nav)
            assert positions[area_index] < nav.index(f">{title}</", positions[area_index]) < following, (url, page["slug"])


def test_a_page_shows_its_area_and_level_and_opens_its_nav_group():
    client = app_module.app.test_client()

    for page in ml_models_docs.ready_pages():
        body = client.get(f"/ml-models/{page['slug']}").get_data(as_text=True)
        area = ml_models_docs.find_area(page["area"])
        assert f'href="/ml-models#area-{area["slug"]}">{escape(area["title"])}</a>' in body
        assert f'<span class="jj-badge">{page["level"]}</span>' in body
        assert f'<details class="jj-nav-group" open>\n          <summary>{escape(area["title"])}</summary>' in body


def test_ready_topic_pages_have_diagrams_tables_and_a_snippet():
    client = app_module.app.test_client()

    for url in topic_urls():
        body = client.get(url).get_data(as_text=True)
        svgs = re.findall(r"<svg\b.*?</svg>", body, re.S)
        assert len(svgs) >= 2, url
        for svg in svgs:
            assert 'role="img"' in svg, url
            assert "<title" in svg and "<desc" in svg, url
        assert TABLE_HEADER in body or TERM_TABLE_HEADER in body, url
        assert "<pre><code" in body, url


def test_ready_pages_follow_the_page_format():
    client = app_module.app.test_client()

    for page in ml_models_docs.ready_pages():
        if page["slug"] in FORMAT_EXEMPT:
            continue
        body = client.get(f"/ml-models/{page['slug']}").get_data(as_text=True)
        ids = re.findall(r'<h2 id="([^"]+)"', body)
        assert [section for section in ids if section in FORMAT_SECTIONS] == FORMAT_SECTIONS, page["slug"]
        assert 'class="ml-connections"' in body, page["slug"]


def test_connections_partial_links_ready_pages_and_marks_the_rest(monkeypatch):
    pages = [dict(page) for page in ml_models_docs.PAGES]
    by_slug = {page["slug"]: page for page in pages}
    by_slug["attention"]["ready"] = True
    by_slug["embeddings"]["ready"] = False
    monkeypatch.setattr(ml_models_docs, "PAGES", pages)

    with app_module.app.test_request_context():
        html = app_module.app.jinja_env.get_template("ml_models/_connections.html").render(
            connections=ml_models_docs.connections("attention")
        )

    assert '<span class="jj-nav-pending">Embeddings</span>' in html
    assert '<a href="/ml-models/transformer">The Transformer</a>' in html
    assert 'id="connections-before"' in html and 'id="connections-after"' in html


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


def test_progress_queue_lists_every_page_after_its_prerequisites():
    with open(os.path.join(ROOT, "specs", "ml-models-progress.md")) as handle:
        progress = handle.read()
    queue_section = progress[progress.index("## Queue"):]
    queue = re.findall(r"^\d+\. `([a-z-]+)`", queue_section, re.M)

    assert sorted(queue) == sorted(page["slug"] for page in ml_models_docs.PAGES)
    position = {slug: index for index, slug in enumerate(queue)}
    for page in ml_models_docs.PAGES:
        for prerequisite in page["prerequisites"]:
            assert position[prerequisite] < position[page["slug"]], (page["slug"], prerequisite)
    for page in ml_models_docs.ready_pages():
        assert re.search(rf"^\d+\. `{page['slug']}` ✓", queue_section, re.M), page["slug"]


def test_broadcast_shape_follows_the_numpy_rules():
    assert ml_models_docs.broadcast_shape((8, 1, 6, 1), (7, 1, 5)) == (8, 7, 6, 5)
    assert ml_models_docs.broadcast_shape((32, 10, 512), (512,)) == (32, 10, 512)
    assert ml_models_docs.broadcast_shape((3, 1), (1, 4)) == (3, 4)
    assert ml_models_docs.broadcast_shape((2,), (3, 1), (1, 1, 1)) == (1, 3, 2)
    with pytest.raises(ValueError):
        ml_models_docs.broadcast_shape((3,), (4,))


def test_broadcast_steps_pad_on_the_left():
    steps = ml_models_docs.broadcast_steps((7, 1, 5), (8, 1, 6, 1))
    assert steps["padded"] == [(1, 7, 1, 5), (8, 1, 6, 1)]
    assert [step["result"] for step in steps["steps"]] == [8, 7, 6, 5]


def test_strides_and_offsets_of_a_contiguous_tensor():
    strides = ml_models_docs.contiguous_strides((2, 3, 4))
    assert strides == (12, 4, 1)
    assert ml_models_docs.element_offset((1, 2, 3), strides) == 23
    assert ml_models_docs.is_contiguous((2, 3, 4), strides)


def test_transpose_swaps_strides_and_breaks_contiguity():
    shape, strides = ml_models_docs.transpose_layout((2, 3, 4), (12, 4, 1), 0, 1)
    assert (shape, strides) == ((3, 2, 4), (4, 12, 1))
    assert not ml_models_docs.is_contiguous(shape, strides)
    assert ml_models_docs.element_offset((2, 1, 3), strides) == 23
    assert ml_models_docs.is_contiguous((1, 4), (99, 1))


def test_dot_product_and_norms():
    assert ml_models_docs.dot_product([2, 3], [2, 1]) == 7
    assert ml_models_docs.vector_norm([3, 4]) == 5
    assert ml_models_docs.vector_norm([3, -4], p=1) == 7
    assert ml_models_docs.vector_norm([3, -4], p=math.inf) == 4
    with pytest.raises(ValueError):
        ml_models_docs.dot_product([1, 2], [1, 2, 3])


def test_cosine_similarity_ignores_length_and_guards_zero():
    assert ml_models_docs.cosine_similarity([1, 2], [2, 4]) == pytest.approx(1)
    assert ml_models_docs.cosine_similarity([1, 2], [-2, 1]) == 0
    assert ml_models_docs.cosine_similarity([0, 0], [1, 0]) == 0
    assert ml_models_docs.angle_degrees([1, 0], [0, 3]) == pytest.approx(90)


def test_projection_leaves_an_orthogonal_residual():
    parts = ml_models_docs.projection([2, 2], [3, 1])
    assert parts["scale"] == pytest.approx(0.8)
    assert parts["along"] == pytest.approx([2.4, 0.8])
    assert ml_models_docs.dot_product(parts["residual"], [3, 1]) == pytest.approx(0)


def test_similarity_ranking_shows_dot_product_rewards_length():
    ranking = ml_models_docs.similarity_ranking(ml_models_docs.SIMILARITY_EXAMPLE)
    assert ranking["by_dot"] == ["d1", "d4", "d2", "d3"]
    assert ranking["by_cosine"] == ["d1", "d2", "d4", "d3"]
    assert ranking["by_distance"][0] == "d2"


def test_matmul_is_rows_dotted_with_columns():
    example = ml_models_docs.MATMUL_EXAMPLE
    assert ml_models_docs.matmul(example["a"], example["b"]) == [[58, 64], [139, 154]]
    assert ml_models_docs.matmul([[1, 2], [3, 4]], ml_models_docs.identity(2)) == [[1, 2], [3, 4]]


def test_matmul_rejects_mismatched_inner_sizes():
    with pytest.raises(ValueError, match="inner sizes differ"):
        ml_models_docs.matmul([[1, 2, 3]], [[1, 2, 3]])


def test_transpose_of_a_product_reverses_the_order():
    a, b = ml_models_docs.MATMUL_EXAMPLE["a"], ml_models_docs.MATMUL_EXAMPLE["b"]
    t = ml_models_docs.transpose
    assert t(ml_models_docs.matmul(a, b)) == ml_models_docs.matmul(t(b), t(a))


@pytest.mark.parametrize(
    "first, second, expected",
    [
        ((3,), (3,), ()),
        ((2, 3), (3, 4), (2, 4)),
        ((3,), (3, 4), (4,)),
        ((2, 3), (3,), (2,)),
        ((10, 2, 3), (3, 4), (10, 2, 4)),
        ((5, 1, 2, 3), (7, 3, 4), (5, 7, 2, 4)),
        ((10, 3), (8, 3, 4), (8, 10, 4)),
    ],
)
def test_matmul_shape_follows_torch_matmul_rules(first, second, expected):
    assert ml_models_docs.matmul_shape(first, second) == expected


@pytest.mark.parametrize("first, second", [((3,), (4,)), ((2, 3), (4, 5)), ((2, 2, 3), (3, 3, 4))])
def test_matmul_shape_rejects_incompatible_shapes(first, second):
    with pytest.raises(ValueError):
        ml_models_docs.matmul_shape(first, second)


def test_matmul_flops_count_a_multiply_and_an_add_per_term():
    assert ml_models_docs.matmul_flops(2, 3, 2) == 24
    assert ml_models_docs.matmul_flops(2048, 4096, 4096) == 68_719_476_736


def test_linear_layer_multiplies_by_the_transposed_weight_and_adds_bias():
    example = ml_models_docs.LINEAR_EXAMPLE
    assert ml_models_docs.linear_layer(example["x"], example["weight"], example["bias"]) == [[-2, 4], [-2, 8.5]]


def test_inverse_2x2_undoes_the_matrix():
    matrix = ml_models_docs.INVERSE_EXAMPLE
    inverse = ml_models_docs.inverse_2x2(matrix)
    assert inverse == [[1, -1], [-1, 2]]
    assert ml_models_docs.matmul(matrix, inverse) == ml_models_docs.identity(2)
    with pytest.raises(ValueError, match="singular"):
        ml_models_docs.inverse_2x2([[1, 2], [2, 4]])


def test_slope_table_secants_approach_the_derivative():
    table = ml_models_docs.slope_table(ml_models_docs.SLOPE_EXAMPLE)
    assert table["exact"] == 6
    errors = [row["error"] for row in table["rows"]]
    assert errors == pytest.approx(ml_models_docs.SLOPE_EXAMPLE["steps"], rel=1e-6)
    assert errors == sorted(errors, reverse=True)


def test_numerical_gradient_matches_the_bowl_gradient():
    scale = ml_models_docs.BOWL_EXAMPLE["scale"]
    point = [3, 2]
    numeric = ml_models_docs.numerical_gradient(lambda p: ml_models_docs.bowl(p, scale), point)
    assert numeric == pytest.approx(ml_models_docs.bowl_gradient(point, scale), rel=1e-6)
    assert ml_models_docs.bowl_gradient(point, scale) == [6, 12]


def test_numerical_jacobian_matches_the_exact_jacobian():
    point = ml_models_docs.JACOBIAN_EXAMPLE["point"]
    exact = ml_models_docs.jacobian_example_exact(point)
    numeric = ml_models_docs.numerical_jacobian(ml_models_docs.jacobian_example_function, point)
    assert exact == [[3, 2], [1, 6]]
    for row, expected in zip(numeric, exact):
        assert row == pytest.approx(expected, rel=1e-6)


def test_bowl_descent_shrinks_each_coordinate_by_a_constant_factor():
    steps = ml_models_docs.bowl_descent(ml_models_docs.BOWL_EXAMPLE)
    assert len(steps) == ml_models_docs.BOWL_EXAMPLE["steps"] + 1
    assert steps[0]["value"] == 21
    assert steps[1]["point"] == pytest.approx([2.4, 0.8])
    assert steps[2]["point"] == pytest.approx([1.92, 0.32])
    values = [step["value"] for step in steps]
    assert values == sorted(values, reverse=True)


def test_bowl_descent_diverges_above_the_stable_learning_rate():
    example = ml_models_docs.BOWL_EXAMPLE
    assert ml_models_docs.stable_learning_rate(example["scale"]) == pytest.approx(1 / 3)
    steps = ml_models_docs.bowl_descent(example, lr=example["unstable_lr"])
    assert steps[1]["point"] == pytest.approx([0.6, -2.8])
    values = [step["value"] for step in steps]
    assert values[1:] == sorted(values[1:])


def test_bowl_contours_are_ellipses_through_equal_values():
    scale = ml_models_docs.BOWL_EXAMPLE["scale"]
    for contour in ml_models_docs.bowl_contours(scale, [1, 4, 9]):
        rx, ry = contour["radii"]
        assert ml_models_docs.bowl([rx, 0], scale) == pytest.approx(contour["level"])
        assert ml_models_docs.bowl([0, ry], scale) == pytest.approx(contour["level"])


def test_scalar_chain_multiplies_local_derivatives():
    chain = ml_models_docs.scalar_chain(ml_models_docs.CHAIN_EXAMPLE)
    assert (chain["u"], chain["f"]) == (4, 16)
    assert chain["df_dx"] == chain["df_du"] * chain["du_dx"] == 24
    f = lambda x: (3 * x + 1) ** 2
    assert ml_models_docs.numerical_gradient(lambda p: f(p[0]), [1])[0] == pytest.approx(24, rel=1e-6)


def test_two_layer_pass_has_the_hand_derived_values():
    result = ml_models_docs.two_layer_pass(ml_models_docs.TWO_LAYER_EXAMPLE)
    assert result["z1"] == [2, -1]
    assert result["h"] == [2, 0]
    assert result["y"] == 4
    assert result["loss"] == 0.5
    assert result["dw2"] == [2, 0]
    assert result["dh"] == [2, 3]
    assert result["dz1"] == [2, 0]
    assert result["dw1"] == [[4, 2], [0, 0]]
    assert result["dx"] == [2, -2]


def test_two_layer_gradients_match_finite_differences():
    example = ml_models_docs.TWO_LAYER_EXAMPLE
    result = ml_models_docs.two_layer_pass(example)
    loss = ml_models_docs.two_layer_loss

    def w1_loss(flat):
        return loss(example["x"], [flat[:2], flat[2:]], example["b1"], example["w2"], example["b2"], example["target"])

    flat_w1 = example["w1"][0] + example["w1"][1]
    numeric = ml_models_docs.numerical_gradient(w1_loss, flat_w1)
    assert numeric == pytest.approx(result["dw1"][0] + result["dw1"][1], abs=1e-6)

    def x_loss(x):
        return loss(x, example["w1"], example["b1"], example["w2"], example["b2"], example["target"])

    assert ml_models_docs.numerical_gradient(x_loss, example["x"]) == pytest.approx(result["dx"], abs=1e-6)

    def w2_loss(w2):
        return loss(example["x"], example["w1"], example["b1"], w2, example["b2"], example["target"])

    assert ml_models_docs.numerical_gradient(w2_loss, example["w2"]) == pytest.approx(result["dw2"], abs=1e-6)


def test_reverse_mode_costs_one_pass_per_output():
    costs = ml_models_docs.mode_costs(ml_models_docs.MODE_COST_EXAMPLE["widths"])
    assert costs["per_pass"] == 2_001_000
    assert costs["reverse"] == costs["per_pass"]
    assert costs["forward"] == 1000 * costs["per_pass"]


def test_bernoulli_pmf_sums_to_one():
    p = ml_models_docs.BERNOULLI_EXAMPLE["p"]
    assert ml_models_docs.bernoulli_pmf(1, p) == p
    assert ml_models_docs.bernoulli_pmf(0, p) + ml_models_docs.bernoulli_pmf(1, p) == pytest.approx(1)


def test_categorical_from_logits_is_a_stable_softmax():
    result = ml_models_docs.categorical_from_logits(ml_models_docs.CATEGORICAL_EXAMPLE["logits"])
    assert sum(result["probs"]) == pytest.approx(1)
    assert result["probs"] == pytest.approx([0.6652, 0.2447, 0.0900], abs=1e-4)
    shifted = ml_models_docs.categorical_from_logits([v + 1000 for v in ml_models_docs.CATEGORICAL_EXAMPLE["logits"]])
    assert shifted["probs"] == pytest.approx(result["probs"])


def test_inverse_cdf_sampling_follows_the_cumulative_sums():
    example = ml_models_docs.CATEGORICAL_EXAMPLE
    probs = ml_models_docs.categorical_from_logits(example["logits"])["probs"]
    samples = [ml_models_docs.inverse_cdf_sample(probs, u) for u in example["uniforms"]]
    assert samples == [0, 0, 1, 2]
    grid = [(i + 0.5) / 1000 for i in range(1000)]
    counts = [0, 0, 0]
    for u in grid:
        counts[ml_models_docs.inverse_cdf_sample(probs, u)] += 1
    assert [c / 1000 for c in counts] == pytest.approx(probs, abs=1e-3)


def test_normal_density_matches_the_closed_form():
    assert ml_models_docs.normal_pdf(0, 0, 1) == pytest.approx(0.398942, abs=1e-6)
    assert ml_models_docs.normal_log_prob(2, 0, 1) == pytest.approx(-2.918939, abs=1e-6)
    assert ml_models_docs.normal_pdf(3, 1, 2) == pytest.approx(ml_models_docs.normal_pdf(1, 0, 1) / 2)
    assert ml_models_docs.normal_cdf(0, 0, 1) == 0.5
    assert [ml_models_docs.normal_band(k) for k in (1, 2, 3)] == pytest.approx([0.6827, 0.9545, 0.9973], abs=1e-4)


def test_joint_table_marginals_conditionals_and_independence():
    table = ml_models_docs.joint_table(ml_models_docs.JOINT_EXAMPLE)
    assert table["total"] == 100
    assert table["row_marginal"] == pytest.approx([0.3, 0.7])
    assert table["column_marginal"] == pytest.approx([0.31, 0.69])
    assert table["given_row"][0] == pytest.approx([0.8, 0.2])
    assert table["given_column"][0][0] == pytest.approx(24 / 31)
    assert table["independent"] is False
    assert ml_models_docs.joint_table({"counts": [[6, 4], [12, 8]]})["independent"] is True


def test_die_expectation_and_variance():
    values = ml_models_docs.DIE_EXAMPLE["values"]
    probs = [1 / 6] * 6
    assert ml_models_docs.expectation(values, probs) == pytest.approx(3.5)
    assert ml_models_docs.variance(values, probs) == pytest.approx(35 / 12)
    doubled = [2 * v + 3 for v in values]
    assert ml_models_docs.expectation(doubled, probs) == pytest.approx(10)
    assert ml_models_docs.variance(doubled, probs) == pytest.approx(4 * 35 / 12)


def test_covariance_and_correlation():
    result = ml_models_docs.covariance(ml_models_docs.COVARIANCE_EXAMPLE["pairs"])
    assert result["cov"] == pytest.approx(15)
    assert result["var_x"] == pytest.approx(2)
    assert result["corr"] == pytest.approx(15 / math.sqrt(2 * 118.8))
    assert ml_models_docs.covariance([(-2, 4), (-1, 1), (0, 0), (1, 1), (2, 4)])["cov"] == pytest.approx(0)


def test_running_means_converge_within_the_standard_error():
    example = ml_models_docs.DIE_EXAMPLE
    rolls = ml_models_docs.die_rolls(example["checkpoints"][-1], example["seed"])
    assert set(rolls) == set(example["values"])
    assert ml_models_docs.die_rolls(10, example["seed"]) == rolls[:10]
    rows = ml_models_docs.running_means(rolls, example["values"], example["checkpoints"])
    assert [row["n"] for row in rows] == example["checkpoints"]
    assert all(abs(row["error"]) < row["standard_error"] for row in rows)
    assert rows[-1]["standard_error"] == pytest.approx(math.sqrt(35 / 12) / 100)


def test_sum_pmf_spreads_into_a_bell():
    two = ml_models_docs.sum_pmf([1, 2, 3, 4, 5, 6], 2)
    assert two[7] == pytest.approx(6 / 36)
    assert sum(two.values()) == pytest.approx(1)
    five = ml_models_docs.sum_pmf([1, 2, 3, 4, 5, 6], 5)
    assert min(five) == 5 and max(five) == 30
    assert ml_models_docs.expectation(list(five), list(five.values())) == pytest.approx(17.5)
    assert ml_models_docs.variance(list(five), list(five.values())) == pytest.approx(5 * 35 / 12)


def test_minibatch_gradients_are_unbiased_and_shrink_with_batch_size():
    example = ml_models_docs.MINIBATCH_EXAMPLE
    result = ml_models_docs.minibatch_gradients(example)
    assert result["full"] == pytest.approx(-31)
    n = len(example["x"])
    single = result["sizes"][0]["variance"]
    for size in result["sizes"]:
        b = size["batch_size"]
        assert size["count"] == math.comb(n, b)
        assert size["mean"] == pytest.approx(result["full"])
        assert size["variance"] == pytest.approx(single / b * (n - b) / (n - 1))


def test_entropy_cross_entropy_and_kl_on_the_weather_example():
    example = ml_models_docs.ENTROPY_EXAMPLE
    p, q = example["p"], example["q"]
    assert ml_models_docs.entropy(p) == pytest.approx(1.75)
    assert ml_models_docs.entropy(q) == pytest.approx(2)
    assert ml_models_docs.cross_entropy(p, q) == pytest.approx(2)
    assert ml_models_docs.kl_divergence(p, q) == pytest.approx(0.25)
    assert ml_models_docs.kl_divergence(p, p) == pytest.approx(0)
    assert ml_models_docs.information_content(0.125) == pytest.approx(3)
    assert ml_models_docs.entropy([1, 0]) == 0


def test_kl_is_asymmetric_and_infinite_where_q_has_no_mass():
    example = ml_models_docs.ASYMMETRY_EXAMPLE
    forward = ml_models_docs.kl_divergence(example["p"], example["q"])
    backward = ml_models_docs.kl_divergence(example["q"], example["p"])
    assert forward == pytest.approx(0.531, abs=1e-3)
    assert backward == pytest.approx(0.737, abs=1e-3)
    assert ml_models_docs.kl_divergence([0.5, 0.5], [1, 0]) == math.inf
    assert ml_models_docs.kl_divergence([1, 0], [0.5, 0.5]) == pytest.approx(1)


def test_logits_cross_entropy_matches_softmax_and_its_gradient():
    result = ml_models_docs.logits_cross_entropy([2.0, 1.0, 0.0], 0)
    assert result["loss"] == pytest.approx(math.log(math.e ** 2 + math.e + 1) - 2)
    assert result["loss"] == pytest.approx(-math.log(result["probs"][0]))
    assert sum(result["gradient"]) == pytest.approx(0)
    assert result["gradient"][0] == pytest.approx(result["probs"][0] - 1)
    one_hot = [1, 0, 0]
    assert result["loss"] == pytest.approx(ml_models_docs.cross_entropy(one_hot, result["probs"], base=math.e))


def test_perplexity_is_the_exponentiated_mean_negative_log_likelihood():
    example = ml_models_docs.PERPLEXITY_EXAMPLE
    result = ml_models_docs.perplexity(example)
    assert result["perplexity"] == pytest.approx(math.prod(1 / p for p in example["probs"]) ** (1 / 4))
    assert ml_models_docs.perplexity({"probs": [0.25] * 3})["perplexity"] == pytest.approx(4)


def test_mutual_information_is_zero_only_for_independent_variables():
    result = ml_models_docs.mutual_information(ml_models_docs.JOINT_EXAMPLE)
    assert result["mutual"] == pytest.approx(0.348, abs=1e-3)
    assert result["h_xy"] <= result["h_x"] + result["h_y"]
    independent = ml_models_docs.mutual_information({"counts": [[2, 6], [3, 9]]})
    assert independent["mutual"] == pytest.approx(0, abs=1e-12)


def test_huber_is_quadratic_inside_delta_and_linear_outside():
    assert ml_models_docs.huber(0.5) == pytest.approx(0.125)
    assert ml_models_docs.huber(1.0) == pytest.approx(0.5)
    assert ml_models_docs.huber(-3.0) == pytest.approx(2.5)
    assert ml_models_docs.huber(3.0, delta=2.0) == pytest.approx(4.0)
    losses = ml_models_docs.regression_losses(-3.0, delta=2.0)
    assert losses == {"mse": 9.0, "mae": 3.0, "huber": pytest.approx(4.0)}


def test_fitting_a_constant_gives_the_mean_median_and_a_robust_middle():
    example = ml_models_docs.CONSTANT_FIT_EXAMPLE
    fit = ml_models_docs.fit_constant(example["targets"], example["delta"])
    assert fit["mse"] == pytest.approx(sum(example["targets"]) / len(example["targets"]))
    assert fit["mae"] == pytest.approx(3.1)
    assert fit["huber"] == pytest.approx(3.26)
    assert fit["mae"] < fit["huber"] < fit["mse"]
    slope = sum(max(-2.0, min(2.0, fit["huber"] - y)) for y in example["targets"])
    assert slope == pytest.approx(0, abs=1e-9)


def test_bce_with_logits_is_stable_and_matches_the_naive_formula():
    for logit in [-3.0, 0.0, 2.0]:
        p = 1 / (1 + math.exp(-logit))
        for target in [0, 1]:
            naive = -(target * math.log(p) + (1 - target) * math.log(1 - p))
            assert ml_models_docs.bce_with_logits(logit, target) == pytest.approx(naive)
    assert ml_models_docs.bce_with_logits(-1000.0, 1) == pytest.approx(1000.0)
    assert ml_models_docs.bce_with_logits(1000.0, 1) == pytest.approx(0.0)


def test_margin_losses_bound_the_zero_one_loss():
    for margin in [-2.0, -0.5, 0.0, 0.5, 1.0, 2.0]:
        losses = ml_models_docs.margin_losses(margin)
        assert losses["hinge"] >= losses["zero_one"]
        assert losses["logistic"] / math.log(2) >= losses["zero_one"]
    assert ml_models_docs.margin_losses(1.5)["hinge"] == 0


def test_triplet_and_info_nce_losses():
    result = ml_models_docs.triplet_loss(ml_models_docs.TRIPLET_EXAMPLE)
    assert result["d_ap"] == pytest.approx(1.0)
    assert result["d_an"] == pytest.approx(math.sqrt(3.25))
    assert result["loss"] == pytest.approx(2 - math.sqrt(3.25))
    example = ml_models_docs.INFONCE_EXAMPLE
    warm = ml_models_docs.info_nce(example["similarities"], 1.0)
    cold = ml_models_docs.info_nce(example["similarities"], 0.1)
    assert cold["loss"] < warm["loss"]
    assert cold["loss"] == pytest.approx(math.log(1 + math.exp(-6) + math.exp(-8)))


def test_reduction_skips_ignored_targets_in_the_mean():
    result = ml_models_docs.reduce_losses(ml_models_docs.REDUCTION_EXAMPLE)
    assert result["none"] == [0.5, 1.2, 0.0, 2.0]
    assert result["sum"] == pytest.approx(3.7)
    assert result["count"] == 3
    assert result["mean"] == pytest.approx(3.7 / 3)


def test_least_squares_line_matches_the_normal_equations():
    pairs = ml_models_docs.COVARIANCE_EXAMPLE["pairs"]
    line = ml_models_docs.least_squares_line(pairs)
    assert line["slope"] == pytest.approx(7.5)
    assert line["intercept"] == pytest.approx(43.5)
    assert line["residuals"] == pytest.approx([1, 1.5, -5, 1.5, 1])
    assert sum(line["residuals"]) == pytest.approx(0)
    assert line["sse"] == pytest.approx(31.5)
    assert line["r2"] == pytest.approx(1 - 31.5 / 594)
    normal = ml_models_docs.normal_equations([[x] for x, _ in pairs], [y for _, y in pairs])
    assert normal["gram"] == [[55, 15], [15, 5]]
    assert normal["moment"] == [1065, 330]
    assert normal["solution"] == pytest.approx([7.5, 43.5])


def test_solve_linear_pivots_past_a_zero():
    assert ml_models_docs.solve_linear([[0, 1], [2, 0]], [3, 4]) == pytest.approx([2, 3])


def test_line_descent_is_slow_on_raw_features_and_fast_when_centered():
    pairs = ml_models_docs.COVARIANCE_EXAMPLE["pairs"]
    example = ml_models_docs.LINE_DESCENT_EXAMPLE
    raw = ml_models_docs.line_descent(pairs, example["raw_lr"], example["raw_steps"])
    assert raw[1] == pytest.approx([17.04, 5.28])
    assert raw[100][0] == pytest.approx(10.23, abs=0.01)
    assert abs(raw[-1][1] - 43.5) > 0.5
    centered = ml_models_docs.line_descent(pairs, example["centered_lr"], example["centered_steps"], centered=True)
    assert centered[-1] == pytest.approx([7.5, 66.0], abs=0.01)
    eigen = ml_models_docs.symmetric_eigen_2x2(ml_models_docs.mse_hessian(pairs))
    assert eigen["values"][0] / eigen["values"][1] == pytest.approx(70, abs=0.1)
    assert ml_models_docs.mse_hessian(pairs, centered=True) == [[4, 0], [0, 2]]


def test_quadratic_ellipse_points_sit_on_the_level_set():
    matrix = ml_models_docs.mse_hessian(ml_models_docs.COVARIANCE_EXAMPLE["pairs"])
    for w, b in ml_models_docs.quadratic_ellipse(matrix, [7.5, 43.5], 5.0, count=12):
        dw, db = w - 7.5, b - 43.5
        excess = 0.5 * (matrix[0][0] * dw * dw + 2 * matrix[0][1] * dw * db + matrix[1][1] * db * db)
        assert excess == pytest.approx(5.0)


def test_ridge_shares_weight_and_lasso_drops_features():
    paths = ml_models_docs.regularization_paths(ml_models_docs.REGULARIZATION_EXAMPLE)
    assert paths["corr"][0][1] == pytest.approx(19 / 21)
    assert paths["ols"] == pytest.approx([9.04, 4.51, 0.60], abs=0.01)
    ridge = {entry["alpha"]: entry["coef"] for entry in paths["ridge"]}
    assert ridge[0] == pytest.approx(paths["ols"])
    assert ridge[2][1] > ridge[0][1]
    assert ridge[80][0] / ridge[80][1] == pytest.approx(1.05, abs=0.01)
    assert all(abs(v) > 0 for v in ridge[80])
    lasso = {entry["alpha"]: entry["coef"] for entry in paths["lasso"]}
    assert lasso[0] == pytest.approx(paths["ols"], abs=1e-6)
    assert lasso[1.0] == pytest.approx([8.84, 3.69, 0.0], abs=0.01)
    first_zero = [min(a for a, coef in lasso.items() if coef[j] == 0) for j in range(3)]
    assert first_zero == [13.25, 8.25, 0.75]


def test_soft_threshold():
    assert ml_models_docs.soft_threshold(3.0, 1.0) == 2.0
    assert ml_models_docs.soft_threshold(-3.0, 1.0) == -2.0
    assert ml_models_docs.soft_threshold(0.5, 1.0) == 0.0


def test_sigmoid_is_stable_and_symmetric():
    assert ml_models_docs.sigmoid(0) == 0.5
    assert ml_models_docs.sigmoid(-1000) == 0.0
    assert ml_models_docs.sigmoid(1000) == 1.0
    for z in [-3.0, -0.5, 2.0]:
        assert ml_models_docs.sigmoid(z) + ml_models_docs.sigmoid(-z) == pytest.approx(1.0)


def test_logistic_newton_reaches_the_stationary_point():
    fit = ml_models_docs.logistic_fit_1d(ml_models_docs.LOGISTIC_EXAMPLE)
    assert fit["w"] == pytest.approx(1.4245, abs=1e-4)
    assert fit["boundary"] == pytest.approx(3.25)
    assert fit["newton"][-1]["grad_norm"] < 1e-9
    assert fit["newton"][0]["loss"] == pytest.approx(math.log(2))
    assert fit["newton_excess"][4] < 1e-7 < fit["newton_excess"][3]
    passed = ml_models_docs.LOGISTIC_EXAMPLE["passed"]
    assert sum(fit["probs"]) == pytest.approx(sum(passed))
    assert fit["descent_excess"][2000] < 1e-7 < fit["descent_excess"][500]
    assert fit["descent_final"] == pytest.approx([fit["w"], fit["b"]], abs=0.01)


def test_logistic_objective_matches_the_bce_loss():
    rows, y = [[1.0], [2.0]], [0, 1]
    expected = ml_models_docs.bce_with_logits(0.5 - 1, 0) + ml_models_docs.bce_with_logits(1.0 - 1, 1)
    assert ml_models_docs.logistic_objective(rows, y, [0.5, -1]) == pytest.approx(expected)
    assert ml_models_docs.logistic_objective(rows, y, [0.5, -1], c=2) == pytest.approx(expected + 0.25 / 4)


def test_boundary_fits_shrink_with_smaller_c_and_diverge_without_penalty():
    result = ml_models_docs.boundary_fits(ml_models_docs.BOUNDARY_EXAMPLE)
    norms = [fit["norm"] for fit in result["fits"]]
    assert norms == sorted(norms)
    assert norms[0] < 0.5 < 5 < norms[2]
    growth = result["unpenalized"]
    assert all(b["norm"] > a["norm"] for a, b in zip(growth, growth[1:]))
    assert growth[-1]["loss"] < 1e-3


def test_xor_network_solves_xor_and_no_linear_model_can():
    result = ml_models_docs.xor_network(ml_models_docs.XOR_EXAMPLE)
    assert [row["y"] for row in result["rows"]] == ml_models_docs.XOR_EXAMPLE["targets"]
    assert result["collapsed"]["outputs"] == [2, 1, 1, 0]
    assert result["best_linear"]["outputs"] == pytest.approx([0.5] * 4)


def test_collapse_linear_matches_stacked_linear_layers():
    layers = [([[1, 2], [3, 4]], [1, -1]), ([[2, 0], [1, 1]], [0, 5]), ([[1, -1]], [2])]
    weight, bias = ml_models_docs.collapse_linear(layers)
    for x in ([1, 0], [0, 1], [2, -3]):
        h = x
        for w, b in layers:
            h = [ml_models_docs.dot_product(row, h) + c for row, c in zip(w, b)]
        assert [ml_models_docs.dot_product(row, x) + c for row, c in zip(weight, bias)] == h


def test_relu_interpolant_hits_its_knots_and_improves_with_units():
    fits = ml_models_docs.approximation_fits(ml_models_docs.APPROXIMATION_EXAMPLE)
    for fit in fits:
        for k, v in zip(fit["knots"], fit["values"]):
            assert ml_models_docs.evaluate_interpolant(fit, k) == pytest.approx(v, abs=1e-12)
    assert fits[0]["max_error"] > 0.4 > 0.1 > fits[1]["max_error"]
    assert [fit["params"] for fit in fits] == [10, 25]


def test_mlp_param_count():
    counts = ml_models_docs.mlp_param_count([784, 256, 128, 10])
    assert [layer["total"] for layer in counts["layers"]] == [200960, 32896, 1290]
    assert counts["total"] == 235146
    assert ml_models_docs.mlp_param_count([512, 2048, 512])["total"] == 2099712


def test_backprop_pass_matches_finite_differences():
    example = ml_models_docs.BACKPROP_EXAMPLE
    net = ml_models_docs.backprop_example(example)["before"]
    assert net["z1"] == [1, 1, -1] and net["h"] == [1, 1, 0] and net["logits"] == [0, 1]
    assert net["loss"] == pytest.approx(math.log(1 + math.e))
    assert net["dlogits"] == pytest.approx([-0.7311, 0.7311], abs=1e-4)
    assert net["dz1"][2] == 0 and net["dw1"][2] == [0.0, 0.0]
    checks = ml_models_docs.gradient_check_all(example)
    assert len(checks) == 6 + 3 + 6 + 2
    assert max(row["error"] for row in checks) < 1e-8


def test_one_sgd_step_lowers_the_loss():
    run = ml_models_docs.backprop_example(ml_models_docs.BACKPROP_EXAMPLE)
    assert run["updated"]["w1"][0][1] == pytest.approx(0.1 * 1.4621, abs=1e-4)
    assert run["after"]["loss"] < run["before"]["loss"] / 5
    assert run["after"]["probs"][0] > 0.8


def test_gradient_check_shows_truncation_and_roundoff():
    check = ml_models_docs.gradient_check(ml_models_docs.BACKPROP_EXAMPLE, ml_models_docs.GRADIENT_CHECK_EXAMPLE)
    rows = {round(-math.log10(row["h"])): row for row in check["rows"]}
    assert rows[2]["forward_error"] == pytest.approx(10 * rows[3]["forward_error"], rel=0.05)
    assert rows[2]["central_error"] == pytest.approx(100 * rows[3]["central_error"], rel=0.05)
    best = min(check["rows"], key=lambda row: row["central_error"])
    assert 1e-7 <= best["h"] <= 1e-4 and best["central_error"] < 1e-10
    assert rows[12]["central_error"] > 1e3 * best["central_error"]


def test_gradient_norms_vanish_or_explode_with_depth():
    curves = {c["label"]: c["norms"] for c in ml_models_docs.gradient_norms_by_depth(ml_models_docs.DEPTH_EXAMPLE)}
    assert all(len(norms) == 31 and norms[-1] == 1 for norms in curves.values())
    assert curves["ReLU, gain 0.7"][0] < 1e-3
    assert 0.3 < curves["ReLU, He init"][0] < 3
    assert curves["ReLU, gain 1.4"][0] > 1e3
    assert curves["sigmoid, Xavier init"][0] < 1e-15


def test_optimizer_step_follows_pytorch_update_rules():
    step = ml_models_docs.optimizer_step
    state = {}
    assert step("momentum", [1.0], [2.0], state, {"lr": 0.1, "momentum": 0.9}) == pytest.approx([0.8])
    assert step("momentum", [0.8], [2.0], state, {"lr": 0.1, "momentum": 0.9}) == pytest.approx([0.8 - 0.1 * 3.8])
    assert step("nesterov", [1.0], [2.0], {}, {"lr": 0.1, "momentum": 0.9}) == pytest.approx([1.0 - 0.1 * 3.8])
    assert step("sgd", [1.0], [0.0], {}, {"lr": 0.1, "weight_decay": 0.5}) == pytest.approx([0.95])
    assert step("adamw", [1.0], [0.0], {}, {"lr": 0.1, "weight_decay": 0.5}) == pytest.approx([0.95])
    first = step("adam", [0.0, 0.0], [1e-3, -50.0], {}, {"lr": 0.01})
    assert first == pytest.approx([-0.01, 0.01], rel=1e-4)
    assert step("rmsprop", [0.0], [3.0], {}, {"lr": 0.01}) == pytest.approx([-0.1], rel=1e-6)


def test_optimizer_race_rewards_momentum_on_an_ill_conditioned_bowl():
    runs = {run["label"]: run for run in ml_models_docs.optimizer_race(ml_models_docs.OPTIMIZER_BOWL)}
    assert runs["SGD, lr 0.042"]["diverged"]
    assert not runs["SGD, lr 0.036"]["diverged"]
    assert runs["momentum 0.7, lr 0.03"]["final"] < runs["SGD, lr 0.036"]["final"] / 100
    assert all(len(run["path"]) == 31 for run in runs.values())
    assert sum(run["plot"] for run in runs.values()) == 3


def test_adam_trace_normalizes_gradient_scale():
    rows = ml_models_docs.adam_trace(ml_models_docs.ADAM_EXAMPLE)
    assert [row["t"] for row in rows] == [1, 2, 3]
    assert rows[0]["m"] == pytest.approx([0.002, -0.4])
    assert rows[0]["m_hat"] == pytest.approx(rows[0]["grads"])
    for row in rows:
        assert all(0.0009 < abs(u) <= 0.001 for u in row["update"])
    assert rows[-1]["params"][0] == pytest.approx(0.5 + sum(row["update"][0] for row in rows))


def test_uncorrected_adam_overshoots_early():
    ratio = ml_models_docs.uncorrected_step_ratio
    assert ratio((0.9, 0.999), 1) == pytest.approx(math.sqrt(10))
    peak = max(range(1, 200), key=lambda t: ratio((0.9, 0.999), t))
    assert 10 <= peak <= 14 and ratio((0.9, 0.999), peak) > 6.5
    assert ratio((0.9, 0.999), 5000) == pytest.approx(1, abs=0.01)


def test_l2_inside_adam_decays_quiet_weights_faster_than_adamw():
    curves = {(c["kind"], c["scale"]): c["values"] for c in ml_models_docs.weight_decay_paths(ml_models_docs.WEIGHT_DECAY_EXAMPLE)}
    assert curves[("adamw", 1.0)][200] == pytest.approx(curves[("adamw", 0.01)][200], rel=1e-6)
    assert curves[("adamw", 1.0)][200] == pytest.approx(0.999**200, rel=0.03)
    assert curves[("adam", 0.01)][200] < 0.05 < 0.7 < curves[("adam", 1.0)][200]


def test_optimizer_memory_counts_state_tensors():
    rows = {row["name"]: row for row in ml_models_docs.optimizer_memory(7e9)}
    assert rows["SGD"]["gigabytes"] == 0
    assert rows["Adam / AdamW"]["bytes_per_param"] == 8
    assert rows["Adam / AdamW"]["gigabytes"] == pytest.approx(56)


def test_newton_schulz_polynomial_matches_pinned_coefficients():
    assert ml_models_docs.MUON_EXAMPLE["coefficients"] == (3.4445, -4.7750, 2.0315)
    assert ml_models_docs.newton_schulz_polynomial(0.0) == 0
    assert ml_models_docs.newton_schulz_polynomial(1.0) == pytest.approx(0.701)
    assert ml_models_docs.newton_schulz_polynomial(0.1) > 3 * 0.1


def test_muon_newton_schulz_pushes_singular_values_toward_one():
    example = ml_models_docs.muon_example()
    first, last = example["singular"][0], example["singular"][-1]
    assert len(example["trace"]) == ml_models_docs.MUON_EXAMPLE["steps"] + 1
    assert sum(s * s for s in first) == pytest.approx(1.0)
    assert min(first) < 0.05
    assert all(0.5 < s < 1.5 for s in last)
    assert example["polar_gap"] > 0.1
    assert len(example["trace"][-1]) == 3 and len(example["trace"][-1][0]) == 4


def test_muon_newton_schulz_transposes_tall_matrices():
    wide = ml_models_docs.MUON_EXAMPLE["gradient"]
    tall = ml_models_docs.transpose(wide)
    out_wide = ml_models_docs.muon_newton_schulz(wide)[-1]
    out_tall = ml_models_docs.muon_newton_schulz(tall)[-1]
    flat_tall = [x for row in ml_models_docs.transpose(out_tall) for x in row]
    assert flat_tall == pytest.approx([x for row in out_wide for x in row])


def test_muon_adjusted_lr_follows_each_rule():
    lr = ml_models_docs.muon_adjusted_lr
    assert lr(0.02, (4096, 1024)) == pytest.approx(0.04)
    assert lr(0.02, (1024, 4096)) == pytest.approx(0.02)
    assert lr(1.0, (1024, 4096), "match_rms_adamw") == pytest.approx(12.8)
    assert lr(1.0, (1024, 4096), "spectral_unclamped") == pytest.approx(0.5)


def test_qk_clip_caps_each_head_at_tau():
    rows = ml_models_docs.qk_clip([42.0, 400.0], tau=100.0)
    assert rows[0]["gamma"] == 1.0 and rows[0]["clipped_logit"] == 42.0
    assert rows[1]["gamma"] == pytest.approx(0.25)
    assert rows[1]["scale"] == pytest.approx(0.5)
    assert rows[1]["clipped_logit"] == pytest.approx(100.0)


def test_embedding_lookup_equals_one_hot_matmul():
    example = ml_models_docs.EMBEDDING_EXAMPLE
    ids = example["batch"][0]
    looked_up = ml_models_docs.embedding_lookup(example["table"], ids)
    via_matmul = ml_models_docs.matmul(ml_models_docs.one_hot_rows(ids, len(example["vocab"])), example["table"])
    assert looked_up == via_matmul
    batch = ml_models_docs.embedding_lookup(example["table"], example["batch"])
    assert len(batch) == 2 and len(batch[0]) == 6 and len(batch[0][0]) == 3
    assert batch[1][4] == [0.0, 0.0, 0.0]


def test_embedding_gradient_accumulates_rows_and_skips_padding():
    ones = [[[1.0, 2.0]] * 3] * 2
    ids = [[1, 2, 1], [0, 1, 3]]
    grad = ml_models_docs.embedding_gradient(4, 2, ids, ones, padding_idx=0)
    assert grad[1] == [3.0, 6.0]
    assert grad[2] == [1.0, 2.0]
    assert grad[0] == [0.0, 0.0]
    mean = ml_models_docs.embedding_gradient(4, 2, ids, ones, padding_idx=0, scale_grad_by_freq=True)
    assert mean[1] == [1.0, 2.0]
    unpadded = ml_models_docs.embedding_gradient(4, 2, ids, ones)
    assert unpadded[0] == [1.0, 2.0]


def test_skipgram_pairs_use_a_symmetric_window():
    assert ml_models_docs.skipgram_pairs([["a", "b", "c"]], 1) == [("a", "b"), ("b", "a"), ("b", "c"), ("c", "b")]
    assert len(ml_models_docs.skipgram_pairs([["a", "b", "c"]], 2)) == 6


def test_skipgram_places_words_that_share_contexts_together():
    result = ml_models_docs.train_skipgram(ml_models_docs.WORD2VEC_EXAMPLE)
    vectors = result["vectors"]
    cosine = ml_models_docs.cosine_similarity
    assert result["losses"][0] > result["uniform_loss"] * 0.8
    assert result["losses"][-1] < result["losses"][0] * 0.75
    assert cosine(vectors["car"], vectors["truck"]) > 0.95
    assert cosine(vectors["fish"], vectors["meat"]) > 0.9
    assert cosine(vectors["cat"], vectors["dog"]) > 0.9
    assert cosine(vectors["cat"], vectors["car"]) < 0
    assert ml_models_docs.nearest_words(vectors, "car", 1)[0][0] in {"truck", "bus"}


def test_tied_parameter_counts_for_gpt2_small():
    counts = ml_models_docs.tied_parameter_counts(50257, 768, 85_842_432)
    assert counts["table"] == 38_597_376
    assert counts["tied_total"] == 124_439_808
    assert counts["untied_total"] - counts["tied_total"] == counts["table"]


def test_scaled_attention_matches_the_single_head_helper():
    example = ml_models_docs.ATTENTION_EXAMPLE
    reference = ml_models_docs.attention_weights(example)
    result = ml_models_docs.scaled_attention(example["queries"], example["keys"], example["values"])

    for got, want in zip(result["weights"], reference["weights"]):
        assert got == pytest.approx(want)
    for got, want in zip(result["outputs"], reference["outputs"]):
        assert got == pytest.approx(want)


def test_boolean_mask_directions_are_opposite():
    allowed = ml_models_docs.causal_allowed_mask(3, 3)
    masked_out = [[not cell for cell in row] for row in allowed]

    assert ml_models_docs.allowed_to_additive(allowed) == ml_models_docs.masked_out_to_additive(masked_out)
    assert ml_models_docs.allowed_to_additive(allowed)[0] == [0.0, -math.inf, -math.inf]


def test_causal_variants_align_differently_for_rectangular_masks():
    upper = ml_models_docs.causal_allowed_mask(3, 4, "upper_left")
    lower = ml_models_docs.causal_allowed_mask(3, 4, "lower_right")

    assert upper == [[True, False, False, False], [True, True, False, False], [True, True, True, False]]
    assert lower == [[True, True, False, False], [True, True, True, False], [True, True, True, True]]
    assert ml_models_docs.causal_allowed_mask(3, 3, "upper_left") == ml_models_docs.causal_allowed_mask(3, 3, "lower_right")


def test_fully_masked_row_gives_nan_like_pytorch():
    result = ml_models_docs.scaled_attention([[1, 0]], [[1, 0], [0, 1]], [[1, 0], [0, 1]], [[-math.inf, -math.inf]])

    assert all(math.isnan(weight) for weight in result["weights"][0])


def test_split_and_merge_heads_round_trip():
    matrix = [[1, 2, 3, 4], [5, 6, 7, 8]]
    split = ml_models_docs.split_heads(matrix, 2)

    assert split == [[[1, 2], [5, 6]], [[3, 4], [7, 8]]]
    assert ml_models_docs.merge_heads(split) == matrix


def test_packed_projection_equals_three_separate_projections():
    example = ml_models_docs.MULTIHEAD_EXAMPLE
    packed = ml_models_docs.packed_in_projection(example["x"], example["in_proj_weight"])
    size = example["embed_dim"]

    for part, name in enumerate("qkv"):
        rows = example["in_proj_weight"][part * size:(part + 1) * size]
        assert packed[name] == ml_models_docs.matmul(example["x"], ml_models_docs.transpose(rows))


def test_multihead_attention_heads_are_independent_and_rows_sum_to_one():
    example = ml_models_docs.MULTIHEAD_EXAMPLE
    result = ml_models_docs.multihead_attention(example)

    assert len(result["heads"]) == example["heads"]
    for head in result["heads"]:
        for row in head["weights"]:
            assert sum(row) == pytest.approx(1)
    assert result["output"] == ml_models_docs.matmul(
        result["merged"], ml_models_docs.transpose(example["out_proj_weight"])
    )
    for row in result["average_weights"]:
        assert sum(row) == pytest.approx(1)


def test_padding_mask_zeroes_pad_columns_and_causal_zeroes_the_future():
    example = ml_models_docs.MULTIHEAD_EXAMPLE
    rows = len(example["x"])
    padding = ml_models_docs.key_padding_additive(example["padding"], rows)
    causal = ml_models_docs.allowed_to_additive(ml_models_docs.causal_allowed_mask(rows, rows))

    padded = ml_models_docs.multihead_attention(example, padding)
    both = ml_models_docs.multihead_attention(example, ml_models_docs.add_masks(padding, causal))

    for head in padded["heads"]:
        assert all(row[3] == 0 for row in head["weights"])
    for head in both["heads"]:
        for i, row in enumerate(head["weights"]):
            assert all(weight == 0 for weight in row[i + 1:])
    assert both["heads"][0]["weights"][0] == [1.0, 0.0, 0.0, 0.0]


def test_gqa_groups_and_kv_cache_savings():
    assert ml_models_docs.gqa_groups(8, 2) == [0, 0, 0, 0, 1, 1, 1, 1]
    assert ml_models_docs.gqa_groups(4, 4) == [0, 1, 2, 3]
    with pytest.raises(ValueError):
        ml_models_docs.gqa_groups(6, 4)
    full = ml_models_docs.kv_cache_bytes_per_token(32, 32, 128, 2)
    grouped = ml_models_docs.kv_cache_bytes_per_token(32, 8, 128, 2)
    assert (full, grouped) == (524288, 131072)


def test_multihead_param_count_matches_transformer_attention():
    count = ml_models_docs.multihead_param_count(512)

    assert count["total"] == ml_models_docs.transformer_param_count(512, 1, 0, 2048)["attention"]
    assert count["in_proj"] == 3 * 512 * 512
    assert ml_models_docs.multihead_param_count(8, bias=False)["total"] == 4 * 64


def test_layer_norm_row_has_zero_mean_and_unit_variance():
    out = ml_models_docs.layer_norm_row([2.0, 4.0, 6.0, 8.0], eps=0.0)
    assert abs(sum(out) / 4) < 1e-12
    assert abs(sum(v * v for v in out) / 4 - 1) < 1e-12


def test_layer_norm_applies_scale_and_shift_after_normalising():
    plain = ml_models_docs.layer_norm_row([1.0, 2.0, 3.0])
    shifted = ml_models_docs.layer_norm_row([1.0, 2.0, 3.0], [2, 2, 2], [1, 1, 1])
    assert shifted == [2 * v + 1 for v in plain]


def test_layer_norm_ignores_input_scale_and_shift():
    base = ml_models_docs.layer_norm_row([1.0, 2.0, 4.0], eps=0.0)
    moved = ml_models_docs.layer_norm_row([21.0, 42.0, 84.0], eps=0.0)
    shifted = ml_models_docs.layer_norm_row([11.0, 12.0, 14.0], eps=0.0)
    assert all(abs(a - b) < 1e-9 for a, b in zip(base, moved))
    assert all(abs(a - b) < 1e-9 for a, b in zip(base, shifted))


def test_rms_norm_keeps_the_mean_unlike_layer_norm():
    row = [1.0, 2.0, 3.0, 6.0]
    rms = ml_models_docs.rms_norm_row(row, eps=0.0)
    assert abs(sum(v * v for v in rms) / 4 - 1) < 1e-12
    assert abs(sum(rms) / 4) > 0.1
    assert [v / rms[0] for v in rms] == [v / row[0] for v in row]


def test_batch_norm_normalises_each_column_across_the_batch():
    out = ml_models_docs.batch_norm_columns([[1.0, 10.0], [3.0, 10.0], [5.0, 40.0]], eps=0.0)
    for column in zip(*out):
        assert abs(sum(column) / 3) < 1e-12
        assert abs(sum(v * v for v in column) / 3 - 1) < 1e-12


def test_batch_norm_depends_on_the_batch_and_layer_norm_does_not():
    row = [1.0, 2.0, 3.0]
    alone = ml_models_docs.batch_norm_columns([row, [0.0, 0.0, 0.0]])[0]
    other = ml_models_docs.batch_norm_columns([row, [9.0, 9.0, 9.0]])[0]
    assert alone != other
    assert ml_models_docs.layer_norm_row(row) == ml_models_docs.layer_norm_row(list(row))


def test_group_norm_one_group_is_layer_norm_and_per_channel_is_zero():
    row = [1.0, 2.0, 4.0, 8.0]
    assert ml_models_docs.group_norm_row(row, 1) == ml_models_docs.layer_norm_row(row)
    assert all(v == 0 for v in ml_models_docs.group_norm_row(row, 4))
    with pytest.raises(ValueError):
        ml_models_docs.group_norm_row(row, 3)


def test_running_stats_use_the_unbiased_variance_and_momentum():
    mean, var = ml_models_docs.running_stats_update(0.0, 1.0, [1.0, 3.0], momentum=0.1)
    assert abs(mean - 0.2) < 1e-12
    assert abs(var - (0.9 + 0.1 * 2.0)) < 1e-12


def test_batch_norm_eval_uses_the_stored_statistics():
    assert abs(ml_models_docs.batch_norm_eval(5.0, 3.0, 4.0, eps=0.0) - 1.0) < 1e-12


def test_pre_norm_keeps_an_untouched_identity_path():
    x = [1.0, 2.0, 3.0, 4.0]
    norm = ml_models_docs.layer_norm_row
    zero = lambda v: [0.0] * len(v)
    assert ml_models_docs.residual_block(x, zero, norm, True) == x
    assert ml_models_docs.residual_block(x, zero, norm, False) != x


def test_post_norm_resets_the_stream_scale_every_block():
    x = [10.0, -20.0, 30.0, -40.0]
    double = lambda v: [2 * a for a in v]
    _, post = ml_models_docs.residual_stream_norms(x, [double] * 3, ml_models_docs.layer_norm_row, False)
    _, pre = ml_models_docs.residual_stream_norms(x, [double] * 3, ml_models_docs.layer_norm_row, True)
    assert post[1] == pytest.approx(post[2], rel=1e-4) == pytest.approx(post[3], rel=1e-4)
    assert pre[3] > pre[0]


def test_norm_param_counts():
    assert ml_models_docs.norm_param_count("layer", 512) == 1024
    assert ml_models_docs.norm_param_count("layer", 512, bias=False) == 512
    assert ml_models_docs.norm_param_count("rms", 512) == 512
    assert ml_models_docs.norm_param_count("batch", 64) == 128
    assert ml_models_docs.transformer_param_count(512, 1, 0, 2048)["layer_norm"] == ml_models_docs.norm_param_count("layer", 512)


def test_residual_demo_pre_norm_grows_and_post_norm_stays_fixed():
    demo = ml_models_docs.residual_demo(6)
    assert len(demo["pre"]) == len(demo["post"]) == 7
    assert demo["pre"][-1] > 2 * demo["pre"][0]
    assert all(abs(v - demo["post"][1]) < 1e-3 for v in demo["post"][1:])


def test_lr_schedule_warms_up_then_follows_a_cosine_to_the_floor():
    schedule = ml_models_docs.lr_schedule(0.2, 2, 8, 0.02)
    assert schedule[:3] == pytest.approx([0.1, 0.2, 0.2])
    assert all(a >= b for a, b in zip(schedule[2:], schedule[3:]))
    assert schedule[-1] > 0.02
    assert ml_models_docs.lr_at(8, 0.2, 2, 8, 0.02) == pytest.approx(0.02)


def test_linear_warmup_matches_the_linear_lr_recursion():
    warmup, start = 5, 1 / 5
    lr, expected = start, [start]
    for epoch in range(1, warmup):
        lr *= 1.0 + (1.0 - start) / ((warmup - 1) * start + (epoch - 1) * (1.0 - start))
        expected.append(lr)
    assert ml_models_docs.lr_schedule(1.0, warmup, warmup + 1)[:warmup] == pytest.approx(expected)


def test_smoothed_cross_entropy_blends_the_loss_with_a_uniform_target():
    logits = [2.0, 1.0, -1.0]
    plain = ml_models_docs.logits_cross_entropy(logits, 0)["loss"]
    assert ml_models_docs.smoothed_cross_entropy(logits, 0, 0.0) == pytest.approx(plain)
    uniform = -sum(ml_models_docs.categorical_from_logits(logits)["log_probs"]) / 3
    assert ml_models_docs.smoothed_cross_entropy(logits, 0, 1.0) == pytest.approx(uniform)


def test_masked_mean_loss_divides_by_the_kept_targets_only():
    rows = [[0.0, 0.0, 0.0, 0.0]] * 3
    result = ml_models_docs.masked_mean_loss(rows, [1, -100, 2])
    assert result["count"] == 2
    assert result["loss"] == pytest.approx(math.log(4))
    assert math.isnan(ml_models_docs.masked_mean_loss(rows, [-100] * 3)["loss"])


def test_bigram_gradient_matches_finite_differences():
    weights = [[0.1 * (i - j) for j in range(4)] for i in range(4)]
    inputs, targets = [0, 1, 2, 3], [1, 2, -100, 0]
    grad = ml_models_docs.bigram_gradient(weights, inputs, targets)
    base = ml_models_docs.masked_mean_loss([weights[x] for x in inputs], targets)["loss"]
    for i, j in [(0, 1), (1, 0), (2, 2), (3, 3)]:
        bumped = [list(row) for row in weights]
        bumped[i][j] += 1e-6
        loss = ml_models_docs.masked_mean_loss([bumped[x] for x in inputs], targets)["loss"]
        assert (loss - base) / 1e-6 == pytest.approx(grad[i][j], abs=1e-4)
    assert grad[2] == [0.0] * 4


def test_clip_by_global_norm_only_shrinks():
    clipped = ml_models_docs.clip_by_global_norm([3.0, 4.0], 1.0)
    assert clipped["total_norm"] == pytest.approx(5.0)
    assert clipped["clipped"] and math.hypot(*clipped["grads"]) == pytest.approx(1.0, rel=1e-5)
    untouched = ml_models_docs.clip_by_global_norm([0.3, 0.4], 1.0)
    assert untouched["coef"] == 1.0 and untouched["grads"] == [0.3, 0.4]


def test_training_run_starts_at_log_vocab_and_loss_falls():
    run = ml_models_docs.training_run(ml_models_docs.TRAINING_EXAMPLE)
    losses = [row["loss"] for row in run["rows"]]
    assert losses[0] == pytest.approx(math.log(4))
    assert all(a > b for a, b in zip(losses, losses[1:]))
    assert run["rows"][0]["clipped"] and not run["rows"][1]["clipped"]
    assert all(row["count"] == 5 for row in run["rows"])


def test_accumulation_needs_token_weights_when_batches_have_padding():
    weights = [[0.0] * 4 for _ in range(4)]
    result = ml_models_docs.accumulation_check(weights, [([0, 1, 2], [1, 2, 3]), ([3, 1], [-100, 2])])
    assert result["exact"] == pytest.approx(result["full"])
    assert max(abs(a - b) for a, b in zip(result["naive"], result["full"])) > 0.01


def test_float16_underflow_is_rescued_by_loss_scaling():
    plain = ml_models_docs.scaled_gradient_roundtrip(1e-8, 2.0**16)
    assert plain["plain"] == 0.0
    assert plain["scaled"] > 0
    assert plain["recovered"] == pytest.approx(1e-8, rel=1e-3)
    assert ml_models_docs.to_float16(1e6) == math.inf


def test_grad_scaler_backs_off_on_overflow_and_grows_after_the_interval():
    example = ml_models_docs.SCALER_EXAMPLE
    rows = ml_models_docs.grad_scaler_trace(example["scale"], example["growth_interval"], example["overflows"])
    assert [row["scale"] for row in rows][:4] == [65536.0, 65536.0, 65536.0, 131072.0]
    assert rows[3]["overflow"] and rows[3]["next_scale"] == 65536.0
    assert rows[-1]["next_scale"] == 131072.0


def test_training_memory_is_sixteen_bytes_per_parameter_for_adam():
    rows = ml_models_docs.training_memory(7e9)
    assert rows[-1]["bytes_per_param"] == 16
    assert rows[-1]["gigabytes"] == pytest.approx(112.0)


def test_gpt2_small_parameter_count_matches_the_released_124m_model():
    config = {k: v for k, v in ml_models_docs.GPT2_SMALL.items() if k != "heads"}
    counts = ml_models_docs.decoder_param_count(**config)
    assert counts["token_table"] == 38_597_376
    assert counts["per_block"] == 7_087_872
    assert counts["total"] == 124_439_808
    untied = ml_models_docs.decoder_param_count(**config, tied=False)
    assert untied["total"] == counts["total"] + counts["token_table"]


def test_decoder_block_is_the_encoder_layer_count():
    layer = ml_models_docs.transformer_param_count(768, 1, 0, 3072)["encoder_layer"]
    assert ml_models_docs.decoder_param_count(50257, 1024, 768, 12)["per_block"] == layer


def test_decoder_param_count_defaults_to_a_four_times_feed_forward():
    explicit = ml_models_docs.decoder_param_count(100, 16, 8, 2, d_ff=32)
    assert ml_models_docs.decoder_param_count(100, 16, 8, 2) == explicit


def test_next_token_pairs_shift_by_one():
    pairs = ml_models_docs.next_token_pairs([5, 6, 7, 8])
    assert pairs == {"inputs": [5, 6, 7], "targets": [6, 7, 8]}


def test_causal_outputs_ignore_later_tokens_but_bidirectional_ones_do_not():
    check = ml_models_docs.causal_prefix_check(ml_models_docs.ATTENTION_EXAMPLE, 3)
    assert check["causal_gap"] == pytest.approx(0.0, abs=1e-12)
    assert check["bidirectional_gap"] > 0.1


def test_sequence_nll_averages_next_token_losses_and_exponentiates():
    uniform = [[0.0] * 4 for _ in range(4)]
    result = ml_models_docs.sequence_nll(uniform, [0, 1, 2, 3])
    assert result["mean"] == pytest.approx(math.log(4))
    assert result["perplexity"] == pytest.approx(4.0)


def test_greedy_generation_follows_the_trained_bigram_table():
    run = ml_models_docs.training_run(ml_models_docs.TRAINING_EXAMPLE)
    example = ml_models_docs.GENERATION_EXAMPLE
    tokens = ml_models_docs.greedy_generate(run["weights"], example["start"], example["steps"])
    assert tokens == [0, 1, 2, 3, 0, 1]


def test_generation_positions_without_a_cache_grow_quadratically():
    assert ml_models_docs.generation_positions(10, 20) == 390
    assert ml_models_docs.generation_positions(10, 20, cached=True) == 29
    assert ml_models_docs.generation_positions(3, 1) == ml_models_docs.generation_positions(3, 1, cached=True) + 1 - 1


def test_temperature_sharpens_and_flattens_the_distribution():
    logits = ml_models_docs.DECODING_EXAMPLE["logits"]
    cold, base, hot = (ml_models_docs.temperature_probs(logits, t) for t in (0.5, 1, 2))
    assert cold[0] > base[0] > hot[0]
    assert ml_models_docs.entropy(cold) < ml_models_docs.entropy(base) < ml_models_docs.entropy(hot)
    assert all(abs(sum(p) - 1) < 1e-12 for p in (cold, base, hot))


def test_top_k_and_top_p_keep_the_head_and_renormalize():
    probs = ml_models_docs.temperature_probs(ml_models_docs.DECODING_EXAMPLE["logits"], 1)
    top_k = ml_models_docs.top_k_filter(probs, 3)
    assert top_k["kept"] == [0, 1, 2]
    assert abs(sum(top_k["probs"]) - 1) < 1e-12
    top_p = ml_models_docs.top_p_filter(probs, 0.9)
    assert top_p["kept"] == [0, 1, 2, 3]
    assert top_p["mass"] >= 0.9 > sum(probs[:3])
    assert ml_models_docs.top_p_filter(probs, 0.1)["kept"] == [0]


def test_repeat_penalty_lowers_seen_tokens_whatever_their_sign():
    out = ml_models_docs.repeat_penalty([2.0, -1.0, 0.5], {0, 1}, 2.0)
    assert out == [1.0, -2.0, 0.5]


def test_constrained_probs_zero_the_disallowed_tokens():
    probs = ml_models_docs.constrained_probs(ml_models_docs.DECODING_EXAMPLE["logits"], {2, 3})
    assert probs[0] == probs[1] == 0.0
    assert abs(sum(probs) - 1) < 1e-12
    assert probs[2] > probs[3]


def test_sample_frequencies_are_seeded_and_close_to_the_distribution():
    probs = [0.5, 0.3, 0.2]
    first = ml_models_docs.sample_frequencies(probs, 2000, 0)
    assert first == ml_models_docs.sample_frequencies(probs, 2000, 0)
    assert all(abs(a - b) < 0.05 for a, b in zip(first, probs))


def test_beam_search_beats_greedy_on_the_example():
    steps = ml_models_docs.BEAM_STEP_PROBS
    greedy_tokens, greedy_score = ml_models_docs.greedy_path(steps, 4)
    best_tokens, best_score = ml_models_docs.beam_search(steps, 2, 4)[0]
    assert greedy_tokens == ["<s>", "x", "end"]
    assert best_tokens == ["<s>", "y", "end"]
    assert best_score > greedy_score
    assert abs(math.exp(greedy_score) - 0.2) < 1e-12
    assert abs(math.exp(best_score) - 0.4) < 1e-12
    assert ml_models_docs.beam_search(steps, 1, 4)[0][0] == greedy_tokens


def test_speculative_step_reproduces_the_target_distribution():
    example = ml_models_docs.SPECULATIVE_EXAMPLE
    result = ml_models_docs.speculative_step(example["target"], example["draft"])
    assert abs(result["acceptance"] - 0.75) < 1e-12
    assert abs(sum(result["residual"]) - 1) < 1e-12
    for got, want in zip(result["output"], example["target"]):
        assert abs(got - want) < 1e-12


def test_speculative_tokens_per_pass_is_a_geometric_sum():
    assert ml_models_docs.speculative_tokens_per_pass(0.0, 4) == 1
    assert ml_models_docs.speculative_tokens_per_pass(1.0, 4) == 5
    assert abs(ml_models_docs.speculative_tokens_per_pass(0.5, 4) - 1.9375) < 1e-12


def test_cached_decode_matches_full_causal_attention_with_less_work():
    result = ml_models_docs.cached_decode(ml_models_docs.ATTENTION_EXAMPLE)
    assert result["gap"] < 1e-12
    assert result["cached_projections"] == 4
    assert result["uncached_projections"] == 10
    assert result["score_dots"] == 10


def test_kv_cache_totals_scale_with_heads_length_and_batch():
    config = ml_models_docs.KV_CONFIG
    one = ml_models_docs.kv_cache_total_bytes(config, config["kv_heads"], 1)
    assert one == 131_072
    assert ml_models_docs.kv_cache_total_bytes(config, config["kv_heads"], 8192) == 8192 * one == 2**30
    assert ml_models_docs.kv_cache_total_bytes(config, 32, 1) == 4 * one
    assert ml_models_docs.kv_cache_total_bytes(config, 1, 1) * 8 == one
    assert ml_models_docs.kv_cache_total_bytes(config, 8, 10, batch=3) == 30 * one


def test_decode_attention_intensity_is_independent_of_length_and_grows_with_sharing():
    assert ml_models_docs.decode_attention_intensity(32, 32, 2) == 1.0
    assert ml_models_docs.decode_attention_intensity(32, 8, 2) == 4.0
    assert ml_models_docs.decode_attention_intensity(32, 1, 2) == 32.0


def test_paged_allocation_wastes_less_than_contiguous_reservation():
    result = ml_models_docs.paged_allocation(**ml_models_docs.PAGED_EXAMPLE)
    assert result["blocks"] == [3, 8, 1, 4]
    assert result["used"] == 226
    assert result["paged_slots"] == 256
    assert result["paged_waste"] == 30
    assert result["contiguous_slots"] == 512
    assert result["contiguous_waste"] == 286


def test_kmeans_run_converges_and_inertia_never_rises():
    start = [ml_models_docs.LEARNING_POINTS[0], ml_models_docs.LEARNING_POINTS[1]]
    history = ml_models_docs.kmeans_run(ml_models_docs.LEARNING_POINTS, start, 6)
    inertias = [step["inertia"] for step in history]
    assert len(history) == 4
    assert inertias == sorted(inertias, reverse=True)
    assert inertias[0] == pytest.approx(74.92)
    assert inertias[-1] == pytest.approx(5.888)
    assert history[-1]["assign"] == ml_models_docs.LEARNING_TRUTH
    assert history[-1]["centers"][1] == pytest.approx((4.3, 3.9))


def test_two_labels_name_clusters_better_than_nearest_label():
    points = ml_models_docs.LEARNING_POINTS
    truth = ml_models_docs.LEARNING_TRUTH
    labeled = ml_models_docs.LEARNING_LABELED
    nearest = ml_models_docs.nearest_labeled(points, labeled)
    clusters = ml_models_docs.kmeans_run(points, [points[0], points[8]], 6)[-1]["assign"]
    named = ml_models_docs.cluster_then_label(clusters, labeled)
    assert ml_models_docs.prediction_accuracy(nearest, truth) == pytest.approx(8 / 9)
    assert nearest[4] == 1
    assert ml_models_docs.prediction_accuracy(named, truth) == 1.0


def test_masked_pairs_hide_one_token_each():
    tokens = ml_models_docs.LEARNING_TEXT
    pairs = ml_models_docs.masked_pairs(tokens, [1, 5])
    assert [pair["target"] for pair in pairs] == ["cat", "mat"]
    assert pairs[0]["input"][1] == "[MASK]"
    assert pairs[0]["input"].count("[MASK]") == 1
    assert len(pairs[0]["input"]) == len(tokens)


def test_bigram_next_token_loss_beats_uniform_guessing():
    result = ml_models_docs.bigram_next_token_loss(ml_models_docs.LEARNING_TEXT)
    assert result["pairs"] == 9
    assert result["uniform_loss"] == pytest.approx(math.log(7))
    assert 0 < result["mean_loss"] < result["uniform_loss"]


def test_polynomial_fit_recovers_an_exact_line():
    xs = [0.0, 0.5, 1.0]
    weights = ml_models_docs.polynomial_fit(xs, [1.0, 2.0, 3.0], 1)
    assert [ml_models_docs.polynomial_predict(weights, x) for x in xs] == pytest.approx([1.0, 2.0, 3.0])


def test_generalization_train_error_falls_while_heldout_error_turns_up():
    rows = {row["degree"]: row for row in ml_models_docs.generalization_rows(range(0, 10))}
    train = [rows[d]["train_mse"] for d in range(10)]
    assert train == sorted(train, reverse=True)
    assert rows[9]["train_mse"] == pytest.approx(0.0, abs=1e-9)
    assert rows[1]["train_mse"] == pytest.approx(0.3327, abs=1e-3)
    assert rows[3]["heldout_mse"] == pytest.approx(0.0089, abs=1e-3)
    assert rows[9]["heldout_mse"] == pytest.approx(0.067, abs=2e-3)
    best = min(rows, key=lambda d: rows[d]["heldout_mse"])
    assert best == 5
    assert rows[9]["heldout_mse"] > 10 * rows[best]["heldout_mse"]


def test_generalization_shift_breaks_the_cubic_outside_the_training_range():
    rows = {row["degree"]: row for row in ml_models_docs.generalization_rows([3])}
    assert rows[3]["shifted_mse"] > 1000 * rows[3]["heldout_mse"]


def test_stratified_allocation_keeps_class_proportions():
    labels = ml_models_docs.SPLIT_LABELS
    assert ml_models_docs.class_counts(labels, range(20)) == {0: 16, 1: 4}
    assert ml_models_docs.stratified_allocation(labels, 0.25) == {0: 4, 1: 1}
    assert sum(ml_models_docs.stratified_allocation(labels, 0.4).values()) == 8


def test_an_unlucky_plain_split_can_leave_no_positives_in_test():
    labels = ml_models_docs.SPLIT_LABELS
    order = ml_models_docs.SPLIT_UNLUCKY_ORDER
    assert sorted(order) == list(range(20))
    assert ml_models_docs.class_counts(labels, order[:5]) == {0: 5}
    assert ml_models_docs.chance_test_misses_class(labels, 5, 1) == pytest.approx(4368 / 15504)


def test_record_level_split_leaks_every_group_but_a_group_split_leaks_none():
    groups = ml_models_docs.SPLIT_GROUPS
    order = ml_models_docs.SPLIT_GROUP_ORDER
    assert sorted(order) == list(range(18))
    assert ml_models_docs.leaked_group_records(groups, order[:6]) == 6
    whole_groups = [i for i, g in enumerate(groups) if g in (4, 5)]
    assert ml_models_docs.leaked_group_records(groups, whole_groups) == 0


def test_random_split_flatters_a_time_series_forecast():
    series = ml_models_docs.SPLIT_SERIES
    random_test = ml_models_docs.SPLIT_RANDOM_TEST_MONTHS
    random_train = [t for t in range(12) if t not in random_test]
    random_mse = ml_models_docs.nearest_in_time_mse(series, random_train, random_test)
    forward_mse = ml_models_docs.nearest_in_time_mse(series, list(range(9)), [9, 10, 11])
    assert random_mse == pytest.approx(4.2175)
    assert forward_mse == pytest.approx(17.2867, abs=1e-3)


def test_accuracy_standard_error_shrinks_with_the_test_set():
    assert ml_models_docs.accuracy_standard_error(0.8, 100) == pytest.approx(0.04)
    assert ml_models_docs.accuracy_standard_error(0.8, 400) == pytest.approx(0.02)


def test_standardized_columns_have_zero_mean_and_unit_spread():
    for column in (ml_models_docs.PREPROCESS_AGE, ml_models_docs.PREPROCESS_INCOME):
        mean, std = ml_models_docs.column_mean_std(column)
        scaled = ml_models_docs.standardize_with(column, mean, std)
        assert sum(scaled) == pytest.approx(0, abs=1e-9)
        assert ml_models_docs.column_mean_std(scaled)[1] == pytest.approx(1)
    assert ml_models_docs.column_mean_std(ml_models_docs.PREPROCESS_AGE) == pytest.approx((43.0, 13.2212), abs=1e-4)


def test_min_max_scale_maps_the_range_onto_zero_one():
    scaled = ml_models_docs.min_max_scale(ml_models_docs.PREPROCESS_INCOME, 30000, 250000)
    assert scaled[0] == 0 and scaled[-1] == 1
    assert scaled[1] == pytest.approx(0.1)


def test_raw_distance_ignores_age_until_features_are_scaled():
    age, income = ml_models_docs.PREPROCESS_AGE, ml_models_docs.PREPROCESS_INCOME
    rows = list(zip(age, income))
    a, b, c = rows[1], rows[2], rows[0]
    assert ml_models_docs.pair_distance(a, b) == pytest.approx(9000.008, abs=1e-3)
    assert ml_models_docs.pair_distance(a, c) == pytest.approx(22000.004, abs=1e-3)
    am, asd = ml_models_docs.column_mean_std(age)
    im, isd = ml_models_docs.column_mean_std(income)
    scaled = list(zip(ml_models_docs.standardize_with(age, am, asd), ml_models_docs.standardize_with(income, im, isd)))
    assert ml_models_docs.pair_distance(scaled[1], scaled[2]) == pytest.approx(0.9147, abs=1e-4)
    assert ml_models_docs.pair_distance(scaled[1], scaled[0]) == pytest.approx(1.0219, abs=1e-4)


def test_fit_statistics_from_train_rows_shift_the_test_value():
    train = ml_models_docs.PREPROCESS_AGE[:4]
    mean, std = ml_models_docs.column_mean_std(train)
    assert (mean, std) == pytest.approx((38.75, 11.3220), abs=1e-4)
    assert ml_models_docs.standardize_with([60], mean, std)[0] == pytest.approx(1.8769, abs=1e-4)


def test_log_transform_pulls_the_mean_toward_the_median():
    income = ml_models_docs.PREPROCESS_INCOME
    logs = ml_models_docs.log10_column(income)
    assert sum(income) / 5 == 96600 and ml_models_docs.median(income) == 61000
    assert sum(logs) / 5 == pytest.approx(4.8661, abs=1e-4)
    assert ml_models_docs.median(logs) == pytest.approx(4.7853, abs=1e-4)
    assert ml_models_docs.median([1, 2, 3, 4]) == 2.5


def test_encoders_order_categories_alphabetically():
    categories, rows = ml_models_docs.one_hot_encode(ml_models_docs.PREPROCESS_COLORS)
    assert categories == ["blue", "green", "red"]
    assert rows[0] == [0, 0, 1] and rows[1] == [0, 1, 0]
    assert ml_models_docs.ordinal_encode(ml_models_docs.PREPROCESS_COLORS) == [2, 1, 0, 1, 2]


def test_selection_on_all_rows_inflates_noise_accuracy():
    one = ml_models_docs.leaky_selection_demo(seed=3)
    assert one["leaky_test_accuracy"] == 0.75 and one["honest_test_accuracy"] == 0.25
    assert one["honest_train_accuracy"] == 0.9
    average = ml_models_docs.leaky_selection_average()
    assert average["leaky_test_accuracy"] == pytest.approx(0.7285, abs=1e-4)
    assert average["honest_test_accuracy"] == pytest.approx(0.479, abs=1e-4)
    assert average["honest_train_accuracy"] == pytest.approx(0.827, abs=1e-4)


def test_duplicates_across_splits_lift_a_memorizer():
    train, test = ml_models_docs.LEAK_DUP_TRAIN, ml_models_docs.LEAK_DUP_TEST
    assert ml_models_docs.duplicate_overlap(train, test) == 4
    assert ml_models_docs.lookup_accuracy(train, test) == 0.7
    assert ml_models_docs.lookup_accuracy(train, test, skip_seen=True) == 0.5


def test_a_feature_from_after_the_outcome_predicts_perfectly():
    defaulted = ml_models_docs.LEAK_LOAN_DEFAULTED
    assert ml_models_docs.best_threshold_rule(ml_models_docs.LEAK_LOAN_NOTICES, defaulted) == (0.5, 1.0)
    cut, accuracy = ml_models_docs.best_threshold_rule(ml_models_docs.LEAK_LOAN_DEBT_RATIO, defaulted)
    assert cut == pytest.approx(0.365) and accuracy == 0.6


def test_threshold_sweep_trades_precision_for_recall():
    labels, scores = ml_models_docs.METRIC_LABELS, ml_models_docs.METRIC_SCORES
    assert ml_models_docs.confusion_counts(labels, scores, 0.5) == (3, 2, 1, 4)
    assert ml_models_docs.confusion_counts(labels, scores, 0.9) == (1, 0, 3, 6)
    assert ml_models_docs.precision_recall_f1(3, 2, 1) == pytest.approx((0.6, 0.75, 2 / 3))
    assert ml_models_docs.precision_recall_f1(1, 0, 3) == pytest.approx((1.0, 0.25, 0.4))
    assert ml_models_docs.precision_recall_f1(0, 0, 5) == (0.0, 0.0, 0.0)
    recalls = [ml_models_docs.precision_recall_f1(*ml_models_docs.confusion_counts(labels, scores, t)[:3])[1] for t in (0.9, 0.7, 0.5, 0.35)]
    assert recalls == sorted(recalls)


def test_trapezoid_auc_equals_the_pairwise_ranking_probability():
    labels, scores = ml_models_docs.METRIC_LABELS, ml_models_docs.METRIC_SCORES
    points = ml_models_docs.roc_points(labels, scores)
    assert points[0] == (0.0, 0.0) and points[-1] == (1.0, 1.0)
    assert ml_models_docs.trapezoid_area(points) == pytest.approx(0.875)
    assert ml_models_docs.rank_auc(labels, scores) == pytest.approx(0.875)
    assert ml_models_docs.rank_auc([1, 0], [0.5, 0.5]) == 0.5


def test_average_precision_is_the_recall_weighted_precision_sum():
    labels, scores = ml_models_docs.METRIC_LABELS, ml_models_docs.METRIC_SCORES
    assert ml_models_docs.pr_points(labels, scores)[0] == (0.25, 1.0)
    assert ml_models_docs.average_precision(labels, scores) == pytest.approx(0.85416667)
    assert ml_models_docs.average_precision([1, 0], [0.9, 0.1]) == 1.0


def test_log_loss_punishes_confident_mistakes_and_micro_macro_differ():
    assert ml_models_docs.binary_log_loss(ml_models_docs.METRIC_LABELS, ml_models_docs.METRIC_SCORES) == pytest.approx(0.50470531)
    assert ml_models_docs.binary_log_loss([1, 0], [0.99, 0.01]) == pytest.approx(0.01005034)
    assert ml_models_docs.binary_log_loss([1], [0.01]) == pytest.approx(4.60517019)
    per_class, macro, micro = ml_models_docs.averaged_f1(ml_models_docs.METRIC_CLASS_COUNTS)
    assert per_class["cat"] == pytest.approx(0.8) and per_class["bird"] == 0.0
    assert macro == pytest.approx(0.36190476) and micro == pytest.approx(0.6)


def test_kfold_splits_match_sklearn_sizes_and_partition():
    splits = ml_models_docs.kfold_splits(10, 3)
    assert [len(te) for _, te in splits] == [4, 3, 3]
    assert sorted(i for _, te in splits for i in te) == list(range(10))
    for train, test in splits:
        assert not set(train) & set(test)
        assert len(train) + len(test) == 10


def test_stratified_kfold_keeps_class_balance():
    labels = [0] * 6 + [1] * 4
    for train, test in ml_models_docs.stratified_kfold_splits(labels, 2):
        assert sum(labels[i] for i in test) == 2
        assert len(test) == 5
        assert not set(train) & set(test)


def test_group_kfold_never_splits_a_group():
    groups = list("aaabbccdde")
    for train, test in ml_models_docs.group_kfold_splits(groups, 3):
        assert not {groups[i] for i in train} & {groups[i] for i in test}
    assert sorted(len(te) for _, te in ml_models_docs.group_kfold_splits(groups, 3)) == [3, 3, 4]


def test_time_series_splits_train_only_on_the_past():
    splits = ml_models_docs.time_series_splits(12, 3)
    assert [(len(tr), len(te)) for tr, te in splits] == [(3, 3), (6, 3), (9, 3)]
    for train, test in splits:
        assert max(train) < min(test)


def test_cv_summary_uses_sample_standard_deviation():
    mean, spread = ml_models_docs.cv_summary([0.6, 0.8, 1.0])
    assert mean == pytest.approx(0.8)
    assert spread == pytest.approx(0.2)


def test_cv_estimate_varies_with_the_shuffle():
    data = ml_models_docs.centroid_cv_data()
    assert ml_models_docs.centroid_cv_data() == data
    means = ml_models_docs.repeated_cv_means(data, 5)
    assert max(means) - min(means) > 0.05
    mean, spread = ml_models_docs.cv_summary(means)
    assert 0.7 < mean < 0.85
    assert 0 < spread < 0.05


def test_selection_bias_demo_best_of_many_is_optimistic_but_nested_is_honest():
    best, nested = ml_models_docs.selection_bias_demo()
    assert best > 0.62
    assert abs(nested - 0.5) < 0.03


def test_tree_impurities_match_hand_values():
    assert ml_models_docs.gini_impurity([5, 7]) == pytest.approx(1 - (5 / 12) ** 2 - (7 / 12) ** 2)
    assert ml_models_docs.gini_impurity([4, 0]) == 0.0
    assert ml_models_docs.entropy_impurity([1, 1]) == pytest.approx(1.0)
    assert ml_models_docs.entropy_impurity([5, 7]) == pytest.approx(0.97986876)
    assert ml_models_docs.entropy_impurity([6, 0]) == 0.0


def test_tree_root_split_matches_sklearn_run():
    rows = ml_models_docs.TREE_TOY_ROWS
    best = ml_models_docs.best_split(rows)
    assert (best["feature"], best["threshold"]) == (0, 5.5)
    assert (best["n_left"], best["n_right"]) == (7, 5)
    assert best["gain"] == pytest.approx(0.24801587)
    assert best["weighted"] == pytest.approx(0.23809524)


def test_grown_tree_fits_training_rows_and_matches_sklearn_shape():
    rows = ml_models_docs.TREE_TOY_ROWS
    tree = ml_models_docs.grow_tree(rows)
    assert ml_models_docs.tree_accuracy(tree, rows) == 1.0
    assert len(ml_models_docs.tree_leaves(tree)) == 6
    assert ml_models_docs.tree_depth(tree) == 5
    assert len(ml_models_docs.tree_nodes(tree)) == 11
    assert ml_models_docs.grow_tree(rows, max_depth=1)["left"]["feature"] is None


def test_tree_stopping_rules_limit_growth():
    rows = ml_models_docs.TREE_TOY_ROWS
    shallow = ml_models_docs.grow_tree(rows, max_depth=2)
    assert ml_models_docs.tree_depth(shallow) == 2
    leafy = ml_models_docs.grow_tree(rows, min_samples_leaf=3)
    assert all(leaf["n"] >= 3 for leaf in ml_models_docs.tree_leaves(leafy))
    assert ml_models_docs.grow_tree(rows, min_samples_split=13)["feature"] is None


def test_tree_feature_importances_sum_to_one_and_match_sklearn():
    tree = ml_models_docs.grow_tree(ml_models_docs.TREE_TOY_ROWS)
    imp = ml_models_docs.tree_feature_importances(tree, 2)
    assert sum(imp) == pytest.approx(1.0)
    assert imp == pytest.approx([0.6244898, 0.3755102])


def test_cost_complexity_path_matches_sklearn():
    tree = ml_models_docs.grow_tree(ml_models_docs.TREE_TOY_ROWS)
    path = ml_models_docs.cost_complexity_path(tree)
    assert [round(a, 8) for a, _, _ in path] == [0.0, 0.0462963, 0.09920635, 0.24801587]
    assert [leaves for _, leaves, _ in path] == [6, 3, 2, 1]
    assert [round(r, 8) for _, _, r in path] == [0.0, 0.13888889, 0.23809524, 0.48611111]


def test_pruning_with_alpha_keeps_the_subtree_at_that_alpha():
    tree = ml_models_docs.grow_tree(ml_models_docs.TREE_TOY_ROWS)
    assert len(ml_models_docs.tree_leaves(ml_models_docs.prune_tree(tree, 0.0))) == 6
    assert len(ml_models_docs.tree_leaves(ml_models_docs.prune_tree(tree, 0.05))) == 3
    assert len(ml_models_docs.tree_leaves(ml_models_docs.prune_tree(tree, 0.1))) == 2
    assert len(ml_models_docs.tree_leaves(ml_models_docs.prune_tree(tree, 1.0))) == 1
    assert len(ml_models_docs.tree_leaves(tree)) == 6


def test_depth_sweep_shows_training_accuracy_outrunning_test_accuracy():
    sweep = ml_models_docs.depth_sweep()
    assert [row[0] for row in sweep] == [1, 2, 3, 4, 6, None]
    train = [row[2] for row in sweep]
    assert train == sorted(train) and train[-1] == 1.0
    best_test = max(row[3] for row in sweep)
    assert sweep[-1][3] < best_test
    assert sweep[0][1:] == (2, 0.75, 0.6825)


def test_impurity_importance_credits_a_pure_noise_feature():
    signal, noise_float, noise_bit = ml_models_docs.importance_demo()
    assert signal > noise_float > noise_bit
    assert noise_float > 0.2


def test_regression_split_picks_the_lowest_sse_threshold():
    xs, ys, rows, total = ml_models_docs.regression_split_demo()
    best = min(rows, key=lambda r: r["sse"])
    assert best["threshold"] == 4.5
    assert best["mean_left"] == pytest.approx(1.2) and best["mean_right"] == pytest.approx(4.1)
    assert best["sse"] == pytest.approx(0.3)
    assert total == pytest.approx(sum((y - sum(ys) / len(ys)) ** 2 for y in ys))


def test_toy_tree_diagram_layout_matches_the_grown_tree():
    tree = ml_models_docs.grow_tree(ml_models_docs.TREE_TOY_ROWS, max_depth=2)
    assert (tree["feature"], tree["threshold"]) == (0, 5.5)
    assert tree["right"]["feature"] is None and tree["right"]["n"] == 5
    assert (tree["left"]["feature"], tree["left"]["threshold"]) == (1, 2.5)
    assert tree["left"]["left"]["feature"] is None
    assert tree["left"]["right"]["feature"] is None


def test_boost_stumps_match_sklearn_gradient_boosting_run():
    init, history = ml_models_docs.boost_stumps(ml_models_docs.BOOST_XS, ml_models_docs.BOOST_YS, 4, 0.5)
    assert init == pytest.approx(2.65)
    assert [round(r["mse"], 6) for r in history] == [0.745, 0.503264, 0.375855, 0.276978]
    assert [r["threshold"] for r in history] == [2.5, 6.5, 2.5, 7.5]
    assert history[0]["left"] == pytest.approx(-1.1)
    assert history[0]["right"] == pytest.approx(0.366667, abs=1e-6)


def test_each_boosting_round_lowers_training_error_on_the_toy_data():
    _, history = ml_models_docs.boost_stumps(ml_models_docs.BOOST_XS, ml_models_docs.BOOST_YS, 8, 0.5)
    errors = [r["mse"] for r in history]
    assert errors == sorted(errors, reverse=True)


def test_boosting_curve_shows_shrinkage_and_early_stopping():
    def best(curve):
        test = [t for _, t in curve]
        return min(range(len(test)), key=test.__getitem__) + 1, min(test)

    fast = ml_models_docs.boosting_curve(1.0, 300)
    slow = ml_models_docs.boosting_curve(0.1, 300)
    fast_round, fast_best = best(fast)
    slow_round, slow_best = best(slow)
    assert (fast_round, round(fast_best, 4)) == (2, 0.3141)
    assert (slow_round, round(slow_best, 4)) == (40, 0.2901)
    assert slow_best < fast_best
    assert fast[-1][0] < 1e-6 and fast[-1][1] > 0.45
    assert slow[-1][1] > slow_best


def test_newton_scan_matches_xgboost_run():
    grads = [0.5 - label for label in ml_models_docs.NEWTON_LABELS]
    hessians = [0.25] * len(grads)
    scan = ml_models_docs.newton_scan(ml_models_docs.NEWTON_XS, grads, hessians, reg_lambda=1.0)
    best = max(scan["candidates"], key=lambda c: c["loss_chg"])
    assert best["threshold"] == 3.5
    assert best["loss_chg"] == pytest.approx(2.2857143, abs=1e-6)
    assert best["w_left"] == pytest.approx(-0.857143, abs=1e-6)
    assert best["w_right"] == pytest.approx(0.666667, abs=1e-6)
    assert (best["h_left"], best["h_right"]) == (0.75, 1.25)


def test_newton_scan_regularization_gamma_and_min_child_weight():
    grads = [0.5 - label for label in ml_models_docs.NEWTON_LABELS]
    hessians = [0.25] * len(grads)

    def best(**kwargs):
        scan = ml_models_docs.newton_scan(ml_models_docs.NEWTON_XS, grads, hessians, **kwargs)
        kept = [c for c in scan["candidates"] if c["kept"]]
        return max(kept, key=lambda c: c["loss_chg"]) if kept else None

    assert best(reg_lambda=0.0)["w_left"] == pytest.approx(-2.0)
    assert best(reg_lambda=4.0)["w_left"] == pytest.approx(-0.315789, abs=1e-6)
    assert best(reg_lambda=1.0, gamma=2.2) is not None
    assert best(reg_lambda=1.0, gamma=2.3) is None
    assert best(reg_lambda=1.0, min_child_weight=1.0)["threshold"] == 4.5


def test_regression_tree_helper_fits_a_step_function_exactly():
    xs = [1, 2, 3, 4]
    tree = ml_models_docs.grow_regression_tree(xs, [1.0, 1.0, 5.0, 5.0], 3)
    assert [ml_models_docs.regression_tree_predict(tree, x) for x in xs] == [1.0, 1.0, 5.0, 5.0]
    assert tree["threshold"] == 2.5


def test_poly_ridge_fit_matches_sklearn_ridge_with_free_intercept():
    weights = ml_models_docs.poly_ridge_fit([0.0, 0.25, 0.5, 0.75, 1.0], [0.0, 1.0, 0.0, -1.0, 0.5], 2, 0.5)
    assert weights == pytest.approx([0.0090909, -0.1666667, 0.1818182], abs=1e-6)


def test_poly_ridge_with_zero_alpha_matches_the_plain_polynomial_fit():
    xs, ys = ml_models_docs.GENERALIZATION_X, ml_models_docs.generalization_train_targets()
    assert ml_models_docs.poly_ridge_fit(xs, ys, 3, 0.0) == pytest.approx(ml_models_docs.polynomial_fit(xs, ys, 3))


def test_learning_curves_separate_high_bias_from_high_variance():
    sizes = [15, 40, 320]
    simple = ml_models_docs.polynomial_learning_curve(1, sizes)
    flexible = ml_models_docs.polynomial_learning_curve(9, sizes)
    assert simple[-1][2] > 0.3 and simple[-1][2] - simple[-1][1] < 0.1
    assert flexible[0][2] > 100 * flexible[0][1]
    assert flexible[-1][2] < simple[-1][2] / 2
    assert flexible[-1][2] - flexible[-1][1] < 0.05


def test_ridge_strength_sweep_has_an_interior_best_value():
    rows = ml_models_docs.ridge_strength_sweep([0, 0.01, 10])
    assert rows[1][2] < rows[0][2] / 10 and rows[1][2] < rows[2][2]


def test_memorization_demo_fits_random_labels_without_generalizing():
    demo = ml_models_docs.memorization_demo()
    assert demo["train_accuracy"] == 1.0
    assert 0.45 < demo["test_accuracy"] < 0.6
    assert demo["leaves"] > 10


def test_bias_variance_decomposition_adds_up_and_tracks_flexibility():
    stiff = ml_models_docs.bias_variance_decomposition(1, repeats=60)
    mid = ml_models_docs.bias_variance_decomposition(3, repeats=60)
    wild = ml_models_docs.bias_variance_decomposition(9, repeats=60)
    assert stiff["bias2"] > mid["bias2"]
    assert wild["variance"] > 10 * mid["variance"]
    assert wild["variance"] > stiff["variance"]
    for r in (stiff, mid, wild):
        assert abs(r["error"] - (r["bias2"] + r["variance"])) < 1e-6 * max(1, r["error"])
        assert r["noise"] == 0.3 ** 2


def test_bias_variance_ridge_and_bagging_cut_variance():
    plain = ml_models_docs.bias_variance_decomposition(9, alpha=1e-3, repeats=40)
    bagged = ml_models_docs.bias_variance_decomposition(9, alpha=1e-3, repeats=40, bags=10)
    stronger = ml_models_docs.bias_variance_decomposition(9, alpha=1e-2, repeats=40)
    assert bagged["variance"] < plain["variance"]
    assert stronger["variance"] < plain["variance"]


def test_penalized_fits_lasso_zeroes_noise_features_and_ridge_does_not():
    fits = ml_models_docs.penalized_fits(20, 0.4)
    assert all(c == 0.0 for c in fits["lasso"][3:])
    assert all(c != 0.0 for c in fits["ridge"])
    assert sum(abs(c) for c in fits["ridge"]) < sum(abs(c) for c in fits["ols"])
    assert sum(abs(c) for c in fits["lasso"]) < sum(abs(c) for c in fits["ols"])


def test_lasso_sparsity_path_shrinks_the_active_set():
    path = ml_models_docs.lasso_sparsity_path([0, 0.2, 0.8, 3.2])
    counts = [count for _, count, _ in path]
    assert counts[0] == 8
    assert counts == sorted(counts, reverse=True)
    assert counts[-1] < counts[1]


def test_dropout_statistics_is_unbiased_with_inverted_scaling():
    stats = ml_models_docs.dropout_statistics([1.0, 2.0, -3.0], 0.5, trials=3000)
    assert stats["scale"] == 2.0
    assert abs(stats["kept_fraction"] - 0.5) < 0.03
    for mean, value in zip(stats["means"], [1.0, 2.0, -3.0]):
        assert abs(mean - value) < 0.2
    assert stats["exact_variances"] == [1.0, 4.0, 9.0]
    for estimate, exact in zip(stats["variances"], stats["exact_variances"]):
        assert abs(estimate - exact) < 0.15 * exact


def test_adam_decay_decoupled_is_independent_of_gradient_scale_and_l2_is_not():
    small = ml_models_docs.adam_weight_decay_comparison(0.1)
    large = ml_models_docs.adam_weight_decay_comparison(100.0)
    assert abs(small["decoupled_extra_shrink"] - large["decoupled_extra_shrink"]) < 1e-6
    assert small["l2_extra_shrink"] > 10 * large["l2_extra_shrink"] > 0


def test_activation_slopes_match_finite_differences():
    for name, f, d in ml_models_docs.ACTIVATIONS:
        for x in (-2.5, -0.7, 0.4, 1.9):
            assert abs(ml_models_docs.numeric_slope(f, x) - d(x)) < 1e-6, (name, x)


def test_activation_values_and_landmarks():
    table = {r["name"]: r for r in ml_models_docs.activation_table([-3, 0, 3])}
    assert table["sigmoid"]["values"][1] == 0.5 and table["sigmoid"]["slopes"][1] == 0.25
    assert table["tanh"]["slopes"][1] == 1.0
    assert table["relu"]["values"] == [0.0, 0.0, 3]
    assert table["leaky_relu"]["values"][0] == -0.03
    assert abs(table["softplus"]["values"][1] - math.log(2)) < 1e-12
    assert abs(table["gelu"]["values"][2] - 2.9959502) < 1e-6


def test_gelu_tanh_approximation_is_close_but_not_equal():
    worst, at = ml_models_docs.gelu_tanh_max_error()
    assert 0 < worst < 1e-3
    assert 2 < abs(at) < 4


def test_chain_gradient_vanishes_for_sigmoid_but_not_relu():
    assert ml_models_docs.chain_gradient("sigmoid", 10, 0.0) == 0.25**10
    assert ml_models_docs.chain_gradient("relu", 10, 2.0) == 1.0
    assert ml_models_docs.chain_gradient("relu", 10, -2.0) == 0.0
    assert ml_models_docs.chain_gradient("sigmoid", 10, 4.0) < ml_models_docs.chain_gradient("sigmoid", 10, 0.0)


def test_glu_variants_gate_one_half_with_the_other():
    out = ml_models_docs.glu_variants(1.0, 2.0)
    assert abs(out["glu"] - 1.0 * ml_models_docs.sigmoid(2.0)) < 1e-12
    assert abs(out["swiglu"] - ml_models_docs.silu(1.0) * 2.0) < 1e-12
    assert out["reglu"] == 2.0


def test_relu_active_fraction_collapses_with_a_negative_bias():
    assert 0.45 < ml_models_docs.relu_active_fraction(0.0) < 0.55
    assert ml_models_docs.relu_active_fraction(-5.0) == 0.0
    assert ml_models_docs.relu_active_fraction(-3.0) < 0.01


def _close_matrices(first, second, tol=1e-9):
    return all(abs(a - b) < tol for r1, r2 in zip(first, second) for a, b in zip(r1, r2))


def test_jacobi_eigh_matches_the_closed_form_and_sorts_ascending():
    eigen = ml_models_docs.jacobi_eigh([[2, 1], [1, 2]])
    assert [round(x, 12) for x in eigen["values"]] == [1.0, 3.0]
    closed = ml_models_docs.symmetric_eigen_2x2([[2, 1], [1, 2]])
    assert abs(eigen["values"][1] - closed["values"][0]) < 1e-12
    for value, vector in zip(eigen["values"], eigen["vectors"]):
        image = [ml_models_docs.dot_product(row, vector) for row in [[2, 1], [1, 2]]]
        assert all(abs(a - value * b) < 1e-12 for a, b in zip(image, vector))


def test_jacobi_eigh_rebuilds_a_symmetric_3x3():
    s = [[4, 1, 2], [1, 3, 0], [2, 0, 5]]
    eigen = ml_models_docs.jacobi_eigh(s)
    q = ml_models_docs.transpose(eigen["vectors"])
    rebuilt = ml_models_docs.matmul(
        ml_models_docs.matmul(q, [[v if i == j else 0 for j, v in enumerate(eigen["values"])] for i in range(3)]),
        eigen["vectors"],
    )
    assert _close_matrices(rebuilt, s)
    assert abs(sum(eigen["values"]) - 12) < 1e-12


def test_power_iteration_converges_at_the_eigenvalue_ratio():
    example = ml_models_docs.EIGEN_EXAMPLE
    trace = ml_models_docs.power_iteration(example["matrix"], example["start"], example["steps"])
    errors = [3 - step["value"] for step in trace]
    assert all(e > 0 for e in errors)
    for before, after in zip(errors, errors[1:]):
        assert abs(after / before - 1 / 9) < 0.02


def test_svd_of_the_geometry_example():
    factors = ml_models_docs.svd(ml_models_docs.SVD_EXAMPLE)
    assert abs(factors["S"][0] - 3 * math.sqrt(5)) < 1e-12
    assert abs(factors["S"][1] - math.sqrt(5)) < 1e-12
    assert _close_matrices(ml_models_docs.from_svd(factors), ml_models_docs.SVD_EXAMPLE)
    assert abs(ml_models_docs.condition_number(ml_models_docs.SVD_EXAMPLE) - 3) < 1e-12


def test_svd_factors_are_orthonormal_for_tall_and_wide_matrices():
    for matrix in (ml_models_docs.RATINGS_EXAMPLE["ratings"], [[1, 2, 3], [4, 5, 6]]):
        factors = ml_models_docs.svd(matrix)
        k = len(factors["S"])
        assert factors["S"] == sorted(factors["S"], reverse=True)
        assert _close_matrices(ml_models_docs.matmul(factors["Vh"], ml_models_docs.transpose(factors["Vh"])), ml_models_docs.identity(k))
        assert _close_matrices(ml_models_docs.matmul(ml_models_docs.transpose(factors["U"]), factors["U"]), ml_models_docs.identity(k))
        assert _close_matrices(ml_models_docs.from_svd(factors), matrix)


def test_low_rank_error_is_the_sum_of_dropped_squared_singular_values():
    errors = ml_models_docs.low_rank_errors(ml_models_docs.RATINGS_EXAMPLE["ratings"])
    assert errors[0]["error"] == pytest.approx(214)
    for entry in errors:
        assert entry["error"] == pytest.approx(entry["dropped"], abs=1e-9)
    assert [e["error"] for e in errors] == sorted((e["error"] for e in errors), reverse=True)
    assert errors[2]["kept_share"] > 0.98


def test_eckart_young_beats_other_rank_one_choices():
    ratings = ml_models_docs.RATINGS_EXAMPLE["ratings"]
    best = ml_models_docs.low_rank_errors(ratings)[1]["error"]
    rng = __import__("random").Random(0)
    for _ in range(50):
        v = [rng.uniform(-1, 1) for _ in range(4)]
        n = ml_models_docs.vector_norm(v)
        v = [x / n for x in v]
        u = [ml_models_docs.dot_product(row, v) for row in ratings]
        error = sum((ratings[i][j] - u[i] * v[j]) ** 2 for i in range(5) for j in range(4))
        assert error >= best - 1e-9


def test_matrix_rank_uses_the_torch_tolerance():
    assert ml_models_docs.matrix_rank(ml_models_docs.RANK_EXAMPLE) == 2
    assert ml_models_docs.matrix_rank(ml_models_docs.identity(3)) == 3
    assert ml_models_docs.rank_from_singular_values([1.0, 1e-17], (2, 2)) == 1
    assert ml_models_docs.rank_from_singular_values([1.0, 0.1], (2, 2), atol=0.5) == 1


def test_an_ill_conditioned_solve_amplifies_a_tiny_change():
    result = ml_models_docs.perturbed_solve(ml_models_docs.CONDITION_EXAMPLE)
    assert [round(x, 6) for x in result["x"]] == [1.0, 1.0]
    assert [round(x, 6) for x in result["x_nudged"]] == [0.0, 2.0]
    assert 40000 < result["cond"] < 40004
    assert 1000 < result["amplification"] <= result["cond"]


def test_unit_circle_image_reaches_the_singular_values():
    points = ml_models_docs.unit_circle_image(ml_models_docs.SVD_EXAMPLE, count=720)
    lengths = [ml_models_docs.vector_norm(p["out"]) for p in points]
    assert max(lengths) == pytest.approx(3 * math.sqrt(5), rel=1e-4)
    assert min(lengths) == pytest.approx(math.sqrt(5), rel=1e-4)


def test_lora_param_counts():
    counts = ml_models_docs.lora_param_counts(4096, 4096, 8)
    assert counts == {"full": 16777216, "lora": 65536, "share": 65536 / 16777216}


def test_svd_stages_rotate_stretch_then_rotate_to_the_image():
    stages = ml_models_docs.svd_stages(ml_models_docs.SVD_EXAMPLE, count=36)
    factors = ml_models_docs.svd(ml_models_docs.SVD_EXAMPLE)
    for rotated in stages["rotated"]:
        assert ml_models_docs.vector_norm(rotated) == pytest.approx(1)
    for stretched, image in zip(stages["stretched"], stages["image"]):
        rebuilt = [ml_models_docs.dot_product(row, stretched) for row in factors["U"]]
        assert rebuilt == pytest.approx(image)


def test_templates_only_read_pin_keys_that_exist():
    for name in os.listdir(TEMPLATES_DIR):
        with open(os.path.join(TEMPLATES_DIR, name)) as handle:
            source = handle.read()
        for library, key in re.findall(r"pins\.(\w+)\.(\w+)", source):
            assert key in ml_models_docs.PINS[library], (name, library, key)


def test_fill_values_match_simple_imputer_statistics():
    rows = ml_models_docs.MISSING_EXAMPLE["rows"]
    age = ml_models_docs.column_fill_values([row[0] for row in rows])
    income = ml_models_docs.column_fill_values([row[1] for row in rows])
    assert (age["missing"], age["mean"], age["median"]) == (2, pytest.approx(36.3333333), 36.5)
    assert (income["missing"], income["mean"], income["median"]) == (3, pytest.approx(61.2), 61)
    assert age["constant"] == income["constant"] == 0
    assert ml_models_docs.missing_indicator([row[1] for row in rows]) == [0, 1, 0, 0, 1, 0, 0, 1]
    assert len(ml_models_docs.complete_rows(rows)) == 3


def test_impute_column_keeps_observed_values():
    column = [1, None, 5, None]
    assert ml_models_docs.impute_column(column, "mean") == [1, 3, 5, 3]
    assert ml_models_docs.impute_column(column, "constant", fill_value=-1) == [1, -1, 5, -1]


def test_mechanisms_bias_complete_case_and_regression_imputation():
    mcar, mar, mnar = (ml_models_docs.mechanism_estimates(m) for m in ("MCAR", "MAR", "MNAR"))
    for result in (mcar, mar, mnar):
        assert result["missing_share"] == pytest.approx(0.4, abs=0.02)
    assert abs(mcar["complete_case_mean"] - mcar["true_mean"]) < 0.2
    assert mar["true_mean"] - mar["complete_case_mean"] > 2.5
    assert abs(mar["regression_mean"] - mar["true_mean"]) < 0.2
    assert mnar["true_mean"] - mnar["regression_mean"] > 1.0
    for result in (mcar, mar, mnar):
        assert result["mean_imputed_std"] < 0.8 * result["true_std"]
        assert result["mean_imputed_corr"] < result["true_corr"] - 0.15


def test_iterative_impute_matches_the_round_robin_rule():
    comparison = ml_models_docs.iterative_comparison()
    rounds = comparison["rounds"]
    assert len(rounds) == 9
    assert all(not r["converged"] for r in rounds[:-1]) and rounds[-1]["converged"]
    assert rounds[-1]["change"] < comparison["threshold"] <= rounds[-2]["change"]
    assert comparison["order"] == [0, 1, 2]
    assert comparison["iterative_rmse"] < 0.5 * comparison["mean_rmse"]


def test_iterative_impute_keeps_observed_cells():
    truth, observed = ml_models_docs.iterative_rows()
    filled = ml_models_docs.iterative_impute(observed)["rows"]
    for o_row, f_row in zip(observed, filled):
        for o, f in zip(o_row, f_row):
            if o is not None:
                assert f == o


def test_missing_indicator_helps_when_missingness_is_informative():
    result = ml_models_docs.indicator_comparison()
    assert result["with_indicator"]["mse"] < 0.7 * result["imputed"]["mse"]
    assert result["with_indicator"]["weights"][2] > 1


def test_routing_matches_xgboost_default_direction():
    result = ml_models_docs.routing_example()
    best = result["native"]["best"]
    assert (best["threshold"], best["missing_go"]) == (3.5, "left")
    assert best["loss_chg"] == pytest.approx(2.638888, abs=1e-5)
    assert (best["w_left"], best["w_right"]) == (pytest.approx(5 / 6), pytest.approx(2.25))
    assert result["fill"] == 4.0
    imputed = result["imputed"]["best"]
    assert imputed["loss_chg"] == pytest.approx(0.638888, abs=1e-5)
    assert imputed["missing_go"] == "right"


def test_routing_without_missing_values_sends_missing_right():
    scan = ml_models_docs.missing_split_scan([1, 2, 3, 4], [-1, -1, -3, -3], [1, 1, 1, 1])
    assert scan["missing_h"] == 0
    assert {c["missing_go"] for c in scan["candidates"]} == {"left", "right"}
    assert scan["best"]["missing_go"] == "right"


def test_routing_ties_keep_the_forward_scan():
    scan = ml_models_docs.missing_split_scan([1, 2, None], [-2, 2, 0], [1, 1, 1])
    assert scan["candidates"][0]["loss_chg"] == pytest.approx(scan["candidates"][1]["loss_chg"])
    assert scan["best"]["missing_go"] == "right"


def test_graph_records_pytorch_node_names_and_edges():
    result = ml_models_docs.graph_example()
    assert [(n["tensor"], n["name"], n["next"]) for n in result["nodes"]] == [
        ("a", "MulBackward0", ["AccumulateGrad", None]),
        ("y", "AddBackward0", ["MulBackward0", "AccumulateGrad"]),
        ("loss", "MulBackward0", ["AddBackward0", "AddBackward0"]),
    ]
    assert [n["sequence_nr"] for n in result["nodes"]] == [0, 1, 2]
    assert result["leaf"] == {"x": True, "w": True, "b": True, "a": False, "y": False, "loss": False}
    assert result["requires_grad"]["x"] is False


def test_graph_backward_matches_the_chain_rule():
    example = ml_models_docs.GRAPH_EXAMPLE
    result = ml_models_docs.graph_example()
    y = example["w"] * example["x"] + example["b"]
    assert result["grads"] == {"x": None, "w": 2 * y * example["x"], "b": 2 * y, "a": None, "y": None}

    def loss(w, b):
        return (w * example["x"] + b) ** 2

    h = 1e-6
    assert result["grads"]["w"] == pytest.approx((loss(3 + h, 1) - loss(3 - h, 1)) / (2 * h), rel=1e-6)


def test_graph_engine_runs_newest_ready_node_first():
    trace = ml_models_docs.graph_example()["trace"]
    assert [(t["name"], t["grad"]) for t in trace] == [
        ("MulBackward0", 1.0), ("AddBackward0", 14.0), ("AccumulateGrad", 14.0),
        ("MulBackward0", 14.0), ("AccumulateGrad", 28.0),
    ]


def test_graph_second_backward_fails_without_retain_graph():
    message = ml_models_docs.graph_example()["second_backward"]
    assert message.startswith("Trying to backward through the graph a second time")
    assert "retain_graph=True" in message


def test_graph_controls():
    result = ml_models_docs.graph_controls()
    assert result["retained"] == {"first": 28.0, "second": 56.0, "b": 28.0}
    assert result["hooked"] == {"w": 14.0, "b": 7.0}
    assert result["detached"] == {"w": 14.0, "b": 7.0, "value": 49.0}
    assert result["no_grad"] == {"requires_grad": False, "grad_fn": None, "is_leaf": True}
    assert result["clamps"]["clamp"]["w"] == 0.0
    assert result["clamps"]["straight_through_clamp"] == {
        "name": "StraightThroughClampBackward", "value": 25.0, "w": 20.0, "b": 10.0,
    }


def test_graph_hook_needs_requires_grad():
    engine = ml_models_docs.Autograd()
    with pytest.raises(RuntimeError, match="doesn't require gradient"):
        engine.register_hook(engine.tensor(1.0), lambda g: g)


def test_conv_output_size_matches_the_pytorch_formula():
    sizes = {row["label"]: row["out"] for row in ml_models_docs.output_size_rows()}
    assert sizes["3×3, stride 1, padding 1"] == 32
    assert sizes["3×3, stride 2, padding 1"] == 16
    assert sizes["7×7, stride 2, padding 3"] == 112
    assert ml_models_docs.conv_output_size(32, 3, padding=2, dilation=2) == 32
    assert ml_models_docs.pool_output_size(5, 2) == 2
    assert ml_models_docs.pool_output_size(5, 2, ceil_mode=True) == 3
    assert ml_models_docs.pool_output_size(112, 3, 2, 1) == 56


def test_conv2d_is_a_sliding_dot_product():
    example = ml_models_docs.conv_example()
    assert example["output"] == [[0, 9, 9, 0]] * 4
    assert example["term_sum"] == example["output"][0][1]
    assert len(example["padded"]) == 6 and len(example["strided"]) == 3
    assert example["dilated"] == [[9, 9], [9, 9]]
    x = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    weight = [[[[1]], [[10]]]]
    assert ml_models_docs.conv2d(x, weight, bias=[1]) == [[[52, 63], [74, 85]]]


def test_pooling_reduces_each_window():
    example = ml_models_docs.conv_example()
    assert example["max_pool"] == [[6, 2], [2, 7]]
    assert example["avg_pool"] == [[3.5, 1.0], [1.0, 4.25]]


def test_receptive_fields_grow_with_depth_and_stride():
    comparison = ml_models_docs.stacking_comparison()
    assert comparison["stacked_rf"] == comparison["single_rf"] == 7
    assert comparison["stacked_params"] == 27 * 64 * 64
    assert comparison["single_params"] == 49 * 64 * 64
    assert ml_models_docs.resnet_receptive_fields()[-1] == {"layer": "layer4.1 conv2", "size": 435, "jump": 32}


def test_lenet_stack_shapes_and_params():
    stack = ml_models_docs.lenet_stack()
    assert [row["shape"] for row in stack["rows"]][1:6] == [[6, 28, 28], [6, 14, 14], [16, 10, 10], [16, 5, 5], [400]]
    assert stack["total"] == 61706


def test_resnet18_stack_matches_the_published_size():
    stack = ml_models_docs.resnet18_stack()
    assert [row["shape"] for row in stack["rows"]][:6] == [
        [64, 112, 112], [64, 56, 56], [64, 56, 56], [128, 28, 28], [256, 14, 14], [512, 7, 7],
    ]
    assert [row.get("downsample") for row in stack["rows"][2:6]] == [False, True, True, True]
    assert stack["total"] == 11_689_512


def test_chain_rule_factors_rebuild_the_joint_exactly():
    rows = ml_models_docs.chain_rule_factors(ml_models_docs.AR_JOINT)
    assert len(rows) == 8
    for row in rows:
        assert row["product"] == pytest.approx(row["joint"])
    first = {row["sequence"]: row["factors"] for row in rows}
    assert first[(0, 0, 0)] == pytest.approx([0.5, 0.7, 6 / 7])
    assert first[(1, 1, 1)] == pytest.approx([0.5, 0.8, 0.75])


def test_markov_approximation_loses_information():
    result = ml_models_docs.markov_approximation(ml_models_docs.AR_JOINT)
    assert sum(result["approx"].values()) == pytest.approx(1.0)
    assert result["kl_bits"] == pytest.approx(0.0394939, abs=1e-6)
    assert ml_models_docs.table_sizes(2, 3) == {"joint": 7, "chain": 7, "markov": 5}
    sizes = ml_models_docs.table_sizes(50_000, 3)
    assert sizes["joint"] == sizes["chain"] == 50_000 ** 3 - 1


def test_ancestral_samples_follow_the_joint():
    frequencies = ml_models_docs.ancestral_samples(ml_models_docs.AR_JOINT, 1000, 0)
    assert sum(frequencies.values()) == pytest.approx(1.0)
    for sequence, p in ml_models_docs.AR_JOINT.items():
        assert abs(frequencies[sequence] - p) < 0.05


def test_teacher_forcing_counts_are_the_maximum_likelihood_fit():
    example = ml_models_docs.teacher_forcing_example()
    assert example["inputs"] == ["<s>", "the", "cat", "ran"]
    assert example["targets"] == ["the", "cat", "ran", "."]
    assert [row["prob"] for row in example["rows"]] == pytest.approx([1, 2 / 3, 0.5, 1])
    assert example["total_nll"] == pytest.approx(math.log(3))
    assert example["perplexity"] == pytest.approx(3 ** 0.25)
    assert example["max_gradient"] < 1e-12


def test_exposure_bias_free_running_accuracy_decays():
    rows = ml_models_docs.exposure_bias_curve()
    assert rows[0]["free_running"] == pytest.approx(0.9)
    assert rows[1]["free_running"] == pytest.approx(0.81 + 0.1 * 0.1 / 3)
    assert all(row["teacher_forced"] == 0.9 for row in rows)
    assert all(a["free_running"] > b["free_running"] > 0.25 for a, b in zip(rows, rows[1:]))
    assert all(row["free_running"] >= row["all_correct"] - 1e-12 for row in rows)


def test_causal_convolution_never_reads_the_future():
    check = ml_models_docs.causality_check()
    assert check["first_changed"] == check["changed"]
    assert check["before"][: check["changed"]] == check["after"][: check["changed"]]
    assert ml_models_docs.causal_stack([1, 2, 3, 4, 5, 6, 7, 8])[-1][-1] == 4.5
    assert ml_models_docs.causal_conv1d([1, 2, 3], [1, 10], dilation=2) == [10, 20, 31]
    assert ml_models_docs.causal_receptive_field(2, [1, 2, 4]) == 8
    sizes = [row["size"] for row in ml_models_docs.wavenet_receptive_fields()]
    assert sizes == [2, 11, 1024, 3070]


def test_pixelcnn_masks_and_blind_spot():
    assert ml_models_docs.pixelcnn_mask(3, "A") == [[1, 1, 1], [1, 0, 0], [0, 0, 0]]
    assert ml_models_docs.pixelcnn_mask(3, "B") == [[1, 1, 1], [1, 1, 0], [0, 0, 0]]
    assert sum(map(sum, ml_models_docs.pixelcnn_mask(5, "A"))) == 12
    result = ml_models_docs.pixelcnn_dependencies(3)
    grid = result["grid"]
    assert grid[5][3] == "target"
    assert result["blind"] == 3
    assert grid[3][6] == grid[4][5] == grid[4][6] == "blind"
    assert all(cell == "far" for cell in grid[0])


def test_bpe_merges_the_most_frequent_pair_each_step():
    result = ml_models_docs.bpe_train(merges=10)
    steps = result["steps"]

    assert result["start_tokens"] == 95
    assert [s["pair"] for s in steps[:5]] == [("e", "s"), ("es", "t"), ("est", "</w>"), ("l", "o"), ("lo", "w")]
    assert [s["count"] for s in steps[:3]] == [9, 9, 9]
    previous = result["start_tokens"]
    for step in steps:
        assert previous - step["tokens"] == step["count"]
        previous = step["tokens"]
    assert steps[-1]["vocab_size"] == len(result["base"]) + 10


def test_bpe_encodes_unseen_words_from_learned_merges():
    merges = [s["pair"] for s in ml_models_docs.bpe_train(merges=10)["steps"]]

    assert ml_models_docs.bpe_encode("lowest", merges) == ["low", "est</w>"]
    assert ml_models_docs.bpe_encode("newer", merges) == ["new", "e", "r", "</w>"]
    assert ml_models_docs.bpe_encode("low", merges) == ["low</w>"]


def test_wordpiece_picks_the_largest_likelihood_gain():
    rows = ml_models_docs.wordpiece_gains()

    assert rows[0]["pair"] == ("s", "t")
    assert rows == sorted(rows, key=lambda r: -r["gain"])
    bpe_first = ml_models_docs.bpe_train(merges=1)["steps"][0]["pair"]
    assert bpe_first != rows[0]["pair"]


def test_unigram_viterbi_finds_the_most_likely_segmentation():
    rows = ml_models_docs.unigram_segmentations("lowest")
    best = ml_models_docs.unigram_viterbi("lowest")

    assert len(rows) == 14
    assert best["pieces"] == rows[0]["pieces"] == ["low", "est"]
    assert math.isclose(best["log_prob"], math.log(0.12) + math.log(0.10))
    assert math.isclose(sum(r["share"] for r in rows), 1.0)
    assert all("".join(r["pieces"]) == "lowest" for r in rows)


def test_utf8_lengths_and_digit_groups():
    rows = {r["text"]: r for r in ml_models_docs.utf8_lengths()}

    assert [rows[t]["byte_count"] for t in ["cat", "café", "猫", "🐈"]] == [3, 5, 3, 4]
    assert rows["café"]["bytes"][-2:] == [195, 169]
    assert ml_models_docs.digit_groups(12345) == ["123", "45"]
    assert ml_models_docs.digit_groups(1234567, from_right=True) == ["1", "234", "567"]


def test_batch_ids_pad_mask_and_shift_targets():
    batch = ml_models_docs.batch_ids(["the cat sat", "the dog"])

    assert batch["ids"] == [[1, 3, 4, 5, 2], [1, 3, 6, 2, 0]]
    assert batch["mask"] == [[1, 1, 1, 1, 1], [1, 1, 1, 1, 0]]
    assert batch["targets"] == [[3, 4, 5, 2], [3, 6, 2, -100]]


def test_minkowski_metrics_order_by_p():
    rows = {r["name"]: r["distance"] for r in ml_models_docs.metric_table()}

    assert rows["manhattan"] == 7.0
    assert rows["euclidean"] == 5.0
    assert rows["chebyshev"] == 4.0
    assert rows["chebyshev"] < rows["minkowski"] < rows["euclidean"]


def test_knn_reproduces_the_sklearn_docstring_examples():
    examples = ml_models_docs.docstring_examples()

    assert examples["predict_1_1"] == 0
    assert math.isclose(examples["proba_0_9"][0], 2 / 3)
    assert math.isclose(examples["proba_0_9"][1], 1 / 3)
    assert examples["regress_1_5"] == 0.5


def test_knn_vote_flips_with_k_and_distance_weights():
    sweep = ml_models_docs.k_sweep()
    weighted = ml_models_docs.knn_classify(k=5, weights="distance")

    assert [r["prediction"] for r in sweep] == [0, 0, 1, 0, 0]
    assert sweep[2]["votes"] == {0: 2.0, 1: 3.0}
    assert weighted["prediction"] == 1
    assert math.isclose(weighted["neighbors"][0]["weight"], 1 / math.hypot(0.2, 1.0))
    assert ml_models_docs.neighbor_weights([0.0, 2.0, 0.0], "distance") == [1.0, 0.0, 1.0]


def test_leave_one_out_error_picks_a_middle_k():
    rows = {r["k"]: r["errors"] for r in ml_models_docs.leave_one_out()}

    assert rows == {1: 2, 3: 0, 5: 0, 7: 1, 9: 1, 15: 16}


def test_distances_concentrate_as_dimension_grows():
    ratios = [r["ratio"] for r in ml_models_docs.distance_concentration()]
    edges = [r["edge"] for r in ml_models_docs.neighborhood_edge()]

    assert ratios == sorted(ratios)
    assert ratios[0] < 0.01 and ratios[-1] > 0.9
    assert math.isclose(edges[1], 0.1)
    assert edges[-1] > 0.95


def test_kd_tree_matches_sklearn_sizes_and_prunes():
    assert ml_models_docs.tree_size(16, 2) == {"n_levels": 3, "n_nodes": 7}
    assert ml_models_docs.tree_size(1000, 40) == {"n_levels": 5, "n_nodes": 31}

    tree = ml_models_docs.kd_tree_build()
    leaves = [n for n in tree["nodes"] if n["leaf"]]
    assert [len(n["points"]) for n in leaves] == [4, 4, 4, 4]
    assert (tree["nodes"][0]["split_dim"], tree["nodes"][0]["split_value"]) == (0, 5.0)

    one = ml_models_docs.kd_tree_query(k=1)
    assert one["scanned"] == 4 and one["trimmed"] == [3, 5, 6]
    assert one["neighbors"][0]["index"] == 7
    assert ml_models_docs.kd_tree_query(k=5)["scanned"] == 16

    ball = ml_models_docs.ball_bound_example(label=0)
    assert 0 < ball["bound"] <= ball["true_min"]


def test_metrics_disagree_raw_and_agree_after_normalizing():
    result = ml_models_docs.metric_agreement()
    raw, unit = result["raw"], result["normalized"]

    assert raw["by_dot"] == ["A", "D", "B", "C", "E"]
    assert raw["by_cosine"] == ["C", "A", "B", "D", "E"]
    assert raw["by_distance"] == ["C", "B", "E", "D", "A"]
    assert unit["by_dot"] == unit["by_cosine"] == unit["by_distance"] == raw["by_cosine"]
    for row in result["identity"]:
        assert math.isclose(row["squared_distance"], row["two_minus_two_cos"], abs_tol=1e-12)


def test_brute_force_search_cost():
    cost = ml_models_docs.brute_force_search_cost(1_000_000, 768)

    assert cost["flops"] == 1_536_000_000
    assert cost["index_bytes"] == 3_072_000_000
    assert cost["intensity"] == 0.5
    assert ml_models_docs.brute_force_search_cost(10, 4, queries=3)["flops"] == 240


def test_bm25_matches_the_lucene_formula():
    result = ml_models_docs.bm25_scores()
    rows = {row["name"]: row for row in result["rows"]}

    assert result["avgdl"] == 8.75
    assert math.isclose(result["idf"]["cat"], math.log(2))
    assert math.isclose(result["idf"]["mat"], math.log(3.5 / 1.5 + 1))
    norm = 1.2 * (1 - 0.75 + 0.75 * 6 / 8.75)
    assert math.isclose(rows["d1"]["parts"]["cat"], math.log(2) * 2.2 / (1 + norm))
    assert rows["d2"]["parts"]["cat"] > rows["d1"]["parts"]["cat"]
    assert rows["d3"]["score"] == 0 and rows["d4"]["score"] == 0
    assert result["ranking"][:2] == ["d1", "d2"]

    weights = [row["weight"] for row in ml_models_docs.bm25_saturation()]
    assert weights[0] == 1.0 and weights == sorted(weights) and weights[-1] < 2.2


def test_reciprocal_rank_fusion():
    fused = ml_models_docs.reciprocal_rank_fusion([["x", "y"], ["y", "z"]], k=60)
    assert math.isclose(fused["scores"]["y"], 1 / 62 + 1 / 61)
    assert fused["ranking"] == ["y", "x", "z"]

    hybrid = ml_models_docs.hybrid_example()
    assert hybrid["lexical"] == ["d1", "d2"]
    assert hybrid["ranking"] == ["d1", "d2", "d3", "d4"]
    assert math.isclose(hybrid["scores"]["d1"], 1 / 61 + 1 / 62)


def test_roofline_separates_matmul_from_elementwise_ops():
    matmul, matvec, relu = ml_models_docs.gpu_op_examples(4096)
    assert matmul["flops"] == 2 * 4096**3
    assert matmul["bytes"] == 3 * 4096**2 * 4
    assert matmul["bound"] == "compute"
    assert matmul["attainable_flops"] == ml_models_docs.EXAMPLE_GPU["peak_flops"]
    assert matvec["bound"] == "memory"
    assert matvec["intensity"] == pytest.approx(0.5, abs=1e-3)
    assert relu["intensity"] == 0.125
    assert relu["bound"] == "memory"
    assert relu["seconds"] == pytest.approx(4096**2 * 8 / 2e12)
    assert matmul["ridge"] == 50
    assert ml_models_docs.roofline_xy(1 / 16, 0.1e12) == (60, 260)
    assert ml_models_docs.roofline_xy(1024, 100e12) == (620, 50)


def test_fusion_and_tiling_cut_memory_traffic():
    fusion = ml_models_docs.fusion_example(numel=1000, ops=3)
    assert fusion["unfused"]["bytes"] == 3 * fusion["fused"]["bytes"]
    assert fusion["speedup"] == pytest.approx(3)
    traffic = [ml_models_docs.tiled_matmul_traffic(4096, tile) for tile in (1, 16, 128)]
    assert traffic[0]["bytes"] == 2 * 4096**3 * 4
    assert traffic[0]["bytes"] == 16 * traffic[1]["bytes"]
    assert [row["intensity"] for row in traffic] == [0.25, 4.0, 32.0]


def test_async_timeline_runs_ahead_of_the_gpu():
    short = ml_models_docs.async_timeline([2] * 10, launch_us=5)
    assert short["cpu_done"] == 50
    assert short["total"] == 52
    assert short["utilization"] == pytest.approx(20 / 52)
    long = ml_models_docs.async_timeline([50] * 10, launch_us=5)
    assert long["cpu_done"] == 50
    assert long["total"] == 505
    assert long["rows"][1] == {"issued": 10, "start": 55, "end": 105}


def test_float_formats_match_their_bit_layouts():
    stats = {
        fmt["name"]: ml_models_docs.float_format_stats(fmt)
        for fmt in ml_models_docs.FLOAT_FORMATS
    }
    assert stats["fp32"]["max"] == pytest.approx(3.4028234663852886e38)
    assert stats["fp16"]["max"] == 65504
    assert stats["fp16"]["smallest_normal"] == 2.0**-14
    assert stats["fp16"]["smallest_subnormal"] == 2.0**-24
    assert stats["bf16"]["smallest_normal"] == stats["fp32"]["smallest_normal"]
    assert stats["bf16"]["epsilon"] == 2.0**-7
    assert stats["tf32"]["epsilon"] == stats["fp16"]["epsilon"]
    assert stats["fp8 e4m3"]["max"] == 448
    assert stats["fp8 e4m3"]["smallest_subnormal"] == 2.0**-9
    assert stats["fp8 e5m2"]["max"] == 57344
    for fmt in ml_models_docs.FLOAT_FORMATS:
        if fmt["name"] != "tf32":
            assert 1 + fmt["exponent"] + fmt["mantissa"] == fmt["bits"]


def test_rounding_agrees_with_struct_and_the_bf16_bit_trick():
    fp16 = ml_models_docs.find_float_format("fp16")
    bf16 = ml_models_docs.find_float_format("bf16")
    fp32 = ml_models_docs.find_float_format("fp32")
    for value in [1 / 3, 0.1, -2.5, 1e-7, 5e-9, 65504, 65519.9, 65520, 70000.0, 3e-5]:
        assert ml_models_docs.round_to_format(value, fp16) == ml_models_docs.fp16_struct_round(value)
        assert ml_models_docs.round_to_format(value, bf16) == ml_models_docs.bf16_round_bits(value)
        assert ml_models_docs.round_to_format(value, fp32) == ml_models_docs.struct.unpack(
            "<f", ml_models_docs.struct.pack("<f", value)
        )[0]
    e4m3 = ml_models_docs.find_float_format("fp8 e4m3")
    e5m2 = ml_models_docs.find_float_format("fp8 e5m2")
    assert ml_models_docs.round_to_format(500.0, e4m3) == 448
    assert ml_models_docs.round_to_format(61440.0, e5m2) == math.inf
    assert ml_models_docs.float_bits(448, e4m3) == {
        "value": 448,
        "sign": "0",
        "exponent": "1111",
        "mantissa": "110",
    }
    assert ml_models_docs.float_bits(1 / 3, fp16)["mantissa"] == "0101010101"
    assert ml_models_docs.float_bits(1e-7, fp16)["exponent"] == "00000"


def test_loss_scaling_rescues_small_fp16_gradients():
    fp16 = ml_models_docs.loss_scaling_example()
    assert [row["plain"] for row in fp16["rows"][3:]] == [0.0, 0.0]
    assert all(row["scaled_error"] < 1e-3 for row in fp16["rows"])
    bf16 = ml_models_docs.loss_scaling_example(fmt_name="bf16")
    assert all(row["plain"] > 0 for row in bf16["rows"])
    assert all(row["plain_error"] < 2e-3 for row in bf16["rows"])


def test_grad_scaler_backs_off_and_grows():
    run = ml_models_docs.grad_scaler_run([0.6] * 12, growth_interval=3)
    assert [row["overflow"] for row in run["rows"]] == [False, False, False, True] * 3
    assert run["rows"][3]["scale"] == 2.0**17
    assert run["rows"][4]["scale"] == 2.0**16
    assert run["skipped"] == 3
    steady = ml_models_docs.grad_scaler_run([0.6] * 100)
    assert steady["skipped"] == 0
    assert steady["final_scale"] == 2.0**16


def test_master_weights_keep_small_updates():
    example = ml_models_docs.master_weight_example()
    assert example["fp16"] == 1.0
    assert example["bf16"] == 1.0
    assert example["fp32"] == pytest.approx(1.01, abs=1e-5)
    assert example["fp32_cast_fp16"] == 1.009765625


def test_affine_qparams_match_the_pytorch_docstring_examples():
    dynamic = ml_models_docs.quantize_roundtrip(ml_models_docs.AFFINE_EXAMPLE)
    assert dynamic["scale"] == pytest.approx(0.011764705882352941)
    assert dynamic["zero_point"] == 85
    assert dynamic["codes"] == [0, 85, 170, 255]
    assert ml_models_docs.quantize_values([-1.0, 0.0, 1.0, 2.0], 0.1, 10, 0, 255) == [0, 10, 20, 30]
    assert ml_models_docs.affine_qparams(0.5, 2.0, 0, 255)[1] == 0
    symmetric = ml_models_docs.quantize_roundtrip(
        ml_models_docs.ACTIVATION_EXAMPLE, "symmetric", "qint8"
    )
    assert symmetric["zero_point"] == 0
    assert symmetric["scale"] == pytest.approx(2.48 / 127.5)
    assert ml_models_docs.symmetric_qparams(-1.0, 2.0, 0, 255)[1] == 128
    affine = ml_models_docs.quantize_roundtrip(ml_models_docs.ACTIVATION_EXAMPLE)
    assert affine["restored"][1] == 0.0
    assert affine["max_error"] <= affine["scale"] / 2
    assert symmetric["max_error"] > affine["max_error"]


def test_fake_quantize_matches_the_docstring_and_masks_clamped_gradients():
    example = ml_models_docs.FAKE_QUANT_EXAMPLE
    result = ml_models_docs.fake_quantize(
        example["values"],
        example["scale"],
        example["zero_point"],
        example["quant_min"],
        example["quant_max"],
    )
    assert result["output"] == pytest.approx([0.1, 1.0, 0.4, 0.0])
    assert result["mask"] == [True, True, True, False]
    assert result["unclamped"][3] == -11
    assert ml_models_docs.straight_through_grad([0.5, -1.0, 2.0, 3.0], result["mask"]) == [
        0.5,
        -1.0,
        2.0,
        0.0,
    ]
    assert ml_models_docs.quantize_values([0.25, 0.75], 0.5, 0, 0, 255) == [0, 2]


def test_per_channel_scales_rescue_small_rows():
    example = ml_models_docs.per_channel_example()
    assert example["tensor_scale"] == pytest.approx(2.40 / 127.5)
    assert example["tensor_codes"][0] == [6, -4, 3, -6]
    assert example["channel_codes"][0][0] == 127
    assert example["tensor_error"][0] > 0.05
    assert all(error < 0.01 for error in example["channel_error"])
    assert example["channel_error"][2] == example["tensor_error"][2]


def test_groups_shrink_int4_error_and_cost_a_fraction_of_a_bit():
    row = ml_models_docs.GROUP_ROW
    whole = ml_models_docs.group_quantize(row)
    grouped = ml_models_docs.group_quantize(row, group_size=4)
    int8 = ml_models_docs.group_quantize(row, bits=8)
    assert whole["restored"][2] == 0.0
    assert grouped["error"] < whole["error"] / 1.5
    assert int8["error"] < grouped["error"]
    memory = ml_models_docs.weight_memory_example()
    bits = [row["bits_per_weight"] for row in memory["rows"]]
    assert bits == [16, 8, 4.125, 4.5]
    assert memory["rows"][0]["bytes"] == 16e9


def test_one_outlier_wrecks_absmax_int8_until_it_is_split_out():
    example = ml_models_docs.outlier_example()
    assert example["exact"] == pytest.approx(0.79)
    assert example["naive_x"][4] == 0.0
    assert abs(example["naive"] - example["exact"]) / example["exact"] > 0.4
    assert example["outliers"] == 1
    assert abs(example["mixed"] - example["exact"]) / example["exact"] < 0.01


def test_discounted_returns_and_value_iteration_reach_the_bellman_fixed_point():
    assert ml_models_docs.discounted_returns([0, 0, 1]) == pytest.approx([0.81, 0.9, 1.0])
    assert ml_models_docs.discounted_returns([1, 1, 1, 1]) == pytest.approx([3.439, 2.71, 1.9, 1.0])
    result = ml_models_docs.value_iteration()
    assert result["history"][1] == pytest.approx([0.0, 0.0, 0.8, 0.0])
    assert result["history"][2] == pytest.approx([0.0, 0.576, 0.944, 0.0])
    assert result["values"] == pytest.approx(ml_models_docs.chain_values_closed_form())
    assert result["values"][2] == pytest.approx(0.8 / (1 - 0.9 * 0.2))
    values = result["values"]
    for row, value in zip(ml_models_docs.chain_q_values(values), values):
        assert max(row.values()) == pytest.approx(value)
        assert row["right"] > row["left"]


def test_q_learning_finds_the_optimal_policy_on_the_slippery_chain():
    update = ml_models_docs.q_update(0.5, 0.0, 0.8, alpha=0.1)
    assert update["target"] == pytest.approx(0.72)
    assert update["new"] == pytest.approx(0.522)
    for seed in range(3):
        result = ml_models_docs.q_learning(seed=seed)
        assert result["greedy"] == ["right", "right", "right"]
        assert result["max_error"] < 0.03


def test_advantages_average_to_zero_under_the_true_values():
    result = ml_models_docs.chain_advantages()
    assert [row["next"] for row in result["rows"]] == [2, 1]
    assert result["rows"][0]["td_error"] > 0 > result["rows"][1]["td_error"]
    assert result["mean"] == pytest.approx(0.0, abs=1e-12)


def test_reinforce_is_unbiased_and_a_baseline_cuts_its_variance():
    plain = ml_models_docs.reinforce_gradient([0.0, 0.0, 0.0])
    assert plain["exact"] == pytest.approx([-4 / 9, -1 / 9, 5 / 9])
    assert plain["mean"] == pytest.approx(plain["exact"])
    based = ml_models_docs.reinforce_gradient([0.0, 0.0, 0.0], baseline=plain["expected"])
    assert based["mean"] == pytest.approx(plain["exact"])
    assert based["variance"] == pytest.approx(14 / 27)
    assert plain["variance"] == pytest.approx(112 / 27)
    rows = ml_models_docs.bandit_training()
    expected = [row["expected"] for row in rows]
    assert expected == sorted(expected)
    assert rows[-1]["probs"][2] > 0.9


def test_ppo_clip_only_removes_the_gradient_in_the_greedy_direction():
    clip = ml_models_docs.ppo_clip
    assert clip(1.5, 1.0)["objective"] == pytest.approx(1.2)
    assert clip(1.5, 1.0)["gradient"] == 0.0
    assert clip(0.5, 1.0)["objective"] == pytest.approx(0.5)
    assert clip(0.5, 1.0)["gradient"] == 1.0
    assert clip(0.5, -1.0)["objective"] == pytest.approx(-0.8)
    assert clip(0.5, -1.0)["gradient"] == 0.0
    assert clip(1.5, -1.0)["objective"] == pytest.approx(-1.5)
    assert clip(1.5, -1.0)["gradient"] == -1.0
    assert clip(1.1, 1.0)["gradient"] == 1.0


def test_diagnostic_test_posterior_matches_the_natural_frequencies():
    result = ml_models_docs.diagnostic_test()
    assert (result["sick"], result["true_positives"], result["false_positives"]) == pytest.approx((100, 90, 891))
    assert result["posterior"] == pytest.approx(90 / 981)
    assert result["true_positives"] / (result["true_positives"] + result["false_positives"]) == pytest.approx(
        result["posterior"]
    )
    beliefs = ml_models_docs.repeated_tests()
    assert beliefs[1] == pytest.approx(result["posterior"])
    assert beliefs[2] == pytest.approx(100 / 199)
    assert beliefs == sorted(beliefs)


def test_likelihood_is_not_a_density_in_the_parameter():
    total = sum(ml_models_docs.binomial_likelihood(0.7, heads, 10) for heads in range(11))
    assert total == pytest.approx(1.0)
    assert ml_models_docs.likelihood_area() == pytest.approx(1 / 11, rel=1e-6)
    curves = ml_models_docs.coin_curves()
    peak = curves["likelihood"].index(1.0)
    assert curves["theta"][peak] == pytest.approx(0.7)


def test_map_shrinks_toward_the_prior_and_fades_with_more_data():
    small = ml_models_docs.coin_estimates()
    assert small["mle"] == pytest.approx(0.7)
    assert small["map"] == pytest.approx(11 / 18)
    assert small["posterior"] == (12, 8)
    large = ml_models_docs.coin_estimates(70, 100)
    assert small["map"] < large["map"] < large["mle"]
    laplace = ml_models_docs.coin_estimates(0, 3, (2, 2))
    assert laplace["mle"] == 0.0
    assert laplace["map"] == pytest.approx(1 / 5)
    xs, ys = [1, 2, 3], [1, 3, 2]
    assert ml_models_docs.ridge_map_1d(xs, ys, 0) == pytest.approx(13 / 14)
    assert ml_models_docs.ridge_map_1d(xs, ys, 1) == pytest.approx(13 / 15)


def test_naive_bayes_matches_the_multinomial_formula_and_smoothing_avoids_zeros():
    rows = ml_models_docs.naive_bayes_posterior()
    assert rows["spam"]["word_probs"] == pytest.approx([0.4, 0.3, 0.1, 0.2])
    assert rows["ham"]["word_probs"] == pytest.approx([2 / 12, 1 / 12, 4 / 12, 5 / 12])
    spam = 0.4 * 0.4 * 0.3 * 0.1
    ham = 0.6 * (2 / 12) * (1 / 12) * (4 / 12)
    assert rows["spam"]["posterior"] == pytest.approx(spam / (spam + ham))
    assert rows["spam"]["posterior"] + rows["ham"]["posterior"] == pytest.approx(1.0)
    raw = ml_models_docs.naive_bayes_posterior([1, 1, 0, 0], alpha=0.0)
    assert raw["ham"]["joint_log"] == -math.inf
    assert raw["spam"]["posterior"] == 1.0
    assert ml_models_docs.naive_bayes_posterior(alpha=0.0)["spam"]["posterior"] is None


def test_balanced_class_weights_match_the_sklearn_formula_and_equalize_class_totals():
    assert ml_models_docs.balanced_class_weights([2, 4]) == pytest.approx([1.5, 0.75])
    paradox = ml_models_docs.accuracy_paradox()
    assert paradox["accuracy"] == pytest.approx(0.99)
    assert paradox["recall"] == 0.0
    assert paradox["balanced_accuracy"] == pytest.approx(0.5)
    assert paradox["weights"] == pytest.approx([1000 / 1980, 50.0])
    assert paradox["weighted_totals"] == pytest.approx([500.0, 500.0])
    assert paradox["pos_weight"] == pytest.approx(99.0)
    assert paradox["sampler_positive_share"] == pytest.approx(0.5)
    assert ml_models_docs.balanced_accuracy(1, 1, 1, 3) == pytest.approx(0.625)


def test_class_weights_oversampling_and_threshold_moving_agree_on_the_toy_data():
    example = ml_models_docs.imbalance_example()
    assert len(example["xs"]) == 200 and sum(example["ys"]) == 20
    plain, weighted = example["plain"], example["weighted"]
    assert example["oversampled"]["w"] == pytest.approx(weighted["w"])
    assert example["oversampled"]["b"] == pytest.approx(weighted["b"])
    assert weighted["recall"] > plain["recall"]
    assert weighted["precision"] < plain["precision"]
    assert plain["accuracy"] > weighted["accuracy"]
    assert plain["balanced_accuracy"] < weighted["balanced_accuracy"]
    assert example["intercept_shift"] == pytest.approx(example["log_weight_ratio"], abs=0.02)
    assert example["moved"]["cut"] == pytest.approx(weighted["cut"], abs=0.02)
    assert example["kept_negatives"] == 20
    assert example["probe_corrected"] == pytest.approx(example["probe_plain"], abs=0.01)
    for name in ("plain", "weighted", "undersampled", "moved"):
        report = example[name]
        assert sum(report["counts"]) == 200
        assert ml_models_docs.sigmoid(report["w"] * report["cut"] + report["b"]) == pytest.approx(report["threshold"])


def test_undersampling_correction_inverts_the_odds_change():
    p, beta = 0.1, 0.25
    odds = p / (1 - p)
    p_sampled = (odds / beta) / (1 + odds / beta)
    assert ml_models_docs.undersample_correction(p_sampled, beta) == pytest.approx(p)
    assert ml_models_docs.undersample_correction(0.3, 1.0) == pytest.approx(0.3)


def test_focal_loss_reduces_to_cross_entropy_and_downweights_easy_examples():
    assert ml_models_docs.focal_loss(0.3, gamma=0.0) == pytest.approx(-math.log(0.3))
    assert ml_models_docs.focal_loss(0.9, gamma=2.0) == pytest.approx(0.01 * -math.log(0.9))
    assert ml_models_docs.focal_loss(0.9, gamma=2.0, alpha_t=0.25) == pytest.approx(0.0025 * -math.log(0.9))
    rows = ml_models_docs.focal_table()
    for row in rows:
        assert row["ratios"][0] == pytest.approx(1.0)
        assert row["losses"] == sorted(row["losses"], reverse=True)
    easy, hard = rows[-1], rows[0]
    assert easy["ratios"][3] < hard["ratios"][3]


def test_forest_tree_splits_with_gini_and_respects_max_features():
    rows = [((0.0, 5.0), 0), ((1.0, 5.0), 0), ((2.0, 5.0), 1), ((3.0, 5.0), 1)]
    tree = ml_models_docs.grow_forest_tree(rows, ml_models_docs.random.Random(0), max_features=1)
    assert tree["feature"] == 0 and tree["threshold"] == pytest.approx(1.5)
    assert [ml_models_docs.forest_tree_predict(tree, x) for x, _ in rows] == [0, 0, 1, 1]
    assert ml_models_docs.forest_tree_importances(tree, 2) == [1.0, 0.0]
    extra = ml_models_docs.grow_forest_tree(rows, ml_models_docs.random.Random(3), 2, random_thresholds=True)
    assert all(ml_models_docs.forest_tree_predict(extra, x) == y for x, y in rows)


def test_bootstrap_leaves_about_a_third_out_of_bag():
    assert ml_models_docs.bootstrap_oob_fraction(100) == pytest.approx(0.366, abs=1e-3)
    assert ml_models_docs.bootstrap_oob_fraction(10**6) == pytest.approx(math.exp(-1), abs=1e-6)
    rows = ml_models_docs.forest_rows(50, 1)
    trees = ml_models_docs.fit_forest(rows, 40, 2, seed=4)
    fraction = sum(1 - len(t["in_bag"]) / 50 for t in trees) / 40
    assert fraction == pytest.approx(0.364, abs=0.03)
    whole = ml_models_docs.fit_forest(rows, 3, 2, bootstrap=False, seed=4)
    assert all(len(t["in_bag"]) == 50 for t in whole)


def test_averaging_trees_beats_one_tree_and_oob_tracks_test_accuracy():
    example = ml_models_docs.forest_example()
    assert example["single"]["train_accuracy"] == 1.0
    for name in ml_models_docs.FOREST_METHODS:
        report = example[name]
        assert len(report["curve"]) == example["n_trees"]
        assert report["test_accuracy"] > example["single"]["test_accuracy"]
        assert report["test_accuracy"] > report["tree_accuracy"]
        if report["oob_accuracy"] is not None:
            assert report["oob_accuracy"] == pytest.approx(report["test_accuracy"], abs=0.05)
            assert report["mean_oob_fraction"] == pytest.approx(0.366, abs=0.02)
    forest = example["forest"]
    assert sum(forest["impurity"]) == pytest.approx(1.0)
    noise = forest["permutation"]["features"][2:]
    signal = forest["permutation"]["features"][:2]
    assert min(f["mean"] for f in signal) > 10 * max(f["mean"] for f in noise)
    assert forest["impurity"][2] > forest["impurity"][3]


def test_feature_subsampling_lowers_tree_correlation():
    methods = ml_models_docs.FOREST_METHODS
    bagged = ml_models_docs.tree_correlation(**methods["bagging"])
    forest = ml_models_docs.tree_correlation(**methods["forest"])
    assert 0 < forest["rho"] < bagged["rho"] < 1
    for c in (bagged, forest):
        assert ml_models_docs.averaged_variance(c["rho"], c["sigma2"], 1) == pytest.approx(c["sigma2"])
        assert ml_models_docs.averaged_variance(c["rho"], c["sigma2"], 10**9) == pytest.approx(c["rho"] * c["sigma2"])
    assert ml_models_docs.averaged_variance(forest["rho"], forest["sigma2"], 100) < ml_models_docs.averaged_variance(
        bagged["rho"], bagged["sigma2"], 100
    )


def test_init_gains_and_fans_match_pytorch():
    assert ml_models_docs.init_gain("relu") == math.sqrt(2.0)
    assert ml_models_docs.init_gain("tanh") == 5.0 / 3
    assert ml_models_docs.init_gain("leaky_relu") == math.sqrt(2.0 / (1 + 0.01 ** 2))
    assert ml_models_docs.fan_in_and_fan_out((30, 20)) == (20, 30)
    assert ml_models_docs.fan_in_and_fan_out((16, 3, 5, 5)) == (75, 400)
    assert math.isclose(ml_models_docs.uniform_bound(ml_models_docs.xavier_std(20, 30)), math.sqrt(6 / 50))


def test_linear_default_init_is_uniform_one_over_sqrt_fan_in():
    for fan_in in (1, 20, 64, 4096):
        assert math.isclose(ml_models_docs.linear_default_bound(fan_in), 1 / math.sqrt(fan_in))
    var = ml_models_docs.linear_default_bound(64) ** 2 / 3
    assert math.isclose(ml_models_docs.relu_moment_factor(64, var), 1 / 6)
    assert math.isclose(ml_models_docs.relu_moment_factor(64, ml_models_docs.kaiming_std(64, "relu") ** 2), 1.0)


def test_kaiming_keeps_a_deep_relu_net_in_range_while_others_vanish_or_explode():
    results = {s["key"]: s["result"] for s in ml_models_docs.init_example()["schemes"]}
    last = {k: r["forward"][-1] for k, r in results.items()}
    assert 0.2 < last["kaiming"] < 5
    assert last["small"] < 1e-20 < 1e8 < last["large"]
    assert last["pytorch"] < last["xavier"] < 1e-2
    assert 0.2 < results["kaiming"]["backward"][0] < 5
    assert results["small"]["backward"][0] < 1e-20
    assert 0.2 < last["tanh-gain"] < 2 and last["tanh-xavier"] < last["tanh-gain"]


def test_rnn_param_count_matches_rnnbase_layout():
    assert ml_models_docs.rnn_param_count("LSTM", 10, 20, 2) == 5920
    assert ml_models_docs.rnn_param_count("GRU", 10, 20, 2) == 4440
    assert ml_models_docs.rnn_param_count("RNN_TANH", 10, 20, 2) == 1480
    assert ml_models_docs.rnn_param_count("LSTM", 10, 20, 1, bias=False) == 80 * 30
    assert ml_models_docs.rnn_param_count("LSTM", 10, 20, 2, bidirectional=True) == 2 * 2560 + 2 * (80 * 40 + 80 * 20 + 160)
    assert ml_models_docs.rnn_param_count("LSTM", 10, 20, 1, proj_size=5) == 80 * 10 + 80 * 5 + 160 + 5 * 20


def test_pack_sequences_matches_pytorch_docstring_examples():
    packed = ml_models_docs.pack_sequences([[1, 2, 3], [4, 5], [6]])
    assert packed["data"] == [1, 4, 6, 2, 5, 3]
    assert packed["batch_sizes"] == [3, 2, 1]
    unsorted = ml_models_docs.pack_sequences([[1, 2], [3], [4, 5, 6]], enforce_sorted=False)
    assert unsorted["data"] == [4, 1, 3, 5, 2, 6]
    assert unsorted["batch_sizes"] == [3, 2, 1]
    assert unsorted["sorted_indices"] == [2, 0, 1]
    assert unsorted["unsorted_indices"] == [1, 2, 0]
    assert ml_models_docs.pack_sequences([list("abc"), ["x"]])["data"] == list("axbc")
    with pytest.raises(ValueError):
        ml_models_docs.pack_sequences([[1], [2, 3]])


def test_rnn_lstm_and_gru_steps_follow_the_pytorch_equations():
    e = ml_models_docs.rnn_example()
    first = e["rnn"][0]
    assert first["h"] == pytest.approx([math.tanh(0.5), math.tanh(-0.2)])
    s = e["lstm"][0]
    assert s["f"] == pytest.approx(ml_models_docs.sigmoid(1.3))
    assert s["c"] == pytest.approx(s["i"] * s["g"])
    assert s["h"] == pytest.approx(s["o"] * math.tanh(s["c"]))
    later = e["lstm"][1]
    assert later["c"] == pytest.approx(later["f"] * s["c"] + later["i"] * later["g"])
    g = e["gru"][1]
    h_prev = e["gru"][0]["h"]
    assert g["n"] == pytest.approx(math.tanh(0.5 + g["r"] * 0.6 * h_prev))
    assert g["h"] == pytest.approx((1 - g["z"]) * g["n"] + g["z"] * h_prev)
    att = e["attention"]
    assert sum(att["weights"]) == pytest.approx(1.0)
    assert att["weights"][-1] == max(att["weights"])


def test_memory_gradients_vanish_for_rnns_and_survive_with_a_large_forget_bias():
    memory = {c["key"]: c["trace"] for c in ml_models_docs.memory_gradient_example()}
    assert abs(memory["rnn-small"][-1]["grad"]) < 1e-8
    assert abs(memory["rnn-large"][-1]["grad"]) < 1e-20
    assert abs(memory["lstm-0"][-1]["grad"]) < 1e-11
    assert memory["lstm-3"][-1]["grad"] > 1e-3
    assert memory["lstm-3"][-1]["direct"] > 0.2

    h = 1e-6
    base = ml_models_docs.lstm_memory_gradient(3.0, 10)
    weights = {k: dict(v) for k, v in ml_models_docs.LSTM_EXAMPLE.items()}
    weights["f"]["b"] = 3.0
    first = ml_models_docs.lstm_step(1.0, 0.0, 0.0, weights)
    c = first["c"] + h
    hh = first["h"]
    for _ in range(9):
        s = ml_models_docs.lstm_step(0.0, hh, c, weights)
        hh, c = s["h"], s["c"]
    finite = (c - base[-1]["c"]) / h
    assert finite == pytest.approx(base[-1]["grad"], rel=1e-4)


def test_linear_autoencoder_learns_the_pca_subspace():
    e = ml_models_docs.autoencoder_example()
    history = e["trained"]["history"]
    assert history[-1] == pytest.approx(e["pca_mse"], rel=1e-4)
    assert history[0] > history[10] > history[-1]
    assert e["cosine"] == pytest.approx(1.0, abs=1e-6)
    top = e["top"]
    for i in range(2):
        for j in range(2):
            assert e["product"][i][j] == pytest.approx(top[i] * top[j], abs=1e-3)
    assert e["pca_mse"] < e["total_mse"]


def test_denoising_map_shrinks_each_principal_direction():
    e = ml_models_docs.autoencoder_example()
    clean, mild, heavy = e["denoise"]
    assert clean["map"][0][0] == pytest.approx(1.0) and clean["map"][0][1] == pytest.approx(0.0, abs=1e-12)
    lam = e["eigenvalues"]
    assert mild["shrink"] == pytest.approx([lam[0] / (lam[0] + 0.25), lam[1] / (lam[1] + 0.25)])
    top = e["top"]
    mapped = [sum(heavy["map"][i][j] * top[j] for j in range(2)) for i in range(2)]
    assert mapped == pytest.approx([heavy["shrink"][1] * t for t in top])


def test_conv_autoencoder_shapes_round_trip_28_by_28():
    assert ml_models_docs.conv_transpose_output_size(7, 3, stride=2, padding=1, output_padding=1) == 14
    assert ml_models_docs.conv_transpose_output_size(7, 3, stride=2, padding=1) == 13
    assert ml_models_docs.conv_transpose_output_size(14, 4, stride=2, padding=1) == 28
    rows = ml_models_docs.conv_autoencoder_shapes()
    assert rows[0]["shape"] == rows[-1]["shape"] == (1, 28, 28)
    assert [r["shape"] for r in rows if r.get("code")] == [(16,)]
    assert sum(r["params"] for r in rows) == 160 + 4640 + 25104 + 26656 + 4624 + 145


def _integrate(fn, low=-12.0, high=12.0, steps=24000):
    width = (high - low) / steps
    return sum(fn(low + (i + 0.5) * width) for i in range(steps)) * width


def test_normal_kl_matches_pytorch_closed_form_and_numeric_integral():
    for p_loc, p_scale, q_loc, q_scale in [(1.0, 0.5, 0.0, 1.0), (-0.3, 2.0, 0.7, 1.5), (2.0, 1.0, 2.0, 1.0)]:
        numeric = _integrate(lambda z: math.exp(ml_models_docs.normal_log_prob(z, p_loc, p_scale)) * (
            ml_models_docs.normal_log_prob(z, p_loc, p_scale) - ml_models_docs.normal_log_prob(z, q_loc, q_scale)))
        assert ml_models_docs.normal_kl(p_loc, p_scale, q_loc, q_scale) == pytest.approx(numeric, abs=1e-6)
    assert ml_models_docs.normal_kl(2.0, 1.0, 2.0, 1.0) == 0.0
    for mu, logvar in [(0.0, 0.0), (1.2, -2.0), (-0.4, 0.7)]:
        assert ml_models_docs.standard_normal_kl(mu, logvar) == pytest.approx(
            ml_models_docs.normal_kl(mu, math.exp(0.5 * logvar), 0.0, 1.0))


def test_elbo_gap_is_the_kl_to_the_exact_posterior():
    e = ml_models_docs.VAE_EXAMPLE
    w, s, x = e["weight"], e["noise"], e["x"]
    evidence = _integrate(lambda z: math.exp(ml_models_docs.normal_log_prob(x, w * z, s) + ml_models_docs.normal_log_prob(z, 0.0, 1.0)))
    assert ml_models_docs.linear_gaussian_evidence(x, w, s) == pytest.approx(math.log(evidence), abs=1e-9)
    ex = ml_models_docs.vae_example()
    for row in ex["rows"]:
        assert row["elbo"] <= ex["evidence"] + 1e-12
        assert row["gap"] == pytest.approx(row["posterior_kl"], abs=1e-12)
        loc, scale = row["loc"], row["scale"]
        expected = _integrate(lambda z: math.exp(ml_models_docs.normal_log_prob(z, loc, scale)) * ml_models_docs.normal_log_prob(x, w * z, s))
        assert row["reconstruction"] == pytest.approx(expected, abs=1e-6)
    assert ex["rows"][-1]["gap"] == pytest.approx(0.0, abs=1e-12)
    assert ex["posterior"] == pytest.approx((1.2, math.sqrt(0.2)))


def test_reparameterized_gradient_is_unbiased_with_lower_variance():
    ex = ml_models_docs.vae_example()
    g = ex["gradients"]
    n = ml_models_docs.VAE_EXAMPLE["samples"]
    assert g["exact"] == pytest.approx(-1.0)
    for name in ["reparam", "score"]:
        assert abs(g[name]["mean"] - g["exact"]) < 3 * g[name]["std"] / math.sqrt(n)
    assert g["reparam"]["std"] == pytest.approx(2 * ml_models_docs.VAE_EXAMPLE["sigma"], rel=0.05)
    assert g["reparam"]["std"] < g["score"]["std"] / 2


def test_vae_code_kl_flags_collapsed_units():
    ex = ml_models_docs.vae_example()
    kls = [c["kl"] for c in ex["code"]]
    assert kls[2] == 0.0
    assert kls[3] < 1e-3
    assert kls[0] > 1.0
    assert ex["code_kl"] == pytest.approx(sum(kls))
    assert [b["penalty"] for b in ex["betas"]] == pytest.approx([b * ex["code_kl"] for b in ml_models_docs.VAE_EXAMPLE["betas"]])


def test_normal_curve_samples_the_density():
    curve = ml_models_docs.normal_curve(0.0, 1.0, -3.0, 3.0, steps=6)
    assert [z for z, _ in curve] == pytest.approx([-3, -2, -1, 0, 1, 2, 3])
    assert curve[3][1] == pytest.approx(1 / math.sqrt(2 * math.pi))
    assert curve[0][1] == pytest.approx(curve[-1][1])


def test_sinusoidal_encoding_follows_the_paper_formula():
    d, base = 8, 10000.0
    assert ml_models_docs.sinusoidal_frequencies(d, base) == pytest.approx([1.0, 0.1, 0.01, 0.001])
    for pos in [0, 1, 7, 33]:
        pe = ml_models_docs.sinusoidal_encoding(pos, d, base)
        for i in range(d // 2):
            assert pe[2 * i] == pytest.approx(math.sin(pos / base ** (2 * i / d)))
            assert pe[2 * i + 1] == pytest.approx(math.cos(pos / base ** (2 * i / d)))
    wavelengths = [2 * math.pi / w for w in ml_models_docs.sinusoidal_frequencies(512, base)]
    assert wavelengths[0] == pytest.approx(2 * math.pi)
    assert 0.9 * 10000 * 2 * math.pi < wavelengths[-1] < 10000 * 2 * math.pi


def test_shifting_a_sinusoidal_encoding_is_a_fixed_rotation():
    d = 16
    for pos in [0, 3, 50]:
        for offset in [1, 4, -2]:
            shifted = ml_models_docs.shift_encoding(ml_models_docs.sinusoidal_encoding(pos, d), offset, d)
            assert shifted == pytest.approx(ml_models_docs.sinusoidal_encoding(pos + offset, d), abs=1e-12)
    e = ml_models_docs.position_example()
    assert e["shifted"] == pytest.approx(e["direct"], abs=1e-12)


def test_sinusoidal_similarity_depends_only_on_the_offset():
    d = 8
    freqs = ml_models_docs.sinusoidal_frequencies(d)
    for k in [0, 1, 5, 12]:
        expected = sum(math.cos(w * k) for w in freqs)
        for p in [0, 9, 100]:
            assert ml_models_docs.sinusoidal_similarity(p, p + k, d) == pytest.approx(expected)
    assert ml_models_docs.sinusoidal_similarity(0, 0, d) == pytest.approx(d / 2)


def test_rope_rotates_without_changing_length_and_scores_depend_on_offset():
    q, k = [1.0, 0.5, -0.5, 1.0], [0.5, 1.0, 1.0, 0.5]
    assert ml_models_docs.rope(q, 0, 100.0) == pytest.approx(q)
    for pos in [1, 6, 41]:
        rotated = ml_models_docs.rope(q, pos, 100.0)
        assert sum(x * x for x in rotated) == pytest.approx(sum(x * x for x in q))
    for m, n in [(0, 3), (7, 10), (100, 103), (5, 2)]:
        assert ml_models_docs.rope_score(q, k, m, n, 100.0) == pytest.approx(
            sum(a * b for a, b in zip(q, ml_models_docs.rope(k, n - m, 100.0))))
    e = ml_models_docs.position_example()
    scores = [r["score"] for r in e["rope_rows"]]
    assert scores == pytest.approx([scores[0]] * len(scores), abs=1e-12)
    absolute = [r["absolute"] for r in e["rope_rows"]]
    assert max(absolute) - min(absolute) > 1.0
    assert e["rope_offsets"][0]["score"] == pytest.approx(e["plain_score"])


def test_alibi_slopes_and_biases_follow_the_paper():
    assert ml_models_docs.alibi_slopes(8) == pytest.approx([2.0 ** -(i + 1) for i in range(8)])
    sixteen = ml_models_docs.alibi_slopes(16)
    assert sixteen[0] == pytest.approx(2 ** -0.5)
    assert sixteen[-1] == pytest.approx(2.0 ** -8)
    bias = ml_models_docs.alibi_bias(4, 0.5)
    assert bias[3] == [-1.5, -1.0, -0.5, 0.0]
    assert bias[0][1:] == [None, None, None]
    flat = ml_models_docs.alibi_weights([0.0] * 5, 0.5)
    assert flat == sorted(flat)
    assert sum(flat) == pytest.approx(1.0)
    e = ml_models_docs.position_example()
    plain, steep, mid, gentle = e["alibi_rows"]
    assert plain["weights"] == pytest.approx(ml_models_docs.softmax_probs(ml_models_docs.POSITION_EXAMPLE["alibi_scores"]))
    assert gentle["weights"] == pytest.approx(plain["weights"], abs=0.01)
    assert steep["weights"][-1] > 2 * plain["weights"][-1]
    assert ml_models_docs.learned_position_params(1024, 768) == 786432


def test_lloyd_never_increases_inertia_and_stops_at_a_fixed_point():
    e = ml_models_docs.cluster_example()
    for history in (e["bad"], e["good"]):
        inertias = [h["inertia"] for h in history]
        assert all(b <= a + 1e-12 for a, b in zip(inertias, inertias[1:]))
        last = history[-1]
        assert ml_models_docs.assign_labels(e["points"], last["centers"]) == last["labels"]
        for c, center in enumerate(last["centers"]):
            members = [p for p, l in zip(e["points"], last["labels"]) if l == c]
            assert center == pytest.approx(tuple(sum(v) / len(members) for v in zip(*members)))
    assert e["bad"][-1]["inertia"] > 5 * e["good"][-1]["inertia"]
    assert e["ari_bad"] < 0.5
    assert e["ari_kmeans"] == pytest.approx(1.0)


def test_kmeans_plusplus_samples_proportional_to_squared_distance():
    points = [(0.0, 0.0), (1.0, 0.0), (3.0, 0.0)]
    chosen, steps = ml_models_docs.kmeans_plusplus(points, 2, 0, [0.5])
    assert steps[0]["probs"] == pytest.approx([0.0, 0.1, 0.9])
    assert chosen == [0, 2]
    chosen, _ = ml_models_docs.kmeans_plusplus(points, 2, 0, [0.05])
    assert chosen == [0, 1]
    e = ml_models_docs.cluster_example()
    assert len(set(e["truth"][i] for i in e["plusplus"]["chosen"])) == 3


def test_silhouette_and_bic_choose_the_generating_k():
    points = [(0.0, 0.0), (0.0, 1.0), (4.0, 0.0)]
    s = ml_models_docs.silhouette_samples(points, [0, 0, 1])
    assert s[0] == pytest.approx((4.0 - 1.0) / 4.0)
    assert s[2] == 0.0
    e = ml_models_docs.cluster_example()
    inertias = [r["inertia"] for r in e["sweep"]]
    assert inertias == sorted(inertias, reverse=True)
    assert e["best_k_silhouette"] == 3
    assert e["best_k_bic"] == 3
    assert [r["params"] for r in e["sweep"]] == [5, 11, 17, 23, 29]


def test_dbscan_marks_core_border_and_noise_like_sklearn():
    points = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (1.9, 0.0), (5.0, 5.0)]
    result = ml_models_docs.dbscan(points, 1.0, 3)
    assert result["neighbors"] == [3, 3, 4, 2, 1]
    assert result["kinds"] == ["core", "core", "core", "border", "noise"]
    assert result["labels"] == [0, 0, 0, 0, -1]
    e = ml_models_docs.cluster_example()
    assert e["dbscan"]["labels"][-2:] == [-1, -1]
    assert e["moons_dbscan"]["ari"] == pytest.approx(1.0)
    assert e["moons_kmeans"]["ari"] < 0.3


def test_gmm_em_climbs_and_gives_soft_assignments():
    e = ml_models_docs.cluster_example()
    lls = e["em"]["log_likelihoods"] + [e["em"]["log_likelihood"]]
    assert all(b >= a - 1e-9 for a, b in zip(lls, lls[1:]))
    assert e["gmm"]["log_likelihood"] > e["em"]["log_likelihood"]
    assert sum(e["gmm"]["weights"]) == pytest.approx(1.0)
    for q in e["queries"]:
        assert sum(q["proba"]) == pytest.approx(1.0)
    assert 0.2 < max(e["queries"][1]["proba"]) < 0.8
    assert ml_models_docs.gmm_n_parameters(3, 2) == 17
    assert ml_models_docs.adjusted_rand_index([0, 0, 1, 1], [1, 1, 0, 0]) == pytest.approx(1.0)
    assert ml_models_docs.adjusted_rand_index([0, 0, 1, 1], [0, 1, 0, 1]) == pytest.approx(-0.5)


def test_ivf_recall_rises_with_nprobe_and_probing_every_list_is_exact():
    s = ml_models_docs.VECTOR_INDEX_EXAMPLE
    e = ml_models_docs.vector_index_example()
    assert sum(e["ivf"]["sizes"]) == s["n"]
    rows = e["ivf"]["rows"]
    recalls = [r["recall"] for r in rows]
    assert recalls == sorted(recalls)
    assert rows[0]["recall"] < 0.8
    assert rows[-1]["nprobe"] == s["nlist"]
    assert rows[-1]["recall"] == 1.0
    assert rows[-1]["distances"] == s["nlist"] + s["n"]
    plane = e["plane"]
    assert plane["probe1"]["ids"] != [plane["nearest"]]
    assert plane["probe2"]["ids"] == [plane["nearest"]]


def test_pq_asymmetric_distance_is_distance_to_the_reconstruction():
    data = [(0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 1.0, 0.0), (1.0, 1.0, 0.0, 0.0)]
    pq = ml_models_docs.pq_train(data, 2, 2, 0, 10)
    q = (0.2, 0.9, 0.4, 0.1)
    tables = ml_models_docs.pq_tables(pq, q)
    for v in data:
        code = ml_models_docs.pq_encode(pq, v)
        approx = sum(tables[j][c] for j, c in enumerate(code))
        assert approx == pytest.approx(ml_models_docs._dist2(q, ml_models_docs.pq_decode(pq, code)))
    e = ml_models_docs.vector_index_example()
    demo = e["pq"]["demo"]
    assert demo["approx"] == pytest.approx(ml_models_docs._dist2(demo["query"], demo["decoded"]))
    rows = e["pq"]["rows"]
    assert [r["bytes"] for r in rows] == [1.0, 2.0, 4.0]
    assert [r["error"] for r in rows] == sorted((r["error"] for r in rows), reverse=True)
    for r in rows:
        assert r["recall"][0] <= r["recall"][30] <= r["recall"][100]
    assert [r["recall"][0] for r in rows] == sorted(r["recall"][0] for r in rows)


def test_hnsw_layers_nest_respect_degree_caps_and_recall_rises_with_ef():
    s = ml_models_docs.VECTOR_INDEX_EXAMPLE
    data, _ = ml_models_docs.vector_dataset(200, 4, 4, 0.5, 1, 0)
    index = ml_models_docs.hnsw_build(data, 4, 20, 1)
    layers = index["layers"]
    assert len(layers[0]) == len(data)
    for upper, lower in zip(layers[1:], layers):
        assert set(upper) <= set(lower)
    for level, layer in enumerate(layers):
        cap = 8 if level == 0 else 4
        assert all(len(links) <= cap and node not in links for node, links in layer.items())
        assert all(nb in layer for links in layer.values() for nb in links)
    q = (0.1, -0.2, 0.3, 0.0)
    exact = ml_models_docs.exact_knn(data, q, 5)
    assert ml_models_docs.hnsw_search(index, data, q, 5, len(data))["ids"] == exact
    e = ml_models_docs.vector_index_example()
    rows = e["hnsw"]["rows"]
    recalls = [r["recall"] for r in rows]
    costs = [r["distances"] for r in rows]
    assert recalls == sorted(recalls) and costs == sorted(costs)
    assert recalls[0] < 0.95 and recalls[-1] == 1.0
    assert costs[-1] < s["n"] / 2
    sizes = e["hnsw"]["layer_sizes"]
    assert sizes[0] == s["n"] and sizes == sorted(sizes, reverse=True)
    assert e["plane"]["route"]["ids"] == [e["plane"]["nearest"]]


def test_vector_index_memory_counts_bytes_per_vector():
    m = ml_models_docs.vector_index_memory(1000, 128, 16, 16, 8)
    assert m["flat"] == 1000 * 128 * 4
    assert m["ivf_flat"] == m["flat"] + 1000 * 8
    assert m["ivf_pq"] == 1000 * 16 + 1000 * 8
    assert m["hnsw_flat"] == pytest.approx(m["flat"] + 1000 * (32 + 16 / 15) * 4)
    scale = ml_models_docs.vector_index_example()["scale"]
    assert scale["flat"] == 307_200_000_000
    assert scale["ivf_pq"] == 10_400_000_000
    assert ml_models_docs.recall_at_k([1, 2, 3, 9], [1, 2, 3, 4]) == 0.75


def test_temperature_softmax_flattens_but_keeps_the_ranking():
    teacher = ml_models_docs.DISTILLATION_EXAMPLE["teacher"]
    previous = None
    for t in [1, 2, 4, 8]:
        probs = ml_models_docs.temperature_softmax(teacher, t)
        assert math.isclose(sum(probs), 1.0)
        assert probs == sorted(probs, reverse=True)
        h = ml_models_docs.entropy(probs)
        if previous is not None:
            assert h > previous
        previous = h
    assert ml_models_docs.temperature_softmax(teacher, 1) == ml_models_docs.softmax_probs(teacher)


def test_kd_loss_gradient_matches_finite_differences():
    e = ml_models_docs.DISTILLATION_EXAMPLE
    out = ml_models_docs.kd_loss(e["student"], e["teacher"], e["label"], e["kd_temperature"], e["alpha"])
    assert math.isclose(out["loss"], e["alpha"] * out["hard"] + (1 - e["alpha"]) * e["kd_temperature"] ** 2 * out["soft"])
    assert out["soft"] > 0
    h = 1e-6
    for i in range(len(e["student"])):
        up, down = list(e["student"]), list(e["student"])
        up[i] += h
        down[i] -= h
        numeric = (ml_models_docs.kd_loss(up, e["teacher"], e["label"], e["kd_temperature"], e["alpha"])["loss"]
                   - ml_models_docs.kd_loss(down, e["teacher"], e["label"], e["kd_temperature"], e["alpha"])["loss"]) / (2 * h)
        assert math.isclose(out["gradient"][i], numeric, abs_tol=1e-6)
    assert math.isclose(sum(out["gradient"]), 0.0, abs_tol=1e-12)


def test_kd_soft_gradient_shrinks_as_one_over_t_squared():
    e = ml_models_docs.DISTILLATION_EXAMPLE
    scaling = ml_models_docs.kd_gradient_scaling(e["student"], e["teacher"], e["scaling_temperatures"])
    rows = scaling["rows"]
    for a, b in zip(rows, rows[1:]):
        assert b["raw_norm"] < a["raw_norm"]
    last = rows[-1]
    assert all(abs(s - l) < 0.06 for s, l in zip(last["scaled"], scaling["limit"]))
    ratio = rows[-2]["raw_norm"] / rows[-1]["raw_norm"]
    assert 3.8 < ratio < 4.2


def test_gaussian_teacher_is_the_bayes_posterior():
    e = ml_models_docs.DISTILLATION_EXAMPLE
    x = (0.3, -0.2)
    logits = ml_models_docs.gaussian_teacher_logits(x, e["means"], e["spreads"])
    densities = [math.exp(-((x[0] - m[0]) ** 2 + (x[1] - m[1]) ** 2) / (2 * s * s)) / (2 * math.pi * s * s)
                 for m, s in zip(e["means"], e["spreads"])]
    posterior = [d / sum(densities) for d in densities]
    for a, b in zip(ml_models_docs.softmax_probs(logits), posterior):
        assert math.isclose(a, b)


def test_distillation_example_soft_targets_beat_hard_labels():
    ex = ml_models_docs.distillation_example()
    e = ml_models_docs.DISTILLATION_EXAMPLE
    assert len(ex["runs"]) == len(e["seeds"])
    for run in ex["runs"]:
        assert sum(run["counts"]) == e["train"]
    hard, soft, mixed, hot = ex["summary"]["students"]
    teacher = ex["summary"]["teacher"]
    assert (hard["alpha"], hard["temperature"]) == (1.0, 1)
    assert teacher["agreement"] == 1.0 and teacher["kl"] == 0.0
    assert hard["train_nll"] < soft["train_nll"]
    assert soft["nll"] < mixed["nll"] < hard["nll"]
    assert soft["accuracy"] > hard["accuracy"]
    assert soft["agreement"] > hard["agreement"]
    assert teacher["nll"] < soft["nll"]
    assert hot["kl"] > soft["kl"]


def test_time_series_split_matches_the_sklearn_docstring():
    split = ml_models_docs.time_series_split
    assert split(12, 3, test_size=2) == [
        (list(range(6)), [6, 7]),
        (list(range(8)), [8, 9]),
        (list(range(10)), [10, 11]),
    ]
    assert [train for train, _ in split(12, 3, test_size=2, gap=2)] == [
        list(range(4)), list(range(6)), list(range(8)),
    ]
    assert split(6, 5) == [(list(range(k + 1)), [k + 1]) for k in range(5)]
    assert split(12, 3, max_train_size=3) == [([0, 1, 2], [3, 4, 5]), ([3, 4, 5], [6, 7, 8]), ([6, 7, 8], [9, 10, 11])]
    with pytest.raises(ValueError):
        split(5, 5)
    with pytest.raises(ValueError):
        split(12, 3, test_size=4)


def test_classical_decomposition_recovers_a_pure_seasonal_pattern():
    pattern = [3.0, -1.0, 0.5, -2.5]
    values = [10 + 0.25 * t + pattern[t % 4] for t in range(24)]
    parts = ml_models_docs.classical_decomposition(values, 4)
    assert parts["indices"] == pytest.approx(pattern)
    assert parts["trend"][:2] == [None, None] and parts["trend"][-2:] == [None, None]
    assert parts["trend"][2:-2] == pytest.approx([10 + 0.25 * t for t in range(2, 22)])
    assert all(abs(r) < 1e-9 for r in parts["residual"] if r is not None)


def test_autocorrelation_sees_the_season():
    values = [math.sin(2 * math.pi * t / 12) for t in range(120)]
    acf = ml_models_docs.autocorrelation(values, 12)
    assert acf[5] < -0.9 and acf[11] > 0.85
    assert ml_models_docs.autocorrelation([1, 2, 3, 4], 1)[0] == pytest.approx(0.25)


def test_forecast_errors_scale_by_in_sample_naive():
    scores = ml_models_docs.forecast_errors([0, 2, 4, 6, 9, 12], [0, 1, 2, 3], [4, 5], [8, 14])
    assert scores["scale"] == 2
    assert scores["mae"] == 1.5 and scores["mase"] == 0.75
    assert scores["rmse"] == pytest.approx(math.sqrt(2.5))


def test_time_series_example_ranks_models_and_exposes_shuffled_leakage():
    e = ml_models_docs.TIME_SERIES_EXAMPLE
    x = ml_models_docs.time_series_example()
    assert len(x["series"]) == e["n"] and len(x["folds"]) == e["n_splits"]
    for fold in x["folds"]:
        assert max(fold["train"]) < min(fold["test"])
        assert len(fold["test"]) == e["test_size"]
    assert sum(x["indices"]) == pytest.approx(0)
    assert max(x["indices"]) > 0.7 * e["amplitude"]
    by_name = {row["name"]: row for row in x["summary"]}
    assert by_name["trend + Fourier"]["mase"] < 1 < by_name["seasonal naive"]["mase"] < by_name["naive"]["mase"]
    assert by_name["trend + Fourier"]["mae"] <= by_name["trend + Fourier"]["rmse"]
    assert x["residual_acf"][0] > x["residual_band"] > abs(x["residual_acf"][4])
    assert x["leakage"]["ordered"] == pytest.approx(by_name["naive"]["mae"])
    assert x["leakage"]["shuffled"] < 0.5 * x["leakage"]["ordered"]
    assert by_name["trend + Fourier"]["mae"] < x["leakage"]["shuffled"] < by_name["trend + lag 12"]["mae"]
    assert by_name["seasonal naive"]["mae"] < by_name["naive"]["mae"]
    assert any(f["models"][1]["mae"] > f["models"][0]["mae"] for f in x["folds"])
    assert len(x["shuffled_test"]) == e["n"] // e["kfold"] + 1
    assert x["true_indices"][3] == pytest.approx(e["amplitude"])


def test_regression_scores_match_hand_checked_values():
    scores = ml_models_docs.regression_scores([1, 2, 3, 4], [2, 2, 2, 6])
    assert scores["mae"] == 1 and scores["mse"] == 1.5
    assert scores["rmse"] == pytest.approx(math.sqrt(1.5))
    assert scores["medae"] == 1 and scores["max_error"] == 2
    assert scores["r2"] == pytest.approx(1 - 6 / 5)
    assert scores["explained_variance"] == pytest.approx(1 - 5 / 5)
    assert scores["mape"] == pytest.approx((1 + 0 + 1 / 3 + 0.5) / 4)
    assert ml_models_docs.regression_scores([3, 3], [3, 3])["r2"] == 1
    assert ml_models_docs.regression_scores([3, 3], [2, 4])["r2"] == 0


def test_pinball_loss_charges_misses_by_side():
    assert ml_models_docs.pinball_loss([10], [8], 0.9) == pytest.approx(1.8)
    assert ml_models_docs.pinball_loss([10], [12], 0.9) == pytest.approx(0.2)
    assert ml_models_docs.pinball_loss([1, 5], [3, 3], 0.5) == pytest.approx(1)


def test_best_constants_are_mean_median_and_quantile():
    x = ml_models_docs.regression_metrics_example()
    y = sorted(ml_models_docs.REGRESSION_METRICS_EXAMPLE["targets"])
    best = dict(x["constants"])
    squared, absolute = best["squared error (MSE)"], best["absolute error (MAE)"]
    pinball, percentage = best["pinball, α = 0.9"], best["percentage error (MAPE)"]
    assert squared["low"] == pytest.approx(x["mean"]) and squared["high"] == pytest.approx(x["mean"])
    assert (absolute["low"], absolute["high"]) == pytest.approx((y[5], y[6]))
    assert pinball["low"] == pytest.approx(y[10]) == pytest.approx(pinball["high"])
    assert percentage["high"] < absolute["low"]


def test_regression_metrics_example_shows_each_pitfall():
    x = ml_models_docs.regression_metrics_example()
    rows = {row["name"]: row for row in x["models"]}
    steady, spiky = rows["steady"], rows["spiky"]
    assert spiky["mae"] < steady["mae"] and spiky["rmse"] > steady["rmse"]
    assert spiky["medae"] < steady["medae"] and spiky["max_error"] > steady["max_error"]
    assert rows["constant mean"]["r2"] == pytest.approx(0)
    assert rows["constant median"]["r2"] < 0 < rows["constant median"]["mae"] < rows["constant mean"]["mae"]
    biased = rows["biased +5"]
    assert biased["explained_variance"] == pytest.approx(1) and biased["r2"] < 1
    assert biased["pinball"] < min(row["pinball"] for row in x["models"] if row is not biased)
    assert x["narrow_scores"]["mae"] == pytest.approx(steady["mae"])
    assert x["narrow_scores"]["r2"] < steady["r2"]
    assert x["over_under"] == pytest.approx({"over": 0.5, "under": 1 / 3})


def test_svm_smo_finds_the_hard_margin_on_two_points():
    fit = ml_models_docs.svm_linear_fit([(0.0, 0.0), (2.0, 0.0)], [-1, 1], 100.0)
    assert fit["w"] == pytest.approx([1.0, 0.0])
    assert fit["b"] == pytest.approx(-1.0)
    assert fit["width"] == pytest.approx(2.0)
    assert fit["alpha"] == pytest.approx([0.5, 0.5])


def test_svm_example_matches_sklearn_and_closes_the_duality_gap():
    x = ml_models_docs.svm_example()
    hard, half, soft = x["fits"]
    assert hard["w"] == pytest.approx([1.0, 1.0]) and hard["b"] == pytest.approx(-5.5)
    assert hard["support"] == [3, 4] and hard["bounded"] == []
    assert half["w"] == pytest.approx([0.5, 0.5]) and half["width"] == pytest.approx(2 * hard["width"])
    assert soft["w"] == pytest.approx([0.45853659, 0.42682927]) and soft["b"] == pytest.approx(-2.34390244)
    assert soft["support"] == [1, 2, 3, 4, 5, 6]
    for fit in x["fits"] + x["with_outlier"]:
        assert fit["primal"] == pytest.approx(fit["dual"], abs=1e-6)
        assert sum(a * y for a, y in zip(fit["alpha"], ml_models_docs.SVM_EXAMPLE["labels"] + [1])) == pytest.approx(0, abs=1e-9)
        assert all(-1e-12 <= a <= fit["C"] + 1e-12 for a in fit["alpha"])
    strict = x["with_outlier"][0]
    assert strict["w"] == pytest.approx([0.5, 1.5]) and strict["b"] == pytest.approx(-5.25)
    assert strict["margins"][-1] < 0 and strict["bounded"] == [8]
    assert x["with_outlier"][-1]["width"] > x["with_outlier"][0]["width"]


def test_svm_kernels_separate_the_ring_and_rbf_decays_to_the_intercept():
    x = ml_models_docs.svm_example()
    assert x["linear_ring"]["accuracy"] < 0.6 and x["poly"]["accuracy"] == 1
    assert x["poly"]["scores"][0] == pytest.approx(-13 / 3)
    assert x["kernel_trick"]["kernel"] == pytest.approx(x["kernel_trick"]["explicit"]) == pytest.approx(9)
    small, mid, large = x["rbf"]
    assert [r["support"] for r in x["rbf"]] == [4, 7, 11]
    assert small["far"] == pytest.approx(-2.79258169, abs=1e-6)
    assert large["far"] == pytest.approx(large["model"]["b"], abs=1e-9)
    assert ml_models_docs.rbf_kernel((0, 0), (1, 1), 0.5) == pytest.approx(math.exp(-1))


def test_svm_scaling_shows_gamma_scale_cannot_fix_mixed_units():
    s = ml_models_docs.svm_example()["scaling"]
    assert s["gamma_raw"] == pytest.approx(4.3915289194983095e-07)
    assert s["gamma_standardized"] == pytest.approx(0.5)
    assert s["kernel_raw_near"] > 0.9999 and s["kernel_raw_far"] < 0.2
    assert s["kernel_std_near"] == pytest.approx(s["kernel_std_far"])


def test_lr_closed_forms_match_the_pytorch_recursions():
    x = ml_models_docs.lr_schedule_example()
    assert x["recursion_error"] < 1e-12
    s = x["schedules"]
    assert s["step"][29] == pytest.approx(0.1) and s["step"][30] == pytest.approx(0.01) and s["step"][99] == pytest.approx(1e-4)
    assert s["exponential"][1] == pytest.approx(0.096)
    assert s["cosine"][50] == pytest.approx(0.05)
    assert s["warmup_cosine"][0] == pytest.approx(0.001) and s["warmup_cosine"][10] == pytest.approx(0.1)
    assert x["cosine_past_end"] == pytest.approx({"at_end": 0.0, "after": 0.05, "back": 0.1})


def test_lr_one_cycle_follows_the_two_phase_cosine():
    x = ml_models_docs.lr_schedule_example()
    lrs, momentum = x["schedules"]["one_cycle"], x["momentum"]
    assert lrs[0] == pytest.approx(0.004) and lrs[29] == pytest.approx(0.1) and max(lrs) == lrs[29]
    assert lrs[99] == pytest.approx(4e-7)
    assert momentum[0] == pytest.approx(0.95) and momentum[29] == pytest.approx(0.85) and momentum[99] == pytest.approx(0.95)
    assert ml_models_docs.lr_one_cycle(64, 100, 0.1)[0] == pytest.approx((0.1 + 4e-7) / 2)


def test_lr_decay_beats_both_constant_rates_on_the_noisy_quadratic():
    x = ml_models_docs.lr_schedule_example()
    runs, floors = x["runs"], x["floors"]
    assert floors["constant"] == pytest.approx(1 / 36)
    assert runs["constant"][-1] == pytest.approx(floors["constant"], rel=1e-6)
    assert runs["slow"][-1] > 5 * runs["constant"][-1]
    for name in ("step", "cosine", "warmup_cosine", "one_cycle"):
        assert runs[name][-1] < runs["constant"][-1] / 2
    assert runs["cosine"][-1] < runs["step"][-1]
    assert runs["warmup_cosine"][10] > runs["constant"][10]


def test_lr_gd_rates_and_range_test_show_the_stability_limit():
    x = ml_models_docs.lr_schedule_example()
    factors = [g["factor"] for g in x["gd"]]
    assert factors == pytest.approx([0.9, 0.0, -0.8, -1.1])
    assert abs(x["gd"][-1]["w"][-1]) > abs(x["gd"][-1]["w"][0])
    r = x["range"]
    assert r["rows"][r["best"]][0] == pytest.approx(1.0)
    assert r["rows"][r["blowup"]][1] > r["rows"][0][1] and r["blowup"] == r["best"] + 3
    assert r["stable_limit"] == 0.25 and r["rows"][r["best"]][0] / 10 < r["stable_limit"]


def test_adam_first_steps_move_by_the_learning_rate_whatever_the_gradient():
    for run in ml_models_docs.lr_schedule_example()["adam"]:
        assert run["updates"] == pytest.approx([1e-3] * 3, rel=1e-3)


def test_gan_optimal_discriminator_turns_the_value_into_jensen_shannon():
    x = ml_models_docs.gan_example()
    data = ml_models_docs.GAN_EXAMPLE["data"]
    for g in x["generators"]:
        assert g["value"] == pytest.approx(-math.log(4) + 2 * g["js"])
        for i, prob in enumerate(g["disc"]):
            if prob is not None and 0.01 < prob < 0.99:
                for step in (-0.01, 0.01):
                    nudged = g["disc"][:i] + [prob + step] + g["disc"][i + 1:]
                    assert ml_models_docs.gan_value(data, g["p"], nudged) < g["value"]
    matched = x["generators"][0]
    assert matched["js"] == 0 and set(matched["disc"]) == {None, 0.5}
    assert all(0 <= g["js"] <= math.log(2) for g in x["generators"])


def test_gan_divergences_differ_on_dropped_modes_and_disjoint_supports():
    by_name = {g["name"]: g for g in ml_models_docs.gan_example()["generators"]}
    assert by_name["one mode"]["kl_forward"] == math.inf
    assert by_name["one mode"]["kl_reverse"] == pytest.approx(math.log(2))
    assert by_name["broad"]["kl_forward"] < math.inf and by_name["broad"]["kl_reverse"] == math.inf
    assert by_name["one mode"]["w1"] == pytest.approx(2.0) and by_name["broad"]["w1"] == pytest.approx(0.6)
    for point in ml_models_docs.gan_example()["points"]:
        assert point["js"] == pytest.approx(math.log(2)) and point["w1"] == point["shift"]


def test_gan_saturating_generator_gradient_vanishes_when_d_rejects_fakes():
    rows = {r["logit"]: r for r in ml_models_docs.gan_example()["saturation"]}
    assert abs(rows[-6.0]["minimax"]) < 0.003 and abs(rows[-6.0]["non_saturating"]) > 0.99
    assert rows[0.0]["minimax"] == rows[0.0]["non_saturating"] == -0.5
    for r in rows.values():
        assert r["minimax"] - r["non_saturating"] == pytest.approx(1 - 2 * r["d"])


def test_dirac_gan_spirals_out_unless_r1_regularized():
    dirac = ml_models_docs.gan_example()["dirac"]
    minimax = dirac["minimax"]["marks"]
    assert minimax == sorted(minimax) and minimax[-1] > 2.7
    assert 0.4 < dirac["non_saturating"]["marks"][-1] < 0.5
    assert dirac["r1"]["marks"][-1] < 1e-9
    assert dirac["minimax"]["radius"][1] > dirac["minimax"]["radius"][0]
    d = ml_models_docs.GAN_EXAMPLE["dirac"]
    theta, psi = ml_models_docs.dirac_gan(d["theta"], d["psi"], d["lr"], 10 * d["steps"], "non_saturating")[-1]
    assert 0.4 < math.hypot(theta, psi) < 0.45


def test_frechet_distance_matches_closed_forms_and_shrinks_with_samples():
    fid = {r["name"]: r["fid"] for r in ml_models_docs.gan_example()["fid"]}
    assert fid["identical"] == pytest.approx(0, abs=1e-12)
    assert fid["mean shifted"] == pytest.approx(0.25)
    assert fid["collapsed"] == pytest.approx(0.5)
    assert fid["correlated"] == pytest.approx(4 - 2 * (math.sqrt(1.8) + math.sqrt(0.2)))
    sampled = [r["fid"] for r in ml_models_docs.gan_example()["fid_sampled"]]
    assert sampled == sorted(sampled, reverse=True) and sampled[-1] < 0.01


def test_dcgan_transposed_convolutions_grow_one_pixel_to_sixty_four():
    assert ml_models_docs.gan_example()["dcgan_sizes"] == [1, 4, 8, 16, 32, 64]
    assert ml_models_docs.conv_transpose_out(4, 3, 2, 1) == 7
    assert ml_models_docs.conv_transpose_out(4, 3, 2, 1, output_padding=1) == 8


def test_encoder_param_count_matches_bert_base_and_the_decoder_block():
    counts = ml_models_docs.encoder_param_count(30000, 512, 2, 768, 12)
    assert counts["d_ff"] == 3072
    assert counts["embeddings"] == 30000 * 768 + 512 * 768 + 2 * 768 + 2 * 768
    assert counts["per_block"] == ml_models_docs.decoder_param_count(30000, 512, 768, 12)["per_block"]
    assert counts["per_block"] == ml_models_docs.transformer_param_count(768, 1, 0, 3072)["encoder_layer"]
    assert counts["total"] == counts["embeddings"] + 12 * counts["per_block"] == 108_490_752
    large = ml_models_docs.encoder_param_count(30000, 512, 2, 1024, 24)
    assert large["total"] == 333_557_760


def test_bert_inputs_mark_segments_positions_and_padding():
    pair = ml_models_docs.bert_inputs(["the", "cat"], ["it"], 8)
    assert pair["tokens"] == ["[CLS]", "the", "cat", "[SEP]", "it", "[SEP]", "[PAD]", "[PAD]"]
    assert pair["segments"] == [0, 0, 0, 0, 1, 1, 0, 0]
    assert pair["positions"] == list(range(8))
    assert pair["padding"] == [False] * 6 + [True] * 2
    assert pair["real"] == 6
    cut = ml_models_docs.bert_inputs(["a", "b", "c", "d"], None, 4)
    assert cut["tokens"] == ["[CLS]", "a", "b", "[SEP]"] and cut["padding"] == [False] * 4


def test_mlm_corrupt_labels_only_chosen_positions_and_never_specials():
    tokens = ml_models_docs.bert_inputs(["w%d" % i for i in range(40)])["tokens"]
    result = ml_models_docs.mlm_corrupt(tokens, 0.15, (0.8, 0.1, 0.1), ["x", "y"], ml_models_docs.random.Random(0))
    assert len(result["chosen"]) == 6
    for i, label in enumerate(result["labels"]):
        if i in result["chosen"]:
            assert label == tokens[i] and tokens[i] not in ("[CLS]", "[SEP]")
        else:
            assert label == ml_models_docs.IGNORE_INDEX and result["inputs"][i] == tokens[i]
    for i, action in result["actions"].items():
        assert (result["inputs"][i] == "[MASK]") == (action == "mask")
        if action == "keep":
            assert result["inputs"][i] == tokens[i]


def test_mlm_corruption_rates_follow_the_80_10_10_split():
    e = ml_models_docs.ENCODER_EXAMPLE
    rates = ml_models_docs.mlm_corruption_rates(100000, 0.15, (0.8, 0.1, 0.1), e["mask_vocab"], e["mask_seed"])
    assert rates["selected"] == 15000
    assert abs(rates["fractions"]["mask"] - 0.12) < 0.003
    assert abs(rates["fractions"]["random"] - 0.015) < 0.002
    assert abs(rates["fractions"]["keep"] - 0.015) < 0.002
    assert rates["changed"] < rates["fractions"]["mask"] + rates["fractions"]["random"]


def test_masked_lm_loss_averages_only_labelled_positions():
    out = ml_models_docs.masked_lm_loss([9.0, 1.0, 9.0, 3.0], [-100, "cat", -100, "mat"])
    assert out == {"kept": 2, "loss": 2.0}


def test_padding_mask_makes_padded_attention_match_the_unpadded_sequence():
    check = ml_models_docs.padding_attention_check(ml_models_docs.ATTENTION_EXAMPLE, 3, [0.0, 0.0], [0.0, 0.0])
    assert check["masked_gap"] < 1e-12
    assert check["unmasked_gap"] > 0.1
    assert all(w > 0 for w in check["pad_weight"])
    assert all(row[3] == 0.0 for row in check["masked"]["weights"][:3])


def test_fill_in_needs_both_sides_to_resolve_the_blank():
    e = ml_models_docs.ENCODER_EXAMPLE
    scores = ml_models_docs.fill_in_scores(tuple(e["fill_corpus"]), tuple(e["fill_test"]), e["fill_alpha"])
    assert scores["accuracy"]["both"] == 1.0
    assert scores["nll"]["both"] < scores["nll"]["left"] and scores["nll"]["both"] < scores["nll"]["right"]
    for row in scores["rows"]:
        assert abs(row["left"] - 3 / 7) < 1e-12 and abs(row["right"] - 3 / 7) < 1e-12
        assert abs(row["both"] - 0.6) < 1e-12


def test_encoder_example_contrasts_bidirectional_and_causal_attention():
    example = ml_models_docs.encoder_example()
    assert example["prefix"]["causal_gap"] < 1e-12 < example["prefix"]["bidirectional_gap"]
    assert all(w > 0 for row in example["bidirectional"]["weights"] for w in row)
    assert [c["counts"]["total"] for c in example["configs"]] == [108_490_752, 333_557_760]
    assert example["batch"][1]["padding"].count(True) == 7


def test_ndcg_matches_hand_computed_values_for_the_example_ranking():
    example = ml_models_docs.ltr_example()
    assert example["order"] == [2, 1, 0, 4, 3]
    assert example["ideal_labels"] == [3, 2, 1, 0, 0]
    assert abs(example["idcg"] - 9.3928) < 1e-4
    assert abs(example["ndcg"] - 0.6153) < 1e-4
    assert abs(example["ndcg_linear"] - 0.6612) < 1e-4
    assert abs(example["ndcg_k"] - 0.5741) < 1e-4


def test_ndcg_is_one_for_an_ideal_ranking_and_ignores_score_scale():
    labels = [3, 2, 0, 1, 0]
    assert ml_models_docs.ndcg_at(labels, [5, 4, 1, 3, 0]) == 1.0
    scores = [0.2, 0.6, 0.9, -0.4, 0.1]
    assert ml_models_docs.ndcg_at(labels, scores) == ml_models_docs.ndcg_at(labels, [10 * s for s in scores])


def test_lambda_gradients_sum_to_zero_and_weight_the_top_swap_most():
    e = ml_models_docs.LTR_EXAMPLE
    out = ml_models_docs.lambda_gradients(e["labels"], e["scores"])
    assert abs(sum(out["grad"])) < 1e-12
    assert all(h > 0 for h in out["hess"])
    biggest = max(out["pairs"], key=lambda p: p["delta"])
    assert (biggest["high"], biggest["low"]) == (0, 2)
    assert len(out["pairs"]) == 9


def test_ranknet_weights_every_pair_equally():
    e = ml_models_docs.LTR_EXAMPLE
    out = ml_models_docs.lambda_gradients(e["labels"], e["scores"], use_metric=False)
    assert all(p["delta"] == 1.0 for p in out["pairs"])
    assert abs(sum(out["grad"])) < 1e-12


def test_newton_steps_improve_ndcg_and_pointwise_loss_disagrees_with_ndcg():
    example = ml_models_docs.ltr_example()
    curve = [h["ndcg"] for h in example["lambdamart"]]
    assert curve[-1] > curve[0]
    assert all(b >= a - 1e-12 for a, b in zip(curve, curve[1:]))
    a, b = example["pointwise"]["a"], example["pointwise"]["b"]
    assert a["mse"] < b["mse"] and a["ndcg"] < b["ndcg"] == 1.0
    assert example["listnet"]["ideal"] < example["listnet"]["start"]


def test_bucketing_and_packing_cut_padding_waste():
    example = ml_models_docs.data_example()
    assert (example["shuffled"]["slots"], example["bucketed"]["slots"], example["packed"]["slots"]) == (304, 220, 192)
    assert example["shuffled"]["efficiency"] < example["bucketed"]["efficiency"] < example["packed"]["efficiency"]
    rows = example["packed"]["rows"]
    assert all(sum(row) <= ml_models_docs.DATA_EXAMPLE["context"] for row in rows)
    assert sorted(x for row in rows for x in row) == sorted(ml_models_docs.DATA_EXAMPLE["lengths"])


def test_distributed_shards_match_distributed_sampler_padding_and_dropping():
    padded = ml_models_docs.distributed_shards(10, 4)
    assert padded["shards"] == [[0, 4, 8], [1, 5, 9], [2, 6, 0], [3, 7, 1]]
    dropped = ml_models_docs.distributed_shards(10, 4, drop_last=True)
    assert dropped["shards"] == [[0, 4], [1, 5], [2, 6], [3, 7]]
    assert ml_models_docs.distributed_shards(3, 8)["indices"] == [0, 1, 2, 0, 1, 2, 0, 1]
    assert (ml_models_docs.loader_length(10, 3, False), ml_models_docs.loader_length(10, 3, True)) == (4, 3)


def test_loader_pipeline_hides_loading_once_workers_keep_up():
    e = ml_models_docs.DATA_EXAMPLE
    runs = ml_models_docs.data_example()["pipelines"]
    assert runs[0]["total_ms"] == (e["load_ms"] + e["compute_ms"]) * e["batches"]
    busy = [r["gpu_busy"] for r in runs]
    assert busy == sorted(busy)
    assert runs[-1]["total_ms"] == e["load_ms"] + e["compute_ms"] * e["batches"]
    for run in runs[1:]:
        limit = e["prefetch_factor"] * run["workers"]
        for i, step in enumerate(run["timeline"]):
            taken = sum(1 for s in run["timeline"][:i] if s["compute_start"] <= step["load_start"])
            assert i - taken < limit


def test_minibatch_gradient_variance_matches_enumeration():
    import itertools
    grads = ml_models_docs.DATA_EXAMPLE["grads"]
    for b in (1, 2, 4, 8):
        means = [sum(c) / b for c in itertools.combinations(grads, b)]
        avg = sum(means) / len(means)
        exact = sum((m - avg) ** 2 for m in means) / len(means)
        assert abs(ml_models_docs.minibatch_gradient_variance(grads, b)["variance"] - exact) < 1e-12


def test_dynamic_batching_cuts_queueing_delay_under_load():
    runs = ml_models_docs.serving_example()["policies"]
    sizes = [[b["size"] for b in run["batches"]] for run in runs]
    assert sizes == [[1] * 16, [1, 4, 4, 4, 3], [3, 4, 4, 4, 1], [3, 5, 7, 1]]
    assert [run["max_ms"] for run in runs] == [74, 22, 22, 21]
    assert runs[0]["mean_ms"] > 2 * runs[1]["mean_ms"]
    assert runs[2]["mean_ms"] > runs[1]["mean_ms"]
    for run in runs:
        assert all(b["size"] <= run["max_batch"] for b in run["batches"])
        assert sum(b["size"] for b in run["batches"]) == 16


def test_dynamic_batching_waits_for_the_deadline_or_a_full_batch():
    out = ml_models_docs.dynamic_batching([0, 10], 2, 1, max_batch=4, max_wait_ms=3)
    assert [(b["start"], b["size"]) for b in out["batches"]] == [(3, 1), (13, 1)]
    out = ml_models_docs.dynamic_batching([0, 1, 2, 10], 2, 1, max_batch=3, max_wait_ms=5)
    assert [(b["start"], b["size"]) for b in out["batches"]] == [(2, 3), (15, 1)]
    assert ml_models_docs.nearest_rank([5, 1, 4, 2, 3], 0.9) == 5


def test_batch_cost_shows_gpu_throughput_needs_large_batches():
    cpu, gpu = ml_models_docs.serving_example()["devices"]
    assert cpu["costs"][0]["latency_ms"] < gpu["costs"][0]["latency_ms"]
    assert gpu["costs"][-1]["per_second"] > 20 * cpu["costs"][-1]["per_second"]
    assert abs(ml_models_docs.batch_cost(3.0, 0.05, 64)["per_second"] - 64000 / 6.2) < 1e-9


def test_continuous_batching_fills_freed_slots():
    example = ml_models_docs.serving_example()
    static, cont = example["static"], example["continuous"]
    assert static["finish"] == [3, 9, 4, 2, 14, 12, 15, 11]
    assert cont["finish"] == [3, 9, 4, 2, 7, 6, 10, 8]
    assert static["tokens"] == cont["tokens"] == 34
    assert (static["busy_steps"], cont["busy_steps"]) == (15, 10)
    assert cont["utilization"] > static["utilization"]
    for run in (static, cont):
        assert sum(len(row["active"]) for row in run["timeline"]) == 34
        assert all(len(row["active"]) + row["idle"] == 4 for row in run["timeline"])


def test_naive_difference_is_the_effect_on_the_treated_plus_selection_bias():
    units = ml_models_docs.CAUSAL_EXAMPLE["units"]
    po = ml_models_docs.potential_outcomes_summary(units)

    assert po["ate"] == 2
    assert po["naive"] == 0
    assert po["naive"] == pytest.approx(po["att"] + po["selection_bias"])
    assert po["observed"] == [u["y1"] if u["t"] else u["y0"] for u in units]


def test_randomized_assignment_is_unbiased_on_average():
    units = ml_models_docs.CAUSAL_EXAMPLE["units"]
    result = ml_models_docs.randomized_assignments(units, 4)

    assert result["count"] == 70
    assert result["mean"] == pytest.approx(ml_models_docs.potential_outcomes_summary(units)["ate"])
    assert result["min"] < 0 < result["max"]


def test_adjustment_and_inverse_weighting_reverse_the_naive_sign():
    example = ml_models_docs.causal_example()
    strat, ipw = example["strat"], example["ipw"]

    assert strat["naive"] == pytest.approx(0.66 - 520 / 700)
    assert strat["naive"] < 0
    assert strat["adjusted"] == pytest.approx(0.10)
    assert ipw["horvitz_thompson"] == pytest.approx(strat["adjusted"])
    assert ipw["hajek"] == pytest.approx(strat["adjusted"])
    for w, s in zip(ipw["weights"], ml_models_docs.CAUSAL_EXAMPLE["strata"]):
        assert w["pseudo_treated"] == pytest.approx(s["treated"] + s["control"])
        assert w["pseudo_control"] == pytest.approx(s["treated"] + s["control"])


def test_logistic_propensity_recovers_stratum_rates_unless_penalized():
    example = ml_models_docs.causal_example()

    assert example["fit"]["propensities"] == pytest.approx([0.25, 0.75])
    assert example["fit"]["bias"] == pytest.approx(math.log(1 / 3))
    assert example["fit_ipw"]["horvitz_thompson"] == pytest.approx(0.10)
    low, high = example["regularized"]["propensities"]
    assert 0.25 < low < high < 0.75
    assert example["regularized_ipw"]["horvitz_thompson"] < 0.10


def test_difference_in_differences_subtracts_the_shared_trend():
    did = ml_models_docs.causal_example()["did"]

    assert did["effect"] == 6
    assert did["before_after"] == 14
    assert did["post_gap"] == 16
    assert did["pre_trend_gap"] == 0
    assert did["counterfactual"] == [48, 50, 56, 58]


def test_uplift_targeting_beats_targeting_likely_responders():
    uplift = ml_models_docs.causal_example()["uplift"]

    assert uplift["by_response"]["names"] == ["B", "D"]
    assert uplift["by_uplift"]["names"] == ["A", "B"]
    assert uplift["by_response"]["incremental"] == pytest.approx(-80)
    assert uplift["by_uplift"]["incremental"] == pytest.approx(220)
    assert uplift["everyone"] == pytest.approx(130)


def test_reliability_bins_match_calibration_curve_binning():
    report = ml_models_docs.calibration_example()["original"]

    counts = [b["count"] for b in report["bins"]]
    assert counts == [5, 2, 2, 3, 8]
    assert [b["accuracy"] for b in report["bins"]] == pytest.approx([0.2, 0.5, 0.5, 2 / 3, 0.75])
    assert [b["confidence"] for b in report["bins"]] == pytest.approx([0.09, 0.325, 0.525, 0.7, 0.935])
    assert report["ece"] == pytest.approx(0.1265)
    assert report["mce"] == pytest.approx(0.185)
    edge = ml_models_docs.reliability_bins([0.2, 0.2001], [0, 1], 5)["rows"]
    assert edge[0]["count"] == 1 and edge[1]["count"] == 1


def test_brier_and_log_loss_reward_calibration_and_discrimination():
    example = ml_models_docs.calibration_example()

    assert ml_models_docs.brier_score([1, 0], [0.8, 0.4]) == pytest.approx((0.04 + 0.16) / 2)
    assert example["constant"]["ece"] == 0
    assert example["constant"]["auc"] == 0.5
    assert example["original"]["brier"] < example["constant"]["brier"]
    assert example["original"]["log_loss"] < example["constant"]["log_loss"]


def test_platt_scaling_uses_smoothed_targets_and_keeps_the_ranking():
    example = ml_models_docs.calibration_example()
    platt = example["platt"]

    assert platt["target_positive"] == pytest.approx(12 / 13)
    assert platt["target_negative"] == pytest.approx(1 / 11)
    assert 0 < platt["a"] < 1
    assert example["platt_report"]["auc"] == example["original"]["auc"]
    assert example["platt_report"]["ece"] < example["original"]["ece"]
    assert example["platt_report"]["log_loss"] < example["original"]["log_loss"]


def test_temperature_scaling_minimizes_log_loss_and_softens_overconfidence():
    example = ml_models_docs.calibration_example()
    temperature = example["temperature"]
    labels = example["example"]["labels"]

    assert temperature["temperature"] > 1
    gradient = sum((p - y) * z for p, y, z in zip(temperature["probabilities"], labels, example["logits"]))
    assert gradient == pytest.approx(0, abs=1e-9)
    assert example["temperature_report"]["accuracy"] == example["original"]["accuracy"]
    assert example["temperature_report"]["auc"] == example["original"]["auc"]
    assert example["temperature_report"]["ece"] < example["platt_report"]["ece"]
    maps = example["maps"]
    assert [m["temperature"] for m in maps] == sorted(m["temperature"] for m in maps)
    assert all(abs(m["temperature"] - 0.5) <= abs(m["p"] - 0.5) for m in maps)


def test_isotonic_pav_pools_violators_into_a_monotone_step_function():
    example = ml_models_docs.calibration_example()
    isotonic = example["isotonic"]
    values = [s["value"] for s in isotonic["steps"]]

    assert values == sorted(values)
    assert values == pytest.approx([0, 1 / 3, 0.5, 5 / 7, 1])
    assert sum(s["weight"] for s in isotonic["steps"]) == 20
    assert isotonic["merges"] == 9
    assert example["isotonic_report"]["ece"] == pytest.approx(0)
    assert example["isotonic_report"]["auc"] != example["original"]["auc"]


def test_scaling_logits_shrinks_correct_loss_and_grows_wrong_loss():
    rows = ml_models_docs.calibration_example()["overconfidence"]

    correct = [r["correct"] for r in rows]
    wrong = [r["wrong"] for r in rows]
    assert correct == sorted(correct, reverse=True)
    assert wrong == sorted(wrong)
    assert all(w == pytest.approx(r["logit"] + c) for r, c, w in zip(rows, correct, wrong))


def test_gcn_normalization_adds_self_loops_and_is_symmetric():
    prop = ml_models_docs.gnn_example()["prop"]
    norm = prop["normalized"]

    assert prop["degrees"] == [3, 3, 4, 3, 2]
    assert all(norm[i][j] == pytest.approx(norm[j][i]) for i in range(5) for j in range(5))
    assert norm[2][3] == pytest.approx(1 / math.sqrt(12))
    assert norm[0][4] == 0
    assert all(norm[i][i] == pytest.approx(1 / d) for i, d in enumerate(prop["degrees"]))


def test_gcn_message_passing_with_index_add_matches_the_matrix_form():
    example = ml_models_docs.gnn_example()

    assert len(example["mp"]["sources"]) == 2 * len(example["example"]["edges"]) + 5
    for row, expected in zip(example["mp"]["aggregated"], example["axw"]):
        assert row == pytest.approx(expected)
    assert example["ax"][0] == pytest.approx(example["ax"][1])
    assert example["gcn"] == [[max(0, v) for v in row] for row in example["axw"]]


def test_index_add_rows_matches_the_torch_docstring_example():
    out = ml_models_docs.index_add_rows(5, [0, 4, 2], [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    assert out == [[1, 2, 3], [0, 0, 0], [7, 8, 9], [0, 0, 0], [4, 5, 6]]


def test_gat_attention_is_a_softmax_over_the_neighbourhood_with_leaky_relu():
    gat = ml_models_docs.gnn_example()["gat"]

    assert gat["neighbours"] == [0, 1, 2, 3]
    assert sum(gat["alpha"]) == pytest.approx(1)
    assert gat["scores"] == pytest.approx([0.75, -0.15, 0.25, -0.25])
    assert gat["output"] == pytest.approx(
        [sum(a * gat["z"][j][k] for a, j in zip(gat["alpha"], gat["neighbours"])) for k in range(2)]
    )


def test_graphsage_concatenates_self_with_the_neighbour_mean_and_normalizes():
    sage = ml_models_docs.gnn_example()["sage"]

    assert sage["neighbours"] == [0, 1, 3]
    assert sage["mean"] == pytest.approx([1 / 3, 1])
    assert sage["concat"] == pytest.approx([1, 1, 1 / 3, 1])
    assert ml_models_docs.vector_norm(sage["output"]) == pytest.approx(1)


def test_repeated_propagation_oversmooths_toward_the_degree_direction():
    rows = ml_models_docs.gnn_example()["smooth"]["rows"]

    cosines = [r["min_cosine"] for r in rows]
    spreads = [r["spread"] for r in rows]
    assert cosines == sorted(cosines)
    assert spreads == sorted(spreads, reverse=True)
    assert cosines[-1] == pytest.approx(1, abs=1e-6)
    assert spreads[-1] < 1e-3


def test_batching_graphs_offsets_edges_and_pools_per_graph():
    batch = ml_models_docs.gnn_example()["batch"]

    assert batch["offsets"] == [0, 5]
    assert batch["batch"] == [0] * 5 + [1] * 3
    assert batch["sources"][-3:] == [5, 6, 5] and batch["targets"][-3:] == [6, 7, 7]
    assert batch["mean_pool"][0] == pytest.approx([0.8, 0.8])
    assert batch["mean_pool"][1] == pytest.approx([1, 2])


def test_diffusion_schedules_match_the_ddpm_endpoints_and_decrease():
    betas = ml_models_docs.diffusion_linear_betas(1000, 1e-4, 0.02)
    assert betas[0] == pytest.approx(1e-4) and betas[-1] == pytest.approx(0.02)
    for schedule in (betas, ml_models_docs.diffusion_cosine_betas(1000)):
        bars = ml_models_docs.diffusion_alpha_bars(schedule)
        assert all(a > b for a, b in zip(bars, bars[1:]))
        assert bars[-1] < 1e-4
    rows = ml_models_docs.diffusion_example()["schedule"]
    assert all(r["cosine"] > r["linear"] for r in rows[1:-1])
    curve = ml_models_docs.diffusion_example()["curve"]
    assert curve[0] == {"t": 0, "linear": 1.0, "cosine": 1.0} and curve[-1]["t"] == 1000
    assert curve[-1]["linear"] == pytest.approx(rows[-1]["linear"])


def test_diffusion_closed_form_matches_iterating_the_one_step_noise():
    it = ml_models_docs.diffusion_example()["iterated"]

    assert it["mean"] == pytest.approx(it["closed_mean"])
    assert it["variance"] == pytest.approx(it["closed_variance"])


def test_diffusion_posterior_mean_equals_the_epsilon_parameterization():
    ex = ml_models_docs.diffusion_example()
    post = ex["posterior"]

    assert post["eps_mean"] == pytest.approx(post["mean"])
    betas = ml_models_docs.diffusion_linear_betas(1000, 1e-4, 0.02)
    assert post["variance"] < betas[post["t"] - 1]


def test_two_point_denoiser_is_the_posterior_mean():
    bars = ml_models_docs.diffusion_alpha_bars(ml_models_docs.diffusion_linear_betas(1000, 1e-4, 0.02))
    ab, xt = bars[300], 0.4
    plus = 0.7 * math.exp(-((xt - math.sqrt(ab)) ** 2) / (2 * (1 - ab)))
    minus = 0.3 * math.exp(-((xt + math.sqrt(ab)) ** 2) / (2 * (1 - ab)))
    x0_hat, eps_hat = ml_models_docs.two_point_denoiser(xt, ab, 0.7)

    assert x0_hat == pytest.approx((plus - minus) / (plus + minus))
    assert xt == pytest.approx(math.sqrt(ab) * x0_hat + math.sqrt(1 - ab) * eps_hat)


def test_ddim_is_deterministic_and_lands_on_the_data():
    ex = ml_models_docs.diffusion_example()
    for run in ex["ddim"]:
        assert len(run["timesteps"]) == run["count"] and run["timesteps"][0] == 999
        finals = [p[-1] for p in run["paths"]]
        for start, final in zip(ex["example"]["ddim_starts"], finals):
            assert final == pytest.approx(math.copysign(1, start) if start else 0, abs=1e-4)


def test_guidance_sharpens_toward_the_condition_and_ddpm_matches_the_data():
    ex = ml_models_docs.diffusion_example()
    plus = [g["plus"] for g in ex["guidance"]]

    assert plus[0] == pytest.approx(0.7, abs=0.02)
    assert plus == sorted(plus) and plus[-1] > 0.9
    assert ex["ddpm"]["max_error"] < 1e-9
    assert ex["ddpm"]["plus"] == pytest.approx(0.5, abs=0.05)


def test_latent_diffusion_compresses_a_512_image_48_times():
    latent = ml_models_docs.diffusion_example()["latent"]

    assert latent["latent_shape"] == [4, 64, 64]
    assert latent["ratio"] == 48


def test_guidance_tilt_tracks_the_guided_sampler():
    assert ml_models_docs.guidance_tilt(0.7, 0.5, 0.0) == pytest.approx(0.7)
    assert ml_models_docs.guidance_tilt(0.7, 0.5, 1.0) == pytest.approx(0.49 / 0.58)
    for row in ml_models_docs.diffusion_example()["guidance"]:
        assert row["plus"] == pytest.approx(row["tilt"], abs=0.01)


def test_span_corruption_reproduces_the_t5_example_and_mlm_splits_its_picks():
    ex = ml_models_docs.pretraining_example()
    assert " ".join(ex["span"]["inputs"]) == "Thank you <X> me to your party <Y> week ."
    assert " ".join(ex["span"]["targets"]) == "<X> for inviting <Y> last <Z>"
    assert ex["causal_targets"] == len(ex["tokens"]) - 1
    mlm = ex["mlm"]
    assert mlm["chosen"] == pytest.approx(76.8)
    assert mlm["mask"] + mlm["random"] + mlm["kept"] == pytest.approx(mlm["chosen"])


def test_training_flops_are_six_per_parameter_per_token():
    lin = ml_models_docs.linear_layer_flops(3, 5, 7)
    assert lin["forward"] == 2 * 3 * 5 * 7 and lin["total"] == 6 * lin["params"] * 3
    ex = ml_models_docs.pretraining_example()
    assert ex["params"]["non_embedding"] == 12 * 32 * 4096 ** 2
    assert ex["forward"]["attention_share"] == pytest.approx(1 / 13)


def test_chinchilla_closed_form_is_the_minimum_on_the_compute_budget():
    c = ml_models_docs.PRETRAINING_EXAMPLE["chinchilla"]
    for compute in (1e21, 5.88e23, 1e25):
        opt = ml_models_docs.chinchilla_optimal(compute, c)
        assert 6 * opt["n"] * opt["d"] == pytest.approx(compute)
        for scale in (0.8, 1.25):
            n = opt["n"] * scale
            assert ml_models_docs.chinchilla_loss(n, compute / (6 * n), c) > opt["loss"]


def test_chinchilla_beats_gopher_and_the_rule_of_thumb_recovers_70b():
    ex = ml_models_docs.pretraining_example()
    chin, gopher = ex["trained"]
    assert chin["loss"] < gopher["loss"]
    for curve in ex["isoflop"]:
        assert min(p["loss"] for p in curve["points"]) == pytest.approx(curve["optimal"]["loss"])
    assert chin["rule"]["n"] == pytest.approx(70e9) and chin["rule"]["d"] == pytest.approx(1.4e12)
    assert ex["kaplan"]["tenfold_n"] * ex["kaplan"]["tenfold_d"] == pytest.approx(10)
    assert ex["days"] == pytest.approx(5.88e23 / (989e12 * 0.4 * 1000) / 86400)


def test_minhash_estimates_jaccard_and_lsh_has_the_expected_threshold():
    ex = ml_models_docs.pretraining_example()
    near = ex["pairs"][0]
    assert near["exact"] == pytest.approx(12 / 14)
    assert near["estimate"] == pytest.approx(near["exact"], abs=0.1)
    assert all(p["exact"] == 0 and p["estimate"] == 0 for p in ex["pairs"][1:])
    assert ml_models_docs.lsh_candidate_probability(ex["threshold"], 16, 8) == pytest.approx(1 - (1 - 1 / 16) ** 16)
    ps = [r["p"] for r in ex["curve"]]
    assert ps == sorted(ps)


def test_mixture_spends_the_budget_and_exact_match_is_a_power_of_per_token_accuracy():
    ex = ml_models_docs.pretraining_example()
    assert sum(m["tokens"] for m in ex["mixture"]) == pytest.approx(1.4e12)
    assert ex["mixture"][-1]["epochs"] == pytest.approx(3.5)
    for row in ex["emergence"]:
        assert row["exact"] == pytest.approx(row["per_token"] ** 10)


def test_centered_cosine_finds_the_two_taste_groups_and_neighbours_predict_from_them():
    ex = ml_models_docs.collab_example()
    sim = ex["similarity"]
    for u in range(5):
        assert sim[u][u] == pytest.approx(1)
        for v in range(5):
            assert sim[u][v] == pytest.approx(sim[v][u])
    assert sim[0][1] > 0.9 and sim[0][3] < -0.9
    assert sim[2][4] == pytest.approx(-1)
    ben = ex["targets"][0]["neighbour"]
    assert [v for _, v in ben["neighbours"]] == [0, 4]
    assert ben["prediction"] == pytest.approx(2.75 + 1.25)


def test_baseline_biases_sum_to_the_ratings_and_ignore_interaction():
    ex = ml_models_docs.collab_example()
    b = ex["baseline"]
    assert b["mu"] == pytest.approx(58 / 20)
    assert ex["user_means"] == pytest.approx([b["mu"] + x for x in b["user_bias"]])
    assert ex["heldout_rmse"]["baseline"] > ex["heldout_rmse"]["global"]
    assert ex["cold_order"][0] == 0 and ex["cold_order"][-1] == 4


def test_als_fits_only_observed_entries_and_beats_zero_filled_nmf_on_held_out():
    ex = ml_models_docs.collab_example()
    objective = [h["objective"] for h in ex["als"]["history"]]
    assert all(b <= a + 1e-9 for a, b in zip(objective, objective[1:]))
    assert ex["als"]["history"][-1]["rmse"] < 0.3 < ex["als"]["history"][0]["rmse"]
    assert ex["als_params"] == 20 and ex["observed"] == 20 and ex["cells"] == 25
    assert ex["targets"][0]["als"] == pytest.approx(4.007, abs=1e-3)
    assert ex["heldout_rmse"]["als"] < ex["heldout_rmse"]["neighbour"] < ex["heldout_rmse"]["nmf"]
    for t in ex["targets"]:
        assert t["nmf"] < t["als"]
    assert all(x >= 0 for row in ex["nmf"]["w"] for x in row)
    assert all(x >= 0 for row in ex["nmf"]["h"] for x in row)


def test_als_row_solve_is_ridge_on_the_items_that_user_rated():
    e = ml_models_docs.COLLAB_EXAMPLE
    ex = ml_models_docs.collab_example()
    items = ex["als"]["items"]
    seen = [(i, r) for i, r in enumerate(e["ratings"][0]) if r is not None]
    a = [[sum(items[i][p] * items[i][q] for i, _ in seen) + (e["l2"] if p == q else 0)
          for q in range(2)] for p in range(2)]
    rhs = [sum(items[i][p] * r for i, r in seen) for p in range(2)]
    solved = ml_models_docs.solve_linear(a, rhs)
    assert solved == pytest.approx(
        ml_models_docs.ridge_coefficients([items[i] for i, _ in seen], [r for _, r in seen], e["l2"]))


def test_implicit_confidence_and_factor_table_size():
    ex = ml_models_docs.collab_example()
    assert [r["confidence"] for r in ex["implicit"]] == [1, 41, 121, 401]
    assert [r["preference"] for r in ex["implicit"]] == [0, 1, 1, 1]
    assert ex["scale_params"] == 70_400_000
    assert ex["scale_bytes"] == pytest.approx(281.6e6)
    assert ex["scale_cells"] / ex["scale_params"] > 1000


def test_accumulating_summed_losses_over_total_tokens_matches_the_full_batch():
    ex = ml_models_docs.accumulation_example()
    assert ex["full"]["tokens"] == sum(ex["lengths"]) == 24
    assert ex["exact"]["grad"] == pytest.approx(ex["full"]["grad"])
    assert ex["exact"]["loss"] == pytest.approx(ex["full"]["loss"])
    assert [m["tokens"] for m in ex["exact"]["micro"]] == [8, 4, 7, 5]
    assert ex["naive"]["grad"][0] != pytest.approx(ex["full"]["grad"][0], rel=1e-3)
    assert ex["unscaled"]["grad"] == pytest.approx([4 * g for g in ex["naive"]["grad"]])


def test_equal_token_micro_batches_make_the_naive_average_exact():
    params = ml_models_docs.GRAD_ACCUM_EXAMPLE["params"]
    seqs = [((1.0, 2.0), (2.0, 3.0)), ((3.0, 7.0), (0.5, 1.0)), ((2.0, 5.0), (1.0, 1.0))]
    full = ml_models_docs.ga_sum(params, seqs)
    naive = ml_models_docs.ga_accumulate(params, seqs, 1, "per_micro_mean")
    assert naive["grad"] == pytest.approx([g / full["tokens"] for g in full["grad"]])


def test_clipping_must_wait_for_the_last_micro_batch():
    ex = ml_models_docs.accumulation_example()
    clip = ex["clip"]
    assert not clip["after"]["clipped"]
    assert clip["after"]["grads"] == pytest.approx(list(ex["full"]["grad"]))
    assert [c["clipped"] for c in clip["per_micro"]] == [True, False, False, False]
    assert math.hypot(*clip["per_micro_grad"]) < clip["after"]["total_norm"]


def test_batch_norm_sees_micro_batch_statistics_and_updates_running_stats_k_times():
    bn = ml_models_docs.accumulation_example()["bn"]
    assert bn["full"] == {"mean": 3.0, "var": 3.5}
    assert [m["mean"] for m in bn["micro"]] == [2.0, 4.0, 2.0, 4.0]
    assert bn["running_once"][0] == pytest.approx(0.3)
    assert bn["effective_momentum"] == pytest.approx(1 - 0.9 ** 4)
    assert bn["running_micro"][0] > bn["running_once"][0]


def test_no_sync_cuts_all_reduce_traffic_by_the_accumulation_factor():
    ex = ml_models_docs.accumulation_example()
    every, once = ex["ddp_every"], ex["ddp_no_sync"]
    assert every["payload"] == pytest.approx(5.2e9)
    assert every["per_reduce"] == pytest.approx(2 * 7 / 8 * 5.2e9)
    assert every["total"] == pytest.approx(8 * once["total"])
    assert ex["global_batch"] == 256 and ex["global_tokens"] == 524_288


def test_latency_decode_is_memory_bound_and_batching_trades_latency_for_throughput():
    ex = ml_models_docs.latency_example()
    decode = ex["decode"]
    assert ex["kv_bytes_per_token"] == 131072
    assert all(step["bound"] == "memory" and step["fits"] for step in decode)
    assert all(step["intensity"] < ex["ridge"] for step in decode)
    assert decode[0]["itl_ms"] == pytest.approx(16e9 * 1000 / 3.35e12, rel=0.02)
    itls = [step["itl_ms"] for step in decode]
    rates = [step["tokens_per_s"] for step in decode]
    assert itls == sorted(itls) and rates == sorted(rates)
    assert rates[-1] > 40 * rates[0] and itls[-1] < 5 * itls[0]
    assert ex["max_batch"] == 238
    assert ml_models_docs.lt_decode_step(238, 2048)["fits"]
    assert not ml_models_docs.lt_decode_step(239, 2048)["fits"]


def test_latency_prefill_is_compute_bound_and_sets_time_to_first_token():
    ex = ml_models_docs.latency_example()
    prefill = ex["prefill"]
    assert prefill["bound"] == "compute"
    assert prefill["intensity"] > ex["ridge"]
    assert prefill["ms"] == pytest.approx(16.84, abs=0.01)
    expected = (prefill["ms"] + 255 * ex["decode"][0]["itl_ms"]) / 1000
    assert ex["single_request_s"] == pytest.approx(expected)


def test_latency_littles_law_fixed_point():
    ex = ml_models_docs.latency_example()
    stable = [row for row in ex["little"] if row["stable"]]
    assert [row["rate"] for row in stable] == [5, 10, 20]
    for row in stable:
        assert row["concurrency"] == pytest.approx(row["rate"] * row["latency_s"], rel=1e-6)
        assert row["concurrency"] <= ex["max_batch"]
    latencies = [row["latency_s"] for row in stable]
    assert latencies == sorted(latencies)
    assert 20 <= ex["max_stable_rate"] < 30
    assert not ml_models_docs.lt_little_fixed_point(ex["max_stable_rate"] + 1, 2048, 1024, 256, 238)["stable"]


def test_latency_queue_tail_grows_faster_than_the_mean():
    ex = ml_models_docs.latency_example()
    rows = ex["queue"]
    for row in rows:
        assert row["mean_ms"] == pytest.approx(row["theory_mean_ms"], rel=0.12)
        assert row["p99_ms"] > row["mean_ms"] > row["p50_ms"] >= 10
    p99 = [row["p99_ms"] for row in rows]
    assert p99 == sorted(p99)
    assert p99[-1] / p99[0] > rows[-1]["mean_ms"] / rows[0]["mean_ms"]
    assert ml_models_docs.lt_queue_latencies(10.0, 0.5, 50, 7) == ml_models_docs.lt_queue_latencies(10.0, 0.5, 50, 7)


def test_latency_fanout_tail():
    slow = {row["width"]: row["slow"] for row in ml_models_docs.latency_example()["fanout"]}
    assert slow[1] == pytest.approx(0.01)
    assert slow[10] == pytest.approx(0.0956, abs=1e-4)
    assert slow[100] == pytest.approx(0.634, abs=1e-3)


def test_latency_roofline_points_sit_under_the_roof():
    ex = ml_models_docs.latency_example()
    gpu = ex["example"]["gpu"]
    for point in ex["roofline"]:
        roof = min(gpu["flops"], gpu["bandwidth"] * point["intensity"]) / 1e12
        assert point["tflops"] == pytest.approx(roof, rel=1e-6), point["label"]
        assert 60 <= point["x"] <= 680 and 20 <= point["y"] <= 200
    assert ex["roofline"][-1]["label"] == "prefill"
    assert ex["roofline"][-1]["tflops"] == pytest.approx(989, rel=1e-6)


def test_online_stream_is_seeded_and_drifts():
    s = ml_models_docs.ONLINE_EXAMPLE["stream"]
    args = (s["n"], s["drift_at"], s["w_before"], s["w_after"], s["noise"], s["seed"])
    stream = ml_models_docs.ol_stream(*args)
    assert stream == ml_models_docs.ol_stream(*args)
    assert len(stream) == 400
    before = ml_models_docs.ol_least_squares_weight(stream[:200])
    after = ml_models_docs.ol_least_squares_weight(stream[200:])
    assert before == pytest.approx(2.0, abs=0.1)
    assert after == pytest.approx(-1.0, abs=0.1)


def test_online_prequential_predicts_before_it_updates():
    stream = [(1.0, 2.0), (0.5, 1.0)]
    run = ml_models_docs.ol_prequential(stream, 0.25)
    assert run["losses"][0] == pytest.approx(4.0)
    assert run["weights"][0] == pytest.approx(1.0)
    assert run["losses"][1] == pytest.approx(0.25)
    assert run["weights"][1] == pytest.approx(1.125)
    frozen = ml_models_docs.ol_prequential(stream, 0.25, w=2.0, frozen=True)
    assert frozen["weights"] == [2.0, 2.0] and frozen["losses"] == [0.0, 0.0]


def test_online_constant_step_tracks_drift_and_decaying_step_does_not():
    ex = ml_models_docs.online_example()
    windows = ex["windows"]
    before, after = slice(1, 4), slice(5, 8)
    assert max(windows["frozen"][before]) < 0.15
    assert min(windows["frozen"][after]) > 2.0
    assert max(windows["constant"][after]) < 0.15
    assert min(windows["decay"][after]) > 1.0
    assert ex["weights_at"]["constant"][250] < -0.5
    assert ex["weights_at"]["decay"][400] > 0.5
    first = ex["first_steps"][0]
    assert first["w_after"] == pytest.approx(-0.1 * 2 * (0.0 - first["y"]) * first["x"])


def test_online_regret_is_sublinear():
    rows = ml_models_docs.online_example()["regret"]
    per_step = [row["per_step"] for row in rows]
    assert per_step == sorted(per_step, reverse=True)
    assert rows[-1]["per_step"] < 0.05
    for row in rows:
        assert row["regret"] == pytest.approx(row["learner_loss"] - row["best_loss"])
        assert row["regret"] > 0


def test_online_bandit_policies_rank_as_expected():
    ex = ml_models_docs.online_example()
    final = {row["policy"]: row["regret"][1000] for row in ex["bandit_rows"]}
    assert final["thompson"] < final["epsilon"] < final["ucb"] < final["greedy"]
    shares = {row["policy"]: row["best_share"] for row in ex["bandit_rows"]}
    assert shares["thompson"] > 0.8 and shares["greedy"] < 0.6
    assert ex["epsilon_floor"] == pytest.approx(0.1 * (0.30 + 0.10) / 3)
    for points in ex["bandit_points"].values():
        assert all(60 <= x <= 660 and 30 <= y <= 200 for x, y in points)


def test_online_ucb_trace_matches_ucb1():
    trace = ml_models_docs.online_example()["ucb_trace"]
    assert [row["arm"] for row in trace[:3]] == [0, 1, 2]
    for row in trace[3:]:
        scores = row["ucb"]
        assert row["arm"] == max(range(3), key=lambda a: scores[a])
        for a in range(3):
            mean = row["successes"][a] / row["counts"][a]
            assert scores[a] == pytest.approx(mean + math.sqrt(2 * math.log(row["t"]) / row["counts"][a]))


def test_online_bandit_runs_share_rewards_across_policies():
    a = ml_models_docs.ol_bandit_run("greedy", [0.2, 0.8], 50, 3, 0.1)
    b = ml_models_docs.ol_bandit_run("greedy", [0.2, 0.8], 50, 3, 0.1)
    assert a == b
    assert sum(a["counts"]) == 50


def test_uncertainty_epistemic_grows_outside_the_training_range():
    probes = {row["x"]: row for row in ml_models_docs.uncertainty_example()["probes"]}
    inside = [probes[x] for x in (-2.5, -1.0, 0.5)]
    assert all(row["aleatoric"] > 10 * row["epistemic"] for row in inside)
    assert probes[3.0]["epistemic"] > probes[2.0]["epistemic"] > 20 * probes[0.5]["epistemic"]
    for row in probes.values():
        assert row["total"] == pytest.approx(row["aleatoric"] + row["epistemic"])
    data = ml_models_docs.UNCERTAINTY_EXAMPLE["data"]
    for x in (-2.5, 0.5):
        assert math.sqrt(probes[x]["aleatoric"]) == pytest.approx(ml_models_docs.unc_noise_sd(x, data), rel=0.15)


def test_uncertainty_bootstrap_ci_brackets_the_mean_and_matches_the_normal_interval():
    boot = ml_models_docs.uncertainty_example()["bootstrap"]
    assert boot["lo"] < boot["mean"] < boot["hi"]
    assert boot["boot_se"] == pytest.approx(boot["se"], rel=0.1)
    assert boot["lo"] == pytest.approx(boot["normal_lo"], abs=0.01)
    assert boot["hi"] == pytest.approx(boot["normal_hi"], abs=0.01)


def test_uncertainty_dropout_samples_are_scaled_and_unbiased():
    e = ml_models_docs.UNCERTAINTY_EXAMPLE["dropout"]
    ex = ml_models_docs.uncertainty_example()
    for shown in ex["dropout_shown"]:
        expected = sum(w * h * m for w, h, m in zip(e["weights"], e["hidden"], shown["mask"])) / (1 - e["p"])
        assert shown["output"] == pytest.approx(expected)
    final = ex["mc"][-1]
    assert final["mean"] == pytest.approx(ex["dropout_deterministic"], abs=3 * ex["dropout_sd"] / math.sqrt(final["samples"]))
    assert final["sd"] == pytest.approx(ex["dropout_sd"], rel=0.05)


def test_uncertainty_conformal_quantile_uses_the_corrected_rank():
    assert ml_models_docs.unc_conformal_rank(9, 0.2) == 8
    assert ml_models_docs.unc_conformal_rank(200, 0.1) == 181
    assert ml_models_docs.unc_conformal_q([0.3, 0.1, 0.2], 0.1) == math.inf
    ex = ml_models_docs.uncertainty_example()
    assert ex["small_q"] == ex["small_sorted"][7]
    assert ex["guarantee_hi"] == pytest.approx(181 / 201)


def test_uncertainty_conformal_coverage_is_marginal_not_conditional():
    ex = ml_models_docs.uncertainty_example()
    assert ex["coverage"]["all"] == pytest.approx(0.9, abs=0.02)
    assert ex["coverage"]["left"] > 0.95 and ex["coverage"]["right"] < 0.85
    normalized = ex["coverage_normalized"]
    assert abs(normalized["left"] - normalized["right"]) < ex["coverage"]["left"] - ex["coverage"]["right"]
    assert ex["repeat_mean"] == pytest.approx(ex["guarantee_hi"], abs=3 * ex["repeat_sd"] / math.sqrt(200))
    assert sum(ex["histogram"]) == ml_models_docs.UNCERTAINTY_EXAMPLE["conformal"]["repeats"]


def test_uncertainty_plot_points_stay_inside_the_frame():
    ex = ml_models_docs.uncertainty_example()
    for points in [ex["points"], ex["truth_points"], ex["band"], *ex["member_points"]]:
        assert all(60 <= x <= 660 and 30 <= y <= 200 for x, y in points)


def test_vit_shape_walk_turns_an_image_into_197_tokens_of_width_768():
    ex = ml_models_docs.vit_example()
    shapes = {row["stage"]: row["shape"] for row in ex["walk"]}
    assert ex["walk"][0]["shape"] == [8, 3, 224, 224]
    assert shapes["transpose(1, 2)"] == [8, 196, 768]
    assert shapes["prepend class token"] == [8, 197, 768]
    assert shapes["per-head attention scores"] == [8, 12, 197, 197]
    assert ex["walk"][-1]["shape"] == [8, 1000]


def test_vit_parameter_counts_match_the_published_models():
    totals = {m["config"]["name"]: m["total"] for m in ml_models_docs.vit_example()["models"]}
    assert totals["ViT-B/16"] == 86_567_656
    assert totals["ViT-B/32"] == 88_224_232
    assert totals["ViT-L/16"] == 304_326_632
    assert totals["ViT-H/14"] == 632_045_800
    params = ml_models_docs.vit_example()["params"]
    assert params["layer_total"] == 7_087_872
    assert params["parts"]["patch_embed"] == 3 * 16 * 16 * 768 + 768


def test_vit_strided_convolution_equals_a_linear_layer_on_flattened_patches():
    ex = ml_models_docs.vit_example()
    assert ex["conv_tokens"] == ex["linear"]
    assert ex["patches"][0] == [1, 2, 3, 4]
    assert len(ex["patches"]) == 4
    assert ex["overlap_side"] == 3


def test_vit_token_count_and_attention_cost_grow_with_resolution():
    rows = {(r["image"], r["patch"]): r for r in ml_models_docs.vit_example()["resolutions"]}
    assert rows[(224, 16)]["tokens"] == 197 and rows[(224, 16)]["relative"] == 1
    assert rows[(384, 16)]["tokens"] == 577
    assert rows[(224, 32)]["tokens"] == 50
    assert rows[(384, 16)]["scores"] == 577 ** 2


def test_unet_parameter_count_matches_stable_diffusion_v1():
    walk = ml_models_docs.unet_example()["walk"]
    assert walk["total"] == 859_520_964
    assert walk["total"] == sum(walk["parts"].values())
    assert walk["skips_left"] == 0


def test_unet_walk_has_twelve_skips_and_matching_up_blocks():
    walk = ml_models_docs.unet_example()["walk"]
    assert len(walk["down"]) == 12
    assert len(walk["up"]) == 12
    assert [r["side"] for r in walk["down"] if r["name"] == "Downsample"] == [32, 16, 8]
    assert walk["middle"] == {"side": 8, "channels": 1280}
    assert walk["up"][-1]["side"] == 64 and walk["up"][-1]["channels"] == 320
    assert all(r["in"] == r["skip"] + (walk["up"][i - 1]["channels"] if i else 1280) for i, r in enumerate(walk["up"]))


def test_unet_attention_runs_only_at_the_three_finer_resolutions():
    e = ml_models_docs.unet_example()
    assert e["attn_sides"] == [64, 32, 16]
    assert not any(r["attn"] for r in e["walk"]["up"] if r["side"] == 8)
    assert e["attention"][0]["self_scores"] == 4096 ** 2


def test_dit_parameter_counts_match_the_paper():
    dits = {d["name"]: d for d in ml_models_docs.unet_example()["dits"]}
    assert dits["DiT-XL/2"]["total"] == 674_834_720
    assert dits["DiT-XL/2"]["tokens"] == 256
    assert dits["DiT-XL/8"]["tokens"] == 16
    assert round(dits["DiT-S/2"]["total"] / 1e6) == 33
    assert round(dits["DiT-B/2"]["total"] / 1e6) == 130
    assert round(dits["DiT-L/2"]["total"] / 1e6) == 458


def test_timestep_embeddings_follow_each_convention():
    e = ml_models_docs.unet_example()
    zero = e["embeddings"][0]
    assert zero["ldm"] == [1.0] * 4 + [0.0] * 4
    assert zero["ddpm"] == [0.0] * 4 + [1.0] * 4
    one = e["embeddings"][1]
    assert one["ldm"][0] == math.cos(1) and one["ddpm"][0] == math.sin(1)
    assert e["frequencies"][-1] == math.exp(-math.log(10000) * 3 / 4)


def test_unet_group_norm_normalises_each_group_separately():
    gn = ml_models_docs.unet_example()["group_norm"]
    assert [s["mean"] for s in gn["stats"]] == [2.0, 12.0]
    assert [s["var"] for s in gn["stats"]] == [0.5, 2.0]
    assert gn["out"][1] == [0.0, 0.0]
    assert ml_models_docs.unet_example()["layer_norm_style"]["stats"][0]["mean"] == 7.0


def test_ft_model_params_match_llama_2_7b():
    assert ml_models_docs.ft_example()["params"]["total"] == 6_738_415_616


def test_ft_lora_counts_match_the_published_peft_totals():
    e = ml_models_docs.ft_example()
    assert e["main"] == 4_194_304
    assert e["params"]["total"] + e["main"] == 6_742_609_920
    grid = {row["target"]: row["counts"] for row in e["grid"]}
    assert grid["all linear"][e["example"]["ranks"].index(8)] == 19_988_480
    assert all(b == 2 * a for a, b in zip(grid["q, v"], grid["q, k, v, o"]))


def test_ft_lora_toy_merges_to_the_same_output():
    toy = ml_models_docs.ft_example()["toy"]
    assert toy["unmerged"] == toy["merged_out"] == [3.0, 1.0, 0.0, 6.0]
    assert toy["delta_rank"] == 1
    assert (toy["full_count"], toy["lora_count"]) == (12, 7)


def test_ft_memory_orders_full_lora_qlora():
    gib = [row["gib"] for row in ml_models_docs.ft_example()["memory"]]
    assert gib[0] > gib[1] > gib[2]
    assert round(gib[0]) == 100


def test_ft_masked_loss_ignores_prompt_tokens():
    sft = ml_models_docs.ft_example()["sft"]
    assert sft["labels"][:5] == [-100] * 5
    assert len(sft["terms"]) == 2
    assert math.isclose(sft["loss"], -(math.log(0.4) + math.log(0.8)) / 2)
    assert len(sft["nll"]) == 7
    assert math.isclose(sft["unmasked"], sum(sft["nll"]) / 7)


def test_ft_forgetting_trades_task_a_for_task_b():
    rows = ml_models_docs.ft_example()["forgetting"]
    assert rows[0]["w"] == 3.0 and rows[0]["loss_a"] == 4.0
    assert [r["loss_a"] < q["loss_a"] for q, r in zip(rows, rows[1:])] == [True] * 3
    assert rows[2]["loss_a"] == rows[2]["loss_b"] == 1.0


def test_tt_query_tower_matches_embedding_bag_mean():
    ex = ml_models_docs.tt_example()
    assert ex["pooled"] == [[1.5, -0.5], [-0.5, 1.5], [1.5, 0.5], [-1.0, 1.0]]
    for v in ex["queries"] + ex["items"]:
        assert math.isclose(ml_models_docs.vector_norm(v), 1.0)


def test_tt_in_batch_uses_the_batch_positives_as_columns():
    ex = ml_models_docs.tt_example()
    tau = ex["example"]["temperature"]
    for r, row in enumerate(ex["plain"]["rows"]):
        assert len(row["logits"]) == 4
        assert math.isclose(sum(row["probs"]), 1.0)
        assert math.isclose(row["loss"], -math.log(row["probs"][r]))
        for k, logit in enumerate(row["logits"]):
            assert math.isclose(logit, ex["cosines"][r][k] / tau)
    assert math.isclose(ex["plain"]["loss"], 0.3788951774317155)
    assert ex["full"]["loss"] > ex["plain"]["loss"]


def test_tt_logq_correction_subtracts_log_frequency():
    ex = ml_models_docs.tt_example()
    freq = ex["example"]["frequencies"]
    positives = ex["example"]["positives"]
    for plain, corrected in zip(ex["plain"]["rows"], ex["corrected"]["rows"]):
        for k, j in enumerate(positives):
            assert math.isclose(corrected["logits"][k], plain["logits"][k] - math.log(freq[j]))
    assert ex["corrected"]["rows"][0]["loss"] < ex["plain"]["rows"][0]["loss"]
    assert ex["corrected"]["rows"][2]["loss"] > ex["plain"]["rows"][2]["loss"]


def test_tt_hard_negative_raises_the_loss():
    ex = ml_models_docs.tt_example()
    hard = ex["hard"]
    assert hard["hard_prob"] > 5 * hard["easy_mean_prob"]
    assert hard["loss_after"] > 3 * hard["loss_before"]
    assert math.isclose(hard["loss_after"], ex["full"]["rows"][2]["loss"])


def test_tt_serving_costs():
    s = ml_models_docs.tt_example()["serving"]
    assert s["table_params"] == 1_920_000_000
    assert s["mlp_params"] == 41_152
    assert s["flat_macs"] == 640_000_000
    assert s["ivf_scanned"] == 78_125
    assert s["rank_all_macs"] // s["rank_candidates_macs"] == 10_000


def test_dt_ring_allreduce_sums_every_rank():
    ring = ml_models_docs.dt_example()["ring"]
    assert len(ring["steps"]) == 6
    assert all(row == [28.0, 32.0, 36.0, 40.0] for row in ring["sum"])
    assert all(row == [7.0, 8.0, 9.0, 10.0] for row in ring["mean"])
    assert ring["sent_per_rank"] == 6
    assert ring["naive_root_traffic"] == 24
    after_rs = ring["steps"][2]["state"]
    for r, c in enumerate(ring["owned"]):
        assert after_rs[r][c] == [28.0, 32.0, 36.0, 40.0][c:c + 1]


def test_dt_ring_rejects_uneven_chunks():
    with pytest.raises(ValueError):
        ml_models_docs.dt_ring_allreduce([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def test_dt_zero_memory_matches_the_paper():
    check = ml_models_docs.dt_example()["zero_check"]
    assert math.isclose(check["ddp"] / 1e9, 120.0)
    assert round(check["zero1"] / 1e9, 1) == 31.4
    assert round(check["zero2"] / 1e9, 1) == 16.6
    assert round(check["zero3"] / 1e9, 1) == 1.9


def test_dt_llama_memory_and_fit():
    ex = ml_models_docs.dt_example()
    assert ex["params"] == 6_738_415_616
    assert ex["memory"]["ddp"] == 16 * 6_738_415_616
    assert ex["memory"]["zero3"] == 2 * 6_738_415_616
    assert ex["memory_fits"] == {"ddp": False, "zero1": True, "zero2": True, "zero3": True}
    assert ex["memory"]["ddp"] > ex["memory"]["zero1"] > ex["memory"]["zero2"] > ex["memory"]["zero3"]


def test_dt_communication_volumes():
    ex = ml_models_docs.dt_example()
    comm = ex["comm"]
    assert math.isclose(comm["ddp"], comm["zero2"])
    assert math.isclose(comm["zero3"], 1.5 * comm["ddp"])
    assert math.isclose(comm["ddp"], 2 * 7 / 8 * 2 * 6_738_415_616)
    assert ex["bucket_params"] == 6_553_600
    assert ex["buckets"] == 1029


def test_dt_tensor_parallel_split_is_exact():
    tp = ml_models_docs.dt_example()["tp"]
    assert tp["summed"] == tp["full"]
    assert tp["full"] == [[2.0, -1.5], [4.0, -1.25]]
    assert tp["row_split_wrong"] != tp["full"]
    assert tp["row_split_pre"][0][2] < 0


def test_dt_tensor_parallel_activation_traffic():
    ex = ml_models_docs.dt_example()
    tc = ex["tp_comm"]
    assert tc["tensor"] == 4096 * 4096 * 2
    assert tc["reduces"] == 128
    assert math.isclose(tc["total"], 128 * 2 * 7 / 8 * tc["tensor"])


def test_dt_pipeline_schedules():
    ex = ml_models_docs.dt_example()
    for key, m in (("gpipe", 4), ("one_f_one_b", 4), ("gpipe_8", 8), ("one_f_one_b_8", 8)):
        sched = ex[key]
        assert sched["total"] == 2 * (m + 3)
        assert math.isclose(sched["bubble"], ml_models_docs.dt_bubble_fraction(4, m))
    assert ex["gpipe_8"]["peak_in_flight"] == [8, 8, 8, 8]
    assert ex["one_f_one_b_8"]["peak_in_flight"] == [4, 3, 2, 1]
    assert [round(b["fraction"], 3) for b in ex["bubbles"]] == [0.75, 0.429, 0.273, 0.158, 0.086]


def test_md_psi_matches_the_continuous_limit():
    ex = ml_models_docs.md_example()
    assert all(math.isclose(s, 0.1) for s in ex["psi_shares"]["reference"])
    assert math.isclose(sum(ex["psi_shares"]["current"]), 1.0)
    assert 0.08 < ex["psi"]["psi"] < ex["psi_continuous"] == pytest.approx(0.09)
    assert ex["psi"]["terms"][0] > ex["psi"]["terms"][5]


def test_md_psi_empty_bin_needs_a_floor():
    ex = ml_models_docs.md_example()
    assert ex["empty"]["psi"] == math.inf
    assert math.isfinite(ex["empty_eps"]["psi"]) and ex["empty_eps"]["psi"] > 2


def test_md_ks_statistic_and_critical_value():
    ex = ml_models_docs.md_example()
    ks = ex["ks"]
    assert abs(ks["d"] - ex["ks_analytic"]) < 1e-3
    assert math.isclose(ks["critical"], 1.3581015157406195 * math.sqrt(2 / 2000))
    assert ks["reject"] and ks["p"] < 1e-10
    large = ex["ks_large"]
    assert large["reject"] and large["p"] < 0.01
    assert ex["psi_large"] < 0.01


def test_md_ks_identical_samples():
    same = ml_models_docs.md_sample(0.0, 100)
    ks = ml_models_docs.md_ks_test(same, list(same), 0.05)
    assert ks["d"] == 0 and not ks["reject"] and ks["p"] == 1.0


def test_md_weeks_and_decisions():
    weeks = ml_models_docs.md_example()["weeks"]
    assert [w["decision"] for w in weeks] == [
        "ok", "ok", "investigate inputs", "recalibrate or retrain", "recalibrate or retrain",
    ]
    covariate = weeks[2]
    assert abs(covariate["gap"]) < 1e-12 and covariate["max_reliability_gap"] < 1e-12
    assert covariate["brier"] > weeks[0]["brier"]
    for w in weeks[3:]:
        assert w["psi"] == 0
        assert w["brier"] > w["oracle_brier"]
    assert round(weeks[3]["gap"], 3) == 0.049


def test_md_platt_recovers_the_new_relationship():
    weeks = ml_models_docs.md_example()["weeks"]
    for w, (a, b) in zip(weeks[3:], [(0.5, -0.5), (1.0, 0.5)]):
        assert math.isclose(w["platt"]["a"], a, abs_tol=1e-6)
        assert math.isclose(w["platt"]["b"], b, abs_tol=1e-6)
        assert math.isclose(w["platt"]["brier"], w["oracle_brier"], rel_tol=1e-6)


def test_md_prior_shift_and_delayed_labels():
    ex = ml_models_docs.md_example()
    assert math.isclose(ex["label_shift"][1]["corrected"], 27 / 34)
    assert all(r["corrected"] > r["score"] for r in ex["label_shift"])
    assert math.isclose(ml_models_docs.md_prior_shift(0.3, 0.2, 0.2), 0.3)
    maturity = ex["maturity"]
    assert maturity[-1]["observed"] == pytest.approx(ex["weeks"][0]["observed_rate"])
    assert maturity[0]["observed"] < maturity[-1]["observed"] / 4


def test_mm_clip_loss_is_symmetric_cross_entropy_on_scaled_cosines():
    ex = ml_models_docs.mm_example()
    clip = ex["clip"]
    n = len(ex["example"]["images"])
    assert clip["loss"] == pytest.approx((sum(clip["image_loss"]) + sum(clip["text_loss"])) / (2 * n))
    assert all(-1 <= c <= 1 for row in ex["cosines"] for c in row)
    assert all(math.isclose(ex["cosines"][i][i], max(row), rel_tol=0) for i, row in enumerate(ex["cosines"]))
    assert clip["image_top1"] == clip["text_top1"] == 1.0
    losses = [r["loss"] for r in ex["sweep"]]
    assert losses == sorted(losses, reverse=True)
    assert losses[0] < ex["chance"]
    zero = ml_models_docs.mm_clip_loss([[0.0] * n for _ in range(n)])
    assert zero["loss"] == pytest.approx(math.log(n))


def test_mm_clip_gradient_matches_finite_differences():
    ex = ml_models_docs.mm_example()
    e = ex["example"]
    logits = ml_models_docs.mm_clip_logits(e["images"], e["texts"], ex["init_scale"])
    grad = ml_models_docs.mm_clip_loss(logits)["grad"]
    h = 1e-6
    for i in range(len(logits)):
        for j in range(len(logits)):
            bumped = [row[:] for row in logits]
            bumped[i][j] += h
            numeric = (ml_models_docs.mm_clip_loss(bumped)["loss"] - ml_models_docs.mm_clip_loss(logits)["loss"]) / h
            assert numeric == pytest.approx(grad[i][j], abs=1e-5)
    assert all(grad[i][i] < 0 for i in range(len(grad)))
    assert sum(sum(row) for row in grad) == pytest.approx(0, abs=1e-12)


def test_mm_zero_shot_picks_the_closest_class_and_ensembles_prompts():
    zs = ml_models_docs.mm_example()["zero_shot"]
    assert sum(zs["single"]) == pytest.approx(1)
    assert sum(zs["ensemble"]) == pytest.approx(1)
    best = max(range(3), key=lambda k: zs["classes"][k]["single"])
    assert best == max(range(3), key=lambda k: zs["single"][k]) == 1
    assert zs["ensemble"][2] > zs["single"][2]


def test_mm_vision_tokens_and_fusion_costs():
    ex = ml_models_docs.mm_example()
    v = ex["vision"]
    assert (v["side"], v["per_tile"], v["tiled"], v["pooled"]) == (24, 576, 2880, 144)
    plain, tiled, latents = ex["fusion"]
    assert plain["kv_per_token"] == 2 * 32 * 4096 * 2 == 524288
    assert plain["concat_scores"] == 32 * 676 ** 2
    assert plain["xattn_scores"] == 32 * 100 ** 2 + 8 * 100 * 576
    assert plain["concat_kv"] == 4 * plain["xattn_kv"]
    assert tiled["concat_kv"] == 5 * plain["concat_kv"]
    assert latents["concat_scores"] < plain["xattn_scores"] * 2


def test_mm_gate_starts_closed_and_audio_token_rates():
    gates = ml_models_docs.mm_example()["gates"]
    assert gates["rows"][0]["out"] == gates["x"]
    assert [r["gate"] for r in gates["rows"]] == sorted(r["gate"] for r in gates["rows"])
    assert all(r["gate"] < 1 for r in gates["rows"])
    audio = ml_models_docs.mm_example()["audio"]
    assert (audio["mel_frames"], audio["encoder_tokens"], audio["encoder_rate"]) == (3000, 1500, 50)
    assert audio["codec_rate"] == 75 and audio["bits"] == 10
    assert [r["codebooks"] for r in audio["codec"]] == [2, 4, 8, 16, 32]
    assert all(r["per_second"] * audio["bits"] == r["kbps"] * 1000 for r in audio["codec"])


def test_pca_components_are_covariance_eigenvectors_and_variance_is_s_squared():
    ex = ml_models_docs.pca_example()
    model = ex["model"]
    assert model["explained_variance"] == pytest.approx(ex["eigenvalues"])
    assert model["explained_variance"] == pytest.approx([s * s / (ex["n"] - 1) for s in model["singular_values"]])
    assert sum(model["ratio"]) == pytest.approx(1.0)
    assert model["total_variance"] == pytest.approx(ex["cov"][0][0] + ex["cov"][1][1])
    for value, component in zip(model["explained_variance"], model["components"]):
        image = [ml_models_docs.dot_product(row, component) for row in ex["cov"]]
        assert image == pytest.approx([value * c for c in component])
        assert max(component, key=abs) > 0
    assert ml_models_docs.dot_product(*model["components"]) == pytest.approx(0, abs=1e-12)
    assert ex["power"][-1]["vector"] == pytest.approx(model["components"][0], abs=1e-5)
    assert ex["power"][-1]["value"] == pytest.approx(model["explained_variance"][0])


def test_pca_scores_whitening_and_reconstruction():
    ex = ml_models_docs.pca_example()
    model = ex["model"]
    for point, score in zip(ex["example"]["points"], model["scores"]):
        assert ml_models_docs.pca_transform(model, point) == pytest.approx(score)
        assert ml_models_docs.pca_inverse(model, score) == pytest.approx(point)
    assert ex["whitened_cov"] == [pytest.approx(row, abs=1e-12) for row in ([1, 0], [0, 1])]
    assert ex["one_error"] == pytest.approx(model["singular_values"][1] ** 2)
    assert ex["query_scores"] == pytest.approx([-1.029366, 0.754631], abs=1e-6)
    assert ex["query_back"] == pytest.approx([2.463542, 2.530736], abs=1e-6)


def test_pca_scale_dominates_until_features_are_standardized():
    ex = ml_models_docs.pca_example()
    assert ex["fruit_raw"]["ratio"][0] > 0.99999
    assert abs(ex["fruit_raw"]["components"][0][0]) > 0.9999
    assert ex["fruit_scaled"]["ratio"][0] == pytest.approx(0.602874, abs=1e-6)
    assert [abs(c) for c in ex["fruit_scaled"]["components"][0]] == pytest.approx([2 ** -0.5] * 2)


def test_pca_survey_keeps_two_components_and_errors_are_dropped_variance():
    ex = ml_models_docs.pca_example()
    survey = ex["survey"]
    assert len(ex["survey_rows"]) == 30 and len(ex["survey_rows"][0]) == 6
    assert survey["explained_variance"] == pytest.approx(ex["survey_eigenvalues"])
    assert ex["survey_keep"] == 2
    assert survey["cumulative"][0] < 0.9 < survey["cumulative"][1]
    assert ml_models_docs.pca_n_components_for([0.5, 0.9, 1.0], 0.9) == 3
    for row in ex["survey_errors"]:
        assert row["error"] == pytest.approx(row["dropped"], abs=1e-9)
    errors = [row["error"] for row in ex["survey_errors"]]
    assert errors == sorted(errors, reverse=True)
    assert ex["survey_errors"][2]["noise_variance"] == pytest.approx(0.072292, abs=1e-6)


def test_pca_folds_an_arc_and_t_kernel_has_heavier_tails():
    ex = ml_models_docs.pca_example()
    fold = ex["arc"]["fold"]
    assert fold["gap"] == pytest.approx(0, abs=1e-9)
    assert fold["along"] == pytest.approx(math.pi)
    rows = ex["kernels"]
    assert rows[0]["gaussian"] == rows[0]["student"] == 1
    assert all(a["student"] >= b["student"] for a, b in zip(rows, rows[1:]))
    assert rows[-1]["ratio"] > 1000


def test_moe_top_k_gates_renormalize_over_the_chosen_experts():
    ex = ml_models_docs.moe_example()
    for full, raw in zip(ex["top2"], ex["top2_raw"]):
        assert sum(full["gates"]) == pytest.approx(1)
        assert full["experts"] == raw["experts"]
        assert full["experts"][0] == max(range(4), key=lambda e: full["logits"][e])
        picked = [full["probs"][e] for e in full["experts"]]
        assert full["gates"] == pytest.approx([p / sum(picked) for p in picked])
        assert raw["gates"] == pytest.approx(picked)
    assert ex["top2"][0]["experts"] == [0, 3]
    assert ex["top2"][0]["gates"][0] == pytest.approx(0.842, abs=1e-3)
    assert [r["experts"][0] for r in ex["top1"]] == ex["first"]
    assert sum(r["gates"][0] for r in ex["top1"]) < len(ex["top1"])


def test_moe_load_balance_loss_is_one_when_uniform_and_e_when_collapsed():
    ex = ml_models_docs.moe_example()
    assert ex["balance_uniform"] == pytest.approx(1)
    assert ex["balance_collapsed"] == pytest.approx(ex["num_experts"])
    assert ex["counts"] == [5, 1, 1, 1]
    assert sum(ex["balance"]["fraction"]) == pytest.approx(1)
    assert sum(ex["balance"]["mean_prob"]) == pytest.approx(1)
    assert ex["balance"]["loss"] == pytest.approx(1.288, abs=1e-3)
    assert ex["z_loss"] > 0


def test_moe_capacity_drops_late_tokens_on_the_busy_expert():
    ex = ml_models_docs.moe_example()
    rows = {row["factor"]: row for row in ex["capacity"]}
    assert rows[1.0]["capacity"] == rows[1.25]["capacity"] == 2
    assert rows[1.0]["dropped"] == [3, 5, 7]
    assert rows[2.0]["dropped"] == [7]
    for row in ex["capacity"]:
        assert sorted(row["kept"] + row["dropped"]) == list(range(8))
        assert max(row["load"]) <= row["capacity"]
        assert all(ex["first"][t] == 0 for t in row["dropped"])
    assert ml_models_docs.moe_capacity([0, 1, 2, 3], 4, 1.0)["dropped"] == []


def test_moe_output_mixes_expert_outputs_by_gate():
    ex = ml_models_docs.moe_example()
    route = ex["top2"][ex["sample"]]
    out = ex["sample_top2"]
    for i, value in enumerate(out["combined"]):
        assert value == pytest.approx(sum(g * out["outputs"][e][i] for e, g in zip(route["experts"], route["gates"])))
    assert ex["sample_top1"]["combined"] == pytest.approx([ex["top1"][ex["sample"]]["gates"][0] * v for v in ex["sample_top1"]["outputs"][0]])


def test_moe_mixtral_parameter_counts_match_the_paper():
    counts = ml_models_docs.moe_example()["mixtral"]
    assert counts["total"] / 1e9 == pytest.approx(46.7, abs=0.05)
    assert counts["active"] / 1e9 == pytest.approx(12.9, abs=0.05)
    assert counts["expert"] == 3 * 4096 * 14336
    assert 0.96 < counts["expert_share"] < 0.97


def test_flow_lognormal_change_of_variables_matches_closed_form_and_integrates_to_one():
    ex = ml_models_docs.flow_example()
    ln, cfg = ex["lognormal"], ex["example"]["lognormal"]
    y, mu, s = cfg["y"], cfg["loc"], cfg["scale"]
    closed = -math.log(y * s * math.sqrt(2 * math.pi)) - (math.log(y) - mu) ** 2 / (2 * s * s)
    assert ln["log_prob"] == pytest.approx(closed)
    assert ln["log_prob"] == pytest.approx(ln["base"] + ln["affine"] + ln["exp"])
    assert ln["mass"] == pytest.approx(1.0, abs=1e-6)


def test_flow_coupling_inverts_and_log_det_matches_finite_differences():
    c = ml_models_docs.flow_example()["coupling"]
    x = ml_models_docs.FLOW_EXAMPLE["coupling"]["x"]
    assert c["inverse"] == pytest.approx(x)
    assert c["jacobian"][0] == pytest.approx([1.0, 0.0], abs=1e-8)
    assert c["det"] == pytest.approx(c["exp_log_det"], rel=1e-6)
    assert c["y"][0] == x[0]


def test_flow_gaussian_path_ode_converges_to_the_exact_transport():
    rows = ml_models_docs.flow_example()["gaussian"]
    g = ml_models_docs.FLOW_EXAMPLE["gaussian"]
    assert rows[0]["x"] == pytest.approx(g["mean"])
    errors = [abs(r["x"] - r["exact_x"]) for r in rows]
    assert errors == sorted(errors, reverse=True)
    assert errors[-1] < 0.02
    assert abs(rows[-1]["log_prob"] - rows[-1]["exact_log_prob"]) < 0.02
    fine = ml_models_docs.gaussian_flow_solve(g["z"], g["mean"], g["std"], 20000)
    assert fine["x"] == pytest.approx(fine["exact_x"], abs=1e-4)
    assert fine["log_prob"] == pytest.approx(fine["exact_log_prob"], abs=1e-4)


def test_flow_two_point_velocity_is_denoiser_minus_noise_and_matches_diffusion():
    ex = ml_models_docs.flow_example()
    p = ex["point"]
    assert p["x1_hat"] == pytest.approx(math.tanh(1.0))
    assert p["velocity"] == pytest.approx(p["x1_hat"] - p["x0_hat"])
    assert p["velocity"] == pytest.approx(0.5232, abs=1e-4)
    assert ex["vp"]["alpha_bar"] == pytest.approx(0.5)
    assert ex["vp"]["x0_hat"] == pytest.approx(p["x1_hat"])
    rng = random.Random(3)
    x, t = 0.5, 0.5
    samples = []
    while len(samples) < 20000:
        x0, x1 = rng.gauss(0.0, 1.0), rng.choice([-1.0, 1.0])
        if abs((1 - t) * x0 + t * x1 - x) < 0.02:
            samples.append(x1 - x0)
    mean = sum(samples) / len(samples)
    assert mean == pytest.approx(p["velocity"], abs=0.05)
    assert sum((v - mean) ** 2 for v in samples) / len(samples) == pytest.approx(p["residual"], abs=0.1)


def test_flow_samplers_one_step_collapses_and_more_steps_reach_the_data():
    rows = {r["steps"]: r for r in ml_models_docs.flow_example()["samplers"]}
    assert rows[1]["euler"]["mean_abs"] == 0.0
    for n in (2, 4, 8, 16, 64, 256):
        assert rows[n]["euler"]["plus"] == 0.5
    assert rows[4]["heun"]["max_error"] < rows[4]["euler"]["max_error"]
    assert rows[16]["euler"]["max_error"] < 1e-9
    assert rows[8]["heun_evals"] == 15


def test_flow_rectified_lines_cross_but_reflow_is_straight():
    ex = ml_models_docs.flow_example()
    t, x = ex["crossing"]
    assert t == pytest.approx(3 / 7)
    assert x == pytest.approx(-1 / 7)
    assert ex["mean_defect"] > 0.1
    by_start = {p["start"]: p for p in ex["paths"]}
    assert by_start[0.1]["length"] > abs(by_start[0.1]["displacement"])
    assert ex["reflow_monotone"]
    assert all(r["max_error"] < 1e-12 for r in ex["reflow"])
    line = ml_models_docs.path_straightness([0.0, 0.25, 0.5, 0.75, 1.0])
    assert line["defect"] == pytest.approx(0.0)


def test_po_bradley_terry_fit_is_a_shift_invariant_maximum_likelihood():
    ex = ml_models_docs.po_example()
    rewards = ex["rewards"]
    assert sum(rewards) == pytest.approx(0, abs=1e-9)
    assert ex["shifted_nll"] == pytest.approx(ex["nll"])
    assert ex["nll"] < ex["zero_nll"] == pytest.approx(math.log(2))
    wins = ex["example"]["wins"]
    for i in range(ex["n"]):
        expected = sum(ex["comparisons"][i][j] * ex["fitted"][i][j] for j in range(ex["n"]) if j != i)
        assert expected == pytest.approx(sum(wins[i]), abs=1e-6)
    for k in range(ex["n"]):
        bumped = list(rewards)
        bumped[k] += 1e-3
        assert ml_models_docs.bradley_terry_nll(bumped, wins) > ex["nll"]
    assert ex["proxy_top"] == 2 and ex["true_top"] == 1
    assert ex["rm_pair"]["loss"] == pytest.approx(-math.log(ex["rm_pair"]["p"]))


def test_po_kl_regularized_optimum_maximizes_the_rlhf_objective():
    ex = ml_models_docs.po_example()
    ref, rewards, beta = ex["example"]["reference"], ex["rewards"], ex["example"]["beta"]
    best = next(row for row in ex["sweep"] if row["beta"] == beta)
    assert best["policy"] == pytest.approx(ex["optimum"])
    rng = random.Random(0)
    for _ in range(200):
        logits = [math.log(p) + rng.gauss(0, 1) for p in ex["optimum"]]
        q = ml_models_docs.softmax_probs(logits)
        value = sum(a * r for a, r in zip(q, rewards)) - beta * ml_models_docs.categorical_kl(q, ref)
        assert value <= best["objective"] + 1e-12
    kls = [row["kl"] for row in ex["sweep"]]
    proxies = [row["proxy"] for row in ex["sweep"]]
    assert kls == sorted(kls) and proxies == sorted(proxies)


def test_po_proxy_reward_keeps_rising_while_true_reward_peaks_then_falls():
    ex = ml_models_docs.po_example()
    trues = [row["true"] for row in ex["sweep"]]
    peak = trues.index(max(trues))
    assert 0 < peak < len(trues) - 1
    assert trues[:peak + 1] == sorted(trues[:peak + 1])
    assert trues[peak:] == sorted(trues[peak:], reverse=True)
    assert trues[-1] < ex["reference_true"]
    assert ex["best"]["beta"] == ex["example"]["beta"]


def test_po_dpo_starts_at_log_two_and_converges_to_the_rlhf_optimum():
    ex = ml_models_docs.po_example()
    assert ex["dpo_start"]["loss"] == pytest.approx(math.log(2))
    assert ex["dpo_start"]["weight"] == pytest.approx(0.5)
    losses = [row["loss"] for row in ex["dpo"]]
    assert losses == sorted(losses, reverse=True)
    assert losses[-1] == pytest.approx(ex["nll"], abs=1e-6)
    assert ex["dpo_gap"] < 1e-4
    final = ex["dpo"][-1]
    implicit = final["implicit"]
    for i in range(ex["n"]):
        for j in range(ex["n"]):
            assert implicit[i] - implicit[j] == pytest.approx(ex["rewards"][i] - ex["rewards"][j], abs=1e-4)
    assert ex["dpo_after"]["loss"] == pytest.approx(ex["rm_pair"]["loss"], abs=1e-4)


def test_po_dpo_gradient_matches_finite_differences():
    ex = ml_models_docs.po_example()
    ref, wins, beta = ex["example"]["reference"], ex["example"]["wins"], ex["example"]["beta"]
    logits = [0.3, -0.2, 0.5, 0.1]
    grad = ml_models_docs.dpo_tabular_gradient(logits, ref, wins, beta)["grad"]
    h = 1e-6
    for k in range(4):
        up = list(logits)
        up[k] += h
        down = list(logits)
        down[k] -= h
        numeric = (ml_models_docs.dpo_tabular_gradient(up, ref, wins, beta)["loss"]
                   - ml_models_docs.dpo_tabular_gradient(down, ref, wins, beta)["loss"]) / (2 * h)
        assert grad[k] == pytest.approx(numeric, abs=1e-6)
    assert sum(grad) == pytest.approx(0, abs=1e-12)


def test_po_dpo_margin_grows_without_bound_on_a_unanimous_pair_while_ipo_stops():
    ex = ml_models_docs.po_example()
    rows = ex["unanimous"]
    dpo = [row["dpo"] for row in rows]
    assert dpo == sorted(dpo) and dpo[-1] > 10
    assert all(b - a > 3 for a, b in zip(dpo[2:], dpo[3:]))
    assert rows[-1]["ipo"] == pytest.approx(ex["ipo_target"]) == pytest.approx(2.0)
    assert rows[-1]["dpo_loss"] > 0


def test_po_token_rewards_and_grpo_advantages():
    ex = ml_models_docs.po_example()
    tok = ex["tokens"]
    assert tok["seq_ratio"] == pytest.approx(tok["seq_logp"] - tok["seq_logref"])
    assert sum(tok["rewards"]) == pytest.approx(tok["total"])
    g = ex["grpo"]
    assert sum(g["advantages"]) == pytest.approx(0, abs=1e-12)
    assert sum(a * a for a in g["advantages"]) / len(g["advantages"]) == pytest.approx(1)
    assert g["advantages"][0] == pytest.approx(math.sqrt(2))
    assert ml_models_docs.grpo_advantages([1.0, 1.0])["advantages"] == [0.0, 0.0]
    for row in ex["k3"]:
        assert row["k3"] >= 0
    assert next(r for r in ex["k3"] if r["ratio"] == 1.0)["k3"] == 0


def test_rag_chunking_overlap_and_sentences_keep_every_answer_whole():
    ex = ml_models_docs.rag_example()
    doc = ex["example"]["document"]
    assert ml_models_docs.word_chunks("a b c d e f g", 4, 2) == ["a b c d", "c d e f", "e f g"]
    assert ml_models_docs.word_chunks("a b c", 4) == ["a b c"]
    for name in ("fixed", "overlap"):
        joined = ex["splits"][name]["chunks"]
        assert all(len(c.split()) <= ex["example"]["chunk_size"] for c in joined)
    assert " ".join(ex["splits"]["fixed"]["chunks"]) == doc
    assert ex["splits"]["fixed"]["found"] == [True, True, True, True, False]
    assert all(ex["splits"]["overlap"]["found"]) and all(ex["splits"]["sentence"]["found"])
    assert " ".join(ex["chunks"]) == doc
    assert all(len(c.split()) <= ex["example"]["sentence_budget"] for c in ex["chunks"])
    assert all(c.endswith(".") for c in ex["chunks"])


def test_rag_bm25_misses_vocabulary_mismatch_and_ranks_only_matches():
    ex = ml_models_docs.rag_example()
    q = {r["text"]: r for r in ex["queries"]}
    charging = q["how long does charging take"]
    assert charging["lexical"] == [0.0] * len(ex["chunks"])
    assert charging["rankings"]["bm25"] == [] and charging["ranks"]["bm25"] is None
    assert charging["ranks"]["trigram"] == 1
    assert ml_models_docs.query_terms("how do I lock the headlamp") == ["lock", "headlamp"]
    swim = q["can I swim with it"]
    assert all(r is None for r in swim["ranks"].values())
    assert ml_models_docs.ranking_from_scores([0.0, 2.0, 0.5, 2.0]) == [1, 3, 2]
    assert ml_models_docs.sparse_cosine({"ab": 1}, {}) == 0.0
    v = ml_models_docs.trigram_vector("lock")
    assert v == {"#lo": 1, "loc": 1, "ock": 1, "ck#": 1}
    assert ml_models_docs.sparse_cosine(v, v) == pytest.approx(1)


def test_rag_fusion_and_rerank_follow_their_formulas():
    ex = ml_models_docs.rag_example()
    k = ex["example"]["rrf_k"]
    for q in ex["queries"]:
        for i, score in q["fused_scores"].items():
            expected = sum(1 / (k + r.index(i) + 1) for r in (q["rankings"]["bm25"], q["rankings"]["trigram"]) if i in r)
            assert score == pytest.approx(expected)
        for i, part in q["rerank_parts"].items():
            assert part["score"] == pytest.approx(sum(part["parts"].values()))
            assert q["rerank_scores"][i] == part["score"]
        pool = q["rankings"]["hybrid"][:ex["example"]["rerank_pool"]]
        assert sorted(q["rankings"]["reranked"]) == sorted(q["rankings"]["hybrid"])
        assert q["rankings"]["reranked"][:len(pool)] == sorted(pool, key=lambda i: -q["rerank_scores"][i])
    lock = ex["queries"][0]
    assert lock["ranks"]["hybrid"] == 2 and lock["ranks"]["reranked"] == 1


def test_rag_metrics_improve_from_bm25_to_hybrid_to_reranked():
    ex = ml_models_docs.rag_example()
    m = ex["metrics"]
    assert m["bm25"] == {"recall": pytest.approx(0.6), "mrr": pytest.approx(0.6)}
    assert m["trigram"]["recall"] == m["hybrid"]["recall"] == m["reranked"]["recall"] == pytest.approx(0.8)
    assert m["trigram"]["mrr"] == pytest.approx(2 / 3)
    assert m["hybrid"]["mrr"] == pytest.approx(0.7)
    assert m["reranked"]["mrr"] == pytest.approx(0.8)
    assert ml_models_docs.retrieval_metrics([1, 2, None, 4], 3) == {"recall": 0.5, "mrr": pytest.approx((1 + 0.5 + 0.25) / 4)}


def test_rag_prompt_budget_and_lost_in_the_middle_order():
    ex = ml_models_docs.rag_example()
    p = ex["prompt"]
    assert p["kept"] == [1, 4] and p["skipped"] == [2, 0]
    assert p["used"] == ex["example"]["overhead_words"] + sum(len(ex["chunks"][i].split()) for i in p["kept"])
    assert p["used"] <= ex["example"]["budget_words"]
    for i in p["skipped"]:
        assert p["used"] + len(ex["chunks"][i].split()) > ex["example"]["budget_words"]
    assert ex["middle"] == [1, 3, 5, 4, 2]
    assert ml_models_docs.lost_in_the_middle_order([]) == []


def test_rag_sequence_and_token_marginals():
    ex = ml_models_docs.rag_example()
    r = ex["rag"]
    probs = ex["example"]["rag"]["token_probs"]
    assert sum(r["doc_probs"]) == pytest.approx(1)
    assert r["doc_probs"][0] == pytest.approx(1 / (1 + math.exp(-1)))
    p0, p1 = r["doc_probs"]
    assert r["sequence"] == pytest.approx(p0 * 0.9 * 0.2 + p1 * 0.1 * 0.8)
    assert r["per_token"] == pytest.approx([p0 * 0.9 + p1 * 0.1, p0 * 0.2 + p1 * 0.8])
    assert r["token"] == pytest.approx(r["per_token"][0] * r["per_token"][1])
    assert r["token"] > r["sequence"]
    same = ml_models_docs.rag_marginals([0.3, -1.0], [[0.5, 0.4], [0.5, 0.4]])
    assert same["sequence"] == pytest.approx(same["token"]) == pytest.approx(0.2)
    assert len(probs) == 2


def test_rag_exact_match_and_token_f1():
    ex = ml_models_docs.rag_example()
    assert [a["em"] for a in ex["answers"]] == [0.0, 0.0, 0.0]
    assert [round(a["f1"], 3) for a in ex["answers"]] == [0.571, 0.4, 0.5]
    assert ml_models_docs.exact_match("The two hours.", "two hours") == 1.0
    assert ml_models_docs.token_f1("blue", "two hours")["f1"] == 0.0
    f = ml_models_docs.token_f1("two two hours", "two hours")
    assert f["precision"] == pytest.approx(2 / 3) and f["recall"] == 1.0


def test_rag_word_ranges_and_answer_spans_match_the_chunks():
    ex = ml_models_docs.rag_example()
    words = ex["example"]["document"].split()
    assert ex["n_words"] == len(words)
    for name, split in ex["splits"].items():
        assert [" ".join(words[a:b]) for a, b in split["ranges"]] == split["chunks"]
        for span, found in zip(ex["spans"], split["found"]):
            assert found == any(a <= span[0] and span[1] <= b for a, b in split["ranges"])
    for span, q in zip(ex["spans"], ex["example"]["queries"]):
        assert ml_models_docs.rag_words(" ".join(words[span[0]:span[1]])) == ml_models_docs.rag_words(q["answer"])
    assert ex["splits"]["fixed"]["ranges"][-1] == [120, 121]
    assert ml_models_docs.phrase_span("a b c", "d") is None


def test_ckpt_full_resume_is_bit_identical_and_each_missing_piece_diverges():
    result = ml_models_docs.ckpt_resume_comparison()
    ex = ml_models_docs.CKPT_EXAMPLE
    assert result["total_steps"] == ex["epochs"] * len(ex["data"]) // ex["batch_size"]
    assert result["saved"]["scheduler"]["step"] == ex["save_at"]
    assert result["saved"]["optimizer"]["t"] == ex["save_at"]
    assert result["saved"]["data"]["batch"] != 0
    runs = result["runs"]
    assert runs["full"]["identical"] and runs["full"]["max_gap"] == 0.0
    assert runs["full"]["log"] == result["straight"]
    for part in ml_models_docs.CKPT_FORGETS:
        assert not runs[part]["identical"]
        assert runs[part]["first_diverged"] == ex["save_at"] + 1
        assert runs[part]["max_gap"] > 0
        assert runs[part]["log"][:ex["save_at"]] == result["straight"][:ex["save_at"]]


def test_ckpt_training_loop_learns_and_follows_its_schedule():
    ex = ml_models_docs.CKPT_EXAMPLE
    total = ex["epochs"] * len(ex["data"]) // ex["batch_size"]
    _, log = ml_models_docs.ckpt_train(ml_models_docs.ckpt_initial_state(ex["seed"]), total)
    assert log[-1]["loss"] < log[0]["loss"] / 10
    assert [round(e["lr"], 12) for e in log[:ex["warmup"]]] == [round(ex["lr"] * (i + 1) / ex["warmup"], 12) for i in range(ex["warmup"])]
    assert log[ex["warmup"]]["lr"] == pytest.approx(ex["lr"])
    assert all(a["lr"] >= b["lr"] for a, b in zip(log[ex["warmup"]:], log[ex["warmup"] + 1:]))
    per_epoch = len(ex["data"]) // ex["batch_size"]
    for epoch in range(ex["epochs"]):
        seen = sorted(i for e in log[epoch * per_epoch:(epoch + 1) * per_epoch] for i in e["batch"])
        assert seen == list(range(len(ex["data"])))
        assert all(e["epoch"] == epoch for e in log[epoch * per_epoch:(epoch + 1) * per_epoch])
    assert ml_models_docs.ckpt_epoch_order(8, ex["seed"], 1) == ml_models_docs.ckpt_epoch_order(8, ex["seed"], 1)
    assert ml_models_docs.ckpt_epoch_order(8, ex["seed"], 0) != ml_models_docs.ckpt_epoch_order(8, ex["seed"], 1)


def test_ckpt_forget_drops_only_the_named_piece():
    ex = ml_models_docs.CKPT_EXAMPLE
    saved, _ = ml_models_docs.ckpt_train(ml_models_docs.ckpt_initial_state(ex["seed"]), ex["save_at"])
    fresh = ml_models_docs.ckpt_initial_state(ex["seed"])
    for part in ("optimizer", "scheduler", "rng"):
        state = ml_models_docs.ckpt_forget(saved, part, ex["seed"])
        assert state[part] == fresh[part]
        assert all(state[k] == saved[k] for k in state if k != part)
    state = ml_models_docs.ckpt_forget(saved, "data_position", ex["seed"])
    assert state["data"] == {"epoch": saved["data"]["epoch"], "batch": 0}
    assert all(state[k] == saved[k] for k in state if k != "data")


def test_ckpt_sizes_add_up_per_parameter():
    sizes = ml_models_docs.checkpoint_sizes(7_000_000_000)
    assert sizes["bytes_per_param"] == 2 + 4 + 4 + 4
    assert sizes["full_gb"] == pytest.approx(98.0)
    assert sizes["weights_gb"] == pytest.approx(14.0)
    assert sizes["ratio"] == 7
    assert sum(r["gb"] for r in sizes["rows"]) == pytest.approx(sizes["full_gb"])


def test_ckpt_young_interval_minimizes_the_waste_model():
    save, mtbf = 60, 6 * 3600
    best = ml_models_docs.young_interval(save, mtbf)
    assert best == pytest.approx(math.sqrt(2 * 60 * 21600))
    waste = ml_models_docs.checkpoint_waste(best, save, mtbf)
    assert save / best == pytest.approx(best / (2 * mtbf))
    for t in (best * 0.5, best * 0.9, best * 1.1, best * 2):
        assert ml_models_docs.checkpoint_waste(t, save, mtbf) > waste
    assert ml_models_docs.checkpoint_waste(900, save, mtbf) == pytest.approx(60 / 900 + 900 / 43200)
    example = ml_models_docs.checkpointing_example()
    assert example["intervals"][1]["interval"] < example["intervals"][0]["interval"]
    assert example["intervals"][1]["waste"] < example["intervals"][0]["waste"]


def test_ckpt_activation_checkpointing_matches_checkpoint_sequential_segments():
    costs = {k: ml_models_docs.activation_checkpoint_cost(16, k) for k in (1, 2, 4, 8, 16)}
    assert costs[1] == {"segments": 1, "segment_size": 16, "last_segment": 16, "stored_inputs": 0, "peak": 16, "recomputed": 0}
    assert costs[4]["peak"] == 3 + 4 and costs[4]["recomputed"] == 12
    assert min(costs.values(), key=lambda c: c["peak"])["segments"] == 4 == math.isqrt(16)
    assert all(costs[k]["recomputed"] == 16 - 16 // k for k in costs)
    uneven = ml_models_docs.activation_checkpoint_cost(10, 3)
    assert uneven["segment_size"] == 3 and uneven["last_segment"] == 4
    assert uneven["peak"] == 2 + 4 and uneven["recomputed"] == 6


def test_ckpt_reshard_plan_covers_every_row_once():
    plan = ml_models_docs.reshard_plan(12, 4, 3)
    assert plan["old"] == [(0, 3), (3, 6), (6, 9), (9, 12)]
    assert [p["rows"] for p in plan["new"]] == [(0, 4), (4, 8), (8, 12)]
    assert plan["new"][1]["reads"] == [
        {"old_rank": 1, "rows": (4, 6), "offset": 1},
        {"old_rank": 2, "rows": (6, 8), "offset": 0},
    ]
    for rows, old, new in ((12, 4, 3), (10, 3, 4), (7, 2, 5), (9, 3, 3)):
        plan = ml_models_docs.reshard_plan(rows, old, new)
        covered = [r for p in plan["new"] for read in p["reads"] for r in range(*read["rows"])]
        assert covered == list(range(rows))
    same = ml_models_docs.reshard_plan(9, 3, 3)
    assert all(len(p["reads"]) == 1 and p["reads"][0]["old_rank"] == p["rank"] for p in same["new"])


def test_ckpt_weights_only_scan_blocks_unlisted_globals_without_loading():
    cases = {c["name"]: c for c in ml_models_docs.checkpoint_pickles()}
    assert cases["plain state dict"]["globals"] == [] and cases["plain state dict"]["loads"]
    assert cases["OrderedDict state dict"]["globals"] == ["collections.OrderedDict"]
    assert cases["OrderedDict state dict"]["loads"]
    assert cases["object with __reduce__"]["blocked"] == ["builtins.print"]
    assert not cases["object with __reduce__"]["loads"]
    import pickle
    blob = pickle.dumps(ml_models_docs.CkptPayload(), protocol=2, fix_imports=False)
    assert ml_models_docs.pickle_globals(blob) == ["builtins.print"]
    verdict = ml_models_docs.weights_only_verdict(blob, ("builtins.print",))
    assert verdict["loads"] and verdict["blocked"] == []


def test_repro_worker_numpy_seed_matches_seed_sequence_values():
    base = ml_models_docs.REPRO_EXAMPLE["base_seed"]
    assert ml_models_docs.worker_numpy_seed(base, 0) == [1310905175, 2081109477, 4124378009, 3038891885]
    assert ml_models_docs.worker_numpy_seed(base, 3) == [1534353524, 2778767537, 1060257585, 3308704576]
    seeds = ml_models_docs.worker_seeds(base, 4)
    assert [s["seed"] - base for s in seeds] == [0, 1, 2, 3]
    assert len({tuple(s["numpy"]) for s in seeds}) == 4
    assert all(0 <= v < 2**32 for s in seeds for v in s["numpy"])


def test_repro_copied_rng_repeats_and_reseeding_separates_workers():
    ex = ml_models_docs.reproducibility_example()
    assert ex["copied"]["distinct"] == 1
    assert len(set(map(tuple, ex["copied"]["rows"]))) == 1
    assert ex["reseeded"]["distinct"] == 4
    again = ml_models_docs.worker_crops([w["seed"] for w in ex["workers"]], 3)
    assert again == ex["reseeded"]


def test_repro_inserting_a_draw_shifts_shared_stream_but_not_derived_seeds():
    ex = ml_models_docs.reproducibility_example()
    assert ex["shared_before"]["embedding"] == ex["shared_after"]["embedding"]
    assert ex["shared_before"]["head"] != ex["shared_after"]["head"]
    assert ex["shared_after"]["flip"] == ex["shared_before"]["head"][:1]
    assert ex["shared_after"]["head"][:2] == ex["shared_before"]["head"][1:]
    assert ex["separate_before"]["head"] == ex["separate_after"]["head"]
    assert ex["separate_before"]["embedding"] == ex["separate_after"]["embedding"]
    assert len(set(ex["derived"].values())) == 3


def test_repro_float32_reduction_order_changes_the_sum():
    sums = ml_models_docs.reproducibility_example()["sums"]
    assert len(sums["values"]) == 4096
    assert all(ml_models_docs.f32(v) == v for v in sums["values"])
    assert all(ml_models_docs.f32(r["sum"]) == r["sum"] for r in sums["rows"])
    assert sums["distinct"] >= 5
    assert sums["spread"] > 0 and sums["spread_ulps"] == sums["spread"] / sums["ulp"]
    assert sums["ulp"] == 2.0 ** -18 and 32 <= abs(sums["exact"]) < 64
    assert all(abs(r["ulps"]) < 64 for r in sums["rows"])
    assert ml_models_docs.f32_sum([1.0, 2.0**-24, 2.0**-24]) == 1.0
    assert ml_models_docs.f32_pairwise([1.0, 2.0**-24, 2.0**-24, 0.0]) == 1.0
    assert ml_models_docs.f32_sum([2.0**-24, 2.0**-24, 1.0]) == 1.0 + 2.0**-23


def test_repro_random_state_int_repeats_and_instance_advances():
    calls = {c["name"]: c for c in ml_models_docs.reproducibility_example()["random_state"]}
    assert calls["random_state=0"]["same"]
    assert not calls["random_state=RandomState(0)"]["same"]
    assert calls["random_state=0"]["first"] == calls["random_state=RandomState(0)"]["first"]
    for c in calls.values():
        for folds in (c["first"], c["second"]):
            assert sorted(i for f in folds for i in f) == list(range(10))
    rng = random.Random(5)
    assert ml_models_docs.check_random_state_stand_in(rng) is rng
    assert ml_models_docs.check_random_state_stand_in(None) is ml_models_docs.check_random_state_stand_in(None)
    with pytest.raises(ValueError):
        ml_models_docs.check_random_state_stand_in("seed")


def test_repro_manifest_hashes_match_git_and_sha256():
    import hashlib
    import subprocess
    ex = ml_models_docs.REPRO_EXAMPLE
    m = ml_models_docs.run_manifest()
    assert m["data"] == hashlib.sha256(ex["csv"].encode()).hexdigest()
    assert m["data"] != m["data_edited"] and m["differing_bytes"] == 1
    assert m["code"] == "f1b034256689f3f67dcb29f0952d111eb5803b86"
    out = subprocess.run(["git", "hash-object", "--stdin"], input=ex["script"].encode(), capture_output=True)
    if out.returncode == 0:
        assert out.stdout.decode().strip() == m["code"]
    assert len(m["environment"]) == 64


def test_ssm_discretizations_match_closed_forms_and_stability():
    rows = {r["step"]: r for r in ml_models_docs.scalar_discretizations(-1.0, (0.1, 0.5, 1.0, 2.5))}
    assert rows[0.5]["exact"] == pytest.approx(math.exp(-0.5))
    assert rows[0.5]["bilinear"] == pytest.approx(0.6) and rows[1.0]["bilinear"] == pytest.approx(1 / 3)
    assert rows[2.5]["euler"] == pytest.approx(-1.5) and not rows[2.5]["euler_stable"]
    assert all(r["bilinear_stable"] for r in rows.values())
    assert rows[0.1]["zoh_b"] == pytest.approx(1 - math.exp(-0.1))
    assert abs(rows[0.1]["bilinear"] - rows[0.1]["exact"]) < abs(rows[0.1]["euler"] - rows[0.1]["exact"])


def test_ssm_hippo_legs_is_normal_plus_low_rank():
    a, b = ml_models_docs.hippo_legs(4)
    assert a[2][0] == pytest.approx(-math.sqrt(5)) and a[3][3] == -4.0 and a[0][3] == 0.0
    assert b == pytest.approx([1, math.sqrt(3), math.sqrt(5), math.sqrt(7)])
    s = ml_models_docs.hippo_normal_plus_low_rank(4)["s"]
    for i in range(4):
        assert s[i][i] == pytest.approx(-0.5)
        for k in range(4):
            if i != k:
                assert s[i][k] == pytest.approx(-s[k][i])
    inv = ml_models_docs.ssm_inverse(a)
    ident = ml_models_docs.ssm_matmul(a, inv)
    assert all(ident[i][k] == pytest.approx(1.0 if i == k else 0.0, abs=1e-12) for i in range(4) for k in range(4))


def test_ssm_recurrence_equals_convolution():
    ex = ml_models_docs.state_space_example()
    assert ex["dual_gap"] < 1e-12
    assert ex["kernel"][0] == pytest.approx(sum(c * b for c, b in zip(ex["example"]["hippo_c"], ex["b_bar"])))
    assert all(x > y > 0 for x, y in zip(ex["kernel"], ex["kernel"][1:]))
    impulse = [1.0] + [0.0] * 7
    rec = ml_models_docs.ssm_recurrent(ex["a_bar"], ex["b_bar"], ex["example"]["hippo_c"], impulse)
    assert rec["y"] == pytest.approx(ex["kernel"])


def test_ssm_selection_holds_gated_values_that_a_fixed_step_cannot():
    ex = ml_models_docs.state_space_example()
    assert ex["target"] == [2.0] * 4 + [-1.0] * 4
    assert ex["sel_error"] < 0.05 and ex["lti_error"] > 1.5
    gated = [r for r in ex["selective"] if r["gate"]]
    filler = [r for r in ex["selective"] if not r["gate"]]
    assert all(r["step"] > 4 for r in gated) and all(r["step"] < 0.003 for r in filler)
    assert all(r["b_bar"] == [0.0, 0.0] for r in filler)


def test_ssm_parallel_scan_matches_sequential_in_log_depth():
    ex = ml_models_docs.state_space_example()
    assert ex["scan"]["h"] == pytest.approx(ex["sequential"], abs=1e-15)
    assert ex["scan"]["depth"] == 3 and ex["scan"]["combines"] == 7 + 6 + 4
    assert [r["h"][0] for r in ex["selective"]] == pytest.approx(ex["sequential"])
    pairs = [(0.5, 1.0), (2.0, -1.0), (0.25, 3.0)]
    left = ml_models_docs.scan_combine(ml_models_docs.scan_combine(pairs[0], pairs[1]), pairs[2])
    right = ml_models_docs.scan_combine(pairs[0], ml_models_docs.scan_combine(pairs[1], pairs[2]))
    assert left == pytest.approx(right)


def test_ssm_costs_grow_with_context_only_for_attention():
    costs = ml_models_docs.state_space_example()["costs"]
    assert costs["state_bytes"] == 48 * 4096 * (16 + 3) * 2
    rows = costs["rows"]
    assert rows[0]["kv_bytes"] == 2 * 48 * 1024 * 2048 * 2
    assert all(r["ssm_bytes"] == costs["state_bytes"] for r in rows)
    assert rows[-1]["kv_bytes"] // rows[0]["kv_bytes"] == 512
    assert rows[-1]["train_attn"] // rows[0]["train_attn"] == 512 ** 2
    assert rows[-1]["train_ssm"] // rows[0]["train_ssm"] == 512


def test_prof_schedule_matches_upstream_cycle():
    ex = ml_models_docs.profiling_example()
    assert ex["actions"] == ["NONE"] * 3 + ["WARMUP", "RECORD", "RECORD_AND_SAVE"] * 1 + [
        "NONE", "WARMUP", "RECORD", "RECORD_AND_SAVE"] + ["NONE"] * 4
    action = ml_models_docs.profiler_schedule(wait=1, warmup=1, active=2, skip_first_wait=1)
    assert [action(s) for s in range(5)] == ["WARMUP", "RECORD", "RECORD_AND_SAVE", "NONE", "WARMUP"]
    endless = ml_models_docs.profiler_schedule(wait=0, warmup=0, active=1)
    assert {endless(s) for s in range(50)} == {"RECORD_AND_SAVE"}


def test_prof_timing_needs_sync_and_warmup():
    t = ml_models_docs.profiling_example()["timing"]
    assert t["timeline"]["total"] == 7000 + 5 and t["timeline"]["cpu_done"] == 30
    assert t["median"] == pytest.approx(7.005)
    assert t["unsynced_mean"] == pytest.approx(0.03)
    assert t["naive_mean"] > 16 * t["median"]
    assert t["synced"][0] > 100 * t["median"]


def test_prof_host_bound_steps_leave_the_gpu_idle():
    h = ml_models_docs.profiling_example()["host_bound"]
    assert h["busy"] == 40 and h["cpu_done"] == 100
    assert h["utilization"] < 0.4


def test_prof_key_averages_splits_self_from_total():
    rows = {r["name"]: r for r in ml_models_docs.profiling_example()["averages"]}
    linear = rows["aten::linear"]
    assert (linear["count"], linear["total"], linear["self"]) == (2, 710, 60)
    step = rows["ProfilerStep#4"]
    assert step["total"] == 9800 and step["self"] == 9800 - sum(
        r["total"] for name, r in rows.items() if name not in ("ProfilerStep#4", "aten::t", "aten::addmm"))
    assert sum(r["self"] for r in rows.values()) == step["total"]
    first = ml_models_docs.profiling_example()["averages"][0]
    assert first["name"].startswith("Optimizer.step")


def test_prof_mfu_counts_model_flops_only():
    m = ml_models_docs.profiling_example()["mfu"]
    assert m["per_token"] == 6 * 1.3e9 + 12 * 24 * 2048 * 2048
    assert m["mfu"] == pytest.approx(0.4592, abs=1e-4)
    assert m["hfu"] > m["mfu"]
    assert m["tokens_per_s"] * 2.6 == pytest.approx(1048576)


def test_prof_data_wait_disappears_once_workers_keep_up():
    rows = ml_models_docs.profiling_example()["loader"]
    assert [r["workers"] for r in rows] == [2, 3, 4]
    assert rows[0]["steady_wait"] == pytest.approx(20.0)
    assert rows[0]["wait_fraction"] == pytest.approx(1 / 3)
    assert rows[1]["wait_fraction"] == 0.0 and rows[2]["wait_fraction"] == 0.0
    assert all(r["first_wait"] == 120.0 for r in rows)


def test_prof_memory_peak_moves_after_first_step_and_long_batch():
    mem = ml_models_docs.profiling_example()["memory"]
    peaks = [p["peak"] for p in mem["peaks"]]
    assert peaks == [4000.0, 5650.0, 5650.0, 8050.0]
    assert all(p["end"] == 3000.0 for p in mem["peaks"])
    assert mem["reserved"] == max(peaks)
    assert mem["events"][0] == {"step": -1, "event": "model.to(device)", "allocated": 1000}


def test_lu_factor_pivots_and_reconstructs():
    ex = ml_models_docs.DECOMPOSITION_EXAMPLE
    lu = ml_models_docs.lu_factor(ex["a"])
    assert lu["pivots"] == [2, 2, 3]
    assert lu["U"] == [[4.0, -6.0, 0.0], [0.0, 4.0, 1.0], [0.0, 0.0, 1.0]]
    assert lu["L"] == [[1.0, 0.0, 0.0], [0.5, 1.0, 0.0], [-0.5, 1.0, 1.0]]
    assert ml_models_docs.matmul(lu["L"], lu["U"]) == ml_models_docs.matmul(lu["P"], ex["a"])
    assert ml_models_docs.lu_solve(lu, ex["b"]) == pytest.approx([1.0, 1.0, 2.0])


def test_cholesky_factor_and_solve():
    ex = ml_models_docs.DECOMPOSITION_EXAMPLE
    lower = ml_models_docs.cholesky(ex["spd"])
    assert lower == [[2.0, 0.0, 0.0], [1.0, 3.0, 0.0], [1.0, 2.0, 4.0]]
    assert ml_models_docs.matmul(lower, ml_models_docs.transpose(lower)) == ex["spd"]
    with pytest.raises(ValueError):
        ml_models_docs.cholesky([[1.0, 2.0], [2.0, 1.0]])
    example = ml_models_docs.decomposition_example()
    assert example["cholesky_y"] == pytest.approx([5.0, 7.0, 8.0])
    assert example["cholesky_x"] == pytest.approx([1.0, 1.0, 2.0])


def test_gram_schmidt_gives_orthonormal_q_and_triangular_r():
    ex = ml_models_docs.DECOMPOSITION_EXAMPLE
    qr = ml_models_docs.gram_schmidt(ex["design"])
    assert ml_models_docs.orthogonality_loss(qr["Q"]) < 1e-12
    assert qr["R"][1][0] == 0
    product = ml_models_docs.matmul(qr["Q"], qr["R"])
    assert [x for row in product for x in row] == pytest.approx([x for row in ex["design"] for x in row])


def test_modified_gram_schmidt_keeps_orthogonality_on_hilbert():
    example = ml_models_docs.decomposition_example()
    assert example["hilbert_cond"] > 1e7
    assert example["hilbert_classical"] > 1e-6
    assert example["hilbert_modified"] < 1e-8


def test_householder_least_squares_matches_normal_equations_on_a_line():
    example = ml_models_docs.decomposition_example()
    assert example["fit"] == pytest.approx([0.9, 0.9])
    assert example["normal_fit"] == pytest.approx([0.9, 0.9])


def test_normal_equations_lose_accuracy_where_qr_does_not():
    rows = {r["eps"]: r for r in ml_models_docs.decomposition_example()["least_squares"]}
    assert rows[1e-7]["normal_error"] > 1e-4
    assert rows[1e-8]["normal"] is None and rows[1e-8]["gram_singular"]
    assert all(r["qr_error"] < 1e-14 for r in rows.values())
    assert rows[1e-4]["cond"] == pytest.approx(math.sqrt(2) * 1e4, rel=1e-6)


def test_matrix_norms_follow_torch_definitions():
    norms = ml_models_docs.matrix_norms(ml_models_docs.DECOMPOSITION_EXAMPLE["a"])
    assert norms["inf"] == 11 and norms["one"] == 14
    assert norms["two"] <= norms["fro"] <= norms["nuc"]
    assert norms["cond"] == pytest.approx(norms["two"] / norms["minus_two"])
    assert ml_models_docs.matrix_norms(ml_models_docs.DECOMPOSITION_EXAMPLE["spd"])["nuc"] == pytest.approx(35.0)


def test_cholesky_samples_have_the_target_covariance():
    sampling = ml_models_docs.decomposition_example()["sampling"]
    target = ml_models_docs.DECOMPOSITION_EXAMPLE["spd"]
    for got, want in zip(sampling["covariance"], target):
        assert got == pytest.approx(want, abs=0.25)


def test_error_exponent_clamps_to_the_plot_floor():
    assert ml_models_docs.error_exponent(0.0) == -16.0
    assert ml_models_docs.error_exponent(1e-3) == pytest.approx(-3.0)
    rows = ml_models_docs.least_squares_errors([1e-2, 1e-8])
    assert rows[0]["qr_log"] == -16.0 or rows[0]["qr_log"] < -15
    assert rows[1]["normal_log"] is None


def test_kv_shrink_steps_multiply_heads_layers_and_bits():
    rows = ml_models_docs.kv_shrink_steps(ml_models_docs.KV_CONFIG)

    assert [row["bytes"] for row in rows] == [524288, 131072, 65536, 32768, 18432]
    assert rows[-1]["bits"] == 4.5
    assert rows[1]["bytes"] == ml_models_docs.kv_cache_bytes_per_token(32, 8, 128, 2)
    with pytest.raises(ValueError):
        ml_models_docs.shared_kv_bytes_per_token(ml_models_docs.KV_CONFIG, 8, layer_share=3)


def test_e4m3_rounding_keeps_three_mantissa_bits():
    assert ml_models_docs.round_to_e4m3(0.325) == 0.3125
    assert ml_models_docs.round_to_e4m3(1.0) == 1.0
    assert ml_models_docs.round_to_e4m3(1.07) == 1.125
    assert ml_models_docs.round_to_e4m3(1000) == 448.0


def test_fp4_block_quantize_snaps_to_the_e2m1_grid():
    result = ml_models_docs.fp4_block_quantize(ml_models_docs.FP4_BLOCK_EXAMPLE)

    assert result["scale"] == 0.3125
    assert all(abs(code) in ml_models_docs.FP4_E2M1_GRID for code in result["codes"])
    assert result["codes"][3] == 6.0 and result["codes"][4] == 0.0
    assert result["bits"] / len(ml_models_docs.FP4_BLOCK_EXAMPLE) == 4.5
    assert result["max_magnitude"] == 2688
    assert round(result["max_error"], 2) == 0.15
    for value, restored in zip(ml_models_docs.FP4_BLOCK_EXAMPLE, result["restored"]):
        assert value * restored >= 0


def test_conjugate_gradient_solves_the_2x2_example_in_two_steps():
    ex = ml_models_docs.ITERATIVE_EXAMPLE
    run = ml_models_docs.iterative_example()["small"]

    assert run["cg"]["steps"] == 2
    assert run["cg"]["x"] == pytest.approx([2.0, -2.0])
    assert run["cg"]["path"][1] == pytest.approx([0.08, -0.6133333333])
    assert abs(run["conjugacy"]) < 1e-12
    assert run["eigen"]["values"] == pytest.approx([2.0, 7.0])
    assert run["kappa"] == pytest.approx(3.5)
    assert run["sd"]["path"][1] == run["cg"]["path"][1]
    assert run["sd"]["steps"] == 10
    for before, after in zip(run["sd"]["path"], run["sd"]["path"][1:]):
        step = [a - b for a, b in zip(after, before)]
        residual = [b - sum(a * x for a, x in zip(row, before)) for row, b in zip(ex["a"], ex["b"])]
        assert step[0] * residual[1] == pytest.approx(step[1] * residual[0])


def test_steepest_descent_steps_are_orthogonal():
    run = ml_models_docs.steepest_descent([[3.0, 2.0], [2.0, 6.0]], [2.0, -8.0], [-2.0, -2.0], tol=1e-6)
    steps = [[a - b for a, b in zip(q, p)] for p, q in zip(run["path"], run["path"][1:])]

    for first, second in zip(steps, steps[1:]):
        assert ml_models_docs.dot_product(first, second) == pytest.approx(0, abs=1e-12)


def test_preconditioning_cuts_cg_steps_on_the_scaled_system():
    run = ml_models_docs.iterative_example()["large"]

    assert [run[key]["steps"] for key in ["sd", "cg", "pcg"]] == [1460, 30, 20]
    assert run["kappa"] == pytest.approx(177.72, abs=0.01)
    assert run["kappa_jacobi"] == pytest.approx(4.965, abs=0.001)
    assert (run["sd_bound"], run["cg_bound"], run["pcg_bound"]) == (1637, 128, 20)
    assert run["sd"]["steps"] <= run["sd_bound"] and run["cg"]["steps"] <= run["cg_bound"]
    assert run["error"] < 1e-8
    assert all(r <= 1e-8 for r in [run["sd"]["residuals"][-1], run["cg"]["residuals"][-1], run["pcg"]["residuals"][-1]])


def test_cg_is_exact_in_n_steps_and_the_bounds_grow_with_kappa():
    matrix = ml_models_docs.scaled_tridiagonal([1.0, 2.0, 3.0, 4.0, 5.0])
    run = ml_models_docs.conjugate_gradient(matrix, [1.0] * 5, [0.0] * 5, tol=1e-12)

    assert run["steps"] <= 5
    assert ml_models_docs.cg_steps_bound(100, 1e-6) < ml_models_docs.cg_steps_bound(10_000, 1e-6)
    assert ml_models_docs.cg_steps_bound(10_000, 1e-6) < ml_models_docs.steepest_descent_steps_bound(10_000, 1e-6)


def test_quadratic_contour_lies_on_its_level_set():
    a, center = [[3.0, 2.0], [2.0, 6.0]], [2.0, -2.0]

    for point in ml_models_docs.quadratic_contour(a, center, 4.0, count=12):
        e = [p - c for p, c in zip(point, center)]
        assert 0.5 * sum(e[i] * a[i][j] * e[j] for i in range(2) for j in range(2)) == pytest.approx(4.0)
