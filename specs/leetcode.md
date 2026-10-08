# rayaq.ca/leetcode — product and technical spec

**Spec v1, 2026-10-08.** This is the contract the `/leetcode` section and its Routine are held
to. Don't edit it without the owner's say-so; record proposed changes under "Decisions" or
"Questions for the owner" in `specs/leetcode-progress.md` instead. Where the build stands lives
in that progress file.

## 1. Goal and audience

The owner's goal: a site that summarizes all the core lessons from studying LeetCode, covering
every algorithmic concept needed to solve the problems an interview asks, the way
[neetcode.io/roadmap](https://neetcode.io/roadmap) organizes them.

- **Audience:** from someone who has never heard of a sliding window to someone refreshing
  before an onsite. Every page starts in plain language and goes all the way to the template
  and its proof.
- **Coverage target:** every problem on **Blind 75**, **Grind 169** (the full Grind list behind
  Grind 75), **NeetCode 150** and **NeetCode 250** has exactly one *home* page, the page whose pattern is its key
  idea, and that page is ready.
- **What a page teaches:** a pattern, not a problem. Problems are evidence and practice.

## 2. Non-goals

- Not a problem archive. No problem statements, no per-problem solution pages.
- Not a judge or a code runner. Nothing executes in the browser or on the server.
- Not a copy of NeetCode or LeetCode editorials. See §3.2.
- No user accounts, progress tracking or comments.

## 3. Hard constraints

### 3.1 Technical

- Pages are static and server-rendered by Flask/Jinja, like the rest of the site. No runtime
  network calls, no JS libraries or CDNs. An optional small vanilla
  `frontend/static/leetcode.js` may add step-through animation as progressive enhancement;
  every page must read in full without it.
- Diagrams are hand-authored inline SVG, using the site's colour variables so they work in
  light and dark mode, each scrolling inside its own container on a phone.
- Add no packages to `backend/requirements.txt` or `backend/requirements-dev.txt`. Worked
  examples are computed by pure-Python (stdlib) helpers in `backend/leetcode_docs.py`.
- No horizontal page scroll at a 390px viewport (`tools/leetcode/check_mobile.js`).
- Never edit `jj.css` or another section's files. The shared registration points (`app.py`,
  `app_tests.py`, `home.html`, `AGENTS.md`, `README.md`) are touched only to add this section.

### 3.2 Copyright and sourcing

- Never copy LeetCode problem statements, examples, constraints or editorial text. Link to
  `https://leetcode.com/problems/<slug>/` and describe the problem in one line of our own words.
- Never copy NeetCode's explanations, code or video transcripts. Its roadmap and lists are used
  only as a topic and coverage index, and are credited in References.
- All prose and code are original. Implementing standard textbook algorithms is fine.
- Problem numbers, titles and difficulties are facts and may be listed.

## 4. Information architecture

### 4.1 Areas

One area per NeetCode roadmap topic, in roadmap order, with *Foundations* first and *Beyond the
interview* last. The canonical list is `leetcode_docs.AREAS`:

foundations · arrays-hashing · two-pointers · sliding-window · stack · binary-search ·
linked-list · trees · tries · heap · backtracking · graphs · advanced-graphs · dp-1d · dp-2d ·
greedy · intervals · math-geometry · bit-manipulation · beyond

### 4.2 Levels

`intro` (first contact with the idea), `core` (the bulk of Medium problems), `advanced` (Hard
problems, or patterns most candidates never need). Pages in *beyond* are always `advanced` and
say on the page that they rarely come up in interviews.

### 4.3 The learning path

`leetcode_docs.LEARNING_PATH`: seven steps (foundations → arrays and pointers → linear
structures → trees and heaps → search → dynamic programming → interview ready). Each step only
names pages whose prerequisites come in the same or an earlier step.

## 5. Page inventory

The canonical inventory is `leetcode_docs.PAGES` (58 pages): slug, title, area, level, summary
and prerequisites. The Routine may add, split or merge pages when research shows a list problem
has no natural home. It records each change, with its reason, in the progress file's Decisions
section, and keeps the queue and the tests consistent.

### 5.1 Problems

`leetcode_docs.PROBLEMS` is one entry per problem on any of the four lists:

| Field | Meaning |
|---|---|
| `number` | LeetCode problem number (unique) |
| `title` | LeetCode title |
| `slug` | the `leetcode.com/problems/<slug>/` slug |
| `difficulty` | `Easy`, `Medium` or `Hard` |
| `lists` | the subset of `blind-75`, `grind-169`, `neetcode-150`, `neetcode-250` it is on |
| `home` | the one page slug where it is taught |
| `patterns` | other page slugs it also uses (may be empty) |
| `insight` | one original sentence: the key insight, without giving away code |

The first Routine run is the research run (§8): it populates `PROBLEMS` for every list at
once, from at least two independent public sources per list, recording each source URL, its
access date and the list's size in the progress file. The test suite then requires each list to
have exactly its stated size.

### 5.2 Build order

The queue in `specs/leetcode-progress.md` lists every page once, in an order where each page's
prerequisites come first. The test suite enforces both.

