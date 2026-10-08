import re

LISTS = [
    {"slug": "blind-75", "title": "Blind 75", "size": 75},
    {"slug": "grind-169", "title": "Grind 169", "size": 169},
    {"slug": "neetcode-150", "title": "NeetCode 150", "size": 150},
]

AREAS = [
    {
        "slug": "foundations",
        "title": "Foundations",
        "summary": "Big-O and amortized cost, the Python data structures and what each operation costs, recursion, and how to work an interview problem.",
    },
    {
        "slug": "arrays-hashing",
        "title": "Arrays and hashing",
        "summary": "Hash maps and sets for constant-time lookup, counting and bucketing, prefix sums, and in-place array tricks.",
    },
    {
        "slug": "two-pointers",
        "title": "Two pointers",
        "summary": "Two indices walking toward each other or in the same direction over a sorted or partitioned array.",
    },
    {
        "slug": "sliding-window",
        "title": "Sliding window",
        "summary": "A contiguous range that grows and shrinks while an invariant about its contents holds.",
    },
    {
        "slug": "stack",
        "title": "Stack",
        "summary": "Last-in, first-out matching and evaluation, and the monotonic stack for next-greater questions.",
    },
    {
        "slug": "binary-search",
        "title": "Binary search",
        "summary": "Halving a sorted range, and binary search over the answer when feasibility is monotonic.",
    },
    {
        "slug": "linked-list",
        "title": "Linked list",
        "summary": "Pointer rewiring, dummy heads, fast and slow pointers, and lists combined with hash maps.",
    },
    {
        "slug": "trees",
        "title": "Trees",
        "summary": "Depth-first and breadth-first traversal, binary search trees, and building and serializing trees.",
    },
    {
        "slug": "tries",
        "title": "Tries",
        "summary": "Prefix trees for word lookup, prefix search and pruning a search over a board.",
    },
    {
        "slug": "heap",
        "title": "Heap / priority queue",
        "summary": "Binary heaps, top-k selection, two heaps for a running median, k-way merging and quickselect.",
    },
    {
        "slug": "backtracking",
        "title": "Backtracking",
        "summary": "Choose, explore, unchoose: generating subsets, permutations and combinations, and pruning constrained searches.",
    },
    {
        "slug": "graphs",
        "title": "Graphs",
        "summary": "Representations, DFS and BFS, grids as graphs, topological sort and union-find.",
    },
    {
        "slug": "advanced-graphs",
        "title": "Advanced graphs",
        "summary": "Weighted shortest paths, minimum spanning trees and Eulerian paths.",
    },
    {
        "slug": "dp-1d",
        "title": "1-D dynamic programming",
        "summary": "Subproblems indexed by one position: memoization versus tabulation, knapsack and subsequence problems.",
    },
    {
        "slug": "dp-2d",
        "title": "2-D dynamic programming",
        "summary": "Subproblems indexed by two positions: grids, two strings, intervals and state machines.",
    },
    {
        "slug": "greedy",
        "title": "Greedy",
        "summary": "When a locally best choice is provably globally best, and Kadane's algorithm for maximum subarrays.",
    },
    {
        "slug": "intervals",
        "title": "Intervals",
        "summary": "Sorting by start, merging and inserting intervals, and sweeping events to count overlaps.",
    },
    {
        "slug": "math-geometry",
        "title": "Math and geometry",
        "summary": "Matrix rotation and spiral order, digit and modular arithmetic, fast exponentiation.",
    },
    {
        "slug": "bit-manipulation",
        "title": "Bit manipulation",
        "summary": "XOR tricks, masks, counting bits and arithmetic without arithmetic operators.",
    },
    {
        "slug": "beyond",
        "title": "Beyond the interview",
        "summary": "Tools that rarely come up in interviews but solve the hard problems: segment and Fenwick trees, string matching, bitmask DP.",
    },
]

LEVELS = ["intro", "core", "advanced"]


