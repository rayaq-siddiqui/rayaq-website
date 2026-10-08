import os
import re

import pytest

import app as app_module
import leetcode_docs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "frontend", "templates", "leetcode")
PROGRESS = os.path.join(ROOT, "specs", "leetcode-progress.md")
FORMAT_SECTIONS = [
    "problem",
    "intuition",
    "mechanics",
    "worked-example",
    "implementation",
    "tradeoffs",
    "problems",
    "connections",
    "check-yourself",
    "references",
]
SIGNALS_HEADER = "<th>Signal</th><th>Pattern</th><th>Why</th>"
QUEUE_LINE = re.compile(r"^\d+\. `([a-z0-9-]+)`(.*)$", re.M)


def page_slugs():
    return [page["slug"] for page in leetcode_docs.PAGES]


def ready_urls():
    return [f"/leetcode/{page['slug']}" for page in leetcode_docs.ready_pages()]


def queue():
    with open(PROGRESS, encoding="utf-8") as handle:
        return [(slug, rest) for slug, rest in QUEUE_LINE.findall(handle.read())]


def test_areas_and_pages_are_consistent():
    area_slugs = [area["slug"] for area in leetcode_docs.AREAS]
    assert len(area_slugs) == len(set(area_slugs))
    assert len(page_slugs()) == len(set(page_slugs()))
    for page in leetcode_docs.PAGES:
        assert page["area"] in area_slugs, page["slug"]
        assert page["level"] in leetcode_docs.LEVELS, page["slug"]
        assert page["title"].strip() and page["summary"].strip()
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", page["slug"])
        for prerequisite in page["prerequisites"]:
            assert prerequisite in page_slugs(), (page["slug"], prerequisite)
            assert prerequisite != page["slug"]
    for area in area_slugs:
        assert any(page["area"] == area for page in leetcode_docs.PAGES), area


def test_beyond_pages_are_advanced():
    for page in leetcode_docs.PAGES:
        if page["area"] == "beyond":
            assert page["level"] == "advanced", page["slug"]


def test_learning_path_names_pages_in_prerequisite_order():
    seen = set()
    for step in leetcode_docs.LEARNING_PATH:
        for slug in step["slugs"]:
            assert slug in page_slugs(), slug
        step_slugs = set(step["slugs"])
        for slug in step["slugs"]:
            page = next(page for page in leetcode_docs.PAGES if page["slug"] == slug)
            for prerequisite in page["prerequisites"]:
                if any(prerequisite in later["slugs"] for later in leetcode_docs.LEARNING_PATH):
                    assert prerequisite in seen | step_slugs, (slug, prerequisite)
        seen |= step_slugs


def test_queue_lists_every_page_once_with_prerequisites_first():
    slugs = [slug for slug, _ in queue()]
    assert sorted(slugs) == sorted(page_slugs())
    assert len(slugs) == len(set(slugs))
    position = {slug: index for index, slug in enumerate(slugs)}
    for page in leetcode_docs.PAGES:
        for prerequisite in page["prerequisites"]:
            assert position[prerequisite] < position[page["slug"]], (page["slug"], prerequisite)


def test_queue_marks_match_the_registry():
    ready = {page["slug"] for page in leetcode_docs.ready_pages()}
    entries = queue()
    for slug, rest in entries:
        assert ("✓" in rest) == (slug in ready), slug
    next_marks = [slug for slug, rest in entries if "← next" in rest]
    unbuilt = [slug for slug, _ in entries if slug not in ready]
    assert next_marks == unbuilt[:1]


def test_problems_are_well_formed():
    list_slugs = {entry["slug"] for entry in leetcode_docs.LISTS}
    numbers = [problem["number"] for problem in leetcode_docs.PROBLEMS]
    assert len(numbers) == len(set(numbers))
    for problem in leetcode_docs.PROBLEMS:
        assert isinstance(problem["number"], int) and problem["number"] > 0
        assert problem["title"].strip()
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", problem["slug"]), problem["number"]
        assert problem["difficulty"] in {"Easy", "Medium", "Hard"}
        assert problem["lists"] and set(problem["lists"]) <= list_slugs, problem["number"]
        assert problem["home"] in page_slugs(), problem["number"]
        assert set(problem["patterns"]) <= set(page_slugs()), problem["number"]
        assert problem["home"] not in problem["patterns"], problem["number"]
        assert problem["insight"].strip(), problem["number"]


