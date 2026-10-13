# rayaq.ca/leetcode — build progress

This is the running log for the leetcode Routine. Read it first and update it last. The
contract is `specs/leetcode.md` (spec v1, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-13 (seventh audit run). All 58 pages are ready and the queue is empty. This audit found and fixed one gap (factual errors in page prose). The owner asked for weekly audits whether or not an audit finds a gap, but this session also had no `update_trigger` tool, so the schedule is still every 5 hours (see Known gaps). **The next run is an audit run** (spec §8.1). Before any other work, it moves this Routine to weekly: `update_trigger` on `trig_01XkmtUwbN1iL5esk5KeGRPa` with `CRON_TZ=America/Los_Angeles 14 4 * * 2`.

## The Routine

"rayaq.ca/leetcode — pattern reference agent" runs every 5 hours in a fresh session (spec §8),
weekly once the build is complete, and pushes straight to `main`. The phone check before each push is
`NODE_PATH=$(npm root -g) node tools/leetcode/check_mobile.js / /leetcode <ready pages>`.

## Research

- [x] Blind 75 in `PROBLEMS` (75 problems), sources recorded below
- [x] Grind 169 in `PROBLEMS` (169 problems), sources recorded below
- [x] NeetCode 150 in `PROBLEMS` (150 problems), sources recorded below
- [x] NeetCode 250 in `PROBLEMS` (250 problems), sources recorded below
- [x] Every problem has a `home` page and a one-line original `insight`

### Sources

| List | Source URL | Accessed | Size |
|---|---|---|---|
| Blind 75 | https://github.com/neetcode-gh/leetcode/blob/main/.problemSiteData.json (`blind75` flag) | 2026-10-08 | 75 |
| Blind 75 | https://github.com/wislertt/leetcode-py (`.claude/.dev/problem_lists/blind_75.py`) | 2026-10-08 | 75 |
| Blind 75 | https://github.com/open-minded13/leetcode-blind-75-solutions (README; cross-check only) | 2026-10-08 | 68 |
| Grind 169 | https://github.com/wislertt/leetcode-py (`.claude/.dev/problem_lists/grind.py`) | 2026-10-08 | 169 |
| Grind 169 | https://github.com/open-minded13/leetcode-grind-169-solutions (README, Parts 1–16) | 2026-10-08 | 169 |
| NeetCode 150 | https://github.com/neetcode-gh/leetcode/blob/main/.problemSiteData.json (`neetcode150` flag) | 2026-10-08 | 150 |
| NeetCode 150 | https://github.com/wislertt/leetcode-py (`.claude/.dev/problem_lists/neetcode_150.py`) | 2026-10-08 | 150 |
| NeetCode 250 | https://github.com/wislertt/leetcode-py (`.claude/.dev/problem_lists/neetcode_250.py`) | 2026-10-08 | 250 |
| NeetCode 250 | https://github.com/ascherj/neetcode-250-guide (`neetcode_250_complete.json`) | 2026-10-08 | 250 |
| Titles, slugs, difficulty | https://github.com/wislertt/leetcode-py (per-problem JSON `problem_title`), cross-checked with the sources above | 2026-10-08 | 297 |

## Coverage

| List | Problems with a ready home | Size |
|---|---|---|
| Blind 75 | 75 | 75 |
| Grind 169 | 169 | 169 |
| NeetCode 150 | 150 | 150 |
| NeetCode 250 | 250 | 250 |

## Queue

Prerequisites come first (tested). `✓` marks ready pages; `← next` marks the next page to
build once research is done.

1. `complexity-analysis` ✓
2. `python-toolkit` ✓
3. `recursion` ✓
4. `hash-maps-and-sets` ✓
5. `counting-and-bucketing` ✓
6. `prefix-sums` ✓
7. `in-place-array-tricks` ✓
8. `two-pointers` ✓
9. `fixed-size-window` ✓
10. `variable-size-window` ✓
11. `stack` ✓
12. `monotonic-stack` ✓
13. `binary-search` ✓
14. `binary-search-on-answer` ✓
15. `linked-list-basics` ✓
16. `fast-slow-pointers` ✓
17. `linked-list-design` ✓
18. `tree-dfs` ✓
19. `tree-bfs` ✓
20. `binary-search-trees` ✓
21. `tree-construction` ✓
22. `tries` ✓
23. `heaps` ✓
24. `top-k-elements` ✓
25. `k-way-merge` ✓
26. `two-heaps` ✓
27. `quickselect` ✓
28. `subsets-and-permutations` ✓
29. `constraint-backtracking` ✓
30. `graph-traversal` ✓
31. `grid-graphs` ✓
32. `topological-sort` ✓
33. `union-find` ✓
34. `dijkstra` ✓
35. `bellman-ford` ✓
36. `minimum-spanning-trees` ✓
37. `eulerian-paths` ✓
38. `dp-fundamentals` ✓
39. `linear-dp` ✓
40. `knapsack-dp` ✓
41. `palindrome-dp` ✓
42. `longest-increasing-subsequence` ✓
43. `grid-dp` ✓
44. `string-dp` ✓
45. `interval-dp` ✓
46. `state-machine-dp` ✓
47. `greedy` ✓
48. `kadanes-algorithm` ✓
49. `interval-merging` ✓
50. `sweep-line` ✓
51. `matrix-manipulation` ✓
52. `number-math` ✓
53. `bit-manipulation` ✓
54. `interview-approach` ✓
55. `segment-trees` ✓
56. `fenwick-trees` ✓
57. `string-matching` ✓
58. `bitmask-dp` ✓

## Decisions

- **Scaffolding (2026-10-08).** The registry follows the NeetCode roadmap's 18 topics, plus
  *Foundations* and *Beyond the interview*. Pages teach patterns, not problems; each problem
  has exactly one home page. The section reuses `jj.css` for layout, like `/ml-models`.
- **Owner answers (2026-10-08).** Coverage adds **NeetCode 250** as a fourth list (spec v1
  updated with the owner's approval). Page code stays Python only. Once an audit run finds no
  gaps, the Routine moves itself to weekly audits. Notifications stay push.
- **Three pages per build run (2026-10-08, owner).** A build run does not stop until it has
  built three queue items (or emptied the queue), pushing after each one. (Briefly five,
  then lowered to three the same day.)
- **Page helpers (2026-10-08).** Each page's worked-example helpers live in `leetcode_docs.py`
  and are passed to templates through `render()`'s context; list problems render through the
  shared `leetcode/_problems.html` partial (home problems by difficulty with list badges and
  insights, then the "also uses" list). Pages are marked ready by adding their slug to `READY`.
- **Research reconciliation (2026-10-08).** The list sites (leetcode.com, neetcode.io,
  techinterviewhandbook.org) are blocked by the network policy, so every list comes from two
  independent GitHub-hosted sources that agree exactly (see Sources). Blind 75 follows
  NeetCode's version (39 Combination Sum); open-minded13's README omits the seven premium
  problems and uses 377 Combination Sum IV instead, and was used only as a cross-check.
  Grind 169 excludes the "Additional Exercises" beyond Part 16. Union: 297 problems.
  Edit Distance (72) is Medium (two sources against one); 242 Valid Anagram is Easy; title
  casing follows LeetCode's (e.g. "Remove Duplicates from Sorted Array").
- **Homes (2026-10-08).** Every problem has one home; no pages were added, split or merged.
  Seven pages own no problems by design and teach through `patterns` and prose instead:
  `complexity-analysis`, `dp-fundamentals`, `interview-approach`, `segment-trees`,
  `fenwick-trees`, `string-matching`, `bitmask-dp`.

- **Pull before every change (2026-10-09, owner).** The Routine runs `git pull --rebase
  origin main` before it starts each page or any other development, not only at the start of a
  run, and re-reads this file if anything came in.

- **Audit checks (2026-10-12).** Audit runs render every ready page and check internal links and
  `#anchors`, problem link format, home and "also uses" problems, the quiz count and the
  references. Spec §6's textbook list (CLRS, Skiena, Sedgewick & Wayne) is read as all three per
  page, and `test_ready_page_follows_the_format` now enforces it. Sedgewick & Wayne section
  numbers were checked against the `Section x.y` headers in the algs4 sources on GitHub.
- **Worked-example tables (2026-10-12).** Spec §6's "traced step by step in a table" is read as
  an HTML `<table>` inside the `worked-example` section; an SVG drawn as a grid elsewhere on the
  page does not count. `test_ready_page_follows_the_format` now enforces it.
- **Brute-force baselines (2026-10-12).** Spec §6's "the brute-force baseline" is read as an
  explicit mention (brute force, naive or baseline) inside the `tradeoffs` section; a baseline
  given only under Problem does not count. `test_ready_page_follows_the_format` now enforces it.
  Pages whose "also uses" list is empty show none: the list is built from `PROBLEMS`, and no
  problem's `patterns` names them.
- **Sedgewick & Wayne sections (2026-10-12).** Every Sedgewick & Wayne citation names a section
  (or chapter) of the 4th edition, and never 6.2 (B-trees) or 6.4 (max flow), which no page
  teaches. Section titles were checked against the `Section x.y` headers in the algs4 sources
  (`FordFulkerson.java` is 6.4, `BTree.java` 6.2, `AcyclicSP.java` 4.4, `NFA.java` 5.4,
  `LongestCommonSubstring.java` 6.3). `test_sedgewick_citations_name_real_sections` enforces it.

- **Runnable page code (2026-10-12).** Every ready page's `<pre><code>` blocks, joined in page
  order, must parse and import or define every name they use, so a reader can copy them. The only
  exceptions are deliberate placeholders listed in `CODE_PLACEHOLDERS` (the recursion skeleton's
  steps, the toolkit's cheat-sheet variables, LeetCode's own `Node` class in Clone Graph, and the
  submask-loop fragment). `test_page_code_parses_and_imports_what_it_uses` enforces it.

- **Page code gives right answers (2026-10-13).** Audit runs also execute every ready page's code
  and compare each function against an independent brute force on random inputs (within the
  problem's real constraints). A function whose answer is wrong is a gap. Pages state the input
  assumptions they rely on (for example, distinct values in rotated-array search). Functions
  that were wrong get a regression test that runs the page's own code (`run_page_code`).

- **Weekly audits now (2026-10-13, owner).** All 58 pages are ready, so the owner moved the
  Routine from every 5 hours to weekly audits (Tuesdays 04:14 America/Los_Angeles). This applies
  even when an audit finds and fixes a gap. The sixth audit's session had no tool that edits
  Routine schedules, so the next run makes the change (see Known gaps).

- **Prose is fact-checked (2026-10-13).** Audit runs also read every ready page's prose, quiz answers,
  captions, complexity claims, citations and home-problem insights against the rendered values and
  the literature. A false statement is a gap even when the code and tables are right. Captions that
  describe example values bind them from the helper rather than restating numbers by hand.

## Known gaps and questions for the owner

- **Schedule not yet weekly (2026-10-13).** The owner asked for weekly audits, but the session that
  recorded the request had no `update_trigger` tool. The next run calls `update_trigger` on
  `trig_01XkmtUwbN1iL5esk5KeGRPa` with `CRON_TZ=America/Los_Angeles 14 4 * * 2` and clears this
  gap. If it can't, the owner can change the schedule by hand under the Routine's settings at
  claude.ai/code. The seventh audit's session had no `update_trigger` tool either.

## Run log

### 2026-10-08 — scaffolding

Set up `/leetcode`: `leetcode_docs.py` registry, index template, styles, route, tests, spec,
this file, the phone check, and the Routine.

### 2026-10-08 — research run (blocked)

Found only one reachable source (NeetCode's `.problemSiteData.json`: Blind 75 = 75, NeetCode 150 = 150).
No second source for any list and no Grind 169 source. Changed nothing in `PROBLEMS`.

### 2026-10-08 — research run

Populated `PROBLEMS` from GitHub-hosted sources (two per list, reconciled; see Sources and
Decisions): Blind 75 = 75, Grind 169 = 169, NeetCode 150 = 150, NeetCode 250 = 250, 297
problems in all, each with a home page, related patterns and an original one-sentence insight.
No content pages built. Coverage is 0 for every list until pages ship.

### 2026-10-08 — build run

Built `complexity-analysis`, `python-toolkit` and `recursion` (3 of 3), each with tested helpers,
two inline SVGs and the full §6 format; added the shared `_problems.html` partial and diagram
colour classes in `leetcode.css`; made the coverage test independent of which pages are ready.
Coverage: Blind 75 0/75, Grind 169 1/169, NeetCode 150 0/150, NeetCode 250 4/250. Mobile check
passed on `/`, `/leetcode` and all three pages. Next: `hash-maps-and-sets`.

### 2026-10-08 — build run

Built `hash-maps-and-sets`, `counting-and-bucketing` and `prefix-sums` (3 of 3), each with tested
helpers in `leetcode_docs.py`, two or more inline SVGs and the full §6 format. Coverage: Blind 75
7/75, Grind 169 16/169, NeetCode 150 9/150, NeetCode 250 21/250. Mobile check passed on `/`,
`/leetcode` and all six ready pages. Next: `in-place-array-tricks`.

### 2026-10-08 — build run

Built `in-place-array-tricks`, `two-pointers` and `fixed-size-window` (3 of 3), each with tested
helpers in `leetcode_docs.py`, three inline SVGs and the full §6 format. Coverage: Blind 75
11/75, Grind 169 31/169, NeetCode 150 16/150, NeetCode 250 40/250. Mobile check passed on `/`,
`/leetcode` and all nine ready pages. Next: `variable-size-window`.

### 2026-10-08 — build run

Built `variable-size-window`, `stack` and `monotonic-stack` (3 of 3), each with tested helpers
in `leetcode_docs.py`, two inline SVGs and the full §6 format. Mobile check passed on `/`,
`/leetcode` and all eleven ready pages. Coverage: Blind 75 15/75, Grind 169 46/169, NeetCode 150 26/150,
NeetCode 250 59/250. Next: `binary-search`.

### 2026-10-08 — build run (checkout repair)

Built `binary-search`, `binary-search-on-answer` and `linked-list-basics` (3 of 3), each with
tested helpers in `leetcode_docs.py`, two inline SVGs and the full §6 format. Mobile check passed
on `/`, `/leetcode` and all fifteen ready pages. Coverage: Blind 75 20/75, Grind 169 63/169,
NeetCode 150 38/150, NeetCode 250 81/250. Next: `fast-slow-pointers`. The sandbox's local `main`
had no common history with `origin/main`; it was kept as the local branch `backup/stale-local-main`
and `main` was re-pointed at `origin/main` before building.

### 2026-10-09 — build run

Built three pages in queue order: `fast-slow-pointers`, `linked-list-design`, `tree-dfs` (3 of 3).
Each shipped with a tested stdlib helper, two or more inline SVGs and a page test. pytest green
(404 passed); the 390px phone check passed on `/`, `/leetcode` and every ready page.
Coverage: Blind 75 27/75, Grind 169 80/169, NeetCode 150 52/150, NeetCode 250 103/250.
Checkout repair: the local `main` had diverged, so it was saved as `backup-stale-main` and reset
to `origin/main`. Next queue item: `tree-bfs`.

### 2026-10-09 — build run (second)

Built three pages in queue order: `tree-bfs`, `binary-search-trees`, `tree-construction` (3 of 3).
Each shipped with tested stdlib helpers, two inline SVGs and a page test; each was pushed separately.
pytest green (413 passed); the 390px phone check passed on `/`, `/leetcode` and every ready page.
Coverage: Blind 75 33/75, Grind 169 92/169, NeetCode 150 59/150, NeetCode 250 112/250.
Checkout repair: the sandbox's local `main` had diverged from `origin/main` (50 commits each, different
patch ids), so it was left untouched and the work was done on a branch cut from `origin/main` and pushed
to `main`. Next queue item: `tries`.

### 2026-10-09 — build run (third)

Built three pages in queue order: `tries`, `heaps`, `top-k-elements` (3 of 3). Each shipped with tested
stdlib helpers, two or more inline SVGs and a page test; each was pushed separately.
pytest green (436 passed); the 390px phone check passed on `/`, `/leetcode` and every ready page.
Coverage: Blind 75 36/75, Grind 169 99/169, NeetCode 150 65/150, NeetCode 250 120/250.
Checkout repair: local `main` again had unrelated history, so work was done on a branch cut from
`origin/main` and pushed to `main`. Next queue item: `k-way-merge`.

### 2026-10-09 — build run (fourth)

Built three pages in queue order: `k-way-merge`, `two-heaps`, `quickselect` (3 of 3). Each shipped with tested
stdlib helpers, two inline SVGs and a page test; each was pushed separately.
pytest green (445 passed); the 390px phone check passed on `/`, `/leetcode` and every ready page.
Coverage: Blind 75 38/75, Grind 169 103/169, NeetCode 150 69/150, NeetCode 250 125/250.
Checkout repair: local `main` had unrelated history again; it was kept as the local branch `backup-stale-main`
and `main` was reset to `origin/main` before building. Next queue item: `subsets-and-permutations`.

### 2026-10-09 — build run (local main diverged)

The sandbox's local `main` had an unrelated history to `origin/main`, so work started from the fetched `origin/main` tip and pushed to `main` from there.
Built `subsets-and-permutations`, with six tested helpers (`backtrack_tree`, `subsets_of`, `permutations_of`, `subsets_with_duplicates`, `combinations_of`, `parentheses_of`), two inline SVG decision trees and the full §6 format. Mobile check passed on every ready page.
Built `constraint-backtracking`, with four tested helpers (`combination_sum_of`, `n_queens_of`, `word_search_of`, `palindrome_partitions_of`), two inline SVGs (the 4-queens search tree and a word-search path) and the full §6 format.
Built `graph-traversal` (3 of 3 this run), with six tested helpers (`adjacency_list`, `graph_walks`, `connected_components_of`, `directed_cycle_of`, `word_ladder_of`, `clone_graph_of`), two inline SVGs (DFS/BFS visit orders and BFS layers) and the full §6 format. Mobile check passed on `/`, `/leetcode` and all 30 ready pages. Next: `grid-graphs`.

### 2026-10-10 — build run

Built `grid-graphs`, `topological-sort` and `union-find` (3 of 3), each with tested helpers in
`leetcode_docs.py`, two or three inline SVGs and the full §6 format. Coverage: Blind 75 47/75, Grind 169 128/169, NeetCode 150 93/150, NeetCode 250 165/250.
Mobile check passed on `/`, `/leetcode` and all thirty-three ready
pages. The sandbox checkout was shallow and behind `origin/main`; deepened it and fast-forwarded
before starting. Next: `dijkstra`.

### 2026-10-10 — build run (second)

Built `dijkstra`, `bellman-ford` and `minimum-spanning-trees` (3 of 3), with six tested helpers (`dijkstra_trace`, `shortest_path_to`, `network_delay_of`, `minimum_effort_of`, `swim_in_water_of`, `negative_edge_counterexample`), two inline SVGs and the full §6 format; `bellman-ford` adds `bellman_ford_rounds`, `cheapest_flights_of` and `has_negative_cycle_of`. `minimum-spanning-trees` adds `kruskal_trace`, `prim_trace`, `connect_points_cost_of` and `critical_edges_of`. Coverage: Blind 75 47/75, Grind 169 129/169, NeetCode 150 97/150, NeetCode 250 171/250. Mobile check passed on all thirty-six ready pages. The sandbox's local `main` held 50 unpushed ml-models commits unrelated to `origin/main`; they were kept on the local branch `backup-stale-main` and `main` was reset to `origin/main`. Next: `eulerian-paths`.

### 2026-10-10 — build run (third)

Built `eulerian-paths`, `dp-fundamentals` and `linear-dp` (3 of 3), each with tested helpers in `leetcode_docs.py`, two or three inline SVGs and the full §6 format. `linear-dp` adds `climb_table_of`, `min_cost_climb_of`, `house_robber_trace`, `circular_robber_of`, `decode_ways_trace`, `max_product_trace`, `tribonacci_of`, `integer_break_of` and `stone_game_three_of`. Coverage: Blind 75 52/75, Grind 169 133/169, NeetCode 150 104/150, NeetCode 250 181/250. Mobile check passed on `/`, `/leetcode` and all 39 ready pages. The sandbox checkout was shallow; `git fetch --unshallow` fixed a false "no merge base". Next: `knapsack-dp`.

### 2026-10-10 — build run (fourth)

Built `knapsack-dp`, `palindrome-dp` and `longest-increasing-subsequence` (3 of 3; the last adds `lis_dp_trace`, `patience_trace` and `lis_count_of`; palindrome-dp adds `palindrome_table_of`, `expand_centers_trace` and `manacher_of`). `knapsack-dp`: with `subset_sum_trace`, `coin_change_trace`, `greedy_coin_count`, `coin_ways_of`, `word_break_table` and `target_sum_of`, three inline SVGs and the full §6 format. Local `main` again had unrelated history; it was kept as `backup/stale-local-main` and reset to `origin/main`. Coverage: Blind 75 57/75, Grind 169 140/169, NeetCode 150 112/150, NeetCode 250 193/250. Mobile check passed on all 42 ready pages. Next: `grid-dp`.

### 2026-10-10 — build run

Built `grid-dp`, `string-dp` and `interval-dp` (3 of 3), each with tested helpers in
`leetcode_docs.py` (cross-checked against brute force where cheap), two or three inline SVGs and
the full §6 format. The sandbox checkout was a stale shallow clone with no merge base, so it was
unshallowed and fast-forwarded to `origin/main` before any edit. Coverage: Blind 75 59/75, Grind 169 143/169, NeetCode 150 120/150, NeetCode 250 205/250.
Mobile check passed on `/`, `/leetcode` and
every ready page. Next: `state-machine-dp`.

### 2026-10-11 — build run

Built `state-machine-dp`, `greedy` and `kadanes-algorithm` (3 of 3), each with tested helpers in
`leetcode_docs.py` (cross-checked against brute force), two inline SVGs and the full §6 format.
The sandbox's local `main` was an unrelated history with no merge base, so work was done in a
separate git worktree on `origin/main` and pushed from there; the stale local branch was left
untouched. Coverage: Blind 75 63/75, Grind 169 150/169, NeetCode 150 132/150, NeetCode 250 224/250.
Mobile check passed on `/`, `/leetcode` and every ready page. Next: `interval-merging`.

### 2026-10-11 — build run (second)

Built `interval-merging`, `sweep-line` and `matrix-manipulation` (3 of 3), each with tested
helpers in `leetcode_docs.py` (cross-checked against brute force), two inline SVGs and the full
§6 format. The matrix rotation helper is `rotate_matrix_stages`, because `rotate_stages` already
belongs to the array-rotation page. The checkout was a shallow clone that looked diverged
("ahead 50, behind 50"); `git fetch --unshallow origin main` showed it was only behind, and it
fast-forwarded cleanly. Coverage: Blind 75 70/75, Grind 169 158/169, NeetCode 150 140/150,
NeetCode 250 234/250. Mobile check passed on `/`, `/leetcode` and every ready page. Next:
`number-math`.

### 2026-10-11 — build run (third)

Built `number-math` with tested helpers in `leetcode_docs.py` (reverse with the 32-bit check
before the multiply, half-reversal palindrome, square-and-multiply, the multiply-strings slot
array, bijective base 26, Euclid, atoi, Roman numerals, Plus One), each cross-checked against
brute force, two inline SVGs and the full §6 format. Then built `bit-manipulation` the same
way (XOR folds, `n & (n - 1)` popcount, counting bits, the masked XOR/AND adder, reverse bits,
range AND, minimum array end, add binary, missing number). Every problem on all four lists now
has a ready home: Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150, NeetCode 250
250/250. Last, built `interview-approach`: a master signals table linking every ready
pattern page, the interview loop as a flowchart, and Two Sum costed three ways (all pairs,
sort plus two pointers, hash map) with step counts from tested helpers. It is home to no list
problems by design. Three of three queue items built. Mobile check passed on `/`, `/leetcode`
and every ready page. Next: `segment-trees`.

### 2026-10-11 — build run (fourth)

Built `segment-trees` with tested helpers in `leetcode_docs.py` (`segment_tree_of`,
`segment_query_trace` and `segment_update_trace` for sum, min and max, checked against every
range by brute force, and `segment_tree_sizes` for the 4n and 4 log n bounds), two inline SVGs
drawn from the helper output, and the full §6 format with the recursive, bottom-up and lazy
trees. It is home to no list problems, so `_problems.html` now says so for *beyond* pages, and
the page lists off-list practice problems instead. Mobile check passed on `/`, `/leetcode` and
every ready page. Then built `fenwick-trees` the same way: `fenwick_tree_of`,
`fenwick_prefix_trace`, `fenwick_update_trace`, `fenwick_count_smaller_trace` and
`fenwick_costs`, each checked against brute force, with both diagrams drawn as bars over the
positions each slot sums. A row key named `update` rendered as the dict method in Jinja; it is
now `updates`. Last, built `string-matching`: `failure_table`, `kmp_search_trace`,
`naive_search_comparisons`, `string_search_costs` and `rabin_karp_trace` (base 26, modulus
11, small enough to show a collision), with KMP, Rabin–Karp and Z-array code, an alignment
diagram of the KMP slide, and a rolling-hash diagram. Three of three queue items built.
Coverage is unchanged at 100% on all four lists (Blind 75 75/75, Grind 169 169/169,
NeetCode 150 150/150, NeetCode 250 250/250). Mobile check passed on `/`, `/leetcode` and
every ready page. Next: `bitmask-dp`.

### 2026-10-11 — build run (fifth)

Built `bitmask-dp`, the last queue item (1 of 3; the queue ran out). Tested helpers in
`leetcode_docs.py`: `assignment_dp_trace` (DP over job masks, with the greedy order it beats),
`held_karp_of` (every reachable `(mask, last)` state, the closing legs and the tour),
`submasks_of` and `bitmask_state_counts`, each checked against brute force over permutations or
all masks. Two inline SVGs drawn from the helper output: the subset lattice with the cheapest
path, and the Held–Karp tour beside the states it passes through. The page has no home
problems by design; it lists Matchsticks to Square and Partition to K Equal Sum Subsets as
"also uses" and eight off-list practice problems. `bit-manipulation` and `eulerian-paths` now
link to it where they mention bitmask DP. Coverage is unchanged at 100% (Blind 75 75/75,
Grind 169 169/169, NeetCode 150 150/150, NeetCode 250 250/250). Mobile check passed on `/`,
`/leetcode` and every ready page. Next: the first audit run.

### 2026-10-12 — audit run

First audit run. Rendered all 58 ready pages and the index and checked internal links and anchors,
problem links, home and "also uses" problems, quiz counts, SVGs and references. One gap: eight
pages cited only two of spec §6's three textbooks, and two Sedgewick & Wayne citations named
unrelated sections (`longest-increasing-subsequence` cited 6.4, which covers max flow;
`constraint-backtracking` cited a "6.1 of the companion text"). Added the missing citations and
replaced the two wrong ones, and extended the format test to require all three textbooks, NeetCode
and 3–4 quiz questions on every ready page. No content or helpers changed. Coverage is unchanged at
100% (Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150, NeetCode 250 250/250). pytest green
(653 passed); the phone check passed on `/`, `/leetcode` and every ready page. Because this run found a
gap, the schedule stays at every 5 hours. Next: another audit run.

### 2026-10-12 — audit run (second)

Second audit run. Checked every ready page's sections against spec §6 beyond what the format test
covered. One gap: fourteen pages (`bellman-ford`, `minimum-spanning-trees`, `eulerian-paths`,
`dp-fundamentals`, `linear-dp`, `knapsack-dp`, `longest-increasing-subsequence`, `palindrome-dp`,
`grid-dp`, `string-dp`, `interval-dp`, `state-machine-dp`, `greedy`, `kadanes-algorithm`) traced
their worked example only in prose and in an SVG under Mechanics, with no table in the Worked
example section; the `bellman-ford` prose even referred to a table that was missing. Each now has
a step table bound to its existing tested helper's output, and the format test requires one on
every ready page. No helpers changed. Coverage is unchanged at 100% (Blind 75 75/75, Grind 169
169/169, NeetCode 150 150/150, NeetCode 250 250/250). pytest green (664 passed); every ready page
returns 200 and the phone check passed on `/`, `/leetcode` and every ready page. Because this run
found a gap, the schedule stays at every 5 hours. Next: another audit run.

### 2026-10-12 — audit run (third)

Third audit run. Checked every ready page for the §6 rules the format test did not yet cover:
the header summary, `<pre><code>` templates, variations and edge cases, SVG containers, the
"also uses" list, the *beyond* note and the brute-force baseline. One gap: seven pages did not
name a brute-force baseline in Complexity and tradeoffs (`stack`, `recursion` and
`matrix-manipulation` had none; `python-toolkit`, `sweep-line`, `segment-trees` and
`fenwick-trees` compared against naive approaches without naming the baseline). Each now states
it, and the format test requires it on every ready page. No helpers changed. Coverage is
unchanged at 100% (Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150, NeetCode 250
250/250). pytest green (676 passed); every ready page returns 200 and the phone check passed on
`/`, `/leetcode` and every ready page. Because this run found a gap, the schedule stays at every
5 hours. Next: another audit run.

### 2026-10-12 — audit run (fourth)

Fourth audit run. Checked the parts of spec §6 the tests did not yet cover (code-free intuition,
variations and edge cases, SVG colours, the roadmap credit, the *beyond* note, original papers),
then every Sedgewick & Wayne citation against the algs4 sources. One gap: ten pages cited
sections that do not cover their topic or no section at all. `grid-dp`, `interval-dp`,
`state-machine-dp` and `string-dp` cited section 6.4 (max flow), `knapsack-dp` cited 6.4 as
"reductions", `linear-dp` cited 6.2 (B-trees) as "recurrences", `dp-fundamentals` cited an online
DP chapter the book does not have, `subsets-and-permutations` cited 2.3 (quicksort) for
permutations, and `greedy` and `variable-size-window` named no section. Each now cites the
section that applies (4.4 acyclic shortest paths for the DP pages, plus 5.4, 6.3 or 1.1 where
relevant; 4.1 for backtracking; 4.3 and 4.4 for greedy; 1.4 for amortized analysis), and a new
test checks every citation. No content or helpers changed. Coverage is unchanged at 100%
(Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150, NeetCode 250 250/250). pytest green
(748 passed); every ready page returns 200 and the phone check passed on `/`, `/leetcode` and
every ready page. Because this run found a gap, the schedule stays at every 5 hours. Next:
another audit run.

### 2026-10-12 — audit run (fifth)

Fifth audit run. Extracted every ready page's code blocks and checked them with a static
undefined-name pass. All 97 blocks parse. One gap: two pages' code raised `NameError` when
copied. `bitmask-dp`'s assignment and travelling-salesman templates used `math.inf` without
`import math`, and `longest-increasing-subsequence`'s non-decreasing variation called
`bisect_right` while the page imported only `bisect_left`. Each block now imports what it uses,
and a new test fails on any unbound name outside a short placeholder list. No prose or helpers
changed. Coverage is unchanged at 100% (Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150,
NeetCode 250 250/250). pytest green (820 passed); every ready page returns 200 and the phone check
passed on `/`, `/leetcode` and every ready page. Because this run found a gap, the schedule stays
at every 5 hours. Next: another audit run.

### 2026-10-13 — audit run (sixth)

Sixth audit run. Every ready page's code was run against an independent brute force: about 280
functions and classes across 58 pages, on random and edge-case inputs. Two functions were wrong.
`linked-list-design`'s `copy_random_list` built its copies with the LRU cache's `Node`. That
class has `__slots__` and no `random` field, and its first argument is `key`, so the function
raised `AttributeError` on any non-empty list. It now uses its own `RandomNode`.
`graph-traversal`'s `ladder_length` and its helper `word_ladder_of` added the target word to the
graph even when the word list did not contain it. Word Ladder requires the target to be in the list,
so the function returned 5 instead of 0 on such inputs. Both now draw nodes only from the
word list. The worked example now puts "dog" in its word list, and the page explains why. The
displayed values (7 and 2 words dequeued) did not change. New tests run each page's own code.
Coverage is unchanged at 100% (Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150,
NeetCode 250 250/250). pytest green (837 passed); every ready page returns 200 and the phone check
passed on `/`, `/leetcode` and every ready page. Because this run found a gap, the schedule stays
at every 5 hours. Next: another audit run.

### 2026-10-13 — audit run (seventh)

Seventh audit run. Every ready page's prose was fact-checked against its rendered values and the
literature (quiz answers, captions, complexity claims, citations, home-problem insights). One gap:
false statements on 20 pages. Examples: `binary-search-trees` showed a "passes the parent check"
tree that actually failed the parent check (now 5 → 4, 6 → 3, 7, where 3 fails (5, 6)); `bellman-ford`
said Dijkstra would fail on a graph it gets right; `fast-slow-pointers` said speed 3 could miss
forever; `linear-dp` captioned the wrong column and called Stone Game III O(n²); `grid-dp` suggested
Dijkstra for negative costs; `interval-dp` said the first player always wins the even-pile game (it
never loses); `string-matching` missed the zero-border case of the repetition test;
`variable-size-window` quoted the wrong index in a quiz and stated the "shortest" invariant
off by one; `number-math` gave ⌈log₁₀ x⌉ for the digit count and said CPython uses FFT
multiplication. It also fixed caption colours (`fixed-size-window`, `interval-dp`), counts
(`union-find`, `hash-maps-and-sets`, `complexity-analysis`), the heap-layout note in `tree-bfs`,
the 435 insight (touching intervals), the `dijkstra` edge-direction caption, and citations in
`fixed-size-window`, `linked-list-design`, `k-way-merge`, `tries`, `greedy` and `kadanes-algorithm`.
A new test binds the fixed captions to helper output. No helpers changed. Coverage is unchanged
at 100% (Blind 75 75/75, Grind 169 169/169, NeetCode 150 150/150, NeetCode 250 250/250). pytest
green; every ready page returns 200 and the phone check passed on `/`, `/leetcode` and every ready
page. Per the owner's decision the Routine should now be weekly, but this session had no
`update_trigger` tool either, so the schedule gap stays open. Next: another audit run, which
moves the schedule first.
