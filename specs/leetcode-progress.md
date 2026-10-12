# rayaq.ca/leetcode — build progress

This is the running log for the leetcode Routine. Read it first and update it last. The
contract is `specs/leetcode.md` (spec v1, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-12 (third audit run). All 58 pages are ready and the queue is empty. This audit found and fixed one gap (brute-force baselines in Complexity and tradeoffs), so the Routine stays on its 5-hour schedule. **The next run is another audit run** (spec §8.1): it fixes one gap, and if none remain it records "complete" and moves this Routine to weekly audits.

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

## Known gaps and questions for the owner

- None open.

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
