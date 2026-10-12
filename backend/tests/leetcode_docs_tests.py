import heapq
import itertools
import math
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
    worked = body.split('<h2 id="worked-example"', 1)[1].split('<h2 id="implementation"', 1)[0]
    assert "<table" in worked, url
    references = body.split('<h2 id="references"', 1)[1]
    for author in ("Cormen", "Skiena", "Sedgewick", "NeetCode"):
        assert author in references, (url, author)
    assert 3 <= body.count('class="lc-quiz"') <= 4, url


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


def test_hash_helpers_match_the_page():
    trace = leetcode_docs.two_sum_trace([11, 3, 15, 8, 2, 7], 9)
    assert trace["pair"] == (4, 5)
    assert [s["need"] for s in trace["steps"]] == [-2, 6, -6, 1, 7, 2]
    assert [s["hit"] for s in trace["steps"]] == [False] * 5 + [True]
    assert trace["steps"][3]["seen"] == {11: 0, 3: 1, 15: 2}
    assert leetcode_docs.two_sum_trace([1, 2], 10)["pair"] is None
    assert leetcode_docs.two_sum_trace([3, 3], 6)["pair"] == (0, 1)
    buckets = leetcode_docs.bucket_layout([15, 22, 8, 31, 7, 14, 29, 15], 7)
    assert buckets == [[7, 14], [15, 22, 8, 29], [], [31], [], [], []]
    runs = leetcode_docs.consecutive_runs([100, 4, 200, 1, 3, 2, 101, 5, 102])
    assert runs["runs"] == [{"start": 1, "length": 5}, {"start": 100, "length": 3}, {"start": 200, "length": 1}]
    assert (runs["best"], runs["lookups"], runs["unique"]) == (5, 18, 9)
    assert leetcode_docs.consecutive_runs([])["best"] == 0
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/hash-maps-and-sets").get_data(as_text=True))
    assert "returns indices 4 and 5, after 6 lookups" in body
    assert "up to 15 pairs" in body
    assert "18 set lookups for 9 distinct numbers" in body
    assert "one chain of 4 keys" in body


def test_counting_helpers_match_the_page():
    anagram = leetcode_docs.letter_count_rows("listen", "silent")
    assert anagram["anagram"] and len(anagram["rows"]) == 6
    rows = leetcode_docs.letter_count_rows("rat", "car")
    assert not rows["anagram"]
    assert [r["letter"] for r in rows["rows"] if not r["equal"]] == ["c", "t"]
    vote = leetcode_docs.majority_vote_trace([2, 2, 1, 1, 1, 2, 2])
    assert [(s["candidate"], s["count"]) for s in vote["steps"]] == [
        (2, 1), (2, 2), (2, 1), (2, 0), (1, 1), (1, 0), (2, 1)]
    assert vote["candidate"] == 2 and vote["occurrences"] == 4 and vote["is_majority"]
    assert not leetcode_docs.majority_vote_trace([1, 2, 3])["is_majority"]
    freq = leetcode_docs.frequency_buckets([4, 1, 2, 1, 4, 3, 4, 2, 4, 1, 5], 2)
    assert freq["counts"] == {4: 4, 1: 3, 2: 2, 3: 1, 5: 1}
    assert freq["buckets"][1:5] == [[3, 5], [2], [1], [4]] and freq["top"] == [4, 1]
    assert leetcode_docs.anagram_groups(["eat", "tea", "tan", "ate", "nat", "bat"]) == {
        "aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"]}
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/counting-and-bucketing").get_data(as_text=True))
    assert "they are anagrams" in body
    assert "differ for 2 of 4 letters" in body
    assert "counts 4 occurrences in 7 elements, a majority" in body
    assert "<code>aet</code></td><td>eat, tea, ate</td>" in body
    assert "4 and 1. The scan stops" in body


def test_prefix_helpers_match_the_page():
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    prefix = leetcode_docs.prefix_table(nums)
    assert prefix == [0, 3, 4, 8, 9, 14, 23, 25, 31]
    assert [leetcode_docs.range_sum(prefix, l, r) for l, r in [(0, 7), (2, 5), (3, 3), (4, 6)]] == [31, 19, 1, 16]
    assert leetcode_docs.prefix_table([]) == [0]
    trace = leetcode_docs.subarray_sum_trace([3, 4, 7, 2, -3, 1, 4, 2], 7)
    assert [s["running"] for s in trace["steps"]] == [3, 7, 14, 16, 13, 14, 18, 20]
    assert [s["found"] for s in trace["steps"]] == [0, 1, 1, 0, 0, 1, 0, 1]
    assert trace["total"] == 4
    assert leetcode_docs.subarray_sum_trace([0, 0], 0)["total"] == 3
    products = leetcode_docs.product_except_self([1, 2, 3, 4])
    assert products == {"left": [1, 1, 2, 6], "right": [24, 12, 4, 1], "result": [24, 12, 8, 6]}
    assert leetcode_docs.product_except_self([1, 0, 3])["result"] == [0, 3, 0]
    grid = [[3, 0, 1, 4], [5, 6, 3, 2], [1, 2, 0, 1], [4, 1, 0, 1]]
    table = leetcode_docs.prefix_table_2d(grid)
    assert table[4] == [0, 13, 22, 26, 34]
    assert leetcode_docs.rectangle_sum(table, 1, 1, 2, 2) == 11
    assert leetcode_docs.rectangle_sum(table, 0, 0, 3, 3) == 34
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/prefix-sums").get_data(as_text=True))
    assert "<td class=\"num\">[2..5]</td><td class=\"num\">23 − 4</td><td class=\"num\">19</td>" in body
    assert "There are 4 such subarrays" in body
    assert "<code>[24, 12, 8, 6]</code>" in body
    assert "21 − 4 − 9 + 3 = 11" in body


def test_in_place_helpers_match_the_page():
    trace = leetcode_docs.compact_trace([3, 2, 2, 3, 4, 2, 5], 2)
    assert trace["length"] == 4 and trace["result"] == [3, 3, 4, 5]
    assert [s["write"] for s in trace["steps"]] == [1, 1, 1, 2, 3, 3, 4]
    assert leetcode_docs.compact_trace([], 1)["length"] == 0
    stages = leetcode_docs.rotate_stages([1, 2, 3, 4, 5, 6, 7], 3)
    assert stages[1][1] == [7, 6, 5, 4, 3, 2, 1] and stages[3][1] == [5, 6, 7, 1, 2, 3, 4]
    assert leetcode_docs.rotate_stages([1, 2], 5)[-1][1] == [2, 1]
    perm = leetcode_docs.next_permutation_steps([1, 3, 5, 4, 2])
    assert (perm["pivot"], perm["partner"]) == (1, 3)
    assert perm["swapped"] == [1, 4, 5, 3, 2] and perm["result"] == [1, 4, 2, 3, 5]
    assert leetcode_docs.next_permutation_steps([3, 2, 1])["result"] == [1, 2, 3]
    cyc = leetcode_docs.cyclic_placement_trace([3, 4, -1, 1])
    assert len(cyc["swaps"]) == 3 and cyc["placed"] == [1, -1, 3, 4] and cyc["missing"] == 2
    assert leetcode_docs.cyclic_placement_trace([1, 1])["missing"] == 2
    assert leetcode_docs.cyclic_placement_trace([1, 2, 3])["missing"] == 4
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/in-place-array-tricks").get_data(as_text=True))
    assert "The new length is 4 and the kept prefix is <code>[3, 3, 4, 5]</code>" in body
    assert "<code>[1, 4, 2, 3, 5]</code>" in body
    assert "takes 3 swaps and leaves <code>[1, -1, 3, 4]</code>" in body
    assert "<td class=\"num\">[5, 6, 7, 1, 2, 3, 4]</td>" in body


def test_two_pointer_helpers_match_the_page():
    pair = leetcode_docs.converging_pair_trace([1, 3, 4, 6, 8, 11, 15], 14)
    assert [s["action"] for s in pair["steps"]] == ["move right", "move left", "found"]
    assert pair["pair"] == (1, 5)
    assert leetcode_docs.converging_pair_trace([1, 2], 10)["pair"] is None
    box = leetcode_docs.container_trace([1, 8, 6, 2, 5, 4, 8, 3, 7])
    assert box["best"] == 49 and [s["area"] for s in box["steps"]] == [8, 49, 18, 40, 24, 6, 10, 4]
    assert leetcode_docs.container_trace([5])["best"] == 0
    three = leetcode_docs.three_sum_triples([-1, 0, 1, 2, -1, -4, -1])
    assert three["sorted"] == [-4, -1, -1, -1, 0, 1, 2]
    assert three["triples"] == [(-1, -1, 2), (-1, 0, 1)]
    assert leetcode_docs.three_sum_triples([0, 0, 0, 0])["triples"] == [(0, 0, 0)]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/two-pointers").get_data(as_text=True))
    assert "3 comparisons instead of 21 pairs" in body
    assert "The answer is 49." in body
    assert "<code>[-1, -1, 2]</code>, <code>[-1, 0, 1]</code>" in body


def test_fixed_window_helpers_match_the_page():
    win = leetcode_docs.window_sum_trace([2, 1, 5, 1, 3, 2, 9, 1], 3)
    assert [s["sum"] for s in win["steps"]] == [8, 7, 9, 6, 14, 12] and win["best"] == 14
    assert [s["leaving"] for s in win["steps"]] == [None, 2, 1, 5, 1, 3]
    assert leetcode_docs.window_sum_trace([1], 3) == {"steps": [], "best": None}
    ana = leetcode_docs.anagram_window_trace("cbaebabacd", "abc")
    assert ana["starts"] == [0, 6]
    assert [s["differing"] for s in ana["steps"]] == [0, 2, 2, 2, 2, 2, 0, 2]
    assert leetcode_docs.anagram_window_trace("ab", "abc")["starts"] == []
    dup = leetcode_docs.near_duplicate_trace([4, 7, 9, 4, 2], 3)
    assert dup["found"] == 3 and dup["steps"][-1]["window"] == [4, 7, 9]
    assert leetcode_docs.near_duplicate_trace([1, 2, 3, 1, 2, 3], 2)["found"] is None
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/fixed-size-window").get_data(as_text=True))
    assert "The best is 14, found with 6 constant-time updates instead of 18 additions." in body
    assert "The counter reaches zero at starts 0 and 6." in body
    assert "The repeat is found at index 3" in body


def test_variable_window_helpers_match_the_page():
    uniq = leetcode_docs.longest_unique_trace("abcbdace")
    assert [s["left"] for s in uniq["steps"]] == [0, 0, 0, 2, 2, 2, 3, 3]
    assert uniq["best"] == 5 and uniq["best_window"] == "bdace"
    assert leetcode_docs.longest_unique_trace("") == {"steps": [], "best": 0, "best_window": ""}
    assert leetcode_docs.longest_unique_trace("aaaa")["best"] == 1
    sub = leetcode_docs.shortest_subarray_trace(11, [3, 1, 4, 1, 2, 9, 1, 6])
    assert [s["length"] for s in sub["steps"]] == [5, 5, 4, 3, 2, 3]
    assert sub["best"] == 2 and sub["span"] == (4, 5)
    assert leetcode_docs.shortest_subarray_trace(100, [1, 2]) == {"steps": [], "best": 0, "span": None}
    rep = leetcode_docs.replacement_window_trace("ABAABCBBA", 2)
    assert [s["cost"] for s in rep["steps"]] == [0, 1, 1, 1, 2, 2, 2, 2, 2] and rep["best"] == 5
    assert all(s["cost"] <= 2 for s in rep["steps"])
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/variable-size-window").get_data(as_text=True))
    assert "The longest window is bdace, 5 letters" in body
    assert "The shortest valid run is 2 long, at indices 4 to 5." in body
    assert "The best window is 5 letters long." in body


def test_stack_helpers_match_the_page():
    good = leetcode_docs.bracket_trace("{[()()]}")
    assert good["valid"] and good["left_over"] == []
    assert [s["action"] for s in good["steps"]] == ["push", "push", "push", "pop", "push", "pop", "pop", "pop"]
    bad = leetcode_docs.bracket_trace("([)]")
    assert not bad["valid"] and bad["failure"] == {"index": 2, "char": ")", "top": "["}
    assert leetcode_docs.bracket_trace("((")["left_over"] == ["(", "("]
    assert leetcode_docs.bracket_trace(")")["failure"]["top"] is None
    ms = leetcode_docs.min_stack_trace([("push", 5), ("push", 3), ("push", 7), ("push", 2), ("pop",), ("pop",), ("push", 4)])
    assert [s["min"] for s in ms["steps"]] == [5, 3, 3, 2, 3, 3, 3]
    rpn = leetcode_docs.rpn_trace(["8", "3", "2", "*", "-", "10", "5", "/", "+"])
    assert rpn["result"] == 4 and rpn["steps"][3]["applied"] == "3 * 2 = 6"
    assert leetcode_docs.rpn_trace(["7", "-2", "/"])["result"] == -3
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/stack").get_data(as_text=True))
    assert "The stack is empty at the end, so {[()()]} is valid." in body
    assert "arrives while the top is <code>[</code>" in body
    assert "The result is 4." in body


def test_monotonic_stack_helpers_match_the_page():
    warm = leetcode_docs.next_warmer_trace([68, 71, 65, 64, 70, 66, 72])
    assert warm["waits"] == [1, 5, 2, 1, 2, 1, 0]
    assert [s["stack"] for s in warm["steps"]][-1] == [6]
    assert leetcode_docs.next_warmer_trace([5, 4, 3])["waits"] == [0, 0, 0]
    hist = leetcode_docs.histogram_trace([3, 1, 4, 5, 3, 2, 1])
    assert hist["best"] == 9 and hist["best_pop"]["left"] == 2 and hist["best_pop"]["right"] == 4
    assert leetcode_docs.histogram_trace([])["best"] == 0
    assert leetcode_docs.histogram_trace([2, 2, 2])["best"] == 6
    win = leetcode_docs.window_max_trace([4, 2, 12, 3, 8, 1, 6], 3)
    assert win["maxima"] == [12, 12, 12, 8, 8]
    assert leetcode_docs.window_max_trace([1, 2], 3)["maxima"] == []
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/monotonic-stack").get_data(as_text=True))
    assert "The waits are 1, 5, 2, 1, 2, 1, 0" in body
    assert "The largest area is 9, the rectangle of height 3 over bars 2 to 4." in body
    assert "The window maxima are 12, 12, 12, 8, 8." in body


