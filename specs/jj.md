# rayaq.ca/jj — Jujutsu architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-02)

This is the product and technical contract for `rayaq.ca/jj`. The daily implementation
Routine builds and maintains the section against it. Build progress lives in
`specs/jj-progress.md`. Don't edit this spec without the owner's say-so. If the code
and the spec disagree, fix the code or record a deliberate deviation in the progress
file.

---

## 1. Goal

`rayaq.ca/jj` is a very detailed, always-current reference to the internal architecture
of [Jujutsu (jj)](https://github.com/jj-vcs/jj). Someone who has read it should be able
to:

- draw jj's layers and say which crate, module and trait owns each responsibility;
- name every persisted schema (each protobuf message and field), what it means, and
  which Rust type it maps to;
- explain the core data model (commits, trees, conflicts, operations, views, the
  working copy and the index) down to field level;
- trace a real command end to end. The first and most detailed one is `jj fix`.

It's a reference, not a tutorial. Depth and accuracy matter more than approachability,
but every page opens with a short plain-language summary.

## 2. Non-goals

- User documentation for jj commands. Link to `docs.jj-vcs.dev` instead.
- Opinion, comparison with Git, or roadmap speculation.
- Covering every CLI command. Only commands listed in §5 get pages, unless the
  owner adds more.
- Runtime interactivity beyond plain links and anchors.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime
   call to GitHub or any other service, no client-side fetching, no JavaScript
   framework. A page that is fine today must be fine with the network off.
2. **$0 incremental cost.** No new paid service, no new hosting, no new runtime
   dependency in `backend/requirements.txt`.
3. **Every claim is sourced.** Each data structure, field table, schema and algorithm
   description links to the exact upstream file, pinned to the analyzed commit
   (`https://github.com/jj-vcs/jj/blob/<sha>/<path>#L<start>-L<end>`). If something
   can't be traced to source at the pinned commit, it doesn't go on the page.
4. **Pinned to one upstream commit.** The whole section describes exactly one jj commit,
   recorded in code (§7.3) and shown on every page. Never mix facts from different
   upstream versions.
5. **Never fabricate.** Field names, types, protobuf field numbers, defaults and
   function names are copied from source, not paraphrased from memory. When unsure,
   omit and log the gap in the progress file.
6. **Licensing.** jj is Apache-2.0. Reproduced `.proto` schemas and code excerpts keep
   attribution: every page footer credits the jj authors and links the license.
   Excerpts stay short. Field tables and prose are written here; whole files are
   never copied in, except `.proto` schemas (minus their license headers), which are
   short and are the subject of the page.
7. **House rules.** Everything in `CLAUDE.md` applies: route-only `app.py`, tests for
   every route and every piece of logic, `*_tests.py`, no comments except non-obvious
   whys.

## 4. Information architecture

```
/jj                     Overview: summary, the architecture diagram, page index
/jj/<slug>              One deep-dive page per topic (§5)
```

- Every page shares one layout: a section nav listing every page in reading order, a
  breadcrumb, an on-page table of contents built from its `h2`/`h3`, and a footer
  showing the pinned upstream commit, its date, the jj version from `Cargo.toml`, and
  the date of the last analysis.
- Pages are reachable from the homepage through a "jj internals" feature card.
- Unknown slugs return 404. There is no catch-all.
- Headings have stable `id` anchors so deep links survive updates.

## 5. Page inventory

Each page lists the upstream files it is responsible for (its "source set"). The daily
Routine uses source sets to work out which pages an upstream change affects.

| Slug | Title | Must cover | Source set |
|---|---|---|---|
| *(index)* | jj architecture | §6 diagram; one-paragraph tour of each layer; crate map (`cli`, `lib` = jj-lib, `core`, `core/proc-macros`, `lib/gen-protos`, `lib/testutils`); links to every page | `Cargo.toml`, `docs/technical/architecture.md` |
| `storage` | On-disk layout | The `.jj/` tree: `repo/` (`store/` with `type`, `git_target`, `extra/`; `op_store/` with `operations/`, `views/`; `op_heads/heads/`; `index/` with `segments/`, `op_links/`, `changed_paths/`; `submodule_store/`), `working_copy/` (`checkout`, `tree_state`, `type`), `workspace_store/`. Which component owns each path and which format each file uses | `lib/src/repo.rs`, `workspace.rs`, `simple_op_store.rs`, `simple_op_heads_store.rs`, `default_index/store.rs`, `local_working_copy.rs`, `simple_workspace_store.rs` |
| `commits` | Commits and change IDs | `backend::Commit` field by field; `CommitId` (content hash) vs `ChangeId` (stable, reverse-hex display); predecessors (deprecated field vs `Operation.commit_predecessors`); root commit (`make_root_commit`); `Signature`/`Timestamp`; `SecureSig` and signing; `commit::Commit` wrapper; `CommitBuilder`/`DetachedCommitBuilder` | `core/src/backend.rs`, `lib/src/commit.rs`, `commit_builder.rs`, `signing_factory.rs` |
| `trees` | Trees, files and copies | `Tree` (sorted entries), `TreeValue` variants (`File{id, executable, copy_id}`, `Symlink`, `Tree`, `GitSubmodule`); `MergedTree`, `MergedTreeValue = Merge<Option<TreeValue>>`; tree diffs (`TreeDiffEntry`, diff streams); `MergedTreeBuilder`; copy tracking (`CopyId`, `CopyHistory`, `CopyRecord`, `RelatedCopy`) | `core/src/backend.rs`, `lib/src/merged_tree.rs`, `merged_tree_builder.rs`, `tree.rs`, `copies.rs`, `docs/design/copy-tracking.md` |
| `conflicts` | First-class conflicts | `Merge<T>`: the alternating add/remove `SmallVec`, invariants (one more add than removes), `trivial_merge`, `simplify`, `Diff<T>`; conflicted `root_tree` as `Merge<TreeId>` plus `conflict_labels`; how conflicts are stored in each backend; materialization and marker styles (`ConflictMarkerStyle`, `MaterializedTreeValue`); worked example of a 3-sided conflict | `core/src/merge.rs`, `conflict_labels.rs`, `lib/src/conflicts.rs`, `tree_merge.rs`, `docs/technical/conflicts.md` |
| `operations` | The operation log | `Operation` and `OperationMetadata` field by field; `ViewId`/`OperationId`; the op DAG and root operation; `commit_predecessors`; op heads and `OpHeadsStore`; how concurrent operations are detected and merged; `op_walk` and opset expressions; `gc`; how undo/restore work in terms of these structures | `core/src/op_store.rs`, `lib/src/operation.rs`, `op_heads_store.rs`, `simple_op_heads_store.rs`, `simple_op_store.rs`, `op_walk.rs`, `docs/technical/concurrency.md`, `docs/operation-log.md` |
| `view` | Views, bookmarks and tags | `op_store::View` field by field (`head_ids`, `local_bookmarks`, `local_tags`, `remote_views`, `git_refs`, `git_heads`, `wc_commit_ids`); `RefTarget = Merge<Option<CommitId>>` and conflicted refs; `RemoteView`/`RemoteRef`/`RemoteRefState`; `view::View` (the in-memory wrapper); legacy fields and migrations | `core/src/op_store.rs`, `lib/src/view.rs`, `refs.rs`, `docs/bookmarks.md` |
| `transactions` | Repos, transactions and rewriting | `Repo` trait, `ReadonlyRepo`, `RepoLoader`, `MutableRepo`, `Transaction`/`UnpublishedOperation`; the commit lifecycle from builder to published operation; `rewrite.rs` (`CommitRewriter`, `transform_descendants`, `rebase_descendants`, `RebaseOptions`, `EmptyBehavior`); how parent mappings are tracked | `lib/src/repo.rs`, `transaction.rs`, `rewrite.rs` |
| `working-copy` | The working copy | `WorkingCopy`/`LockedWorkingCopy`/`WorkingCopyFactory` traits; snapshot and checkout flows; `LocalWorkingCopy`, `TreeState`, `FileState`, `FileType`, materialized conflict data; the `Checkout` record and stale working copies (`WorkingCopyFreshness`); sparse patterns; fsmonitor/watchman | `lib/src/working_copy.rs`, `local_working_copy.rs`, `fsmonitor.rs`, `docs/working-copy.md` |
| `index` | The commit index | `Index`/`ReadonlyIndex`/`MutableIndex`/`ChangeIdIndex` traits; default index segments (readonly/mutable, composite stacking), entries, `SegmentControl`; changed-path index; how an operation maps to index segments; `id_prefix` shortest-unique-prefix resolution | `lib/src/index.rs`, `default_index/*`, `id_prefix.rs` |
| `revsets` | Revset engine | Pipeline: pest grammar → AST → `RevsetExpression` → symbol resolution (`SymbolResolver`) → `ResolvedExpression` → evaluation by the index's revset engine; filters and extensions; filesets as the path counterpart | `lib/src/revset.rs`, `revset_parser.rs`, `revset.pest`, `default_index/revset_engine.rs`, `fileset.rs`, `docs/technical/revset-evaluation.md` |
| `backends` | Storage backends | `Backend` trait method by method; `Store` (caching layer over a backend); `GitBackend` (jj metadata in `extra/` via `git_store.proto`, change IDs, conflicts in trees); `SimpleBackend`; `SecretBackend`; backend selection through the `type` file and `StoreFactories` | `core/src/backend.rs`, `lib/src/store.rs`, `git_backend.rs`, `simple_backend.rs`, `secret_backend.rs`, `default_backend_factories.rs` |
| `protobufs` | Every schema | All seven `.proto` files, each message and enum with every field, number, type, deprecation status and meaning, plus the Rust type it is converted to and from. Reserved and deprecated fields explained | `lib/src/protos/*.proto` and the `*_store.rs`/`*_working_copy.rs` conversion code |
| `fix` | How `jj fix` works | §8, in full | `lib/src/fix.rs`, `cli/src/commands/fix.rs`, `cli/src/config/revsets.toml`, `docs/config.md` (fix section) |

The owner may add more command pages later (candidates: `rebase`, `absorb`,
`squash`, `git-fetch`). Each one needs a §8-style requirement block in this spec first.

## 6. The architecture diagram

The `/jj` index page centres on one large diagram. Requirements:

- **Hand-authored inline SVG** in the template. No JS rendering library, no external
  image, no image generated at runtime.
- Shows the layers top to bottom:
  1. CLI (`cli`: command dispatch, `CommandHelper`, `WorkspaceCommandHelper`);
  2. Workspace (`Workspace`, `WorkspaceLoader`, workspace store);
  3. Repo layer (`ReadonlyRepo`, `MutableRepo`, `Transaction`, `View`);
  4. Stores: `Store` → `Backend` (Git/Simple), `OpStore`, `OpHeadsStore`,
     `IndexStore`, `SubmoduleStore`, and the `WorkingCopy` beside them;
  5. On-disk `.jj/` layout (§5 `storage`).
- Shows the data model beside the layers: Operation → View → (heads, bookmarks, wc
  commits) → Commit → `Merge<TreeId>` → Tree → `TreeValue` → File/Symlink/Tree/Submodule,
  with arrows labelled by the field that links them (`view_id`, `head_ids`,
  `root_tree`, …).
- Every box links to the page that explains it.
- Readable at desktop width and scrollable sideways inside its own container on mobile;
  the page itself never scrolls horizontally.
- Has `role="img"`, a `<title>`, and a `<desc>` that summarises it in text.
- Uses the site's colour variables so it works in light and dark mode.
- Deep-dive pages may include smaller focused SVG diagrams under the same rules. The
  `fix` page needs at least two (§8).

## 7. Technical design

### 7.1 Routing

- `app.py` gets `/jj` and `/jj/<slug>` and stays route-only: it asks `jj_docs` for the
  page and renders it, and returns 404 for unknown slugs.
- `backend/jj_docs.py` owns the page registry and upstream pin (§7.3), and builds the
  nav, breadcrumb and footer context. It must be unit-testable without Flask.

### 7.2 Templates and assets

- `frontend/templates/jj/base.html` holds the shared layout (§4). Each page is
  `frontend/templates/jj/<slug>.html` and extends it; the index is
  `frontend/templates/jj/index.html`.
- `frontend/static/jj.css` holds section styles (tables, code blocks, diagrams, the
  nav), built on `style.css` variables. Static URLs go through `url_for` so they pick
  up `static_assets` versioning.
- Code and schema blocks are plain `<pre><code>`. No highlighting library.
- Tables are the primary format for fields: **Field · Type · Proto # (if persisted) ·
  Meaning · Source**.

### 7.3 Upstream pin

`backend/jj_docs.py` holds:

```python
UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj",
    "commit": "<40-char sha>",
    "commit_date": "YYYY-MM-DD",
    "version": "<workspace.package.version from Cargo.toml>",
    "analyzed_on": "YYYY-MM-DD",
}
```

and a helper that builds pinned source links, which templates use for every source
link. Bumping the pin is the only way a page's described version changes.

### 7.4 Page registry

An ordered list of pages, each with `slug`, `title`, `summary` (one sentence, used on
the index and in `<meta name="description">`), and `sources` (its §5 source set). The
nav, the index page list and the slug allowlist all derive from this one list. A page
appears in the registry only once its template exists and meets its §5 bar.
Until then it's listed on the index as "In progress", without a link.

### 7.5 Tests (`backend/tests/jj_docs_tests.py`, plus `app_tests.py` additions)

- `/jj` and every registered slug return 200; an unknown slug returns 404.
- Every registered page has a template, a non-empty summary, and at least one source.
- Every source link on every page points at `github.com/jj-vcs/jj/blob/<pinned sha>/`.
  No unpinned `blob/main` links.
- The pin is well-formed: 40 hex chars, ISO dates, semver version.
- The index includes the architecture SVG with `<title>` and `<desc>`, and links to
  every registered page.
- The `protobufs` page names every message and enum in a committed list
  (`PROTO_MESSAGES` in `jj_docs.py`). The Routine refreshes that list from upstream
  when it bumps the pin.
- The homepage links to `/jj`.

## 8. `jj fix` deep dive — requirements

The `fix` page is the flagship command page. It must explain, with source links:

1. **Purpose and CLI surface.** `FixArgs`: `-s/--source` (revsets), positional
   `FILESETS`, `--include-unchanged-files`, `-a/--all-lines`. The default revset comes
   from `revsets.fix` (`reachable(@, mutable())` in `cli/src/config/revsets.toml`).
   `check_rewritable_expr` refuses immutable targets.
2. **Configuration.** The `fix.tools.<name>` table: `command`, `patterns` (filesets,
   unioned), `enabled` (default true), `line-range-args` (templates using `$first` and
   `$last`), `run-tool-if-zero-line-ranges` (only valid with `line-range-args`). Tools
   are sorted by name, then disabled ones are dropped. The two config errors (none
   configured, none enabled). Command variables `$path` and `$root`.
3. **End-to-end flow** as a sequence diagram (SVG): `cmd_fix` → `get_tools_config` →
   resolve the revset → `start_transaction` → `fix_files` (jj-lib) → `ParallelFileFixer`
   → `fix_one_file` per unique file → `run_tool` subprocess →
   `transform_descendants` rewrite → `tx.finish("fixed N commits")`.
4. **Choosing which files to fix** (`lib/src/fix.rs::fix_files`):
   - targets are the descendants of the given roots;
   - `get_base_commit_map`: each commit's "base" is the set of nearest ancestors
     *outside* the fixed set, not its direct parent. Show a worked example on a small
     DAG with a merge;
   - diff of the merged base tree against the commit's tree (or against the empty tree
     with `--include-unchanged-files`), skipping deletions;
   - paths found in a base commit carry forward to its descendants, so descendants
     re-fix the same paths and keep the fixes;
   - every side of a conflicted file becomes its own `FileToFix`, so all sides get
     fixed;
   - `FileToFix { file_id, base_file_id, repo_path }`, and why deduplicating on that
     triple means each distinct content is formatted once. That is also why tools
     must be deterministic.
