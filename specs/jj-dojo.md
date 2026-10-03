# rayaq.ca/jj-dojo — Jujutsu Dojo architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-03)

This is the product and technical contract for `rayaq.ca/jj-dojo`. The daily implementation
Routine builds and maintains the section against it. Build progress lives in
`specs/jj-dojo-progress.md`. Don't edit this spec without the owner's say-so. If the code
and the spec disagree, fix the code or record a deliberate deviation in the progress file.

---

## 1. Goal

`rayaq.ca/jj-dojo` is a very detailed, always-current reference to the internal architecture
of [Jujutsu Dojo](https://github.com/jj-vcs/jj-dojo), the VS Code extension for jj that
Google is open-sourcing. Someone who has read it should be able to:

- draw the extension's layers (extension host, webviews, UI features, and the planned API and
  client layers) and say which module, class and file owns each responsibility;
- name every message and type in the contract between the extension host and the commit graph
  webview (`src/ui/commit_graph/api/*`), field by field;
- explain how the commit graph is laid out and drawn (`preprocess.ts`, `drawer.ts`,
  `range_manager.ts`, `focus_mode.ts`) down to the algorithm level;
- trace each user-facing feature (the commit graph view, merge-conflict CodeLens and
  decorations, the "Accept all sides"/"Accept one side" commands, the icon theme service) end
  to end, from `package.json` contribution or VS Code event to the code that handles it;
- tell what exists in the repository today from what `docs/intro.md` says is planned.

It's a reference, not a tutorial or a user guide. Every page opens with a short
plain-language summary.

## 2. Non-goals

- User documentation for the extension or for jj. Link to the upstream README and to
  `docs.jj-vcs.dev`.
- Opinion, comparison with other VS Code SCM extensions, or roadmap speculation beyond what
  upstream `docs/intro.md` states.
- Re-explaining jj internals. Where the extension depends on a jj concept (conflicts, change
  IDs, the op log, templates), link to the matching `/jj/<slug>` page.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime call
   to GitHub or any other service, no client-side fetching, no JavaScript framework. A page
   that is fine today must be fine with the network off.
2. **$0 incremental cost.** No new paid service, no new hosting, no new runtime dependency
   in `backend/requirements.txt`.
3. **Every claim is sourced.** Each type, message, algorithm and flow links to the exact
   upstream file, pinned to the analyzed commit
   (`https://github.com/jj-vcs/jj-dojo/blob/<sha>/<path>#L<start>-L<end>`). If something can't
   be traced to source at the pinned commit, it doesn't go on the page.
4. **Pinned to one upstream commit.** The whole section describes exactly one jj-dojo
   commit, recorded in code (§7.3) and shown on every page.
5. **Never fabricate.** Type names, field names, command IDs, setting keys, defaults and
   function names are copied from source, not paraphrased from memory. When unsure, omit
   and log the gap in the progress file.
6. **Planned vs. real.** The project is mid-externalization. Anything described only in
   `docs/intro.md` (ApiStateManager, WorkspaceStateManager, PendingSnapshotsManager,
   ActionsQueue, the subprocess client, forge managers, …) is shown visibly as *planned*
   (a "Planned" badge and dashed outlines in diagrams), sourced to `docs/intro.md`, and never
   described as if it were implemented. When it lands upstream it moves to *implemented*.
7. **Licensing.** jj-dojo is Apache-2.0 (Google LLC). Every page footer credits the upstream
   authors and links the license. Code excerpts stay short; whole files are never copied in.
8. **Section isolation.** Four Routines push to this repo. This section owns only its own
   files (§7). It never edits `jj_docs.py`, `templates/jj/`, `jj.css`, or another section's
   files. Shared files (`app.py`, `home.html`, `app_tests.py`, `CLAUDE.md`) get additive
   edits only.
9. **House rules.** Everything in `CLAUDE.md` applies: route-only `app.py`, tests for every
   route and every piece of logic, `*_tests.py`, no comments except non-obvious whys.