def test_binary_search_helpers_match_the_page():
    nums = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    lb = leetcode_docs.lower_bound_trace(nums, 23)
    assert lb["index"] == 5 and lb["found"] and [s["mid"] for s in lb["steps"]] == [5, 2, 4]
    assert leetcode_docs.lower_bound_trace(nums, 20)["index"] == 5
    assert not leetcode_docs.lower_bound_trace(nums, 20)["found"]
    assert leetcode_docs.lower_bound_trace(nums, 100)["index"] == 10
    assert leetcode_docs.lower_bound_trace([], 1) == {"steps": [], "index": 0, "found": False}
    rot = [15, 19, 23, 38, 2, 5, 8, 12]
    assert leetcode_docs.rotated_search_trace(rot, 5)["index"] == 5
    assert leetcode_docs.rotated_search_trace(rot, 6)["index"] == -1
    assert all(leetcode_docs.rotated_search_trace(rot, v)["index"] == i for i, v in enumerate(rot))
    mn = leetcode_docs.rotated_min_trace(rot)
    assert mn["index"] == 4 and mn["value"] == 2 and len(mn["steps"]) == 3
    assert leetcode_docs.rotated_min_trace([1, 2, 3])["index"] == 0
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/binary-search").get_data(as_text=True))
    assert "The search stops at index 5, and 23 equals the target" in body
    assert "Searching for 20 instead stops at index 5" in body
    assert "The value 5 is at index 5." in body
    assert "The minimum is 2 at index 4." in body


def test_binary_search_on_answer_helpers_match_the_page():
    koko = leetcode_docs.min_speed_trace([3, 6, 7, 11], 8)
    assert koko["answer"] == 4 and [s["mid"] for s in koko["steps"]] == [6, 3, 5, 4]
    assert leetcode_docs.eating_hours([3, 6, 7, 11], 4) == 8
    assert leetcode_docs.min_speed_trace([5], 5)["answer"] == 1
    ship = leetcode_docs.ship_capacity_trace(list(range(1, 11)), 5)
    assert ship["answer"] == 15 and leetcode_docs.days_needed(list(range(1, 11)), 15) == 5
    assert leetcode_docs.days_needed(list(range(1, 11)), 14) == 6
    med = leetcode_docs.median_partition_trace([1, 3, 8, 9, 15], [7, 11, 18, 19, 21, 25])
    assert med["median"] == 11 and med["steps"][-1]["i"] == 4 and med["steps"][-1]["j"] == 2
    assert leetcode_docs.median_partition_trace([1, 2], [3, 4])["median"] == 2.5
    assert leetcode_docs.median_partition_trace([], [2])["median"] == 2
    assert leetcode_docs.median_partition_trace([2], [1, 3])["median"] == 2
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/binary-search-on-answer").get_data(as_text=True))
    assert "The slowest speed that finishes in time is 4." in body
    assert "The smallest capacity that works is 15." in body
    assert "the median is the largest value on the left: 11." in body


def test_linked_list_helpers_match_the_page():
    rev = leetcode_docs.reverse_list_trace([1, 2, 3, 4, 5])
    assert rev["result"] == [5, 4, 3, 2, 1] and rev["steps"][1]["remaining"] == [3, 4, 5]
    assert leetcode_docs.reverse_list_trace([])["result"] == []
    mer = leetcode_docs.merge_sorted_trace([1, 4, 6, 9], [2, 3, 7])
    assert mer["result"] == [1, 2, 3, 4, 6, 7, 9] and mer["leftover"] == [9]
    assert leetcode_docs.merge_sorted_trace([], [1, 2])["result"] == [1, 2]
    rm = leetcode_docs.remove_nth_from_end_trace([1, 2, 3, 4, 5], 2)
    assert rm["result"] == [1, 2, 3, 5] and rm["removed"] == 4 and rm["steps"][-1]["trailer"] == 2
    assert leetcode_docs.remove_nth_from_end_trace([1, 2, 3], 3)["result"] == [2, 3]
    assert leetcode_docs.remove_nth_from_end_trace([7], 1)["result"] == []
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/linked-list-basics").get_data(as_text=True))
    assert "The reversed list is 5, 4, 3, 2, 1." in body
    assert "The merged list is 1, 2, 3, 4, 6, 7, 9." in body
    assert "so the node after it, holding 4, is cut. The list becomes 1, 2, 3, 5." in body


def test_fast_slow_pointer_helpers_match_the_page():
    nxt = [1, 2, 3, 4, 5, 6, 7, 3]
    fl = leetcode_docs.floyd_trace(nxt)
    assert fl["has_cycle"] and fl["meeting"] == 5 and fl["entrance"] == 3
    assert fl["tail_length"] == 3 and fl["cycle_length"] == 5
    assert (len(fl["steps"]) - 1) % fl["cycle_length"] == 0
    assert not leetcode_docs.floyd_trace([1, 2, 3, -1])["has_cycle"]
    assert not leetcode_docs.floyd_trace([-1])["has_cycle"]
    self_loop = leetcode_docs.floyd_trace([0])
    assert self_loop["entrance"] == 0 and self_loop["tail_length"] == 0 and self_loop["cycle_length"] == 1
    dup = leetcode_docs.floyd_trace([3, 1, 3, 4, 2])
    assert dup["entrance"] == 3 and dup["meeting"] == 2
    assert leetcode_docs.middle_trace(7)["middle"] == 3
    assert leetcode_docs.middle_trace(6)["middle"] == 3
    assert leetcode_docs.middle_trace(1)["middle"] == 0
    with pytest.raises(ValueError):
        leetcode_docs.middle_trace(0)
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/fast-slow-pointers").get_data(as_text=True))
    assert "They meet at node 5 after 5 turns" in body
    assert "the cycle begins at node 3, the tail has 3 nodes and the loop has 5." in body
    assert "The entrance is 3, and that is the repeated value" in body


def test_linked_list_design_helpers_match_the_page():
    ops = [["put", "a", 1], ["put", "b", 2], ["put", "c", 3], ["get", "a"], ["put", "d", 4], ["get", "b"],
           ["put", "c", 30], ["put", "e", 5], ["get", "a"], ["get", "d"]]
    lru = leetcode_docs.lru_trace(3, ops)
    assert lru[3]["result"] == 1 and lru[3]["order"] == ["a", "c", "b"]
    assert lru[4]["evicted"] == "b" and lru[5]["result"] == -1
    assert lru[6]["evicted"] is None and lru[6]["order"] == ["c", "d", "a"]
    assert lru[7]["evicted"] == "a" and lru[-1]["order"] == ["d", "e", "c"] and lru[-1]["result"] == 4
    assert leetcode_docs.lru_trace(1, [["put", 1, 1], ["put", 2, 2], ["get", 1]])[-1]["result"] == -1
    cr = leetcode_docs.copy_random_trace([2, 0, 4, -1, 1])
    assert cr["copies"] == [0, 1, 2, 3, 4]
    assert cr["wires"][3] == {"node": 3, "next": 4, "random": None}
    assert cr["wires"][4] == {"node": 4, "next": None, "random": 1}
    assert leetcode_docs.copy_random_trace([])["wires"] == []
    pushes = [["push", v] for v in [4, 6, 4, 8, 6, 4]]
    fq = leetcode_docs.freq_stack_trace(pushes + [["pop"]] * 4)
    assert fq[5]["levels"] == [[4, 6, 8], [4, 6], [4]] and fq[5]["counts"] == {4: 3, 6: 2, 8: 1}
    assert [step["popped"] for step in fq[6:]] == [4, 6, 4, 8]
    with pytest.raises(ValueError):
        leetcode_docs.freq_stack_trace([["pop"]])
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/linked-list-design").get_data(as_text=True))
    assert "The first eviction is key b" in body
    assert "After the last step the cache holds d, e, c." in body
    assert "The pops return 4, 6, 4, 8." in body


def test_tree_dfs_helpers_match_the_page():
    tree = [5, [3, [1, None, [2, None, None]], [4, None, None]], [8, None, [9, None, None]]]
    orders = leetcode_docs.tree_orders(tree)
    assert orders["preorder"] == [5, 3, 1, 2, 4, 8, 9]
    assert orders["inorder"] == [1, 2, 3, 4, 5, 8, 9]
    assert orders["postorder"] == [2, 1, 4, 3, 9, 8, 5]
    ht = leetcode_docs.tree_height_trace(tree)
    assert ht["depth"] == 4 and ht["diameter"] == 5
    assert ht["steps"][-1]["node"] == 5 and ht["steps"][-1]["height"] == 4
    lay = leetcode_docs.tree_layout(tree)
    assert len(lay["nodes"]) == 7 and len(lay["edges"]) == 6
    path_tree = [6, [-3, [5, None, None], [2, None, None]], [4, [-1, None, None], None]]
    assert leetcode_docs.max_path_sum_trace(path_tree)["best"] == 12
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/tree-dfs").get_data(as_text=True))
    assert "so the tree has depth 4" in body
    assert "so the diameter is 5." in body
    assert "The best bent path sum is 12." in body


def test_tree_bfs_helpers_match_the_page():
    tree = [5, [3, [1, None, [2, None, None]], [4, None, None]], [8, None, [9, None, None]]]
    info = leetcode_docs.tree_bfs_info(tree)
    assert info["levels"] == [[5], [3, 8], [1, 4, 9], [2]]
    assert info["order"] == [5, 3, 8, 1, 4, 9, 2]
    assert info["right_view"] == [5, 8, 9, 2]
    assert info["zigzag"] == [[5], [8, 3], [1, 4, 9], [2]]
    assert info["widths"] == [1, 2, 4, 1] and info["max_width"] == 4
    assert leetcode_docs.tree_bfs_info([1, None, None])["levels"] == [[1]]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/tree-bfs").get_data(as_text=True))
    assert "The right-side view is 5, 8, 9, 2." in body
    assert "The zigzag order is 5 | 8, 3 | 1, 4, 9 | 2." in body
    assert "so the maximum width is 4." in body


def test_bst_helpers_match_the_page():
    bst = [8, [3, [1, None, None], [6, [4, None, None], [7, None, None]]], [10, None, [14, [13, None, None], None]]]
    assert leetcode_docs.tree_orders(bst)["inorder"] == [1, 3, 4, 6, 7, 8, 10, 13, 14]
    assert leetcode_docs.bst_validate_trace(bst)["valid"] is True
    bad = [5, [1, None, None], [4, [3, None, None], [6, None, None]]]
    trace = leetcode_docs.bst_validate_trace(bad)
    assert trace["valid"] is False
    assert [(s["node"], s["low"], s["high"], s["ok"]) for s in trace["steps"]] == [
        (5, None, None, True), (1, None, 5, True), (4, 5, None, False)]
    leaky = [5, [1, None, None], [6, [3, None, None], [7, None, None]]]
    assert leetcode_docs.bst_validate_trace(leaky)["valid"] is False
    kth = leetcode_docs.bst_kth_smallest(bst, 4)
    assert kth["value"] == 6 and kth["visited"] == [1, 3, 4, 6]
    assert leetcode_docs.bst_kth_smallest(bst, 10)["value"] is None
    assert leetcode_docs.bst_lca_path(bst, 4, 7) == {"path": [8, 3, 6], "ancestor": 6}
    assert leetcode_docs.bst_lca_path(bst, 1, 13)["ancestor"] == 8
    after_leaf = leetcode_docs.bst_delete(bst, 13)
    assert leetcode_docs.tree_orders(after_leaf)["inorder"] == [1, 3, 4, 6, 7, 8, 10, 14]
    after_two = leetcode_docs.bst_delete(bst, 3)
    assert after_two[1][0] == 4 and leetcode_docs.tree_orders(after_two)["inorder"] == [1, 4, 6, 7, 8, 10, 13, 14]
    assert leetcode_docs.bst_delete(bst, 99) == bst
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/binary-search-trees").get_data(as_text=True))
    assert "The 4th smallest value is 6" in body
    assert "so the lowest common ancestor is 6." in body
    assert "fails its interval (5, +inf)" in body