def test_each_list_is_empty_or_complete():
    for entry in leetcode_docs.LISTS:
        count = sum(1 for problem in leetcode_docs.PROBLEMS if entry["slug"] in problem["lists"])
        assert count in (0, entry["size"]), (entry["slug"], count)


def test_problem_url():
    assert leetcode_docs.problem_url("two-sum") == "https://leetcode.com/problems/two-sum/"


def test_coverage_counts_only_ready_homes(monkeypatch):
    pages = [{**page, "ready": False} for page in leetcode_docs.PAGES]
    pages[0]["ready"] = True
    problems = [
        {"number": 1, "home": pages[0]["slug"], "lists": ["blind-75", "neetcode-150"]},
        {"number": 2, "home": pages[1]["slug"], "lists": ["blind-75"]},
    ]
    monkeypatch.setattr(leetcode_docs, "PAGES", pages)
    monkeypatch.setattr(leetcode_docs, "PROBLEMS", problems)
    by_list = {entry["slug"]: entry for entry in leetcode_docs.coverage()}
    assert (by_list["blind-75"]["known"], by_list["blind-75"]["covered"]) == (2, 1)
    assert (by_list["neetcode-150"]["known"], by_list["neetcode-150"]["covered"]) == (1, 1)
    assert by_list["grind-169"]["covered"] == 0
    assert by_list["neetcode-250"]["known"] == 0


def test_index_renders_every_area_and_page():
    body = app_module.app.test_client().get("/leetcode").get_data(as_text=True)
    for area in leetcode_docs.AREAS:
        assert f'id="area-{area["slug"]}"' in body
    for page in leetcode_docs.PAGES:
        assert page["title"].replace("'", "&#39;") in body
    for entry in leetcode_docs.LISTS:
        assert entry["title"] in body


def test_not_ready_pages_404():
    client = app_module.app.test_client()
    for page in leetcode_docs.PAGES:
        if not page["ready"]:
            assert client.get(f"/leetcode/{page['slug']}").status_code == 404


def test_every_ready_page_has_a_template():
    for page in leetcode_docs.ready_pages():
        assert os.path.exists(os.path.join(TEMPLATES_DIR, f"{page['slug']}.html")), page["slug"]


@pytest.mark.parametrize("url", ready_urls())
def test_ready_page_follows_the_format(url):
    body = app_module.app.test_client().get(url).get_data(as_text=True)
    ids = re.findall(r'<h2 id="([^"]+)"', body)
    assert ids == FORMAT_SECTIONS, url
    assert SIGNALS_HEADER in re.sub(r">\s+<", "><", body), url
    svgs = re.findall(r"<svg\b[^>]*>.*?</svg>", body, re.S)
    assert len(svgs) >= 2, url
    for svg in svgs:
        assert 'role="img"' in svg and "<title" in svg and "<desc" in svg, url


@pytest.mark.parametrize("url", ["/leetcode"] + ready_urls())
def test_internal_links_point_at_ready_pages(url):
    body = app_module.app.test_client().get(url).get_data(as_text=True)
    ready = {page["slug"] for page in leetcode_docs.ready_pages()}
    for slug in re.findall(r'href="/leetcode/([^"#?]+)', body):
        assert slug in ready, (url, slug)


def test_ready_pages_list_their_home_problems():
    for page in leetcode_docs.ready_pages():
        body = app_module.app.test_client().get(f"/leetcode/{page['slug']}").get_data(as_text=True)
        for problem in leetcode_docs.problems_for(page["slug"]):
            assert leetcode_docs.problem_url(problem["slug"]) in body, (page["slug"], problem["number"])


def test_no_new_server_dependencies():
    for name in ("requirements.txt", "requirements-dev.txt"):
        with open(os.path.join(ROOT, "backend", name), encoding="utf-8") as handle:
            text = handle.read().lower()
        for package in ("numpy", "networkx", "sortedcontainers", "leetcode"):
            assert package not in text, (name, package)


