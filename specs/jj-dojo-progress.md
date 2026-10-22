# rayaq.ca/jj-dojo — build progress

Running log for the weekly jj-dojo maintenance Routine. Read this first, update it last.
The contract is `specs/jj-dojo.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-22 (ninth run, weekly maintenance). **The build is complete:** all nine §5 pages are
ready and every §10 criterion is met. From here the Routine runs weekly in maintenance mode only.

## Upstream pin

`jj-vcs/jj-dojo@4cff5a1c554863c1be7ae9dea240372028522a8d` (committed 2026-10-20), analyzed
2026-10-22. `package.json` version still 0.0.1. Held in `jj_dojo_docs.UPSTREAM`.

## §10 acceptance criteria

- [x] `/jj-dojo` renders the §6 diagram and links to every page in §5 (boxes for unbuilt pages
      link to pinned source until the page exists).
- [x] Every §5 page exists, meets its "Must cover" column, and is registered: all nine pages
      are ready.
- [x] `graph-layout` meets all eight §8 items with at least two SVG diagrams (two deviations below).
- [x] Planned components are visibly marked as planned everywhere they appear.
- [x] Every source link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass (148 tests in the suite, all sections).
- [x] Homepage card links to `/jj-dojo`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj-dojo` and every ready page (checked in
      headless Chromium this run).
- [x] The Routine has run in maintenance mode (second to fourth runs: no upstream change;
      fifth, eighth and ninth runs: pin bumped; sixth and seventh runs: no upstream change). It now runs weekly.

## Ninth run (2026-10-22): maintenance

| Commit | What |
|---|---|
| `a74e0be` | Pin bump `5fecc7a` → `4cff5a1` across ten pages. `utils` gains the commit-topology helpers and their 19 tests; `graph-protocol` the multi-select message pair; `graph-layout` and `graph-webview` the one-SVG-per-tile rendering (priority-sorted `<g>` line groups, z-index from the top priority) and the hint renderers as functions; `build-and-test` the `license_header.txt` template (`npm run addlicense` now fixes, CI checks), `fakeCommit`, `newRepo({remote})`, the Git ≥ 2.41 `PATH` fix and the sixth `//src/testing` user; `roadmap` and index status rows. Every displayed line range now matches its link |
| `record progress` | `L…` labels on `graph-protocol` and `utils` re-synced to their (already correct) links, plus this log |

Nothing moved from planned to implemented: the new code is helpers and protocol messages that
activation does not reach. `PROTOCOL_TYPES` unchanged (`api/` only gained license lines). Suite
green (1058 tests across all sections); smoke test, pinned-link check (793 links) and 390 px check on all ten pages pass.

## Eighth run (2026-10-15): maintenance

| Commit | What |
|---|---|
| `948323c` | Pin bump `67c5c1f` → `5fecc7a`. Upstream turned `//` comments into `/** */` doc comments across 27 files, so every shifted link on `activation`, `graph-layout`, `graph-protocol`, `graph-webview`, `merge-conflicts` and `utils` was re-anchored (difflib line map, unmapped endpoints checked by hand). `graph-webview` also covers the split chip passing hover to both halves and empty chips rendering nothing |
| `b352ebf` | New upstream code, none of it wired into activation, so it goes on `roadmap` (deviation below): §3 rewritten around the `Client` interface and `SubprocessClient` (`snapshotWithoutIntegrating`, `getCommits`, the template, display IDs, divergence, six integration tests); `//src/api` commit types; new §4 for the bare `OpHeadWatcher`, `NetworkReconnectWatcher` and `Telemetry` interfaces; watcher §5 updated (relative paths, `realpath`, 20 tests). Index repository map and status rows; `build-and-test` gains the `newRepo` helper and the `//src/client` test target |

Moved from planned: JJ PubSub is now *in progress* (the `OpHeadWatcher` interface, no
implementation); the client layer has a real `SubprocessClient`, still unwired. Not in the plan
but now on `roadmap`: `NetworkReconnectWatcher` and `Telemetry` interfaces. Suite green (1034
tests across all sections); smoke test and pinned-link check pass; 390 px check clean on all
ten changed pages.

## Sixth run (2026-10-08): build complete

| Commit | What |
|---|---|
| `a955a9c` | `icon-theme` page: finding the theme, parsing, the `IconTheme` model, icon resolution order, `FileIcon` and the webview URIs, caching, tests |
| `5919dd5` | `utils` page: `HashMap`/`HashSet` and why they exist, `check`, `dispose`, `time` |
| `fa0c1b6` | `build-and-test` page: `MODULE.bazel`, root targets, the `deps` scheme, the in-repo Bazel rules, the pinned `jj`, the Jasmine helpers and fake VS Code API, CI, the enum generator. Also fixed a wrong claim on `utils` (the `ts_library` macro drops `*_test.ts`) and linked `icon-theme`'s tests to the new page |
| `a7e00b3` | `roadmap` page: the three layers with a status SVG, milestones, `src/client/` and `src/file_system_watcher/` (the deliberate addition), design considerations including the read-only jj flags |

