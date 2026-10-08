# rayaq.ca/leetcode — build progress

This is the running log for the leetcode Routine. Read it first and update it last. The
contract is `specs/leetcode.md` (spec v1, read-only without the owner's say-so). This file
records where the build actually stands.

**Last updated:** 2026-10-08 (scaffolding). The section, registry (58 pages in 20 areas),
index page, tests and Routine exist. No content pages are ready and `PROBLEMS` is empty.
**The 2026-10-08 research run was blocked by network access (see Known gaps); the next run retries the research run** (spec §8 step 3): populate `PROBLEMS` for all four lists.

## The Routine

"rayaq.ca/leetcode — pattern reference agent" runs every 5 hours in a fresh session (spec §8),
weekly once the build is complete, and pushes straight to `main`. The phone check before each push is
`NODE_PATH=$(npm root -g) node tools/leetcode/check_mobile.js / /leetcode <ready pages>`.

## Research

- [ ] Blind 75 in `PROBLEMS` (75 problems), sources recorded below
- [ ] Grind 169 in `PROBLEMS` (169 problems), sources recorded below
- [ ] NeetCode 150 in `PROBLEMS` (150 problems), sources recorded below
- [ ] NeetCode 250 in `PROBLEMS` (250 problems), sources recorded below
- [ ] Every problem has a `home` page and a one-line original `insight`

### Sources

| List | Source URL | Accessed | Size |
|---|---|---|---|

## Coverage

| List | Problems with a ready home | Size |
|---|---|---|
| Blind 75 | 0 | 75 |
| Grind 169 | 0 | 169 |
| NeetCode 150 | 0 | 150 |
| NeetCode 250 | 0 | 250 |

## Queue

Prerequisites come first (tested). `✓` marks ready pages; `← next` marks the next page to
build once research is done.

1. `complexity-analysis` ← next
2. `python-toolkit`
3. `recursion`
4. `hash-maps-and-sets`
5. `counting-and-bucketing`
6. `prefix-sums`
7. `in-place-array-tricks`
8. `two-pointers`
9. `fixed-size-window`
10. `variable-size-window`
11. `stack`
12. `monotonic-stack`
13. `binary-search`
14. `binary-search-on-answer`
15. `linked-list-basics`
16. `fast-slow-pointers`
17. `linked-list-design`
18. `tree-dfs`
19. `tree-bfs`
20. `binary-search-trees`
21. `tree-construction`
22. `tries`
23. `heaps`
24. `top-k-elements`
25. `k-way-merge`
26. `two-heaps`
27. `quickselect`
28. `subsets-and-permutations`
29. `constraint-backtracking`
30. `graph-traversal`
31. `grid-graphs`
32. `topological-sort`
33. `union-find`
34. `dijkstra`
35. `bellman-ford`
36. `minimum-spanning-trees`
37. `eulerian-paths`
38. `dp-fundamentals`
39. `linear-dp`
40. `knapsack-dp`
41. `palindrome-dp`
42. `longest-increasing-subsequence`
43. `grid-dp`
44. `string-dp`
45. `interval-dp`
46. `state-machine-dp`
47. `greedy`
48. `kadanes-algorithm`
49. `interval-merging`
50. `sweep-line`
51. `matrix-manipulation`
52. `number-math`
53. `bit-manipulation`
54. `interview-approach`
55. `segment-trees`
56. `fenwick-trees`
57. `string-matching`
58. `bitmask-dp`

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

## Known gaps and questions for the owner

- **Research run blocked (2026-10-08).** The egress proxy returns 403/blocked for
  techinterviewhandbook.org, neetcode.io and leetcode.com, and the Tech Interview Handbook
  repo's Grind data file could not be located on raw.githubusercontent.com. Only
  `neetcode-gh/leetcode/.problemSiteData.json` is reachable; it flags 150 NeetCode 150 and 75
  Blind 75 problems (450 entries total, with difficulty and pattern) but is a single source and
  has no Grind 169 or NeetCode 250 data. `PROBLEMS` was left empty rather than filled from memory. Owner: allow
  those hosts in the environment's network policy, or point the Routine at a reachable second
  source for each list (and for Grind 169).

## Run log

### 2026-10-08 — scaffolding

Set up `/leetcode`: `leetcode_docs.py` registry, index template, styles, route, tests, spec,
this file, the phone check, and the Routine.

### 2026-10-08 — research run (blocked)

Found only one reachable source (NeetCode's `.problemSiteData.json`: Blind 75 = 75, NeetCode 150 = 150).
No second source for any list and no Grind 169 source. Changed nothing in `PROBLEMS`.
