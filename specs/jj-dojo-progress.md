# rayaq.ca/jj-dojo — build progress

Running log for the weekly jj-dojo maintenance Routine. Read this first, update it last.
The contract is `specs/jj-dojo.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-11-26 (thirteenth run, weekly maintenance). **The build is complete:** all nine §5 pages are
ready and every §10 criterion is met. From here the Routine runs weekly in maintenance mode only.

## Upstream pin

`jj-vcs/jj-dojo@8fb0fd5eaa495f16e1624b73eb5cfaeb7b48d522` (committed 2026-11-23, 5 commits after `e4a1514`), analyzed
2026-11-26. `package.json` version still 0.0.1. Held in `jj_dojo_docs.UPSTREAM`.

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
      fifth and eighth to thirteenth runs: pin bumped; sixth and seventh runs: no upstream change). It now runs weekly.

## Thirteenth run (2026-11-26): maintenance

| Commit | What |
|---|---|
| `e18853e` | Pin bump `e4a1514` → `8fb0fd5`. `build-and-test`: jj now comes from `versions.bzl` plus a `jj` module extension (six platforms, Windows arm64 included), `copy_jj_<slug>` per version; `jasmine_test` gains `use_jj`/`jj_versions`/`tags`/`size` and builds one test per jj version; `install_global_jj` uses `hermetic_jj.ts`; `newRepo` checks `JJ_VERSION`; CI cache keys include `tools/bazel/jj/*.bzl`. `graph-layout`: the real-jj blocks moved to `*_integration_test.ts`. `graph-webview`: display-ID search no longer lowercases per row. `roadmap`, `utils`: link remaps |
| `31b08ae`, `record progress` | `build-and-test`: thirteen `:tests` packages (adds `//src/testing`), algorithms' `:integration_tests`; this log |

Nothing moved from planned to implemented. `PROTOCOL_TYPES` unchanged (`api/` untouched).
Suite green (1087 tests); smoke test passes.

## Twelfth run (2026-11-19): maintenance

| Commit | What |
|---|---|
| `7a39d12` | Pin bump `574832c` → `e4a1514`, every line range remapped on nine pages. `roadmap`: the second provider (`FileIdFileSystemProvider`, `jj-file-id`), `RepoState.conflictedFiles`/`currentWorkspace`, 36 client tests, the watcher's gitignore/VCS filtering (`WorkspaceIgnoreManager`, two-pass batches); `SelectedCommitManager` added to the unwired list |
| `067306a` | `activation` and `graph-protocol`: the `jj-file-id` registration and `SelectedCommitManager` (tested, unwired) |
| `c366a68` | `utils`, `graph-webview`, `graph-layout`: topology helper changes, search matching full change-ID prefixes, the real-jj layout and focus-mode tests |
| `74dd7d4` | `build-and-test` (watcher BUILD deps, `FakeTextEdit`, nine `//src/testing` users, wider `newRepo` use), `merge-conflicts` (activation tests against conflicts the pinned jj writes), index (two providers) |
| `b4e7a38`, `record progress` | Index: client test count 31 → 36; `build-and-test`: twelve `:tests` packages (adds `//src/state`, `//src/ui/commands`), plus this log |

Moved from planned to implemented: the `jj-file-id` provider (registered on activation). Still
unwired: the watcher, the estimator, `SelectedCommitManager`; the graph still gets the fake
state. `PROTOCOL_TYPES` unchanged (`CommitNode.changeId` is optional and no host code fills it
yet). Suite green (1079 tests); smoke test and pinned-link check (816 links) pass.

## Eleventh run (2026-11-12): maintenance

| Commit | What |
|---|---|
| `ff1ea79` | Pin bump `0d6f5e5` → `574832c`. Activation now builds `SubprocessClient` → `ApiImpl` → `JjUi(context, api)` (returns early with no workspace folder) and registers a read-only, case-sensitive `jj-commits` file system (`CommitIdFileSystemProvider`). `roadmap` gains a file system providers section; index diagram, map and status rows mark the client and providers landed |
| `ed7e9ff` | `Commit.isElidedRevisions`: `~` glyph, italic title in `--jj-elided-revisions-color`, never draggable, never a drop target, no-op inserts. `newRepo` can `activate` with a `FakeExtensionContext` and disposes after each test; CI `jj` 0.45.1 → 0.47.1; `restrict-merge.yaml` removed. Every line link re-swept against the new pin; `graph-protocol` caption ranges re-synced |

Moved from planned to implemented: the client layer (wired, though the graph still gets the fake
state; only file reads go through it) and the `jj-commits` file system. `PROTOCOL_TYPES` unchanged
(one new optional field). Suite green (1073 tests); smoke test passes.

## Tenth run (2026-10-29): maintenance

`1a1e2d3`: pin `4cff5a1` → `0d6f5e5` across seven pages (client file reads, `Merge`, pnpm via `packageManager`).
Nothing moved to implemented; suite green (1067 tests).

## Eighth and ninth runs (2026-10-15, 10-22)

`948323c`, `b352ebf` (`67c5c1f` → `5fecc7a`): comment-style re-anchoring; `Client`,
`SubprocessClient` and the watcher interfaces on `roadmap`. `a74e0be` (`5fecc7a` → `4cff5a1`):
commit-topology helpers, multi-select messages, one-SVG-per-tile rendering, `newRepo({remote})`.

## Sixth and seventh runs (2026-10-08)

`a955a9c` `icon-theme`, `5919dd5` `utils`, `fa0c1b6` `build-and-test`, `a7e00b3` `roadmap`; the
build was complete. No upstream change on the seventh run.

## First to fifth runs (2026-10-03 to 10-07)

Run 1 (`104252a`…`8692aac`): scaffold, `graph-layout` in four parts, index diagram and tables.
Runs 2–4 (`1f2a888`, `6d109d3`, `7c46312`): `graph-protocol`, `activation`, `merge-conflicts`.
Run 5 (`d27aaa7`, `311c9a3`): pin `978c25d` → `67c5c1f`, `graph-webview`.
The `graph-protocol` type tables come from a scratch parser over `api/types.ts` that fails on any
undescribed field; the `graph-layout` worked-example SVGs come from compiling the pinned
`algorithms/*.ts` with `tsc` and running `createCommitNodes`. Redo either when its source changes.

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

Proposed (owner's call, not built): a `file-system-providers` page (`src/ui/file_system_providers/`,
both providers wired); a `state` page for `OptimisticStateEstimator` (`src/state/`, not yet wired); the
gitignore matcher; `src/ui/config/` (focus-mode and write-back config caches); `src/ui/commands/`
(command types and hooks). Until then they are on `roadmap` or logged below.

The build queue is empty. Weekly maintenance: diff upstream against the pin, update affected
pages, refresh `PROTOCOL_TYPES`, and move items from planned to implemented on `roadmap`, the
index's implemented-vs-planned table and the §6 diagram as they land. When a new module is wired
into activation, propose a page for it here first.

## Deliberate deviations

- **No elided range in the worked example.** §8 items 3 and 7. Since `574832c` an elided range
  is an ordinary node with `isElidedRevisions` (drawn as `~`); the layout has no other concept
  of it. The page says so and keeps the four-parent merge as the example.
- **"How ranges are merged" (§8 item 5).** `RangeManager` never merges ranges. It only
  appends and checks for collisions. The page describes that instead.
- **New modules go on `roadmap`, not new pages.** `src/client/` (`SubprocessClient`), `src/api/`
  and `src/ui/file_system_providers/` have been wired into activation since `574832c`, but each is
  still a section of `roadmap` (page proposals under Queue). `src/file_system_watcher/`,
  `src/state/` and the `op_head_watcher`, `network_reconnect_watcher` and `telemetry` interfaces
  are still not reached from activation. Proposal, recorded as a deliberate addition: `roadmap` must also cover what each
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
  `SubprocessClient` is wired in, but only the `jj-commits` and `jj-file-id` reads use it.
  `CommitNode.changeId` (for search prefix matching) is never set by host code yet.
- **Two commit types.** `src/api` defines its own `Commit`, separate from the webview's
  `api/types.ts` one; nothing converts between them yet. On `roadmap#gaps`.
- **10 MiB output cap.** Since `0d6f5e5` the subprocess helper caps output at 10 MiB; larger logs or
  files would fail. On `roadmap#gaps`.
- **Milestones moved off-repo (`roadmap`).** `intro.md` now links a GitHub project board instead of
  M1–M4. A board can't be pinned, so the page keeps the old timeline, labelled as such.
- **Merge-commit parents.** `showParent` fails on merge commits until jj PR 10464 (upstream TODO,
  stated on `roadmap`). `Commit.files` is now filled from `diff.files()`, so that gap is closed.
- **Contribution scope.** The README now limits contributions to Google developers. Not on any page.
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
- **`@parcel/watcher` loose ends.** The `vsix` target has a TODO about packaging the native module
  (on `roadmap#gaps`). Resolved: the symlink gap (`5fecc7a`, the root is `realpath`ed) and the
  missing ignore list (`e4a1514`, `WorkspaceIgnoreManager` supplies one).
- **Selection is not wired (`graph-protocol`).** `MultiSelectManager` and, since `e4a1514`,
  `SelectedCommitManager` have tests, but nothing constructs either, so the host still ignores
  `$onClick`. Revisit when they are wired in.
- **Unused topology helpers (`utils`).** Four commit-topology functions have no callers outside
  their tests; only `SubprocessClient.getCommits` uses the rest. The page states this.
- **`//:test` does not exist (`build-and-test`).** The spec's "Must cover" names a `//:test`
  target. There is none at this pin: `npm test` runs `bazel test //...` over thirteen `:tests` targets.
  The page describes what exists.