## 4. Information architecture

```
/jj-dojo              Overview: summary, the architecture diagram, page index
/jj-dojo/<slug>       One deep-dive page per topic (§5)
```

- Every page shares one layout: a section nav listing every page, a breadcrumb, an on-page
  table of contents built from its `h2`/`h3`, and a footer showing the pinned upstream
  commit, its date, the extension version from `package.json`, and the date of the last
  analysis.
- Pages are reachable from the homepage through a "jj-dojo internals" feature card, and
  the `/jj-dojo` index links to `/jj` as the reference for jj itself.
- Unknown slugs return 404. There is no catch-all. Headings have stable `id` anchors.

## 5. Page inventory

Each page lists the upstream files it is responsible for (its "source set"). The Routine
uses source sets to work out which pages an upstream change affects. Paths are relative to
the jj-dojo repo root.

| Slug | Title | Must cover | Source set |
|---|---|---|---|
| *(index)* | jj-dojo architecture | §6 diagram; one-paragraph tour of each layer; repository map (`src/` subtrees, `tools/bazel`, `third_party`, `scripts`, `spec`); implemented-vs-planned summary; links to every page | `README.md`, `docs/intro.md`, `package.json`, `src/extension.ts` |
| `activation` | Activation and wiring | `package.json` contributions field by field (activation events, `extensionKind`, views, commands, colors, configuration); `activate`/`deactivate` in `extension.ts`; what `ui.ts` registers and in which order; disposables and lifecycle; logging setup (`src/logging/*`) and error reporting (`src/error/*`) | `package.json`, `src/extension.ts`, `src/ui/ui.ts`, `src/logging/*`, `src/error/*` |
| `graph-protocol` | The graph webview protocol | Every type in `api/types.ts` field by field; the `extension_shape` and `webview_shape` interfaces method by method; message direction, handshake (and its timeout), request/response pairing; how `commit_graph_provider` and `extension_shape_impl` implement the host side; `webview_module.ts` on the webview side | `src/ui/commit_graph/api/*`, `src/ui/commit_graph_provider/*`, `src/ui/commit_graph/webview_module.ts` |
| `graph-layout` | Commit graph layout | The flagship (§8) | `src/ui/commit_graph/algorithms/*` |
| `graph-webview` | The graph webview UI | The component tree from `app.ts` down: rows, chips, glyphs, lines, tiles, top bar, search box (`search_box_state`, `search_highlighter`), focus-mode text, garbage section, hint bubbles, rebase/insert hints, drag and drop (publisher, state, subscriber), context menus, resize controller; `safe_html` and how untrusted text is rendered; styles and theme colours | `src/ui/commit_graph/components/*`, `src/ui/commit_graph/utils/*` |
| `merge-conflicts` | Merge conflict support | Conflict-marker parsing (`parser.ts`): the marker grammar it accepts, with the test vectors from `parser_test.ts` as a table; the tracker; decorations (including the third-side colour `jj.mergeConflict.thirdSideBackground` and the minimap); CodeLens; the resolver and the two commands; how this maps to jj's materialized conflicts (link `/jj/conflicts`) | `src/ui/merge_conflict/*` |
| `icon-theme` | Icon theme service | How the active file-icon theme is located, parsed (`icon_theme_json_parser.ts`, `jsonc-parser`) and served to webviews; the `IconTheme` model; caching and invalidation | `src/ui/icon_theme_service/*` |
| `build-and-test` | Build, test and packaging | Bazel layout (`MODULE.bazel`, `BUILD.bazel` targets `//:extension`, `//:vsix`, `//:test`), the `deps` restriction scheme from `docs/intro.md`, the in-repo Bazel rules under `tools/bazel/*`, addlicense, the Jasmine setup and the fake VS Code API under `src/testing/*`, CI workflows | `BUILD.bazel`, `MODULE.bazel`, `tools/bazel/*`, `spec/support/jasmine.json`, `src/testing/*`, `.github/workflows/*`, `src/**/BUILD.bazel` |
| `roadmap` | Externalization plan | The planned UI/API/client layers from `docs/intro.md`, each with its status at the pinned commit (done, in progress, planned) and, where it has landed, a link to the page that now covers it; the milestones verbatim in substance; the design considerations (Bazel deps, few dependencies, "reads should stay reads" with the jj flags it names) | `docs/intro.md`, `docs/resources/architecture.svg` |
| `utils` | Shared utilities | `HashMap`/`HashSet` (and why they exist), `check`, `dispose`, `time` | `src/utils/*` |