def test_complexity_helpers_match_the_page():
    rows = leetcode_docs.doubling_append_costs(9)
    assert [row["cost"] for row in rows] == [1, 2, 3, 1, 5, 1, 1, 1, 9]
    assert [row["capacity"] for row in rows] == [1, 2, 4, 4, 8, 8, 8, 8, 16]
    assert rows[-1]["total"] == 24
    body = app_module.app.test_client().get("/leetcode/complexity-analysis").get_data(as_text=True)
    for row in rows:
        assert f'<td class="num">{row["total"]}</td>' in body
    assert f'{rows[-1]["average"]:.2f}' in body
    for entry in leetcode_docs.budget_table():
        assert f"{entry['max_n']:,}" in body
    assert leetcode_docs.nested_pair_count(5) == 10
    assert leetcode_docs.halving_steps(1024) == 10


def test_budget_table_is_monotone_and_within_budget():
    table = leetcode_docs.budget_table(10 ** 8)
    sizes = [entry["max_n"] for entry in table]
    assert sizes == sorted(sizes, reverse=True)
    assert dict((e["name"], e["max_n"]) for e in table)["O(n²)"] == 10_000
    assert leetcode_docs.max_input_size(lambda n: n * n, 100) == 10


def test_growth_rows():
    row = leetcode_docs.growth_rows([8])[0]
    assert (row["log"], row["linear"], row["nlogn"], row["quadratic"], row["exponential"]) == (3, 8, 24, 64, 256)


def test_toolkit_helpers_match_the_page():
    trace = leetcode_docs.heap_push_trace([5, 3, 8, 1, 9, 2])
    assert trace["final"] == [1, 3, 2, 5, 9, 8]
    assert trace["pop_order"] == [1, 2, 3, 5, 8, 9]
    assert [row["heap"] for row in trace["rows"]][:4] == [[5], [3, 5], [3, 5, 8], [1, 3, 8, 5]]
    for index in range(1, len(trace["final"])):
        assert trace["final"][(index - 1) // 2] <= trace["final"][index]
    search = leetcode_docs.bisect_left_steps([1, 3, 5, 7, 9, 11, 13, 15], 11)
    assert [(s["low"], s["high"], s["middle"], s["value"]) for s in search["steps"]] == [
        (0, 8, 4, 9), (5, 8, 6, 13), (5, 6, 5, 11)]
    assert search["index"] == 5 and search["matches_bisect"]
    assert leetcode_docs.bisect_left_steps([1, 2], 5)["index"] == 2
    assert leetcode_docs.bisect_left_steps([], 5)["steps"] == []
    assert leetcode_docs.front_removal_moves(8) == {"list": 28, "deque": 0}
    body = app_module.app.test_client().get("/leetcode/python-toolkit").get_data(as_text=True)
    assert "[1, 3, 2, 5, 9, 8]" in body
    assert "1, 2, 3, 5, 8, 9" in body
    assert "index 5, reached in 3 probes" in re.sub(r"\s+", " ", body)
    assert "moves 28 elements" in re.sub(r"\s+", " ", body)


def test_recursion_helpers_match_the_page():
    counts = [leetcode_docs.fib_call_counts(n) for n in range(1, 9)]
    assert [c["naive"] for c in counts] == [1, 3, 5, 9, 15, 25, 41, 67]
    assert [c["memo"] for c in counts] == [1, 3, 5, 7, 9, 11, 13, 15]
    assert [c["value"] for c in counts] == [1, 1, 2, 3, 5, 8, 13, 21]
    tree = leetcode_docs.fib_call_tree(5)
    assert len(tree) == 15 and tree[0]["value"] == 5
    assert sum(1 for node in tree if node["n"] == 3) == 2
    assert all(tree[node["parent"]]["depth"] == node["depth"] - 1 for node in tree if node["parent"] is not None)
    trace = leetcode_docs.fast_power_trace(2, 10)
    assert trace["value"] == 1024 and trace["max_depth"] == 5
    calls = [e["exponent"] for e in trace["events"] if e["event"] == "call"]
    assert calls == [10, 5, 2, 1, 0]
    assert [e["value"] for e in trace["events"] if e["event"] == "return"] == [1, 2, 4, 32, 1024]
    assert leetcode_docs.fast_power_trace(3, 0)["value"] == 1
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/recursion").get_data(as_text=True))
    assert "<td class=\"num\">1024</td>" in body
    assert "found with 5 calls and a stack at most 5 frames deep" in body
    assert "15 calls naive, 9 with memoization" in body