def test_tree_construction_helpers_match_the_page():
    built = leetcode_docs.build_from_traversals([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert built["tree"] == [3, [9, None, None], [20, [15, None, None], [7, None, None]]]
    assert built["steps"][0] == {"root": 3, "left": [9], "right": [15, 20, 7]}
    assert [s["root"] for s in built["steps"]] == [3, 9, 20, 15, 7]
    orders = leetcode_docs.tree_orders(built["tree"])
    assert orders["preorder"] == [3, 9, 20, 15, 7] and orders["inorder"] == [9, 3, 15, 20, 7]
    tokens = leetcode_docs.tree_serialize(built["tree"])
    assert tokens == ["3", "9", "#", "#", "20", "15", "#", "#", "7", "#", "#"]
    assert leetcode_docs.tree_deserialize(tokens) == built["tree"]
    assert leetcode_docs.tree_serialize(None) == ["#"] and leetcode_docs.tree_deserialize(["#"]) is None
    negative = [-1, [-2, None, None], None]
    assert leetcode_docs.tree_deserialize(leetcode_docs.tree_serialize(negative)) == negative
    balanced = leetcode_docs.sorted_array_to_tree([-10, -3, 0, 5, 9])
    assert balanced == [0, [-3, [-10, None, None], None], [9, [5, None, None], None]]
    assert leetcode_docs.tree_orders(balanced)["inorder"] == [-10, -3, 0, 5, 9]
    assert leetcode_docs.tree_height_trace(balanced)["depth"] == 3
    assert leetcode_docs.sorted_array_to_tree([]) is None
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/tree-construction").get_data(as_text=True))
    assert "The serialized string has 11 tokens for 5 nodes" in body
    assert "middle element 0 becomes the root" in body


def test_trie_helpers_match_the_page():
    words = ["car", "card", "care", "cat", "do", "dog"]
    layout = leetcode_docs.trie_layout(words)
    assert len(layout["nodes"]) == 10 and layout["letters"] == 19
    assert layout["columns"] == 4 and layout["levels"] == 5
    assert sum(1 for n in layout["nodes"] if n["end"]) == len(words)
    assert leetcode_docs.trie_lookup(words, "car") == {"matched": 3, "is_word": True, "is_prefix": True}
    assert leetcode_docs.trie_lookup(words, "ca") == {"matched": 2, "is_word": False, "is_prefix": True}
    assert leetcode_docs.trie_lookup(words, "cow") == {"matched": 1, "is_word": False, "is_prefix": False}
    assert leetcode_docs.trie_lookup(words, "") == {"matched": 0, "is_word": False, "is_prefix": True}
    assert leetcode_docs.trie_words_under(words, "car") == ["car", "card", "care"]
    assert leetcode_docs.trie_words_under(words, "x") == []
    assert leetcode_docs.trie_wildcard_trace(words, "ca.") == {"found": True, "visited": 3}
    assert leetcode_docs.trie_wildcard_trace(words, "..g") == {"found": True, "visited": 5}
    assert leetcode_docs.trie_wildcard_trace(words, "c.x") == {"found": False, "visited": 2}
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/tries").get_data(as_text=True))
    assert "9 letter nodes for 19 letters" in body
    assert "enters 5 nodes before it finds" in body


def test_heap_helpers_match_the_page():
    values = [7, 3, 9, 1, 5, 2]
    pushed = leetcode_docs.heap_build_trace(values)
    expected = []
    for value in values:
        heapq.heappush(expected, value)
    assert pushed["heap"] == expected == [1, 3, 2, 7, 5, 9]
    assert [s["swaps"] for s in pushed["steps"]] == [0, 1, 0, 2, 0, 1]
    popped = leetcode_docs.heap_pop_trace(pushed["heap"])
    after = list(expected)
    assert heapq.heappop(after) == popped["popped"] == 1
    assert popped["heap"] == after == [2, 3, 9, 7, 5] and popped["moved"] == 9 and popped["swaps"] == 1
    assert leetcode_docs.heap_pop_trace([4]) == {"popped": 4, "moved": 4, "heap": [], "swaps": 0}
    compared = leetcode_docs.heapify_compare([9, 8, 7, 6, 5, 4, 3, 2, 1])
    check = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    heapq.heapify(check)
    assert compared["heap"] == check
    assert (compared["heapify_swaps"], compared["push_swaps"]) == (7, 16)
    layout = leetcode_docs.heap_layout([1, 3, 2, 7, 5, 9])
    assert layout["levels"] == 3 and layout["edges"][-1] == [2, 5]
    assert [n["depth"] for n in layout["nodes"]] == [0, 1, 1, 2, 2, 2]
    smash = leetcode_docs.last_stone_trace([2, 7, 4, 1, 8, 1])
    assert smash["last"] == 1 and len(smash["rounds"]) == 4
    assert smash["rounds"][0] == {"first": 8, "second": 7, "rest": 1, "left": [4, 2, 1, 1, 1]}
    assert leetcode_docs.last_stone_trace([3, 3])["last"] == 0
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/heaps").get_data(as_text=True))
    assert "After 4 rounds the last stone weighs 1." in body
    assert "descending order cost 16 swaps in the example against 7 for heapify" in body


def test_top_k_helpers_match_the_page():
    values = [4, 9, 1, 7, 3, 8, 2, 6]
    trace = leetcode_docs.top_k_largest_trace(values, 3)
    assert trace["answer"] == sorted(values, reverse=True)[:3] == heapq.nlargest(3, values)
    assert trace["kth"] == 7
    assert [s["action"] for s in trace["steps"]] == ["fill", "fill", "fill", "replace 1", "skip", "replace 4", "skip", "skip"]
    assert [s["bar"] for s in trace["steps"]] == [4, 4, 1, 4, 4, 7, 7, 7]
    assert leetcode_docs.top_k_largest_trace([5, 5, 5], 2)["answer"] == [5, 5]
    words = ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"]
    freq = leetcode_docs.top_k_frequent_trace(words, 2)
    assert freq["counts"] == {"the": 4, "day": 1, "is": 3, "sunny": 2}
    assert freq["answer"] == ["the", "is"] and freq["distinct"] == 4
    assert leetcode_docs.top_k_frequent_trace(["b", "a"], 1)["answer"] == ["a"]
    points = [[3, 3], [5, -1], [-2, 4], [1, 1], [0, 2]]
    near = leetcode_docs.closest_points_trace(points, 2)
    assert near["answer"] == [[0, 2], [1, 1]]
    assert [s["dist2"] for s in near["steps"]] == [18, 26, 20, 2, 4]
    assert [s["action"] for s in near["steps"]] == ["fill", "fill", "replace", "replace", "replace"]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/top-k-elements").get_data(as_text=True))
    assert "The answer is 9, 8, 7, and the 3rd largest is the final bar, 7." in body
    assert "The top 2 are the and is." in body


def test_k_way_merge_helpers_match_the_page():
    lists = [[1, 4, 7, 10], [2, 5], [3, 6, 8]]
    trace = leetcode_docs.merge_k_trace(lists)
    assert trace["merged"] == list(heapq.merge(*lists)) == [1, 2, 3, 4, 5, 6, 7, 8, 10]
    assert trace["peak"] == 3
    assert [s["list"] for s in trace["steps"]] == [0, 1, 2, 0, 1, 2, 0, 2, 0]
    assert [s["size"] for s in trace["steps"]] == [3, 3, 3, 3, 2, 2, 2, 1, 0]
    assert leetcode_docs.merge_k_trace([[], [2], []])["merged"] == [2]
    assert leetcode_docs.merge_k_trace([])["merged"] == []
    cost = leetcode_docs.merge_strategy_costs([4] * 8)
    assert cost == {"n": 32, "sequential": 140, "pairwise": 96, "rounds": 3, "heap": 96}
    rng = leetcode_docs.smallest_range_trace([[1, 5, 9], [2, 6, 11], [4, 7, 8]])
    assert rng["range"] == [4, 6] and len(rng["steps"]) == 7
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/k-way-merge").get_data(as_text=True))
    assert "the output is 1, 2, 3, 4, 5, 6, 7, 8, 10." in body
    assert "tightest window that contains one value from every list is [4, 6]" in body
    assert "that is 140 moves, against 96 for the heap" in body


def test_two_heaps_helpers_match_the_page():
    import statistics

    stream = [5, 15, 1, 3, 8, 7, 9, 10]
    trace = leetcode_docs.running_median_trace(stream)
    assert [s["median"] for s in trace["steps"]] == [statistics.median(stream[:i]) for i in range(1, len(stream) + 1)]
    last = trace["steps"][-1]
    assert last["lower"] == [7, 5, 3, 1] and last["upper"] == [8, 9, 10, 15] and trace["median"] == 7.5
    assert all(s["lower"][0] <= s["upper"][0] for s in trace["steps"] if s["upper"])
    assert all(0 <= len(s["lower"]) - len(s["upper"]) <= 1 for s in trace["steps"])
    assert leetcode_docs.running_median_trace([])["median"] is None
    ipo = leetcode_docs.ipo_trace(3, 0, [1, 2, 3, 5, 9], [0, 1, 1, 3, 6])
    assert [s["picked"] for s in ipo["steps"]] == [1, 3, 5] and ipo["wealth"] == 9
    assert [s["unlocked"] for s in ipo["steps"]] == [[1], [2, 3], [5]]
    assert leetcode_docs.ipo_trace(2, 0, [5], [3])["steps"] == []
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/two-heaps").get_data(as_text=True))
    assert "After the 8 arrivals the median is 7.5, the mean of 7 and 8." in body
    assert "The final capital is 9." in body


def test_quickselect_helpers_match_the_page():
    values = [9, 4, 7, 1, 8, 3, 6, 2]
    target = leetcode_docs.kth_largest_target(len(values), 3)
    assert target == 5
    qs = leetcode_docs.quickselect_trace(values, target)
    assert qs["answer"] == sorted(values)[target] == 7
    assert [(r["lo"], r["hi"], r["pivot"], r["index"]) for r in qs["rounds"]] == [(0, 7, 2, 1), (2, 7, 4, 3), (4, 7, 9, 7), (4, 6, 6, 4), (5, 6, 8, 6)]
    assert qs["comparisons"] == 18
    assert values == [9, 4, 7, 1, 8, 3, 6, 2]
    for t in range(len(values)):
        assert leetcode_docs.quickselect_trace(values, t)["answer"] == sorted(values)[t]
    assert leetcode_docs.quickselect_trace([5], 0)["answer"] == 5
    worst = leetcode_docs.quickselect_trace(list(range(1, 9)), 0)
    assert worst["comparisons"] == 28 and len(worst["rounds"]) == 7
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/quickselect").get_data(as_text=True))
    assert "The answer is 7, found after 5 partitions and 18 comparisons" in body
    assert "That costs 7 rounds and 28 comparisons for 8 items" in body


def test_subsets_and_permutations_helpers_match_the_page():
    import itertools
    import math

    items = [1, 2, 3]
    sub = leetcode_docs.subsets_of(items)
    assert sub["calls"] == 8 and len(sub["results"]) == 2 ** 3
    assert sub["results"] == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    perm = leetcode_docs.permutations_of(items)
    assert perm["results"] == [list(p) for p in itertools.permutations(items)]
    assert perm["calls"] == 16
    assert leetcode_docs.permutations_of([])["results"] == [[]]
    assert leetcode_docs.subsets_of([])["results"] == [[]]
    dup = leetcode_docs.subsets_with_duplicates([2, 1, 2])
    assert dup["results"] == [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]] and dup["skipped"] == 2
    assert len(leetcode_docs.subsets_with_duplicates([2, 1, 2], dedupe=False)["results"]) == 8
    comb = leetcode_docs.combinations_of(4, 2)
    assert comb["results"] == [list(c) for c in itertools.combinations(range(1, 5), 2)]
    assert comb["calls"] == 10 and leetcode_docs.combinations_of(4, 2, prune=False)["calls"] == 11
    assert len(leetcode_docs.combinations_of(7, 3)["results"]) == math.comb(7, 3)
    assert leetcode_docs.parentheses_of(3)["results"] == ["((()))", "(()())", "(())()", "()(())", "()()()"]
    assert leetcode_docs.parentheses_of(3)["calls"] == 22
    tree = leetcode_docs.backtrack_tree(items, "permutations")
    assert len(tree["nodes"]) == 16 and tree["columns"] == 6 and tree["levels"] == 4
    assert len(leetcode_docs.backtrack_tree(items, "subsets")["nodes"]) == 8
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/subsets-and-permutations").get_data(as_text=True))
    assert "The search makes 8 calls" in body
    assert "found after 16 calls" in body
    assert "cuts 2 branches and yields 6 distinct subsets" in body
    assert "make 11 calls" in body
    assert "after 22 calls" in body


def test_constraint_backtracking_helpers_match_the_page():
    cs = leetcode_docs.combination_sum_of([2, 3, 6, 7], 7)
    assert cs["results"] == [[2, 2, 3], [7]] and cs["calls"] == 10 and cs["tested"] == 16
    assert leetcode_docs.combination_sum_of([2, 3, 6, 7], 7, prune=False)["tested"] == 27
    cs2 = leetcode_docs.combination_sum_of([10, 1, 2, 7, 6, 1, 5], 8, reuse=False)
    assert cs2["results"] == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    assert leetcode_docs.combination_sum_of([5], 0)["results"] == [[]]
    assert leetcode_docs.combination_sum_of([5], 3)["results"] == []
    q = leetcode_docs.n_queens_of(4)
    assert q["solutions"] == [[1, 3, 0, 2], [2, 0, 3, 1]]
    assert len(q["nodes"]) == 17 and q["columns"] == 6 and q["tried"] == 60
    assert [len(leetcode_docs.n_queens_of(n)["solutions"]) for n in (1, 2, 3, 6, 8)] == [1, 0, 0, 4, 92]
    board = ["ABCE", "SFCS", "ADEE"]
    ws = leetcode_docs.word_search_of(board, "ABCCED")
    assert ws["found"] and len(ws["path"]) == 6 and ws["calls"] == 9
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(ws["path"], ws["path"][1:]))
    miss = leetcode_docs.word_search_of(board, "ABCB")
    assert not miss["found"] and miss["calls"] == 20
    assert board == ["ABCE", "SFCS", "ADEE"]
    pal = leetcode_docs.palindrome_partitions_of("aab")
    assert pal["results"] == [["a", "a", "b"], ["aa", "b"]] and pal["calls"] == 6
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/constraint-backtracking").get_data(as_text=True))
    assert "in 10 calls. The loop examines 16 candidates" in body
    assert "it would examine 27" in body
    assert "tries 60 squares in total, builds 17 safe partial boards and finds 2 solutions" in body
    assert "8 queens has 92 solutions" in body
    assert "succeeds after 9 calls" in body and "fails after 20 calls" in body
    assert "in 6 calls" in body


def test_graph_traversal_helpers_match_the_page():
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (5, 6)]
    adj = leetcode_docs.adjacency_list(7, edges)
    assert adj[3] == [1, 2, 4] and adj[6] == [5]
    walk = leetcode_docs.graph_walks(adj, 0)
    assert walk["dfs"] == [0, 1, 3, 2, 4] and walk["bfs"] == [0, 1, 2, 3, 4]
    assert walk["distance"] == {0: 0, 1: 1, 2: 1, 3: 2, 4: 3}
    assert walk["layers"] == [[0], [1, 2], [3], [4]]
    assert sorted(leetcode_docs.graph_walks(adj, 5)["bfs"]) == [5, 6]
    comps = leetcode_docs.connected_components_of(adj)
    assert [sorted(c) for c in comps] == [[0, 1, 2, 3, 4], [5, 6]]
    cyc_edges = [(0, 1), (1, 2), (2, 3), (2, 4), (3, 1)]
    assert leetcode_docs.directed_cycle_of(leetcode_docs.adjacency_list(5, cyc_edges, True)) == [1, 2, 3, 1]
    assert leetcode_docs.directed_cycle_of(leetcode_docs.adjacency_list(5, cyc_edges[:4], True)) is None
    ladder = leetcode_docs.word_ladder_of("cat", "dog", ["cot", "cog", "dot", "bat", "cut"])
    assert ladder["path"] == ["cat", "cot", "dot", "dog"] and ladder["dequeued"] == 7
    assert leetcode_docs.word_ladder_of("cat", "dog", ["cot"]) == {"path": None, "dequeued": 2}
    clone = leetcode_docs.clone_graph_of(adj, 3)
    assert clone["ids"] == {3: 0, 1: 1, 2: 2, 4: 3, 0: 4}
    back = {new: old for old, new in clone["ids"].items()}
    assert all(sorted(back[n] for n in clone["adj"][new]) == adj[back[new]] for new in clone["adj"])
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/graph-traversal").get_data(as_text=True))
    assert "finds 2 components" in body
    assert "reports the cycle 1 → 2 → 3 → 1" in body
    assert "cat → cot → dot → dog (3 changes) after taking 7 words off the queue" in body
    assert "no sequence after 2 words" in body


def test_grid_graphs_helpers_match_the_page():
    islands = leetcode_docs.grid_islands_of(["11000", "11010", "00100", "00011"])
    assert islands["areas"] == [4, 1, 1, 2] and islands["perimeter"] == 22
    assert islands["labels"][3] == [-1, -1, -1, 3, 3]
    dist = leetcode_docs.grid_distance_from_zeros(["00111", "11111", "11011", "11111"])
    assert dist["dist"][0] == [0, 0, 1, 2, 3] and dist["dist"][3] == [3, 2, 1, 2, 3]
    assert dist["enqueued"] == 20
    assert leetcode_docs.rotting_minutes_of(["211", "110", "011"]) == 4
    assert leetcode_docs.rotting_minutes_of(["211", "011", "101"]) == -1
    assert leetcode_docs.rotting_minutes_of(["022"]) == 0 and leetcode_docs.rotting_minutes_of(["011"]) == -1
    filled = leetcode_docs.flood_fill_of(["112", "110", "101"], 1, 1, "3")
    assert filled == {"grid": ["332", "330", "301"], "changed": 5}
    assert leetcode_docs.flood_fill_of(["11"], 0, 0, "1")["changed"] == 0
    flow = leetcode_docs.pacific_atlantic_of([[1, 2, 2, 3], [3, 2, 3, 4], [2, 4, 5, 3], [6, 7, 1, 4]])
    assert flow["both"] == [(0, 3), (1, 3), (2, 2), (3, 0), (3, 1)]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/grid-graphs").get_data(as_text=True))
    assert "4 islands, areas 4, 1, 1, 2" in body
    assert "Total land perimeter</td><td class=\"num\">same grid</td><td class=\"num\">22<" in body
    assert "changes 5 cells and gives 332 / 330 / 301" in body
    assert "<td class=\"num\">4 minutes</td>" in body and "-1 (impossible)" in body