def _page(slug, title, area, level, summary, prerequisites=()):
    return {
        "slug": slug,
        "title": title,
        "area": area,
        "level": level,
        "summary": summary,
        "prerequisites": list(prerequisites),
        "ready": False,
    }


PAGES = [
    _page("complexity-analysis", "Complexity analysis", "foundations", "intro",
          "Big-O, best and worst case, amortized cost, and reading a problem's constraints to guess the target complexity."),
    _page("python-toolkit", "The Python toolkit", "foundations", "intro",
          "list, dict, set, deque, heapq and bisect: what each operation costs and which interview idioms they enable.",
          ["complexity-analysis"]),
    _page("recursion", "Recursion and the call stack", "foundations", "intro",
          "Base cases, the call stack, recursion trees and how to turn recursion into iteration.",
          ["complexity-analysis"]),
    _page("hash-maps-and-sets", "Hash maps and sets", "arrays-hashing", "intro",
          "Trading memory for constant-time lookup: seen-sets, complement maps and grouping by key.",
          ["python-toolkit"]),
    _page("counting-and-bucketing", "Counting and bucket sort", "arrays-hashing", "core",
          "Frequency maps, bucketing by count and canonical keys for grouping.",
          ["hash-maps-and-sets"]),
    _page("prefix-sums", "Prefix sums and products", "arrays-hashing", "core",
          "Precomputed running totals that answer range queries in constant time, and prefix sums with hash maps.",
          ["hash-maps-and-sets"]),
    _page("in-place-array-tricks", "In-place array tricks", "arrays-hashing", "core",
          "Index marking, cyclic placement and encoding strings so arrays do double duty without extra memory.",
          ["hash-maps-and-sets"]),
    _page("two-pointers", "Two pointers", "two-pointers", "intro",
          "Converging and same-direction pointers over sorted or partitioned arrays, including 3Sum.",
          ["complexity-analysis"]),
    _page("fixed-size-window", "Fixed-size sliding window", "sliding-window", "intro",
          "Sliding a window of width k and updating its summary in constant time per step.",
          ["two-pointers"]),
    _page("variable-size-window", "Variable-size sliding window", "sliding-window", "core",
          "Growing the right edge, shrinking the left until the invariant holds, and tracking the best window.",
          ["fixed-size-window", "hash-maps-and-sets"]),
    _page("stack", "Stacks", "stack", "intro",
          "Matching brackets, evaluating expressions and simulating with a last-in, first-out stack.",
          ["python-toolkit"]),
    _page("monotonic-stack", "Monotonic stack and deque", "stack", "core",
          "Keeping a stack sorted to answer next-greater and largest-rectangle questions, and the monotonic deque for window maxima.",
          ["stack", "fixed-size-window"]),
    _page("binary-search", "Binary search", "binary-search", "intro",
          "Halving a sorted range with a clear loop invariant, and searching rotated arrays.",
          ["complexity-analysis"]),
    _page("binary-search-on-answer", "Binary search on the answer", "binary-search", "core",
          "Searching the space of possible answers when a feasibility check is monotonic, and the median of two arrays.",
          ["binary-search"]),
    _page("linked-list-basics", "Linked list basics", "linked-list", "intro",
          "Reversing, merging and removing nodes with dummy heads and careful pointer rewiring.",
          ["recursion"]),
    _page("fast-slow-pointers", "Fast and slow pointers", "linked-list", "core",
          "Floyd's cycle detection, finding the middle, and treating an array as a linked list.",
          ["linked-list-basics", "two-pointers"]),
    _page("linked-list-design", "Linked lists with hash maps", "linked-list", "core",
          "The LRU cache and copying a list with random pointers: lists for order, maps for lookup.",
          ["linked-list-basics", "hash-maps-and-sets"]),
    _page("tree-dfs", "Tree depth-first search", "trees", "intro",
          "Preorder, inorder and postorder traversal, and returning values up the tree to answer height and path questions.",
          ["recursion"]),
    _page("tree-bfs", "Tree breadth-first search", "trees", "intro",
          "Level-order traversal with a queue, and questions about levels and views of a tree.",
          ["tree-dfs", "python-toolkit"]),
    _page("binary-search-trees", "Binary search trees", "trees", "core",
          "The ordering invariant, validating it, kth smallest, and lowest common ancestor in a BST.",
          ["tree-dfs", "binary-search"]),
    _page("tree-construction", "Building and serializing trees", "trees", "advanced",
          "Rebuilding a tree from traversals, serializing and deserializing, and maximum path sums.",
          ["tree-dfs", "tree-bfs"]),
    _page("tries", "Tries", "tries", "core",
          "Prefix trees for insert, search and prefix queries, wildcard search and pruning a board search.",
          ["tree-dfs", "hash-maps-and-sets"]),
    _page("heaps", "Heaps", "heap", "intro",
          "How a binary heap works, heapq idioms, and simulating schedules with a priority queue.",
          ["python-toolkit"]),
    _page("top-k-elements", "Top-k elements", "heap", "core",
          "Keeping a heap of size k to find the largest, smallest, closest or most frequent elements.",
          ["heaps", "counting-and-bucketing"]),
    _page("two-heaps", "Two heaps", "heap", "advanced",
          "A max-heap and a min-heap balanced around the middle for a running median.",
          ["heaps"]),
    _page("k-way-merge", "K-way merge", "heap", "core",
          "Merging k sorted sequences with a heap of their current heads.",
          ["heaps", "linked-list-basics"]),
    _page("quickselect", "Quickselect", "heap", "advanced",
          "Partitioning to find the kth element in expected linear time, and when it beats a heap.",
          ["top-k-elements", "two-pointers"]),
    _page("subsets-and-permutations", "Subsets, permutations and combinations", "backtracking", "core",
          "The choose-explore-unchoose template that generates every subset, permutation and combination, with and without duplicates.",
          ["recursion"]),
    _page("constraint-backtracking", "Constrained backtracking", "backtracking", "advanced",
          "Pruning searches with constraints: combination sum, word search, palindrome partitioning and N-queens.",
          ["subsets-and-permutations"]),
    _page("graph-traversal", "Graph DFS and BFS", "graphs", "intro",
          "Adjacency lists, visited sets, connected components, cloning a graph and detecting cycles.",
          ["tree-dfs", "tree-bfs"]),
    _page("grid-graphs", "Grids as graphs", "graphs", "core",
          "Flood fill, counting islands and multi-source BFS on a matrix.",
          ["graph-traversal"]),
    _page("topological-sort", "Topological sort", "graphs", "core",
          "Ordering a DAG with Kahn's algorithm or DFS finishing times, and detecting cycles in prerequisites.",
          ["graph-traversal"]),
    _page("union-find", "Union-find", "graphs", "core",
          "Disjoint sets with path compression and union by rank for connectivity and redundant edges.",
          ["graph-traversal"]),
    _page("dijkstra", "Dijkstra's algorithm", "advanced-graphs", "core",
          "Shortest paths with non-negative weights using a heap, and its variants on grids.",
          ["graph-traversal", "heaps"]),
    _page("bellman-ford", "Bellman-Ford and bounded paths", "advanced-graphs", "advanced",
          "Relaxing edges round by round for negative weights and paths limited to k edges.",
          ["dijkstra"]),
    _page("minimum-spanning-trees", "Minimum spanning trees", "advanced-graphs", "advanced",
          "Prim's and Kruskal's algorithms for connecting every node at minimum cost.",
          ["union-find", "heaps"]),
    _page("eulerian-paths", "Eulerian paths", "advanced-graphs", "advanced",
          "Hierholzer's algorithm for using every edge exactly once, as in reconstructing an itinerary.",
          ["graph-traversal"]),
    _page("dp-fundamentals", "Dynamic programming fundamentals", "dp-1d", "intro",
          "Overlapping subproblems, memoization versus tabulation, and the steps from brute force to DP.",
          ["recursion"]),
    _page("linear-dp", "Linear DP", "dp-1d", "core",
          "One-dimensional recurrences: climbing stairs, house robber, decode ways and maximum product subarray.",
          ["dp-fundamentals"]),
    _page("knapsack-dp", "Knapsack DP", "dp-1d", "core",
          "0/1 and unbounded knapsack: coin change, partition equal subset sum and word break.",
          ["dp-fundamentals"]),
    _page("longest-increasing-subsequence", "Longest increasing subsequence", "dp-1d", "advanced",
          "The quadratic DP and the patience-sorting binary search that makes it n log n.",
          ["linear-dp", "binary-search"]),
    _page("palindrome-dp", "Palindromes", "dp-1d", "core",
          "Expanding around centers and DP over substrings for palindromic substring questions.",
          ["dp-fundamentals", "two-pointers"]),
    _page("grid-dp", "Grid DP", "dp-2d", "core",
          "Counting and optimizing paths through a grid, and longest increasing path with memoized DFS.",
          ["dp-fundamentals", "grid-graphs"]),
    _page("string-dp", "Two-string DP", "dp-2d", "advanced",
          "Longest common subsequence, edit distance, interleaving and distinct subsequences.",
          ["dp-fundamentals"]),
    _page("interval-dp", "Interval DP", "dp-2d", "advanced",
          "DP over ranges of an array, as in burst balloons.",
          ["string-dp"]),
    _page("state-machine-dp", "State machine DP", "dp-2d", "advanced",
          "Modelling holding, selling and cooldown as states: the stock problems and target sum.",
          ["linear-dp"]),
    _page("greedy", "Greedy algorithms", "greedy", "core",
          "Exchange arguments and when a local choice is safe: jump game, gas station and hand of straights.",
          ["complexity-analysis"]),
    _page("kadanes-algorithm", "Kadane's algorithm", "greedy", "core",
          "Maximum subarray in one pass, and its circular variant.",
          ["greedy", "prefix-sums"]),
    _page("interval-merging", "Merging intervals", "intervals", "core",
          "Sorting by start to merge, insert and remove overlapping intervals.",
          ["python-toolkit"]),
    _page("sweep-line", "Sweep line", "intervals", "advanced",
          "Turning intervals into start and end events to count overlaps, as in meeting rooms.",
          ["interval-merging", "heaps"]),
    _page("matrix-manipulation", "Matrix manipulation", "math-geometry", "core",
          "Rotating, transposing and spiraling a matrix in place, and setting zeroes with markers.",
          ["in-place-array-tricks"]),
    _page("number-math", "Number math", "math-geometry", "core",
          "Digit manipulation, overflow, fast exponentiation and multiplying big numbers as strings.",
          ["complexity-analysis"]),
    _page("bit-manipulation", "Bit manipulation", "bit-manipulation", "core",
          "XOR to cancel pairs, masks to test and clear bits, counting bits and adding without plus.",
          ["number-math"]),
    _page("interview-approach", "Working an interview problem", "foundations", "core",
          "Clarify, find the brute force, spot the pattern from the signals, optimize, code, test: the loop every page feeds into.",
          ["complexity-analysis"]),
    _page("segment-trees", "Segment trees", "beyond", "advanced",
          "Range queries with point updates in logarithmic time.",
          ["recursion", "prefix-sums"]),
    _page("fenwick-trees", "Fenwick trees", "beyond", "advanced",
          "Binary indexed trees for prefix sums under updates.",
          ["prefix-sums", "bit-manipulation"]),
    _page("string-matching", "String matching", "beyond", "advanced",
          "KMP's failure function and Rabin-Karp rolling hashes for finding a pattern in linear time.",
          ["hash-maps-and-sets"]),
    _page("bitmask-dp", "Bitmask DP", "beyond", "advanced",
          "DP over subsets encoded as bits, for assignment and travelling-salesman-style problems.",
          ["dp-fundamentals", "bit-manipulation"]),
]