Maintenance: upstream `HEAD` still at `67c5c1f`, so the pin stayed (also on the seventh run,
2026-10-08). Mobile check (390 px,
headless Chromium): no page overflow on any of the four new pages.

## Fifth run (2026-10-07)

| Commit | What |
|---|---|
| `d27aaa7` | Pin bump `978c25d` → `67c5c1f`: `activation` gains the `@parcel/watcher` dependency row; index gains repository-map rows for `src/client/` and `src/file_system_watcher/` and mentions them as unwired pieces of the planned layers |
| `311c9a3` | `graph-webview` page: page and app shell, graphs and rows, display ID, chips, top bar, callouts, focus-mode text, search, drag and drop (targets, state, command table, hints), context menus, resize controller, untrusted text, theme colours, helpers and tests; component-tree and drag-and-drop SVGs; required-sections test |

Upstream added `src/client/subprocess_util.ts` and `src/file_system_watcher/`, none wired in.

## Second to fourth runs (2026-10-03 to 10-05)

| Commit | What |
|---|---|
| `1f2a888` | `graph-protocol` page: both RPC interfaces, transport, handshake sequence diagram, entry points, every wire type |
| `6d109d3` | `activation` page: `package.json`, `activate`/`deactivate`, registration order, `Disposable` tree, logging, errors; activation SVG |
| `7c46312` | `merge-conflicts` page: marker grammar, parser vectors, tracker, decorations, CodeLens, resolver; data-flow SVG |

The type tables on `graph-protocol` were generated from `api/types.ts` by a scratch parser that
fails if any field lacks a description. Regenerate them that way when the types change.

## First run (2026-10-03)

| Commit | What |
|---|---|
| `104252a` | Scaffold: `jj_dojo_docs.py` (pin, registry, pinned-link helper, `PROTOCOL_TYPES`), `/jj-dojo` + `/jj-dojo/<slug>`, `jj_dojo/` layout and index, `jj_dojo.css`, §7.5 tests, homepage card, `CLAUDE.md` |
| `b9bda92` | `graph-layout`, part 1: input, pass-order diagram, ordering passes, rows |
| `78829b1` | `graph-layout`, part 2: columns, tiles, insert actions, occupied columns, two-line mode |
| `c3ec20d` | `graph-layout`, part 3: edge shapes, drawing, ranges, focus mode |
| `fdf24f8` | `graph-layout`, part 4: worked example (3 SVGs) and invariants table; page marked ready |
| `8692aac` | §6 architecture diagram, layer tour, repository map, implemented-vs-planned table on the index |

The worked-example SVGs on `graph-layout` were generated by compiling the pinned
`src/ui/commit_graph/algorithms/*.ts` with `tsc` and running `createCommitNodes` on the test
input, so every coordinate and tile is the algorithm's real output. Redo this if the pin
moves and `preprocess.ts` changes.

## Queue

1. ~~Scaffold~~
2. ~~`graph-layout` (flagship, §8)~~
3. ~~§6 architecture diagram on the index~~
4. ~~`graph-protocol`~~
5. ~~`activation`~~
6. ~~`merge-conflicts`~~
7. ~~`graph-webview`~~
8. ~~`icon-theme`~~
9. ~~`build-and-test`~~
10. ~~`utils`~~
11. ~~`roadmap`, which also covers `src/client/` and `src/file_system_watcher/` (deliberate addition,
    see below)~~

The build queue is empty. Weekly maintenance: diff upstream against the pin, update affected
pages, refresh `PROTOCOL_TYPES`, and move items from planned to implemented on `roadmap`, the
index's implemented-vs-planned table and the §6 diagram as they land. When a new module is wired
into activation, propose a page for it here first.

## Deliberate deviations

- **No elided range in the worked example.** §8 items 3 and 7 ask how elided ranges are
  represented and want one in the example. The layout has no such concept at this pin:
  every input commit is drawn, and every `childrenHashes` entry must be present. The page
  says so in its "Lanes and edges" section and uses a four-parent merge as the example.
- **"How ranges are merged" (§8 item 5).** `RangeManager` never merges ranges. It only
  appends and checks for collisions. The page describes that instead.
- **New modules go on `roadmap`, not new pages.** `src/client/` (now `SubprocessClient`, since
  `5fecc7a`), `src/api/`, `src/file_system_watcher/` and the `op_head_watcher`,
  `network_reconnect_watcher` and `telemetry` interfaces are code of the planned layers that
  activation does not reach. Proposal, recorded as a deliberate addition: `roadmap` must also cover what each
  module does today, that neither is wired into activation, and its tests; sources
  `src/client/*`, `src/file_system_watcher/*`. They get their own pages only once they are wired in.