**New code upstream.** When the pin moves and a new top-level module appears under `src/`
(for example the subprocess client, the split editor, a file-system provider, or any of the
planned API-layer managers), the Routine adds a row to the progress file's queue with a
proposed slug, title, "must cover" and source set, and builds it like any other page. The
proposal is recorded as a deliberate addition until the owner folds it into this table.

## 6. The architecture diagram

The `/jj-dojo` index page centres on one large diagram. Requirements:

- **Hand-authored inline SVG** in the template. No JS rendering library, no external image.
- Shows, top to bottom: VS Code (activation events, the SCM view container, commands,
  editors) → extension host (`extension.ts` → `ui.ts` → feature modules) → the commit graph
  webview across its message boundary (`extension_shape` ⇄ `webview_shape`) → the planned
  API layer and client layer (dashed, labelled "planned") → the `jj` CLI / repository.
- Every box links to the page that explains it; planned boxes link to `roadmap`.
- Readable at desktop width and scrollable sideways inside its own container on mobile; the
  page itself never scrolls horizontally.
- Has `role="img"`, a `<title>`, and a `<desc>` that summarises it in text.
- Uses the site's colour variables so it works in light and dark mode.
- Deep-dive pages may include smaller focused SVG diagrams under the same rules.
  `graph-layout` needs at least two, `graph-protocol` needs a sequence diagram.

## 7. Technical design

### 7.1 Routing

- `app.py` gets `/jj-dojo` and `/jj-dojo/<slug>` and stays route-only: it asks
  `jj_dojo_docs` for the page and renders it, and returns 404 for unknown slugs.
- `backend/jj_dojo_docs.py` owns the page registry and upstream pin (§7.3), and builds the
  nav, breadcrumb and footer context. It must be unit-testable without Flask.

### 7.2 Templates and assets

- `frontend/templates/jj_dojo/base.html` holds the shared layout (§4); each page is a
  fragment `frontend/templates/jj_dojo/<slug>.html`; the index is `jj_dojo/index.html`.
- `frontend/static/jj_dojo.css` holds this section's styles, built on `style.css`
  variables. It may visually match `jj.css` and the page may link `jj.css` as well, but it
  never edits it. Static URLs go through `url_for` for `static_assets` versioning.
- Code blocks are plain `<pre><code>`. No highlighting library.
- Tables are the primary format for types and fields: **Field · Type · Meaning · Source**.

### 7.3 Upstream pin

```python
UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-dojo",
    "commit": "<40-char sha>",
    "commit_date": "YYYY-MM-DD",
    "version": "<version from package.json>",
    "analyzed_on": "YYYY-MM-DD",
}
```

plus a `source_url(path, start=None, end=None)` helper that every source link goes through.
Bumping the pin is the only way a page's described version changes. Never link `blob/main`.

### 7.4 Page registry

An ordered `PAGES` list, each entry with `slug`, `title`, `summary` (one sentence, used on
the index and in `<meta name="description">`), `sources` (its §5 source set) and `ready`.
The nav, the index list and the slug allowlist all derive from it. A page is routable only
once its template exists and meets its §5 bar; until then the index lists it as "In
progress", without a link.

### 7.5 Tests (`backend/tests/jj_dojo_docs_tests.py`, plus `app_tests.py` additions)

