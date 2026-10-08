import os
import math
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
FORMAT_EXEMPT = {"transformer"}


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