## 6. The page format

Every page is a fragment `frontend/templates/leetcode/<slug>.html`: a `<header>` with an `<h1>`
and a one-paragraph plain-language summary, then these `h2` sections, in this order, with
exactly these ids:

1. `problem` — **Problem.** What kinds of questions signal this pattern, ending in a
   **Pattern signals** table with the header `Signal | Pattern | Why`.
2. `intuition` — **Intuition.** The core insight in plain language, no code.
3. `mechanics` — **Mechanics.** The invariant, the template in words, and why it is correct.
4. `worked-example` — **Worked example.** A small input traced step by step in a table. The
   table's values come from a tested helper in `leetcode_docs.py`, never typed by hand.
5. `implementation` — **Implementation.** An idiomatic Python template in `<pre><code>`, then
   2–4 variations and the edge cases that break naive versions.
6. `tradeoffs` — **Complexity and tradeoffs.** Time and space with reasons, the brute-force
   baseline, and when the pattern fails or a different one wins.
7. `problems` — **Problems.** The problems whose `home` is this page, grouped Easy / Medium /
   Hard, each with number, title, link, list badges and its `insight`. Then a short "also uses
   this pattern" list of problems whose `patterns` include this page.
8. `connections` — **Connections.** Includes `leetcode/_connections.html`, plus prose on related
   patterns.
9. `check-yourself` — **Check yourself.** 3–4 `<details class="lc-quiz">` questions.
10. `references` — **References.** Textbooks (CLRS, Skiena, Sedgewick & Wayne), original papers
    where an algorithm has one, and the NeetCode roadmap and list pages credited as the index.

Every page also has at least two inline SVGs, each with `role="img"`, a `<title>` and a
`<desc>`, showing the pattern's state over time: pointer positions, window bounds, stack
contents, recursion trees, DP tables or graph frontiers.

## 7. Technical design

### 7.1 Routing

`/leetcode` renders the index; `/leetcode/<slug>` renders a page only when its registry entry
has `"ready": True`, and 404s otherwise. Both go through `rendered_pages.get`.

### 7.2 Files this section owns

`backend/leetcode_docs.py`, `backend/tests/leetcode_docs_tests.py`, `frontend/templates/leetcode/`,
`frontend/static/leetcode.css`, an optional `frontend/static/leetcode.js`,
`tools/leetcode/`, `specs/leetcode.md` (read-only, see top) and `specs/leetcode-progress.md`.

### 7.3 Tests (`backend/tests/leetcode_docs_tests.py`, plus `app_tests.py`)

- The registry is consistent: unique slugs, known areas and levels, prerequisites that exist.
- The learning path names known pages in prerequisite order.
- The queue in the progress file lists every page exactly once, prerequisites first, with `✓`
  exactly on ready pages and `← next` on the first page that isn't.
- `PROBLEMS` entries are well formed; numbers are unique; homes and patterns are known pages;
  each list has either no entries (before research) or exactly its size.
- Every ready page has the §6 sections in order, the Pattern signals table, at least two
  accessible SVGs, renders with 200, and links internally only to ready pages.
- Every worked-example helper returns the values its page shows.
- Unknown and not-ready slugs 404; the homepage links to `/leetcode`.

## 8. The Routine

"rayaq.ca/leetcode — pattern reference agent" runs every 5 hours in a fresh session until the build is
complete, then weekly, and pushes straight to `main`. Each run:

1. Gets a clean, current checkout of `main` and confirms the suite is green.
2. Reads `AGENTS.md`, this spec and the progress file.
3. **Research run** (while any list has no problems in `PROBLEMS`): researches every list
   still missing and the NeetCode
   roadmap, populates `PROBLEMS` with a home for every problem, adjusts `PAGES` if a problem has
   no natural home (§5), and records sources in the progress file. No content pages that run.
4. **Build run**: builds the queue item marked `← next` completely to §6, flips it ready, and
   may build the next one too if time allows, to the same bar.
5. **Audit run** (queue empty): fixes one gap per run: a list problem without a ready home, a
   broken cross-link, or a page short of §6. With no gaps left, it records "complete", changes no
   content, and moves its own schedule to weekly audits (`update_trigger` on its trigger; if it
   cannot, it notes that for the owner in the progress file).
6. Updates the progress file: last-updated line, queue, coverage per list, decisions, gaps and
   a run log entry.
7. Before pushing: pytest green, the app serves every ready page with 200, and
   `NODE_PATH=$(npm root -g) node tools/leetcode/check_mobile.js / /leetcode <ready pages>`
   exits 0.

## 9. Acceptance criteria

- [ ] `PROBLEMS` holds all of Blind 75, Grind 169, NeetCode 150 and NeetCode 250, each with a home page.
- [ ] Every page in the queue is ready and meets §6.
- [ ] Every list problem's home page is ready (coverage 100% on all four lists).
- [ ] §7.3 tests exist and pass.
- [ ] No horizontal scroll at 390px on `/`, `/leetcode` and every ready page.
- [ ] The Routine has run at least once in audit mode and recorded "complete", and now runs weekly.