def test_topological_sort_helpers_match_the_page():
    edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
    kahn = leetcode_docs.kahn_order_of(6, edges)
    assert kahn["order"] == [4, 5, 0, 2, 3, 1]
    assert kahn["rounds"] == [[4, 5], [0, 2], [3], [1]] and kahn["stuck"] == []
    assert kahn["indegree"] == {0: 2, 1: 2, 2: 1, 3: 1, 4: 0, 5: 0}
    assert leetcode_docs.dfs_topological_order_of(6, edges) == [5, 4, 2, 3, 1, 0]
    looped = edges + [(1, 5)]
    assert leetcode_docs.kahn_order_of(6, looped)["stuck"] == [0, 1, 2, 3, 5]
    assert leetcode_docs.dfs_topological_order_of(6, looped) is None
    assert leetcode_docs.kahn_order_of(3, [])["order"] == [0, 1, 2]
    assert leetcode_docs.kahn_order_of(2, [(0, 0)])["stuck"] == [0]
    alien = leetcode_docs.alien_order_of(["wrt", "wrf", "er", "ett", "rftt"])
    assert alien["order"] == "wertf" and ("t", "f") in alien["edges"]
    assert leetcode_docs.alien_order_of(["abc", "ab"])["why"] == "prefix"
    assert leetcode_docs.alien_order_of(["z", "x", "z"])["why"] == "cycle"
    assert leetcode_docs.min_height_roots_of(6, [(3, 0), (3, 1), (3, 2), (3, 4), (5, 4)]) == {"roots": [3, 4], "rounds": 1}
    assert leetcode_docs.min_height_roots_of(1, [])["roots"] == [0]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/topological-sort").get_data(as_text=True))
    assert '<td class="num">4, 5, 0, 2, 3, 1</td>' in body
    assert '<td class="num">5, 4, 2, 3, 1, 0</td>' in body
    assert "5 nodes stuck: 0, 1, 2, 3, 5" in body
    assert "alphabet <code>wertf</code>" in body
    assert "leaves nodes 3 and 4" in body


def test_union_find_helpers_match_the_page():
    demo = leetcode_docs.union_find_trace(7, [(0, 1), (2, 3), (1, 2), (4, 5), (3, 0)])
    assert demo["merged"] == [True, True, True, True, False]
    assert demo["parent"] == [0, 0, 0, 0, 4, 4, 6]
    assert demo["components"] == 3 and demo["redundant"] == (3, 0)
    chain = [(i + 1, i) for i in range(7)]
    queries = chain + [(0, 7)] * 3
    runs = {(s, c): leetcode_docs.union_find_trace(8, queries, s, c) for s in (False, True) for c in (False, True)}
    assert (runs[(False, False)]["deepest"], runs[(False, False)]["hops"]) == (7, 21)
    assert (runs[(False, True)]["deepest"], runs[(False, True)]["hops"]) == (7, 9)
    assert runs[(True, False)]["deepest"] == 1 and runs[(True, True)]["deepest"] == 1
    layout = leetcode_docs.forest_layout_of(runs[(False, False)]["parent"])
    assert layout[0] == (7, 0) and layout[7] == (0, 0)
    assert leetcode_docs.union_find_trace(3, [])["redundant"] is None
    assert leetcode_docs.union_find_trace(2, [(1, 1)])["redundant"] == (1, 1)
    assert leetcode_docs.is_valid_tree_of(5, [(0, 1), (0, 2), (0, 3), (1, 4)]) is True
    assert leetcode_docs.is_valid_tree_of(5, [(0, 1), (1, 2), (2, 3), (1, 3)]) is False
    assert leetcode_docs.is_valid_tree_of(1, []) is True
    merged = leetcode_docs.accounts_merge_of([["John", "a@m", "b@m"], ["John", "c@m"], ["John", "a@m", "d@m"], ["Mary", "e@m"]])
    assert merged == [["John", "a@m", "b@m", "d@m"], ["John", "c@m"], ["Mary", "e@m"]]
    assert leetcode_docs.gcd_traversal_of([2, 3, 6]) is True
    assert leetcode_docs.gcd_traversal_of([3, 9, 5]) is False
    assert leetcode_docs.gcd_traversal_of([4, 3, 12, 8]) is True
    assert leetcode_docs.gcd_traversal_of([1]) is True and leetcode_docs.gcd_traversal_of([1, 2]) is False
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/union-find").get_data(as_text=True))
    assert "0-1 merges; 2-3 merges; 1-2 merges; 4-5 merges; 3-0 is redundant" in body
    assert "<code>0, 0, 0, 0, 4, 4, 6</code> and the count is 3 groups" in body
    assert "<td>Neither</td><td class=\"num\">7</td><td class=\"num\">21</td>" in body
    assert "<td>Path compression only</td><td class=\"num\">7</td><td class=\"num\">9</td>" in body