- **`graph-webview` defers tiles, glyphs and lines to `graph-layout`.** Those components are
  already documented under `graph-layout#components` and `#line-geometry`; the webview page links
  there instead of repeating them.
- **Diagram colours.** As on `/jj`, the site is dark-only, so diagrams use the `--jj-*`
  variables from `jj.css`.

## Open gaps / questions for the owner

- **Version log line (`activation`).** `activate` logs `packageJSON.build`, but `package.json` has
  no `build` field and the `vsix` target packages it unchanged. So outside the test, which injects
  one, the line reads `Extension version: undefined`. The page states this as following from the
  code. It wasn't observed in a running VS Code.
- **Error helpers barely used (`activation`).** Until `67c5c1f` the error helpers had no callers
  outside `src/logging/`. Now `LocalFileSystemWatcher` calls them, but that class is itself not
  wired in, so nothing running reports errors yet. Also, `logAndShowInternalError` marks an
  error as shown even when no feedback provider is registered. Revisit when features start
  reporting errors.
- **RPC edge cases (`graph-protocol`).** Two behaviours in the vendored RPC layer are stated on
  the page as the code shows them: a handshake timeout is an unhandled rejection that leaves
  every later call blocked, and a failed call rejects with a plain `{message, name, stack}`
  object even though an `Error` is built just before. Worth confirming against upstream intent.

- **Focus mode is broader than documented.** `getFocusedCommits`'s comment says it keeps
  the working copy, its ancestors and descendants, and the `disableFocusMode` option's comment
  says ancestors only. The code also keeps siblings and cousins reached through mutable
  ancestors, and the upstream test asserts this (`h` is kept). The page describes the code's
  behaviour and points out both comments.
- **Marker styles the parser misses (`merge-conflicts`).** Following from the code, not observed
  in VS Code: jj's `snapshot` style (`-------` bases fold into the previous side), `git` style,
  markers longer than seven characters, and fallback `side #N` labels are not recognized. The
  page lists them. Upstream's own TODO (`parser.ts:67-68`) acknowledges other styles.
- **Lifecycle leaks (`merge-conflicts`).** The five decoration types and the CodeLens
  registration are never disposed, and tracker entries are never removed. `ConflictSide.changeId`
  is read by nothing.
- **"Minimap" is the overview ruler.** Upstream's decorator test says minimap; the code sets
  only `overviewRulerColor`/`overviewRulerLane`. The page uses the accurate term and notes it.
- **The graph has no real data yet.** `createFakeWebviewState` sends one hard-coded commit.
  `SubprocessClient` landed in `5fecc7a` but nothing calls it. Revisit once it is wired in.
- **Two commit types.** `src/api` defines its own `Commit`, separate from the webview's
  `api/types.ts` one; nothing converts between them yet. On `roadmap#gaps`.
- **1 MiB output buffer.** The subprocess helper keeps `execFile`'s default `maxBuffer`; upstream
  now acknowledges it in a comment. Large logs would fail. On `roadmap#gaps`.
- **Context-menu items are defined nowhere in the repo (`graph-webview`).** Rows, chips and top-bar
  split buttons send contexts with origins such as `commitRow` and `commitRowMultiSelected`, but
  `package.json` has no `webview/context` menu contribution at this pin and nothing else reads those
  origins. The page explains the mechanism and does not claim which items appear.
- **Top-bar context JSON (`graph-webview`).** The split-button context is built by string
  interpolation, not `JSON.stringify`, so an origin or command ID containing a quote would produce
  invalid JSON. Both come from the extension. The page states this.
- **Unbound context-menu callback (`graph-webview`).** `jj-commit-row` passes its private
  `openContextMenu` to the right side unbound. It works because the right side has the same
  `extensionApi`, `state` and `node` properties. Not on the page; worth an upstream fix.
- **No CSP in the webview HTML.** `getHtmlForWebview` sets no Content-Security-Policy meta tag. The
  page states the fact without judging it.
- **`@parcel/watcher` loose ends.** The `vsix` target has a TODO about packaging the native module,
  and `LocalFileSystemWatcher` subscribes without an ignore list. Both are on `roadmap#gaps`.
  The earlier symlink gap is resolved: since `5fecc7a` the watcher `realpath`s its root.
- **Multi-select is not wired (`graph-protocol`).** `MultiSelectManager` landed with tests, but
  nothing else constructs it, so the host still ignores `$onClick`. Revisit when it is wired in.
- **Unused topology helpers (`utils`).** Four commit-topology functions have no callers outside
  their tests; only `SubprocessClient.getCommits` uses the rest. The page states this.
- **`//:test` does not exist (`build-and-test`).** The spec's "Must cover" names a `//:test`
  target. There is none at this pin: `npm test` runs `bazel test //...` over ten `:tests` targets.
  The page describes what exists.