5. **Running tools** (`cli/src/commands/fix.rs::fix_one_file`, `run_tool`): matching
   tools chain in order (each output feeds the next); empty files are skipped; base
   content is loaded only when some tool uses line ranges and `--all-lines` is off;
   stdin/stdout piping, `current_dir` = workspace root, stderr passthrough prefixed
   with the path; a failed or non-zero tool is skipped with a warning, which looks the
   same as "no change"; a new `FileId` is written only when the content changed.
6. **Changed-line ranges.** `compute_regions_to_format` and `compute_changed_ranges`
   (line diff via `ContentDiff::by_line`, 1-based inclusive ranges, deletions produce
   no range, a missing or empty base means the whole file), `compute_file_line_count`
   edge cases, and how ranges expand into `line-range-args`. Include the test vectors
   from the source as a table.
7. **Parallelism.** `ParallelFileFixer` uses rayon `into_par_iter` and
   `try_for_each_init` with an mpsc channel; the result is
   `HashMap<&FileToFix, FileId>`.
8. **Rewriting history.** `transform_descendants` callback: rebuild each commit's tree
   with `MergedTreeBuilder`, keeping `executable` and `copy_id`; write the new tree and
   `reparent()`; commits with no file changes but rewritten parents are still
   reparented. `FixSummary { rewrites, num_checked_commits, num_fixed_commits }`. Why
   this never creates new conflicts.