- `/jj-dojo` and every ready slug return 200; an unknown or not-ready slug returns 404.
- Every ready page has a template, a non-empty summary and at least one source.
- Every jj-dojo source link on every page points at `github.com/jj-vcs/jj-dojo/blob/<pinned sha>/`.
- The pin is well-formed: 40 hex chars, ISO dates, semver version.
- The index includes the architecture SVG with `<title>` and `<desc>` and links to every
  ready page.
- `graph-protocol` names every exported type in a committed list (`PROTOCOL_TYPES` in
  `jj_dojo_docs.py`) that the Routine refreshes from `api/types.ts` when it bumps the pin.
- The homepage links to `/jj-dojo`.

## 8. `graph-layout` deep dive — requirements

The flagship page. It must explain, with source links:

1. **Input.** The commit data the layout consumes (from `api/types.ts`) and where it comes
   from.
2. **Preprocessing pipeline** in `preprocess.ts`, function by function, in call order: what
   each pass computes, its data structures, and its complexity.
3. **Lanes and edges.** How columns are assigned, how edges between non-adjacent rows are
   routed, how merges and elided ranges are represented.
4. **Drawing.** How `drawer.ts` turns the layout into glyphs and line segments, and how the
   components (`lines.ts`, `glyph_tile.ts`, `merge_tile.ts`, `tile_group.ts`) render them.
5. **Ranges.** `range_manager.ts`: what a range is, how ranges are merged and queried.
6. **Focus mode.** `focus_mode.ts`: what is hidden and why, with its test cases.
7. **Worked example.** A small DAG with a merge and an elided range, drawn as SVG at each
   stage (input → lanes → rendered rows), using cases taken from `preprocess_test.ts`.
8. **Invariants and edge cases** the tests pin down, as a table quoting the test names.

## 9. Keeping it current (the daily Routine)

A Routine ("rayaq.ca/jj-dojo — architecture reference agent") runs once a day. Each run:

1. Clones `jj-vcs/jj-dojo` at `HEAD` into scratch space (never into this repo).
2. Compares upstream `HEAD` with `UPSTREAM.commit` and, using the §5 source sets
   (`git diff --stat <pinned>..HEAD -- <paths>`), lists the pages whose sources changed and
   any new top-level module under `src/`.
3. **Build phase** (until every §5 page and every §6/§7/§8 item is done): builds the next
   item from the queue in `specs/jj-dojo-progress.md`. Build order: the scaffold (module,
   routes, layout, tests, homepage card, `CLAUDE.md` notes), `graph-layout`, the §6
   diagram, `graph-protocol`, `activation`, `merge-conflicts`, `graph-webview`,
   `icon-theme`, `build-and-test`, `utils`, `roadmap`, then any queued additions. Pages are
   built against the pinned commit; the pin isn't bumped while a page is half-built.
4. **Maintenance phase** (always once the build is done; before building while it is still
   going): updates every affected page to match the new `HEAD`, refreshes
   `PROTOCOL_TYPES`, moves anything newly implemented from "planned" to "implemented", then
   bumps `UPSTREAM` in the same commit as the content changes. If nothing in any source set
   changed, it bumps the pin and dates only.
5. Runs the full test suite and starts the app to check `/jj-dojo` and every page return
   200, then pushes small commits straight to `main` (merge, never rebase, never force).
6. Rewrites `specs/jj-dojo-progress.md`: status, pin, what changed, open gaps, next queue.

## 10. Acceptance criteria

- [ ] `/jj-dojo` renders the §6 diagram and links to every page in §5.
- [ ] Every §5 page exists, meets its "Must cover" column, and is registered.
- [ ] `graph-layout` meets all eight §8 items with at least two SVG diagrams.
- [ ] Planned components are visibly marked as planned everywhere they appear.
- [ ] Every source link is pinned to `UPSTREAM.commit`.
- [ ] §7.5 tests exist and pass.
- [ ] Homepage card links to `/jj-dojo`.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their container.
- [ ] The daily Routine has run at least once in maintenance mode and either bumped the pin
      or recorded "no relevant upstream change".