def test_dijkstra_helpers_match_the_page():
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3), (2, 5, 8), (4, 5, 1)]
    trace = leetcode_docs.dijkstra_trace(6, edges, 0)
    assert trace["dist"] == [0, 3, 1, 4, 7, 8]
    assert trace["settled"] == [(0, 0), (2, 1), (1, 3), (3, 4), (4, 7), (5, 8)]
    assert (trace["pushes"], trace["pops"], trace["stale"]) == (9, 9, 3)
    assert leetcode_docs.shortest_path_to(trace, 5) == [0, 2, 1, 3, 4, 5]
    assert leetcode_docs.dijkstra_trace(3, [(0, 1, 1)], 0)["dist"] == [0, 1, None]
    assert leetcode_docs.shortest_path_to(leetcode_docs.dijkstra_trace(3, [(0, 1, 1)], 0), 2) is None
    assert leetcode_docs.dijkstra_trace(1, [], 0)["dist"] == [0]
    assert leetcode_docs.network_delay_of([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2) == 2
    assert leetcode_docs.network_delay_of([(1, 2, 1)], 3, 1) == -1
    assert leetcode_docs.minimum_effort_of([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
    assert leetcode_docs.minimum_effort_of([[7]]) == 0
    assert leetcode_docs.swim_in_water_of([[0, 2], [1, 3]]) == 3
    assert leetcode_docs.swim_in_water_of([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]) == 16
    assert leetcode_docs.negative_edge_counterexample() == (1, -3)
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/dijkstra").get_data(as_text=True))
    assert "node 0 at 0; node 2 at 1; node 1 at 3; node 3 at 4; node 4 at 7; node 5 at 8" in body
    assert "<code>0, 3, 1, 4, 7, 8</code>" in body
    assert "0 → 2 → 1 → 3 → 4 → 5, costing 8" in body
    assert "<td>Stale pops skipped</td><td class=\"num\">3</td>" in body
    assert "settles node 1 at distance 1" in body or "node 1 at distance 1 first" in body


def test_bellman_ford_helpers_match_the_page():
    edges = [(3, 4, 2), (1, 3, 3), (2, 3, 6), (2, 1, -2), (0, 2, 1), (0, 1, 4)]
    run = leetcode_docs.bellman_ford_rounds(5, edges, 0)
    inf = float("inf")
    assert run["history"][1] == [0, 4, 1, inf, inf]
    assert run["history"][-2] == run["history"][-1] == [0, -1, 1, 2, 4]
    assert run["stable_at"] == 5 and run["negative_cycle"] is False
    flights = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]
    assert [leetcode_docs.cheapest_flights_of(4, flights, 0, 3, k) for k in (0, 1, 2)] == [-1, 700, 400]
    assert leetcode_docs.cheapest_flights_of(2, [], 0, 0, 0) == 0
    assert leetcode_docs.bellman_ford_rounds(4, flights, 0, 1)["history"][-1][3] == inf
    assert leetcode_docs.bellman_ford_rounds(4, flights, 0, 1, snapshot=False)["history"][-1][3] == 400
    cyc = [(0, 1, 1), (1, 2, -3), (2, 1, 1)]
    assert leetcode_docs.bellman_ford_rounds(3, cyc, 0)["negative_cycle"] is True
    assert leetcode_docs.has_negative_cycle_of(3, cyc) is True
    assert leetcode_docs.has_negative_cycle_of(3, [(0, 1, 1), (1, 2, -1)]) is False
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/bellman-ford").get_data(as_text=True))
    assert "<code>0, -1, 1, 2, 4</code>" in body
    assert "with 0 stops the answer is -1" in body
    assert "with 1 stop it is 700" in body and "with 2 stops it is 400" in body
    assert "reporting 400, which uses three flights" in body
    assert "negative cycle: True" in body


def test_minimum_spanning_tree_helpers_match_the_page():
    edges = [(0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2), (2, 3, 4), (3, 4, 2), (2, 4, 7), (4, 5, 6), (3, 5, 6)]
    kruskal = leetcode_docs.kruskal_trace(6, edges)
    assert kruskal["total"] == 14 and kruskal["connected"] is True
    assert kruskal["chosen"] == [(1, 2, 1), (1, 3, 2), (3, 4, 2), (0, 2, 3), (4, 5, 6)]
    prim = leetcode_docs.prim_trace(6, edges)
    assert prim["total"] == 14 and prim["added"][-1] == (3, 5, 6)
    assert leetcode_docs.kruskal_trace(3, [(0, 1, 1)])["connected"] is False
    assert leetcode_docs.prim_trace(3, [(0, 1, 1)])["connected"] is False
    assert leetcode_docs.kruskal_trace(1, [])["connected"] is True
    assert leetcode_docs.connect_points_cost_of([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
    assert leetcode_docs.connect_points_cost_of([[1, 1]]) == 0
    assert leetcode_docs.critical_edges_of(6, edges) == ([1, 2, 3, 5], [7, 8])
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/minimum-spanning-trees").get_data(as_text=True))
    assert "The tree has 5 edges and total weight 14" in body
    assert "Removing any of edges 1, 2, 3, 5" in body
    assert "Edges 7 and 8 can appear" in body
    assert "3-5 (6)" in body


def test_eulerian_helpers_match_the_page():
    tickets = [("JFK", "ATL"), ("JFK", "LAX"), ("LAX", "SEA"), ("SEA", "JFK")]
    trace = leetcode_docs.hierholzer_trace(tickets, "JFK")
    assert trace["route"] == ["JFK", "LAX", "SEA", "JFK", "ATL"]
    assert len(trace["steps"]) == 9 and trace["steps"][-1][3] == ["ATL", "JFK", "SEA", "LAX", "JFK"]
    assert leetcode_docs.greedy_walk_of(tickets, "JFK") == {"walk": ["JFK", "ATL"], "unused": 3}
    assert leetcode_docs.euler_kind_of(tickets) == {"kind": "path", "start": "JFK", "end": "ATL"}
    assert leetcode_docs.euler_kind_of([("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")])["kind"] == "none"
    assert leetcode_docs.euler_kind_of([("a", "b"), ("a", "c")])["kind"] == "none"
    assert leetcode_docs.euler_kind_of([])["kind"] == "circuit"
    circuit = [("A", "B"), ("B", "C"), ("C", "A"), ("A", "D"), ("D", "A")]
    assert leetcode_docs.euler_kind_of(circuit)["kind"] == "circuit"
    assert leetcode_docs.hierholzer_trace(circuit, "A")["route"] == ["A", "B", "C", "A", "D", "A"]
    assert leetcode_docs.hierholzer_trace([("a", "b"), ("c", "d")], "a")["route"] is None
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/eulerian-paths").get_data(as_text=True))
    assert "Running the algorithm takes 9 steps" in body
    assert "<code>JFK, LAX, SEA, JFK, ATL</code>" in body
    assert "reports a <code>path</code> from JFK to ATL" in body
    assert "stuck at once with 3 tickets unused" in body


def test_dp_fundamentals_helpers_match_the_page():
    tally = leetcode_docs.fib_call_tally(7)
    assert tally == {7: 1, 6: 1, 5: 2, 4: 3, 3: 5, 2: 8, 1: 13, 0: 8} and sum(tally.values()) == 41
    assert leetcode_docs.fib_memo_calls(7) == {"value": 13, "calls": 13, "states": 6}
    assert leetcode_docs.fib_memo_calls(0) == {"value": 0, "calls": 1, "states": 0}
    assert leetcode_docs.fib_table_of(7) == [0, 1, 1, 2, 3, 5, 8, 13]
    assert leetcode_docs.fib_table_of(0) == [0]
    assert 2 * leetcode_docs.fib_table_of(31)[31] - 1 == sum(leetcode_docs.fib_call_tally(30).values())
    result = leetcode_docs.triangle_dp_of([[5], [7, 3], [2, 8, 6], [9, 1, 4, 7]])
    assert result["best_from"] == [[15], [10, 12], [3, 9, 10], [9, 1, 4, 7]]
    assert result["answer"] == 15 and result["greedy"] == 18
    assert result["path"] == [(0, 0), (1, 0), (2, 0), (3, 1)]
    assert leetcode_docs.triangle_dp_of([[4]])["answer"] == 4
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/dp-fundamentals").get_data(as_text=True))
    assert "makes 41 calls" in body and "(2692537)" in body
    assert "it makes 13 calls and computes 6 states" in body
    assert "<code>0, 1, 1, 2, 3, 5, 8, 13</code>" in body
    assert "top cell holds 15" in body and "ends at 18" in body


def test_linear_dp_helpers_match_the_page():
    assert leetcode_docs.climb_table_of(7) == [1, 1, 2, 3, 5, 8, 13, 21]
    assert leetcode_docs.climb_table_of(0) == [1]
    assert leetcode_docs.min_cost_climb_of([4, 2, 9, 3, 6, 1]) == {"table": [0, 0, 2, 2, 5, 5, 6], "answer": 6}
    rob = leetcode_docs.house_robber_trace([4, 9, 3, 2, 8, 5])
    assert rob == {"best": [4, 9, 9, 11, 17, 17], "answer": 17, "chosen": [1, 4]}
    assert leetcode_docs.house_robber_trace([]) == {"best": [], "answer": 0, "chosen": []}
    assert leetcode_docs.circular_robber_of([5, 1, 2, 1, 5]) == {"without_first": 7, "without_last": 7, "answer": 7}
    assert leetcode_docs.house_robber_trace([5, 1, 2, 1, 5])["answer"] == 12
    assert leetcode_docs.circular_robber_of([5])["answer"] == 5
    assert leetcode_docs.decode_ways_trace("2261") == {"table": [1, 1, 2, 3, 3], "answer": 3}
    assert leetcode_docs.decode_ways_trace("1001")["answer"] == 0
    assert leetcode_docs.decode_ways_trace("06")["answer"] == 0
    assert leetcode_docs.decode_ways_trace("")["answer"] == 0
    product = leetcode_docs.max_product_trace([2, -5, -2, -4, 3])
    assert product["rows"] == [(2, 2, 2), (-5, -5, -10), (-2, 20, -2), (-4, 8, -80), (3, 24, -240)]
    assert product["answer"] == 24
    assert leetcode_docs.max_product_trace([-3])["answer"] == -3
    assert leetcode_docs.tribonacci_of(10) == [0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149]
    assert leetcode_docs.integer_break_of(10)["answer"] == 36 and leetcode_docs.integer_break_of(2)["answer"] == 1
    assert leetcode_docs.integer_break_of(10)["table"] == [0, 1, 1, 2, 4, 6, 9, 12, 18, 27, 36]
    game = leetcode_docs.stone_game_three_of([3, -4, 5, 6, -2])
    assert game["lead"] == -4 and game["result"] == "second" and game["diff"] == [-4, 9, 13, 8, -2, 0]
    assert leetcode_docs.stone_game_three_of([5])["result"] == "first"
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/linear-dp").get_data(as_text=True))
    assert "there are 21 ways to climb 7" in body
    assert "<code>4, 9, 9, 11, 17, 17</code>, so the answer is 17, from houses 1 and 4" in body
    assert "giving 3 readings" in body and "The answer is 6" in body
    assert "the answer is 24, the run" in body and "(3 + 3 + 4)" in body
    assert "first player's lead is -4, so the second player wins" in body


def test_knapsack_dp_helpers_match_the_page():
    subset = leetcode_docs.subset_sum_trace([3, 1, 5, 9, 12], 15)
    assert subset["answer"] is True
    assert subset["rows"][1] == (3, [0, 3]) and subset["rows"][2] == (1, [0, 1, 3, 4])
    assert subset["rows"][-1][1][-1] == 15
    assert leetcode_docs.subset_sum_trace([2, 4], 5)["answer"] is False
    assert leetcode_docs.subset_sum_trace([], 0)["answer"] is True
    change = leetcode_docs.coin_change_trace([1, 4, 5], 13)
    assert change["table"] == [0, 1, 2, 3, 1, 1, 2, 3, 2, 2, 2, 3, 3, 3] and change["answer"] == 3
    assert leetcode_docs.coin_change_trace([2], 3)["answer"] == -1
    assert leetcode_docs.coin_change_trace([5], 0)["answer"] == 0
    assert leetcode_docs.greedy_coin_count([1, 4, 5], 13) == [5, 5, 1, 1, 1]
    assert leetcode_docs.greedy_coin_count([4], 6) is None
    ways = leetcode_docs.coin_ways_of([1, 2, 5], 7)
    assert ways["combinations"] == [1, 1, 2, 2, 3, 4, 5, 6] and ways["orders"][7] == 26
    assert leetcode_docs.coin_ways_of([1, 2, 5], 11)["combinations"][11] == 11
    assert leetcode_docs.coin_ways_of([3], 2)["combinations"][2] == 0
    word_break = leetcode_docs.word_break_table("applepen", ["apple", "pen"])
    assert word_break["reach"] == [True, False, False, False, False, True, False, False, True]
    assert leetcode_docs.word_break_table("catsandog", ["cats", "dog", "sand", "and", "cat"])["answer"] is False
    target = leetcode_docs.target_sum_of([1, 1, 2, 3, 1], 2)
    assert target == {"subset_target": 5, "table": [1, 3, 4, 5, 6, 5], "answer": 5}
    assert leetcode_docs.target_sum_of([1, 1, 2, 3, 1], 3)["answer"] == 0
    assert leetcode_docs.target_sum_of([1], 2)["answer"] == 0
    assert leetcode_docs.target_sum_of([0, 0, 1], 1)["answer"] == 4
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/knapsack-dp").get_data(as_text=True))
    assert "<code>0, 1, 2, 3, 1, 1, 2, 3, 2, 2, 2, 3, 3, 3</code>, so 13 needs 3 coins" in body
    assert "counts 6 combinations" in body and "26 ordered sequences" in body
    assert "largest-first uses 5 coins (5 + 5 + 1 + 1 + 1)" in body
    assert "so there are 5 sign assignments" in body
    assert "so the string splits as apple + pen" in body


def test_palindrome_dp_helpers_match_the_page():
    table = leetcode_docs.palindrome_table_of("cabbad")
    assert table["longest"] == "abba" and table["count"] == 8
    assert table["table"][1] == [False, True, False, False, True, False]
    assert table["table"][2][3] is True and table["table"][0][5] is False
    empty = leetcode_docs.palindrome_table_of("")
    assert empty == {"table": [], "longest": "", "count": 0}
    centers = leetcode_docs.expand_centers_trace("cabbad")
    assert len(centers["rows"]) == 11 and centers["rows"][5] == ("gap 2|3", 1, "abba")
    assert centers["longest"] == "abba" and centers["count"] == 8
    assert leetcode_docs.expand_centers_trace("aaaa")["count"] == 10
    assert leetcode_docs.expand_centers_trace("babad")["longest"] == "bab"
    assert leetcode_docs.expand_centers_trace("") == {"rows": [], "longest": "", "count": 0}
    manacher = leetcode_docs.manacher_of("cabbad")
    assert manacher["padded"] == "#c#a#b#b#a#d#"
    assert manacher["radii"] == [0, 1, 0, 1, 0, 1, 4, 1, 0, 1, 0, 1, 0] and manacher["longest"] == "abba"
    assert leetcode_docs.manacher_of("")["longest"] == ""
    for text in ["a", "aaaa", "abacdfgdcaba", "abababab", "abcd"]:
        brute = [text[i : j + 1] for i in range(len(text)) for j in range(i, len(text)) if text[i : j + 1] == text[i : j + 1][::-1]]
        assert leetcode_docs.palindrome_table_of(text)["count"] == len(brute)
        assert leetcode_docs.expand_centers_trace(text)["count"] == len(brute)
        longest = max(map(len, brute))
        assert len(leetcode_docs.palindrome_table_of(text)["longest"]) == longest
        assert len(leetcode_docs.manacher_of(text)["longest"]) == longest
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/palindrome-dp").get_data(as_text=True))
    assert "Counting every step that matched gives 8 palindromic substrings: 6 single letters" in body
    assert "The table agrees: it has 8 true cells and the longest is \"abba\"" in body
    assert "<code>0, 1, 0, 1, 0, 1, 4, 1, 0, 1, 0, 1, 0</code>" in body


def test_lis_helpers_match_the_page():
    nums = [4, 10, 4, 3, 8, 9, 6, 11]
    dp = leetcode_docs.lis_dp_trace(nums)
    assert dp["length"] == [1, 2, 1, 1, 2, 3, 2, 4] and dp["parent"] == [None, 0, None, None, 0, 4, 0, 5]
    assert dp["answer"] == 4 and dp["sequence"] == [4, 8, 9, 11] and dp["indices"] == [0, 4, 5, 7]
    assert leetcode_docs.lis_dp_trace([]) == {"length": [], "parent": [], "answer": 0, "sequence": [], "indices": []}
    assert leetcode_docs.lis_dp_trace([5, 5, 5])["answer"] == 1
    tails = leetcode_docs.patience_trace(nums)
    assert tails["tails"] == [3, 6, 9, 11] and tails["answer"] == 4
    assert tails["rows"][2] == (4, 0, 4, [4, 10]) and tails["rows"][6] == (6, 1, 8, [3, 6, 9])
    assert leetcode_docs.patience_trace([])["answer"] == 0
    assert leetcode_docs.lis_count_of(nums) == {"length": 4, "count": 3}
    assert leetcode_docs.lis_count_of([2, 2, 2]) == {"length": 1, "count": 3}
    assert leetcode_docs.lis_count_of([]) == {"length": 0, "count": 0}
    for case in ([1, 3, 6, 7, 9, 4, 10, 5, 6], [7, 6, 5], [0, 1, 0, 3, 2, 3]):
        assert leetcode_docs.lis_dp_trace(case)["answer"] == leetcode_docs.patience_trace(case)["answer"]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/longest-increasing-subsequence").get_data(as_text=True))
    assert "<code>1, 2, 1, 1, 2, 3, 2, 4</code>, so the answer is 4, for example <code>4, 8, 9, 11</code>" in body
    assert "The final list is <code>3, 6, 9, 11</code>, with length 4" in body
    assert "3 different index choices give a longest run of 4" in body


def test_grid_dp_helpers_match_the_page():
    paths = leetcode_docs.grid_paths_table(3, 4, [(1, 1)])
    assert paths["table"] == [[1, 1, 1, 1], [1, 0, 1, 2], [1, 1, 2, 4]] and paths["answer"] == 4
    assert leetcode_docs.grid_paths_table(3, 7)["answer"] == 28
    assert leetcode_docs.grid_paths_table(1, 5)["answer"] == 1
    assert leetcode_docs.grid_paths_table(2, 2, [(0, 0)])["answer"] == 0
    grid = [[1, 3, 1, 4], [1, 5, 1, 2], [4, 2, 1, 3]]
    cheapest = leetcode_docs.min_path_sum_table(grid)
    assert cheapest["cost"] == [[1, 4, 5, 9], [2, 7, 6, 8], [6, 8, 7, 10]] and cheapest["answer"] == 10
    assert sum(grid[r][c] for r, c in cheapest["path"]) == 10 and cheapest["path"][0] == (0, 0)
    assert leetcode_docs.min_path_sum_table([[5]])["answer"] == 5
    bits = [[1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [1, 1, 1, 1, 0]]
    squares = leetcode_docs.maximal_square_table(bits)
    assert squares["side"][3] == [1, 1, 2, 3, 0] and squares["best"] == 3 and squares["area"] == 9 and squares["corner"] == (3, 3)
    assert leetcode_docs.maximal_square_table([[0, 0]])["area"] == 0
    hills = [[2, 5, 6], [3, 1, 7], [9, 4, 8]]
    climb = leetcode_docs.longest_increasing_path_of(hills)
    assert climb["length"] == [[5, 4, 3], [2, 5, 2], [1, 2, 1]] and climb["answer"] == 5
    values = [hills[r][c] for r, c in climb["path"]]
    assert values == sorted(set(values)) and len(values) == 5
    assert leetcode_docs.longest_increasing_path_of([[1]])["answer"] == 1
    assert leetcode_docs.longest_increasing_path_of([[3, 3], [3, 3]])["answer"] == 1
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/grid-dp").get_data(as_text=True))
    assert "so there are 4 routes" in body
    assert "so the cheapest route costs 10" in body
    assert "The largest side is 3, so the area is 9, with its bottom-right corner at (3, 3)" in body
    assert "and the answer is 5" in body


def test_string_dp_helpers_match_the_page():
    lcs = leetcode_docs.lcs_table("plumber", "humbler")
    assert lcs["answer"] == 5 and lcs["subsequence"] == "umber" and lcs["table"][-1] == [0, 0, 1, 2, 3, 3, 4, 5]
    assert leetcode_docs.lcs_table("", "abc")["answer"] == 0
    assert leetcode_docs.lcs_table("abc", "abc")["subsequence"] == "abc"
    edit = leetcode_docs.edit_distance_table("flaw", "lawn")
    assert edit["answer"] == 2 and edit["script"] == [("delete", "f"), ("insert", "n")]
    assert edit["table"][-1] == [4, 3, 2, 1, 2]
    assert leetcode_docs.edit_distance_table("", "abc")["answer"] == 3
    assert leetcode_docs.edit_distance_table("abc", "")["answer"] == 3
    assert leetcode_docs.edit_distance_table("same", "same")["answer"] == 0
    counts = leetcode_docs.distinct_subsequences_table("aabab", "ab")
    assert counts["answer"] == 5 and [row[-1] for row in counts["table"]] == [0, 0, 0, 2, 2, 5]
    assert leetcode_docs.distinct_subsequences_table("abc", "")["answer"] == 1
    assert leetcode_docs.distinct_subsequences_table("", "a")["answer"] == 0
    assert leetcode_docs.interleave_table("ab", "cd", "acbd")["answer"] is True
    assert leetcode_docs.interleave_table("ab", "cd", "adbc")["answer"] is False
    assert leetcode_docs.interleave_table("ab", "cd", "abc")["answer"] is False
    assert leetcode_docs.regex_match_table("abbc", "ab*c")["answer"] is True
    assert leetcode_docs.regex_match_table("abbc", "a.*d")["answer"] is False
    assert leetcode_docs.regex_match_table("", "a*b*")["answer"] is True
    assert leetcode_docs.regex_match_table("a", "")["answer"] is False
    for a, b in (("abcbdab", "bdcaba"), ("xyz", "zyx"), ("aaaa", "aa")):
        assert leetcode_docs.lcs_table(a, b)["answer"] == leetcode_docs.lcs_table(b, a)["answer"]
        assert leetcode_docs.edit_distance_table(a, b)["answer"] == leetcode_docs.edit_distance_table(b, a)["answer"]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/string-dp").get_data(as_text=True))
    assert "so the longest common subsequence has length 5" in body
    assert "recovers \"umber\"" in body
    assert "takes 2 edits: delete f, then insert n" in body
    assert "appears 5 times as a subsequence" in body
    assert "<code>0, 0, 0, 2, 2, 5</code>" in body


def test_interval_dp_helpers_match_the_page():
    def brute_coins(row):
        if not row:
            return 0
        return max((row[i - 1] if i else 1) * row[i] * (row[i + 1] if i + 1 < len(row) else 1) + brute_coins(row[:i] + row[i + 1 :]) for i in range(len(row)))

    def brute_margin(piles):
        if not piles:
            return 0
        if len(piles) == 1:
            return piles[0]
        return max(piles[0] - brute_margin(piles[1:]), piles[-1] - brute_margin(piles[:-1]))

    balloons = leetcode_docs.burst_balloons_table([2, 4, 3, 5])
    assert balloons["answer"] == 115 == brute_coins([2, 4, 3, 5]) and balloons["order"] == [2, 1, 0, 3]
    assert balloons["coins"][0] == [0, 0, 8, 30, 110, 115] and balloons["padded"] == [1, 2, 4, 3, 5, 1]
    assert leetcode_docs.burst_balloons_table([7])["answer"] == 7
    assert leetcode_docs.burst_balloons_table([])["answer"] == 0
    for row in ([1, 5], [3, 1, 2], [4, 2, 6, 1]):
        assert leetcode_docs.burst_balloons_table(row)["answer"] == brute_coins(row)
    stones = leetcode_docs.stone_game_diff_table([3, 1, 4, 1, 5, 9])
    assert stones["diff"][0] == [3, 2, 2, 5, 0, 9] and stones["margin"] == 9
    assert (stones["first"], stones["second"], stones["first_wins"]) == (16, 7, True)
    for piles in ([3, 1, 4, 1, 5, 9], [8, 2, 7], [5]):
        assert leetcode_docs.stone_game_diff_table(piles)["margin"] == brute_margin(piles)
    two = leetcode_docs.stone_game_two_value([3, 1, 4, 1, 5, 9])
    assert two["answer"] == 16 and two["suffix"][0] == 23 and len(two["memo"]) == 4
    assert leetcode_docs.stone_game_two_value([4])["answer"] == 4
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/interval-dp").get_data(as_text=True))
    assert "the table fills out to 115 coins" in body
    assert "<code>0, 0, 8, 30, 110, 115</code>" in body
    assert "force a margin of 9" in body
    assert "collects 16 and the second 7" in body
    assert "is 16 stones out of 23" in body


def test_state_machine_dp_helpers_match_the_page():
    def brute_cooldown(prices):
        def go(day, holding, cooling):
            if day == len(prices):
                return 0
            best = go(day + 1, holding, False)
            if holding:
                best = max(best, prices[day] + go(day + 1, False, True))
            elif not cooling:
                best = max(best, -prices[day] + go(day + 1, True, False))
            return best

        return go(0, False, False)

    def brute_signs(nums, target):
        import itertools

        return sum(1 for signs in itertools.product((1, -1), repeat=len(nums)) if sum(s * v for s, v in zip(signs, nums)) == target)

    prices = [6, 1, 4, 9, 2, 5, 8, 3]
    cooldown = leetcode_docs.stock_cooldown_table(prices)
    assert cooldown["answer"] == 11 == brute_cooldown(prices)
    assert cooldown["rows"][3] == (-1, 8, 3) and cooldown["rows"][-1] == (5, 6, 11)
    for sample in ([], [5], [3, 1], [1, 2, 3, 0, 2], [7, 6, 4, 3, 1]):
        assert leetcode_docs.stock_cooldown_table(sample)["answer"] == brute_cooldown(sample)
    unlimited = leetcode_docs.stock_unlimited_states(prices)
    assert unlimited["answer"] == unlimited["rises"] == 14
    nums = [2, 3, 1, 4, 2]
    signed = leetcode_docs.target_sum_states(nums, 4)
    assert signed["answer"] == 3 == brute_signs(nums, 4) == leetcode_docs.target_sum_of(nums, 4)["answer"]
    assert [len(layer) for layer in signed["states"]] == [1, 2, 4, 7, 11, 13]
    assert leetcode_docs.target_sum_states([], 0)["answer"] == 1
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/state-machine-dp").get_data(as_text=True))
    assert "best profit with a cooldown is 11" in body
    assert "<code>5, 6, 11</code>" in body
    assert "ends at 14, and adding up the rises also gives 14" in body
    assert "1, 2, 4, 7, 11, 13 distinct sums" in body
    assert "3 sign assignments land on the target" in body


def test_greedy_helpers_match_the_page():
    def can_reach(nums):
        ok = [False] * len(nums)
        ok[0] = True
        for i, step in enumerate(nums):
            if ok[i]:
                for j in range(i + 1, min(len(nums), i + step + 1)):
                    ok[j] = True
        return ok[-1]

    def fewest_jumps(nums):
        best = [None] * len(nums)
        best[0] = 0
        for i, step in enumerate(nums):
            if best[i] is None:
                continue
            for j in range(i + 1, min(len(nums), i + step + 1)):
                if best[j] is None or best[j] > best[i] + 1:
                    best[j] = best[i] + 1
        return best[-1]

    def brute_start(gas, cost):
        n = len(gas)
        for s in range(n):
            tank = 0
            for k in range(n):
                tank += gas[(s + k) % n] - cost[(s + k) % n]
                if tank < 0:
                    break
            else:
                return s
        return -1

    def brute_straights(counts, size):
        if not counts:
            return True
        low = min(counts)
        for value in range(low, low + size):
            if counts.get(value, 0) == 0:
                return False
        rest = dict(counts)
        for value in range(low, low + size):
            rest[value] -= 1
            if not rest[value]:
                del rest[value]
        return brute_straights(rest, size)

    jumps = [2, 3, 1, 1, 4, 2, 1, 1]
    assert leetcode_docs.jump_reach_trace(jumps) == {"trace": [2, 4, 4, 4, 8, 8, 8, 8], "can_finish": True}
    assert leetcode_docs.jump_reach_trace([3, 2, 1, 0, 4, 1])["can_finish"] is False
    assert leetcode_docs.jump_reach_trace([3, 2, 1, 0, 4, 1])["trace"] == [3, 3, 3, 3, None, None]
    levels = leetcode_docs.min_jumps_levels(jumps)
    assert levels["levels"] == [(0, 0), (1, 2), (3, 4), (5, 7)] and levels["jumps"] == 3
    assert leetcode_docs.min_jumps_levels([0, 1])["jumps"] is None
    assert leetcode_docs.min_jumps_levels([5])["jumps"] == 0
    for row in ([2, 3, 1, 1, 4], [1, 1, 1, 1], [4, 0, 0, 0, 1], [1, 2, 0, 1], [0], [2, 0, 0]):
        assert leetcode_docs.jump_reach_trace(row)["can_finish"] == can_reach(row)
        expected = fewest_jumps(row)
        assert leetcode_docs.min_jumps_levels(row)["jumps"] == expected
    station = leetcode_docs.gas_station_trace([3, 1, 2, 5, 4, 1], [4, 2, 2, 3, 3, 2])
    assert station == {"start": 2, "tanks": [-1, -1, 0, 2, 3, 2], "total": 0}
    for gas, cost in (([2, 5, 1, 3, 4, 2], [3, 3, 4, 2, 2, 4]), ([1, 2, 3], [3, 2, 1]), ([5], [4]), ([2, 3, 4], [3, 4, 3])):
        assert leetcode_docs.gas_station_trace(gas, cost)["start"] == brute_start(gas, cost)
    hand = [5, 1, 3, 2, 4, 3, 4, 6, 5]
    assert leetcode_docs.straights_groups(hand, 3) == [[1, 2, 3], [3, 4, 5], [4, 5, 6]]
    assert leetcode_docs.straights_groups([1, 2, 4, 5, 3, 3], 3) == [[1, 2, 3], [3, 4, 5]]
    assert leetcode_docs.straights_groups([1, 2, 4], 3) is None and leetcode_docs.straights_groups([1, 2, 3, 4], 3) is None
    for sample in ([1, 1, 2, 2, 3, 3], [1, 2, 3, 3, 4, 5], [1, 3, 5], [2, 2, 3, 3, 4, 4, 5, 5]):
        counts = {}
        for card in sample:
            counts[card] = counts.get(card, 0) + 1
        got = leetcode_docs.straights_groups(sample, 3) is not None
        assert got == (len(sample) % 3 == 0 and brute_straights(counts, 3))
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/greedy").get_data(as_text=True))
    assert "<code>2, 4, 4, 4, 8, 8, 8, 8</code>" in body
    assert "the fewest jumps is 3" in body
    assert "<code>-1, -1, 0, 2, 3, 2</code>" in body
    assert "the starting station is 2" in body
    assert "<code>1, 2, 3</code>; <code>3, 4, 5</code>; <code>4, 5, 6</code>" in body


def test_kadane_helpers_match_the_page():
    def brute_best(nums):
        return max(sum(nums[i : j + 1]) for i in range(len(nums)) for j in range(i, len(nums)))

    def brute_circular(nums):
        n = len(nums)
        return max(sum(nums[(i + k) % n] for k in range(length)) for i in range(n) for length in range(1, n + 1))

    def brute_product(nums):
        best = nums[0]
        for i in range(len(nums)):
            product = 1
            for j in range(i, len(nums)):
                product *= nums[j]
                best = max(best, product)
        return best

    row = [3, -4, 2, -1, 5, -6, 1, 4]
    trace = leetcode_docs.kadane_trace(row)
    assert trace == {"ending": [3, -1, 2, 1, 6, 0, 1, 5], "best": 6, "span": (2, 4)}
    assert sum(row[trace["span"][0] : trace["span"][1] + 1]) == trace["best"]
    circular = leetcode_docs.circular_max_subarray(row)
    assert (circular["total"], circular["straight"], circular["lowest"], circular["wrapped"], circular["answer"]) == (4, 6, -6, 10, 10)
    assert leetcode_docs.min_subarray_sum(row) == -6 and leetcode_docs.kadane_trace([-x for x in row])["span"] == (5, 5)
    assert leetcode_docs.circular_max_subarray([-3, -2, -5])["answer"] == -2
    assert leetcode_docs.circular_max_subarray([5, -3, 5])["answer"] == 10
    for sample in ([1], [-1], [-2, -1], [1, 2, 3], [5, -2, 5], [4, -1, -1, 4], [-3, 2, -3, 2], [2, -5, 3, 1, -2, 2]):
        assert leetcode_docs.kadane_trace(sample)["best"] == brute_best(sample)
        assert leetcode_docs.circular_max_subarray(sample)["answer"] == brute_circular(sample)
    product = [2, 3, -2, 4, -1, 5, 0, 2]
    result = leetcode_docs.max_product_pairs(product)
    assert result["best"] == 240 == brute_product(product)
    assert result["rows"][3] == (4, -48) and result["rows"][4] == (48, -4)
    for sample in ([-2], [-2, 3, -4], [0, 2], [-1, -1, -1], [2, -5, -2, -4, 3]):
        assert leetcode_docs.max_product_pairs(sample)["best"] == brute_product(sample)
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/kadanes-algorithm").get_data(as_text=True))
    assert "<code>3, -1, 2, 1, 6, 0, 1, 5</code>" in body
    assert "from index 2 to index 4" in body
    assert "4 &minus; (-6) = 10" in body
    assert "The best product is 240" in body
    assert "the smallest product -48 at index 3 becomes the largest, 48" in body


def test_interval_merging_helpers_match_the_page():
    def brute_union(intervals):
        points = {x for s, e in intervals for x in range(2 * s, 2 * e + 1)}
        blocks, run = [], None
        for x in sorted(points):
            if run and x == run[1] + 1:
                run[1] = x
            else:
                run = [x, x]
                blocks.append(run)
        return [(lo // 2, hi // 2) for lo, hi in blocks]

    spans = [(5, 8), (1, 4), (2, 3), (9, 12), (12, 14), (6, 7), (16, 17)]
    trace = leetcode_docs.merge_intervals_trace(spans)
    assert [step["action"] for step in trace["steps"]] == ["new block", "inside", "new block", "inside", "new block", "extend", "new block"]
    assert trace["merged"] == [(1, 4), (5, 8), (9, 14), (16, 17)] == brute_union(spans)
    for sample in ([], [(1, 1)], [(1, 3), (3, 5)], [(4, 9), (1, 2), (2, 4)], [(1, 10), (2, 3), (4, 5), (11, 12)]):
        assert leetcode_docs.merge_intervals_trace(sample)["merged"] == brute_union(sample)
    parts = leetcode_docs.insert_interval_parts([(1, 2), (4, 6), (7, 8), (10, 13), (15, 16)], (5, 11))
    assert parts["before"] == [(1, 2)] and parts["absorbed"] == [(4, 6), (7, 8), (10, 13)] and parts["after"] == [(15, 16)]
    assert parts["result"] == [(1, 2), (4, 13), (15, 16)]
    for existing, new in (([], (2, 5)), ([(3, 4)], (0, 1)), ([(3, 4)], (6, 7)), ([(1, 2), (5, 6)], (0, 9)), ([(1, 5)], (2, 3))):
        assert leetcode_docs.insert_interval_parts(existing, new)["result"] == brute_union(existing + [new])
    clash = leetcode_docs.first_conflict_of([(9, 10), (13, 15), (10, 12), (11, 13)])
    assert clash["conflict"] == ((10, 12), (11, 13))
    assert leetcode_docs.first_conflict_of([(13, 15), (9, 10), (10, 12)])["conflict"] is None
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/interval-merging").get_data(as_text=True))
    assert "The answer is [1, 4], [5, 8], [9, 14], [16, 17]." in body
    assert "grows the new interval to [4, 13]" in body
    assert "first clash at [10, 12) and [11, 13)" in body
    assert "[9, 10), [10, 12), [13, 15) can all be attended" in body


def test_sweep_line_helpers_match_the_page():
    def brute_rooms(meetings):
        times = {t for s, e in meetings for t in (s, e)}
        return max((sum(1 for s, e in meetings if s <= t < e) for t in times), default=0)

    def brute_smallest(intervals, query):
        sizes = [e - s + 1 for s, e in intervals if s <= query <= e]
        return min(sizes) if sizes else -1

    meetings = [(1, 5), (2, 6), (4, 8), (5, 9), (8, 10), (11, 12)]
    sweep = leetcode_docs.room_sweep_trace(meetings)
    assert [count for _, _, count in sweep["steps"]] == [1, 2, 3, 2, 3, 2, 1, 2, 1, 0, 1, 0]
    assert sweep["rooms"] == 3 == brute_rooms(meetings)
    heap = leetcode_docs.rooms_heap_trace(meetings)
    assert heap["rooms"] == 3 and heap["rows"][4]["freed"] == [6, 8] and heap["rows"][4]["heap"] == [9, 10]
    for sample in ([], [(1, 2)], [(1, 3), (3, 5)], [(1, 10), (2, 3), (4, 5), (6, 7)], [(0, 5), (1, 5), (2, 5), (5, 6)]):
        assert leetcode_docs.room_sweep_trace(sample)["rooms"] == brute_rooms(sample) == leetcode_docs.rooms_heap_trace(sample)["rooms"]
    trips = [(2, 1, 4), (3, 2, 6), (2, 5, 8), (1, 7, 9)]
    pool = leetcode_docs.car_pool_trace(trips, 5)
    assert pool["change"] == [0, 2, 3, 0, -2, 2, -3, 1, -2, -1]
    assert pool["load"] == [sum(p for p, s, e in trips if s <= x < e) for x in range(10)]
    assert pool["fits"] and leetcode_docs.car_pool_trace(trips, 4)["first_over"] == 2
    free = leetcode_docs.common_free_time_of([[(1, 3), (6, 7)], [(2, 4)], [(2, 5), (9, 12)]])
    assert free["merged"] == [(1, 5), (6, 7), (9, 12)] and free["free"] == [(5, 6), (7, 9)]
    spans, asks = [(2, 5), (1, 8), (4, 6), (7, 7), (10, 14)], [9, 3, 12, 5, 7]
    queries = leetcode_docs.min_interval_queries_trace(spans, asks)
    assert queries["answers"] == [-1, 4, 5, 3, 1] == [brute_smallest(spans, q) for q in asks]
    assert [row["query"] for row in queries["rows"]] == [3, 5, 7, 9, 12]
    assert queries["rows"][3]["dropped"] == [(7, 7), (4, 6), (2, 5), (1, 8)]
    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/sweep-line").get_data(as_text=True))
    assert "The peak is 3, so 3 rooms are needed." in body
    assert "<code>0, 2, 3, 0, -2, 2, -3, 1, -2, -1</code>" in body and "<code>0, 2, 5, 5, 3, 5, 2, 3, 1, 0</code>" in body
    assert "with 4 seats the load first goes over at location 2" in body
    assert "everyone is free during [5, 6] and [7, 9]" in body
    assert "the answers are <code>-1, 4, 5, 3, 1</code>" in body


def test_matrix_manipulation_helpers_match_the_page():
    square = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    stages = leetcode_docs.rotate_matrix_stages(square)
    assert stages["transposed"] == [[1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15], [4, 8, 12, 16]]
    assert stages["rotated"] == [[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]
    assert (stages["transpose_swaps"], stages["reverse_swaps"]) == (6, 8)
    assert square[0] == [1, 2, 3, 4]
    for n in range(1, 7):
        m = [[n * r + c for c in range(n)] for r in range(n)]
        expected = [[m[n - 1 - c][r] for c in range(n)] for r in range(n)]
        assert leetcode_docs.rotate_matrix_stages(m)["rotated"] == expected
        by_layers = [row[:] for row in m]
        for cycle in leetcode_docs.rotation_cycles(n):
            values = [by_layers[r][c] for r, c in cycle]
            for (r, c), value in zip(cycle[1:] + cycle[:1], values):
                by_layers[r][c] = value
        assert by_layers == expected
        assert len(leetcode_docs.rotation_cycles(n)) == (n // 2) * ((n + 1) // 2)

    cycles = leetcode_docs.rotation_cycles(4)
    assert len(cycles) == 4 and cycles[0] == ((0, 0), (0, 3), (3, 3), (3, 0))

    assert leetcode_docs.transpose_of([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]

    grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    spiral = leetcode_docs.spiral_trace(grid)
    assert spiral["order"] == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
    assert [s["bounds"] for s in spiral["sides"]] == [(1, 2, 0, 3), (1, 2, 0, 2), (1, 1, 0, 2), (1, 1, 1, 2), (2, 1, 1, 2)]

    def peel(matrix):
        out = []
        while matrix:
            out.extend(matrix.pop(0))
            matrix = [list(row) for row in zip(*matrix)][::-1]
        return out

    for rows in range(1, 6):
        for cols in range(1, 6):
            m = [[rows * 10 + r * cols + c for c in range(cols)] for r in range(rows)]
            assert leetcode_docs.spiral_trace(m)["order"] == peel([row[:] for row in m])
    assert leetcode_docs.spiral_trace([])["order"] == []

    zgrid = [[1, 2, 3, 4], [5, 0, 7, 8], [0, 10, 11, 12], [13, 14, 15, 16]]
    zeroes = leetcode_docs.set_zeroes_trace(zgrid)
    assert (zeroes["first_row"], zeroes["first_col"]) == (False, True)
    assert zeroes["marked"] == [[1, 0, 3, 4], [0, 0, 7, 8], [0, 10, 11, 12], [13, 14, 15, 16]]
    assert zeroes["result"] == [[0, 0, 3, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 15, 16]]

    def brute_zeroes(matrix):
        zero_rows = {r for r, row in enumerate(matrix) for v in row if v == 0}
        zero_cols = {c for row in matrix for c, v in enumerate(row) if v == 0}
        return [[0 if r in zero_rows or c in zero_cols else v for c, v in enumerate(row)] for r, row in enumerate(matrix)]

    for seed in range(200):
        rows, cols = 1 + seed % 4, 1 + (seed // 4) % 5
        m = [[(seed * 7 + r * 5 + c * 3) % 6 for c in range(cols)] for r in range(rows)]
        assert leetcode_docs.set_zeroes_trace(m)["result"] == brute_zeroes(m)

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/matrix-manipulation").get_data(as_text=True))
    assert "<td>Rows reversed (8 swaps)</td><td class=\"num\">13 9 5 1</td>" in body
    assert "<td>Transposed (6 swaps)</td><td class=\"num\">1 5 9 13</td>" in body
    assert "order: 1 2 3 4 8 12 11 10 9 5 6 7" in body
    assert "<td>Result</td><td class=\"num\">0 0 3 4</td><td class=\"num\">0 0 0 0</td><td class=\"num\">0 0 0 0</td><td class=\"num\">0 0 15 16</td>" in body
    assert "3 &times; 2 matrix [1, 4], [2, 5], [3, 6]" in body
    assert "6 for n = 4" in body


def test_number_math_helpers_match_the_page():
    rev = leetcode_docs.reverse_digits_trace(-1230)
    assert [(r["digit"], r["rest"], r["before"], r["after"]) for r in rev["rows"]] == [(0, 123, 0, 0), (3, 12, 0, 3), (2, 1, 3, 32), (1, 0, 32, 321)]
    assert (rev["value"], rev["limit"]) == (-321, 2 ** 31)
    over = leetcode_docs.reverse_digits_trace(1534236469)
    assert over["overflow"] and over["value"] == 0
    assert (over["rows"][-1]["digit"], over["rows"][-1]["before"], over["rows"][-1]["safe"]) == (1, 964632435, False)

    def brute_reverse(x):
        r = int(str(abs(x))[::-1]) * (-1 if x < 0 else 1)
        return r if -2 ** 31 <= r <= 2 ** 31 - 1 else 0

    for x in [0, 7, -7, 120, 2 ** 31 - 1, -2 ** 31, 1463847412, -1463847412, 1463847413, -1563847412, 8463847412, -8463847412, 2147483641]:
        assert leetcode_docs.reverse_digits_trace(x)["value"] == brute_reverse(x)

    pal = leetcode_docs.palindrome_half_trace(12321)
    assert [(r["digit"], r["rest"], r["half"]) for r in pal["rows"]] == [(1, 1232, 1), (2, 123, 12), (3, 12, 123)]
    assert pal["is_palindrome"]
    even = leetcode_docs.palindrome_half_trace(1221)
    assert (even["rows"][-1]["rest"], even["rows"][-1]["half"], len(even["rows"])) == (12, 12, 2)
    for x in range(-20, 3000):
        assert leetcode_docs.palindrome_half_trace(x)["is_palindrome"] == (str(x) == str(x)[::-1])

    pw = leetcode_docs.binary_power_trace(3, 13)
    assert [(r["position"], r["bit"], r["power"], r["result"]) for r in pw["rows"]] == [(0, 1, 3, 3), (1, 0, 9, 3), (2, 1, 81, 243), (3, 1, 6561, 1594323)]
    assert (pw["value"], pw["multiplications"]) == (3 ** 13, 6)
    assert leetcode_docs.binary_power_trace(2.0, -2)["value"] == 0.25
    for base in [-3, 2, 5]:
        for exponent in range(40):
            assert leetcode_docs.binary_power_trace(base, exponent)["value"] == base ** exponent

    mul = leetcode_docs.multiply_strings_trace("123", "45")
    assert [s["product"] for s in mul["steps"]] == [15, 12, 10, 8, 5, 4]
    assert (mul["slots"], mul["product"]) == ([0, 5, 5, 3, 5], "5535")
    for a in ["0", "9", "99", "123", "1000", "987654321"]:
        for b in ["0", "1", "45", "999", "123456789"]:
            assert leetcode_docs.multiply_strings_trace(a, b)["product"] == str(int(a) * int(b))

    col = leetcode_docs.column_title_trace(701)
    assert col["title"] == "ZY" and [(r["shifted"], r["next"], r["remainder"], r["letter"]) for r in col["rows"]] == [(700, 26, 24, "Y"), (25, 0, 25, "Z")]

    def column_number(title):
        n = 0
        for letter in title:
            n = n * 26 + ord(letter) - ord("A") + 1
        return n

    for n in range(1, 20000):
        assert column_number(leetcode_docs.column_title_trace(n)["title"]) == n
    assert leetcode_docs.column_title_trace(26)["title"] == "Z"

    eu = leetcode_docs.euclid_trace(6, 4)
    assert eu["gcd"] == 2 and [(r["a"], r["b"], r["remainder"]) for r in eu["rows"]] == [(6, 4, 2), (4, 2, 0)]
    for a in range(1, 60):
        for b in range(1, 60):
            assert leetcode_docs.euclid_trace(a, b)["gcd"] == math.gcd(a, b)
    assert leetcode_docs.gcd_of_strings_of("ABABAB", "ABAB") == "AB"
    assert leetcode_docs.gcd_of_strings_of("ABC", "AB") == ""

    atoi = leetcode_docs.atoi_trace("   -042x7")
    assert [r["state"] for r in atoi["rows"]] == ["space"] * 3 + ["sign", "digit", "digit", "digit", "stop"]
    assert atoi["value"] == -42
    clamp = leetcode_docs.atoi_trace("91283472332")
    assert clamp["rows"][-1]["state"] == "clamp" and clamp["value"] == 2 ** 31 - 1
    for text, expected in [("", 0), ("+", 0), ("+-1", 0), ("  12 3", 12), ("-91283472332", -2 ** 31), ("words 9", 0), ("2147483647", 2 ** 31 - 1), ("-2147483648", -2 ** 31)]:
        assert leetcode_docs.atoi_trace(text)["value"] == expected

    assert leetcode_docs.roman_trace("MCMXCIV")["value"] == 1994
    assert [r["signed"] for r in leetcode_docs.roman_trace("MCMXCIV")["rows"]] == [1000, -100, 1000, -10, 100, -1, 5]

    def to_roman(n):
        out = ""
        for value, symbols in [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
            while n >= value:
                out, n = out + symbols, n - value
        return out

    for n in range(1, 4000):
        assert leetcode_docs.roman_trace(to_roman(n))["value"] == n

    assert leetcode_docs.plus_one_of([9, 9]) == [1, 0, 0] and leetcode_docs.plus_one_of([1, 2, 9]) == [1, 3, 0]
    for n in range(0, 1200):
        digits = [int(c) for c in str(n)]
        assert leetcode_docs.plus_one_of(digits) == [int(c) for c in str(n + 1)]

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/number-math").get_data(as_text=True))
    assert "<td class=\"num\">4</td><td class=\"num\">1</td><td class=\"num\">0</td><td class=\"num\">32</td><td>yes</td><td class=\"num\">321</td>" in body
    assert "Putting the sign back gives <strong>-321</strong>" in body
    assert "<td class=\"num\">964632435</td><td>no</td><td class=\"num\">&mdash;</td>" in body
    assert "<td class=\"num\">3</td><td class=\"num\">1</td><td class=\"num\">6561</td><td class=\"num\">1594323</td>" in body
    assert "6 multiplications give 3<sup>13</sup> = 1594323" in body
    assert "<td class=\"num\">0 5 5 3 5</td>" in body and "<strong>5535</strong>" in body
    assert "<td>ZY</td>" in body and "<td class=\"num\">1994</td>" in body
    assert "<code>\"AB\"</code>" in body and "1 3 0 and 1 0 0" in body
    assert "<td class=\"num\">-42</td>" in body and "<td class=\"num\">2147483647</td>" in body


def test_bit_manipulation_helpers_match_the_page():
    single = leetcode_docs.xor_fold_trace([4, 1, 2, 1, 2])
    assert [r["acc"] for r in single["rows"]] == [4, 5, 7, 6, 4] and single["value"] == 4

    pop = leetcode_docs.popcount_trace(44)
    assert [(r["n"], r["lowest"], r["next"]) for r in pop["rows"]] == [(44, 4, 40), (40, 8, 32), (32, 32, 0)]
    for n in range(0, 5000):
        assert leetcode_docs.popcount_trace(n)["count"] == bin(n).count("1")

    cb = leetcode_docs.counting_bits_table(8)
    assert cb["counts"] == [0, 1, 1, 2, 1, 2, 2, 3, 1]
    assert leetcode_docs.counting_bits_table(1000)["counts"] == [bin(i).count("1") for i in range(1001)]

    add = leetcode_docs.add_without_plus_trace(5, 3)
    assert [(r["a"], r["b"], r["sum"], r["carry"]) for r in add["rows"]] == [(5, 3, 6, 2), (6, 2, 4, 4), (4, 4, 0, 8), (0, 8, 8, 0)]
    assert add["value"] == 8
    neg = leetcode_docs.add_without_plus_trace(-2, 3)
    assert neg["value"] == 1 and neg["rows"][0]["a"] == 2 ** 32 - 2 and len(neg["rows"]) == 31
    for a in range(-40, 41, 3):
        for b in range(-1000, 1001, 37):
            assert leetcode_docs.add_without_plus_trace(a, b)["value"] == a + b

    for n in [0, 1, 0b1011, 43261596, 2 ** 32 - 1, 2 ** 31]:
        assert leetcode_docs.reverse_bits_of(n) == int(format(n, "032b")[::-1], 2)

    rng = leetcode_docs.range_and_trace(9, 12)
    assert [(r["left"], r["right"], r["shift"]) for r in rng["rows"]] == [(9, 12, 0), (4, 6, 1), (2, 3, 2), (1, 1, 3)]
    assert rng["value"] == 8
    for left in range(0, 70):
        for right in range(left, 70):
            expected = left
            for v in range(left, right + 1):
                expected &= v
            assert leetcode_docs.range_and_trace(left, right)["value"] == expected

    mae = leetcode_docs.minimum_array_end_of(3, 4)
    assert mae["value"] == 6 and mae["filled"] == [{"position": 0, "bit": 0}, {"position": 1, "bit": 1}]
    for x in range(1, 40):
        supersets = [v for v in range(x, 4000) if v & x == x]
        for n in range(1, 30):
            assert leetcode_docs.minimum_array_end_of(n, x)["value"] == supersets[n - 1]

    assert leetcode_docs.add_binary_of("1011", "111") == "10010"
    for a in range(0, 40):
        for b in range(0, 40):
            assert leetcode_docs.add_binary_of(bin(a)[2:], bin(b)[2:]) == bin(a + b)[2:]
    assert leetcode_docs.missing_number_xor([3, 0, 1]) == 2
    for n in range(1, 30):
        for gone in range(n + 1):
            assert leetcode_docs.missing_number_xor([v for v in range(n + 1) if v != gone][::-1]) == gone
    assert leetcode_docs.binary_of(44, 6) == "101100" and leetcode_docs.binary_of(-1, 4) == "1111"

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/bit-manipulation").get_data(as_text=True))
    assert "the accumulator ends at <strong>4</strong>" in body
    assert "<td class=\"num\">44</td><td class=\"num\">101100</td><td class=\"num\">4</td><td class=\"num\">40</td>" in body
    assert "<td class=\"num\">7</td><td class=\"num\">0111</td><td class=\"num\">3</td><td class=\"num\">1</td><td class=\"num\">3</td>" in body
    assert "<td class=\"num\">3</td><td class=\"num\">4</td><td class=\"num\">4</td><td class=\"num\">0</td><td class=\"num\">8</td>" in body
    assert "reads back as <strong>1</strong>" in body
    assert "= <strong>8</strong>" in body and "<strong>6</strong>, so the array is 4, 5, 6" in body
    assert "gives 2, and Add Binary on \"1011\" and \"111\" gives \"10010\"" in body


def test_interview_approach_helpers_match_the_page():
    nums, target = [2, 7, 11, 4, 8], 12
    trace = leetcode_docs.hash_two_sum_trace(nums, target)
    assert [(r["value"], r["need"], r["hit"]) for r in trace["rows"]] == [(2, 10, None), (7, 5, None), (11, 1, None), (4, 8, None), (8, 4, 3)]
    assert trace["answer"] == (3, 4) and trace["rows"][-1]["seen"] == {2: 0, 7: 1, 11: 2, 4: 3}
    assert leetcode_docs.hash_two_sum_trace([3, 3], 6)["answer"] == (0, 1)
    assert leetcode_docs.hash_two_sum_trace([3, 2, 4], 6)["answer"] == (1, 2)

    costs = leetcode_docs.two_sum_costs(nums, target)
    assert (costs["brute"]["steps"], costs["sorted"]["comparisons"], costs["sorted"]["moves"], costs["hashed"]["steps"]) == (10, 7, 2, 5)
    assert costs["brute"]["pair"] == costs["sorted"]["pair"] == costs["hashed"]["pair"] == (4, 8)

    growth = leetcode_docs.two_sum_growth([8, 16, 32, 64])
    assert [(r["brute"], r["sorted"], r["hashed"]) for r in growth] == [(28, 18, 8), (120, 46, 16), (496, 110, 32), (2016, 254, 64)]
    for row in growth:
        assert row["brute"] == row["n"] * (row["n"] - 1) // 2 and row["hashed"] == row["n"]

    for seed in range(60):
        values = [(seed * 31 + i * 17) % 23 - 5 for i in range(2 + seed % 9)]
        ordered, count = leetcode_docs._merge_sort_counting(values)
        assert ordered == sorted(values) and count <= len(values) * max(1, math.ceil(math.log2(len(values))))
        pair_sum = values[0] + values[-1]
        found = leetcode_docs.two_sum_costs(values, pair_sum)
        for approach in ("brute", "sorted", "hashed"):
            assert sum(found[approach]["pair"]) == pair_sum

    bug = leetcode_docs.buggy_kadane_counterexample()
    assert bug == {"nums": [-2], "buggy": 0, "correct": -2}
    assert leetcode_docs.buggy_kadane_counterexample(values=range(0, 3)) is None

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/interview-approach").get_data(as_text=True))
    assert "<td class=\"num\">10</td><td class=\"num\">4 + 8</td>" in body
    assert "<td class=\"num\">7 + 2 = 9</td>" in body
    assert "<td class=\"num\">5</td><td class=\"num\">4 + 8</td>" in body
    assert "<td class=\"num\">2: 0, 7: 1, 11: 2, 4: 3</td><td class=\"num\">3</td>" in body
    assert "indices <strong>3 and 4</strong>" in body
    assert "<td class=\"num\">64</td><td class=\"num\">2016</td><td class=\"num\">254</td><td class=\"num\">64</td>" in body
    assert "<strong>[-2]</strong>: the buggy version returns 0, the right answer is -2" in body
    assert "<td>O(n²)</td><td class=\"num\">10,000</td>" in body


def test_segment_trees_helpers_match_the_page():
    nums = [5, 8, 6, 3, 2, 7, 2, 6]
    tree = leetcode_docs.segment_tree_of(nums)
    assert len(tree) == 15 and tree[0]["value"] == sum(nums)
    for entry in tree:
        assert entry["value"] == sum(nums[entry["lo"]:entry["hi"] + 1])

    q = leetcode_docs.segment_query_trace(nums, 2, 6)
    assert [(v["node"], v["kind"]) for v in q["visits"]] == [
        (1, "split"), (2, "split"), (4, "outside"), (5, "inside"), (3, "split"),
        (6, "inside"), (7, "split"), (14, "inside"), (15, "outside"),
    ]
    assert q["value"] == 20 == sum(nums[2:7]) and q["inside"] == [5, 6, 14]
    assert leetcode_docs.segment_query_trace(nums, 2, 6, "min")["value"] == 2 == min(nums[2:7])
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            for combine, fn in (("sum", sum), ("min", min), ("max", max)):
                assert leetcode_docs.segment_query_trace(nums, left, right, combine)["value"] == fn(nums[left:right + 1])

    up = leetcode_docs.segment_update_trace(nums, 3, 10)
    assert [(p["node"], p["old"], p["new"]) for p in up["path"]] == [(11, 3, 10), (5, 9, 16), (2, 22, 29), (1, 39, 46)]
    assert up["nums"] == [5, 8, 6, 10, 2, 7, 2, 6] and up["changed"] == [1, 2, 5, 11]

    sizes = leetcode_docs.segment_tree_sizes([8, 13, 100, 256])
    assert [(r["nodes"], r["largest_index"], r["worst_visits"], r["depth"]) for r in sizes] == [
        (15, 15, 11, 3), (25, 29, 15, 4), (199, 253, 27, 7), (511, 511, 31, 8),
    ]
    for row in sizes:
        assert row["largest_index"] < 4 * row["n"] and row["worst_visits"] <= 4 * row["depth"]

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/segment-trees").get_data(as_text=True))
    assert "sum of [2..6] = 9 + 9 + 2 = 20" in body
    assert "<td class=\"num\">5</td><td class=\"num\">[2..3]</td><td>inside: use whole</td><td class=\"num\">9</td>" in body
    assert "<td class=\"num\">11</td><td class=\"num\">[3..3]</td><td class=\"num\">3</td><td class=\"num\">10</td>" in body
    assert "the root holds <strong>46</strong>" in body
    assert "with <code>min</code> as the combining operation give <strong>2</strong>" in body
    assert "<td class=\"num\">100</td><td class=\"num\">199</td><td class=\"num\">253</td><td class=\"num\">400</td><td class=\"num\">27</td><td class=\"num\">28</td>" in body
    assert "Beyond the interview" in body


def test_fenwick_trees_helpers_match_the_page():
    nums = [5, 8, 6, 3, 2, 7, 2, 6]
    tree = leetcode_docs.fenwick_tree_of(nums)
    assert [(e["i"], e["lo"], e["hi"], e["value"]) for e in tree] == [
        (1, 1, 1, 5), (2, 1, 2, 13), (3, 3, 3, 6), (4, 1, 4, 22),
        (5, 5, 5, 2), (6, 5, 6, 9), (7, 7, 7, 2), (8, 1, 8, 39),
    ]
    for entry in tree:
        assert entry["value"] == sum(nums[entry["lo"] - 1:entry["hi"]])
        assert entry["binary"] == format(entry["i"], "04b")

    p7 = leetcode_docs.fenwick_prefix_trace(nums, 7)
    assert [(s["i"], s["running"], s["next"]) for s in p7["steps"]] == [(7, 2, 6), (6, 11, 4), (4, 33, 0)]
    assert p7["total"] == 33 and leetcode_docs.fenwick_prefix_trace(nums, 2)["total"] == 13
    for i in range(len(nums) + 1):
        assert leetcode_docs.fenwick_prefix_trace(nums, i)["total"] == sum(nums[:i])

    up = leetcode_docs.fenwick_update_trace(nums, 3, 7)
    assert [(s["i"], s["old"], s["new"], s["next"]) for s in up["steps"]] == [(3, 6, 13, 4), (4, 22, 29, 8), (8, 39, 46, 16)]
    assert up["nums"] == [5, 8, 13, 3, 2, 7, 2, 6] and up["changed"] == [3, 4, 8]
    for i in range(1, len(nums) + 1):
        trace = leetcode_docs.fenwick_update_trace(nums, i, 1)
        assert [s["i"] for s in trace["steps"]] == trace["changed"] == [e["i"] for e in tree if e["lo"] <= i <= e["hi"]]

    values = [3, 1, 4, 1, 5, 9, 2, 6]
    cs = leetcode_docs.fenwick_count_smaller_trace(values)
    assert cs["counts"] == [3, 0, 2, 0, 1, 2, 0, 0]
    assert cs["counts"] == [sum(1 for later in values[i + 1:] if later < value) for i, value in enumerate(values)]
    assert cs["ranks"] == {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 9: 7}

    costs = leetcode_docs.fenwick_costs([8, 13, 100, 1000])
    assert [(r["prefix"], r["updates"], r["bits"]) for r in costs] == [(3, 4, 4), (3, 4, 4), (6, 7, 7), (9, 10, 10)]

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/fenwick-trees").get_data(as_text=True))
    assert "prefix(7) = t[7] + t[6] + t[4] = 2 + 9 + 22 = 33" in body
    assert "the sum of positions 3 to 7 is 33 &minus; 13 = <strong>20</strong>" in body
    assert "<td class=\"num\">4</td><td class=\"num\"><code>0100</code></td><td class=\"num\">1..4</td><td class=\"num\">22</td><td class=\"num\">29</td><td class=\"num\">8</td>" in body
    assert "<strong>[3, 0, 2, 0, 1, 2, 0, 0]</strong>" in body
    assert "<td class=\"num\">1000</td><td class=\"num\">9</td><td class=\"num\">10</td><td class=\"num\">10</td>" in body


def test_string_matching_helpers_match_the_page():
    assert [row["lps"] for row in leetcode_docs.failure_table("abcabd")] == [0, 0, 0, 1, 2, 0]
    assert leetcode_docs.failure_table("abcabcabc")[-1]["lps"] == 6
    for word in ["aabaaab", "abababca", "aaaa", "abcab"]:
        for row in leetcode_docs.failure_table(word):
            prefix = word[:row["i"] + 1]
            assert row["lps"] == max(k for k in range(len(prefix)) if prefix[:k] == prefix[len(prefix) - k:])

    kmp = leetcode_docs.kmp_search_trace("abcabcabd", "abcabd")
    assert [(s["before"], s["fallbacks"], s["after"]) for s in kmp["steps"]][4:] == [
        (4, [], 5), (5, [2], 3), (3, [], 4), (4, [], 5), (5, [], 0),
    ]
    assert kmp["matches"] == [3] and kmp["comparisons"] == 10
    assert leetcode_docs.naive_search_comparisons("abcabcabd", "abcabd") == {"comparisons": 14, "matches": [3]}
    for text, pattern in [("aaaaa", "aa"), ("abababab", "abab"), ("xyz", "q"), ("abcabcabd", "abcabd")]:
        expected = [i for i in range(len(text) - len(pattern) + 1) if text[i:i + len(pattern)] == pattern]
        assert leetcode_docs.kmp_search_trace(text, pattern)["matches"] == expected
        assert leetcode_docs.naive_search_comparisons(text, pattern)["matches"] == expected

    costs = leetcode_docs.string_search_costs([[10, 3], [100, 10], [1000, 10], [1000, 100]])
    assert [(r["naive"], r["kmp"]) for r in costs] == [(24, 18), (910, 191), (9910, 1991), (90100, 1901)]
    assert all(r["kmp"] <= 2 * r["n"] for r in costs)

    rk = leetcode_docs.rabin_karp_trace("bcabdadcab", "abd", 26, 11)
    assert rk["target"] == 6 and rk["high"] == 5
    assert [w["hash"] for w in rk["windows"]] == [1, 10, 6, 5, 6, 2, 0, 10]
    assert rk["matches"] == [2] and rk["collisions"] == [4]
    for w in rk["windows"]:
        direct = 0
        for ch in w["window"]:
            direct = (direct * 26 + ord(ch) - ord("a") + 1) % 11
        assert w["hash"] == direct

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/string-matching").get_data(as_text=True))
    assert "<td class=\"num\">5</td><td><code>c</code></td><td class=\"num\">5</td><td class=\"num\">j &rarr; 2</td><td class=\"num\">3</td>" in body
    assert "KMP makes 10 character comparisons and the naive method 14" in body
    assert "<td class=\"num\">4</td><td><code>dad</code></td><td class=\"num\">6</td><td>hash hit, characters differ: collision</td>" in body
    assert "<td class=\"num\">1000</td><td class=\"num\">100</td><td class=\"num\">90100</td><td class=\"num\">1901</td><td class=\"num\">2000</td>" in body
    assert "Its last entry is 6, the border <code>abcabc</code>" in body


def test_bitmask_dp_helpers_match_the_page():
    cost = [[9, 2, 7], [6, 4, 3], [5, 8, 1]]
    assign = leetcode_docs.assignment_dp_trace(cost)
    assert [(r["bits"], r["cost"]) for r in assign["rows"]] == [
        ("000", 0), ("001", 9), ("010", 2), ("100", 7), ("011", 8), ("101", 12), ("110", 5), ("111", 9),
    ]
    assert [(s["worker"], s["job"]) for s in assign["path"]] == [(0, 1), (1, 0), (2, 2)]
    assert assign["greedy"] == [1, 2, 0] and assign["greedy_cost"] == 10
    for matrix in (cost, [[4, 1, 3, 2], [2, 0, 5, 3], [3, 2, 2, 4], [1, 6, 3, 2]], [[5]]):
        n = len(matrix)
        brute = min(sum(matrix[w][j] for w, j in enumerate(order)) for order in itertools.permutations(range(n)))
        assert leetcode_docs.assignment_dp_trace(matrix)["best"] == brute

    dist = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    tsp = leetcode_docs.held_karp_of(dist)
    assert tsp["best"] == 80 and tsp["tour"] == [0, 2, 3, 1, 0]
    assert [(r["end"], r["path"], r["total"]) for r in tsp["closing"]] == [(1, 70, 80), (2, 65, 80), (3, 75, 95)]
    assert [(s["bits"], s["end"], s["cost"]) for s in tsp["states"]] == [
        ("0001", 0, 0), ("0101", 2, 15), ("1101", 3, 45), ("1111", 1, 70),
    ]
    assert len(tsp["rows"]) == 13
    other = [[0, 3, 9, 4, 7], [3, 0, 2, 8, 6], [9, 2, 0, 5, 1], [4, 8, 5, 0, 3], [7, 6, 1, 3, 0]]
    for matrix in (dist, other):
        n = len(matrix)
        brute = min(sum(matrix[a][b] for a, b in zip((0,) + order, order + (0,)))
                    for order in itertools.permutations(range(1, n)))
        result = leetcode_docs.held_karp_of(matrix)
        assert result["best"] == brute
        assert sum(matrix[a][b] for a, b in zip(result["tour"], result["tour"][1:])) == brute

    assert leetcode_docs.submasks_of(11) == [11, 10, 9, 8, 3, 2, 1, 0]
    for mask in range(32):
        assert sorted(leetcode_docs.submasks_of(mask)) == [s for s in range(32) if s & mask == s]
    assert sum(len(leetcode_docs.submasks_of(mask)) for mask in range(1 << 6)) == 3 ** 6
    counts = leetcode_docs.bitmask_state_counts([4, 20])
    assert counts[0] == {"n": 4, "orders": 24, "held_karp": 256, "assignment": 64, "submask_pairs": 81}
    assert counts[1]["orders"] == 2432902008176640000 and counts[1]["assignment"] == 20971520

    body = re.sub(r"\s+", " ", app_module.app.test_client().get("/leetcode/bitmask-dp").get_data(as_text=True))
    assert "<td class=\"num\">3</td><td class=\"num\"><code>011</code></td><td>{0, 1}</td><td class=\"num\">2</td><td class=\"num\">8</td><td>B takes job 0 from mask 2: 2 + 6</td>" in body
    assert "for a total of <strong>9</strong>. The greedy order costs 10." in body
    assert "<td class=\"num\"><code>1101</code></td><td>{0, 2, 3}</td><td class=\"num\">3</td><td class=\"num\">45</td><td class=\"num\">2</td>" in body
    assert "<strong>0 &rarr; 2 &rarr; 3 &rarr; 1 &rarr; 0</strong>, length 80" in body
    assert "<td class=\"num\">20</td><td class=\"num\">2,432,902,008,176,640,000</td><td class=\"num\">419,430,400</td><td class=\"num\">20,971,520</td><td class=\"num\">3,486,784,401</td>" in body
