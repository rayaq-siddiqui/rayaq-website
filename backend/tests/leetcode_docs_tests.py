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
