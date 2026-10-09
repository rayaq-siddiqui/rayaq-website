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