LEARNING_PATH = [
    {"title": "Foundations", "slugs": ["complexity-analysis", "python-toolkit", "recursion"]},
    {"title": "Arrays and pointers", "slugs": ["hash-maps-and-sets", "prefix-sums", "two-pointers", "variable-size-window"]},
    {"title": "Linear structures", "slugs": ["stack", "binary-search", "linked-list-basics"]},
    {"title": "Trees and heaps", "slugs": ["tree-dfs", "tree-bfs", "binary-search-trees", "heaps"]},
    {"title": "Search", "slugs": ["subsets-and-permutations", "graph-traversal", "topological-sort"]},
    {"title": "Dynamic programming", "slugs": ["dp-fundamentals", "linear-dp", "knapsack-dp", "string-dp"]},
    {"title": "Interview ready", "slugs": ["greedy", "interval-merging", "interview-approach"]},
]

PROBLEMS = []

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def problem_url(slug):
    return f"https://leetcode.com/problems/{slug}/"


def ready_pages():
    return [page for page in PAGES if page["ready"]]


def pages_by_area():
    return [
        {"area": area, "pages": [page for page in PAGES if page["area"] == area["slug"]]}
        for area in AREAS
    ]


def connections(slug):
    by_slug = {page["slug"]: page for page in PAGES}
    page = by_slug[slug]
    return {
        "prerequisites": [by_slug[prerequisite] for prerequisite in page["prerequisites"]],
        "leads_to": [entry for entry in PAGES if slug in entry["prerequisites"]],
    }