9. **Observability.** The output `Fixed N commits of M checked.`, the operation
   description, and reviewing with `jj op show -p`.
10. **Worked example.** The A/B/C history from the command's own help, redrawn as an
    SVG showing which files go to which tool in each commit.

## 9. Keeping it current (the daily Routine)

A Routine ("rayaq.ca/jj — architecture reference agent") runs once a day. Each run:

1. Shallow-clones `jj-vcs/jj` at `HEAD` into scratch space (never into this repo).
2. Compares upstream `HEAD` with `UPSTREAM.commit`. Using the §5 source sets, it lists
   the pages whose sources changed (`git diff --stat <pinned>..HEAD -- <paths>`; when
   the pinned commit isn't in a shallow clone, deepen or fetch it).
3. **Build phase** (until every §5 page and §6/§7/§8 item is done): builds the next
   item from the queue in `specs/jj-progress.md`. Pages are built against the pinned
   commit; the pin isn't bumped while a page is half-built.
4. **Maintenance phase** (always, once the build is done; before building new pages
   while the build is still going): updates every affected page so it matches the new
   `HEAD`, refreshes `PROTO_MESSAGES`, then bumps `UPSTREAM` in the same commit as the
   content changes. Never bump the pin without re-checking every affected page. If
   nothing in any source set changed, it bumps the pin and date only.
5. Runs the full test suite and starts the app to check `/jj` and every page return
   200, then pushes small commits straight to `main` (merge, never rebase, never force).
6. Rewrites `specs/jj-progress.md`: status, pin, what changed, open gaps, next queue.

## 10. Acceptance criteria

- [ ] `/jj` renders the §6 diagram and links to every page in §5.
- [ ] Every §5 page exists, meets its "Must cover" column, and is registered.
- [ ] The `fix` page meets all ten §8 items, with at least two SVG diagrams.
- [ ] The `protobufs` page covers all seven `.proto` files, every field.
- [ ] Every source link is pinned to `UPSTREAM.commit`.
- [ ] §7.5 tests exist and pass.
- [ ] Homepage card links to `/jj`.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their
      container.
- [ ] The daily Routine has run at least once in maintenance mode and either bumped
      the pin or recorded "no relevant upstream change".