def learning_path():
    by_slug = {page["slug"]: page for page in PAGES}
    return [
        {"title": step["title"], "pages": [by_slug[slug] for slug in step["slugs"]]}
        for step in LEARNING_PATH
    ]


def problems_for(slug):
    return sorted(
        (problem for problem in PROBLEMS if problem["home"] == slug),
        key=lambda problem: (["Easy", "Medium", "Hard"].index(problem["difficulty"]), problem["number"]),
    )


def coverage():
    ready = {page["slug"] for page in ready_pages()}
    result = []
    for entry in LISTS:
        on_list = [problem for problem in PROBLEMS if entry["slug"] in problem["lists"]]
        covered = sum(1 for problem in on_list if problem["home"] in ready)
        result.append({**entry, "known": len(on_list), "covered": covered})
    return result


def find_area(slug):
    return next((area for area in AREAS if area["slug"] == slug), None)


def find_page(slug):
    return next((page for page in ready_pages() if page["slug"] == slug), None)


def table_of_contents(html):
    return [
        {"level": int(level), "id": anchor, "text": _TAG.sub("", text).strip()}
        for level, anchor, text in _HEADING.findall(html)
    ]


def _neighbours(slug):
    pages = ready_pages()
    slugs = [page["slug"] for page in pages]
    if slug not in slugs:
        return None, None
    position = slugs.index(slug)
    previous = pages[position - 1] if position > 0 else None
    following = pages[position + 1] if position + 1 < len(pages) else None
    return previous, following


def render(slug, render_template):
    if slug is None:
        page = None
        template = "leetcode/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"leetcode/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "areas": AREAS,
        "lists": LISTS,
        "pages_by_area": pages_by_area(),
        "area": find_area(page["area"]) if page else None,
        "connections": connections(page["slug"]) if page else None,
        "learning_path": learning_path(),
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "problems": problems_for(page["slug"]) if page else [],
        "coverage": coverage(),
        "problem_url": problem_url,
        "previous_page": previous,
        "next_page": following,
    }
    content = render_template(template, **context)
    intro, separator, body = content.partition("</header>")
    if not separator:
        intro, body = "", content
    else:
        intro += separator
    return render_template(
        "leetcode/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
