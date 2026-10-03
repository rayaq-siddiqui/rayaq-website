# rayaq.ca/jj-commit-cloud-poc — jj Commit Cloud proof-of-concept architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-03)

This is the product and technical contract for `rayaq.ca/jj-commit-cloud-poc`. The daily
implementation Routine builds and maintains the section against it. Build progress lives in
`specs/jj-commit-cloud-poc-progress.md`. Don't edit this spec without the owner's say-so. If
the code and the spec disagree, fix the code or record a deliberate deviation in the
progress file.

---

## 1. Goal

`rayaq.ca/jj-commit-cloud-poc` is a very detailed, always-current reference to the internal
architecture of [jj-commit-cloud-poc](https://github.com/jj-vcs/jj-commit-cloud-poc), a
proof-of-concept "commit cloud": a gRPC server that stores a jj repository's commits, trees,
files, operations, views and op heads, plus client implementations of jj-lib's storage
traits and a custom `jj` binary that uses them. Someone who has read it should be able to:

- draw the system: the custom `jj` CLI → `cc-lib` store implementations → gRPC (tonic) →
  `jj-cc-server` services → the server's `Store` trait → its storage engines, and say which
  crate, type and file owns each responsibility;
- name every RPC and every protobuf message and field in `common/proto/*.proto`, and the
  jj-lib type each converts to and from;
- explain how each jj-lib trait method (`Backend`, `OpStore`, `OpHeadsStore`) is implemented
  over the wire, and what is left unimplemented;
- explain how the server computes object IDs (`hash_utils.rs`) and why they must match what
  the client expects;
- trace `jj cc init`, and a state-changing command such as `jj describe`, end to end across
  client and server.

It's a reference, not a tutorial. Every page opens with a short plain-language summary.

## 2. Non-goals

- Deployment or usage documentation beyond what is needed to explain the code.
- Opinion, comparison with other commit-cloud systems, or roadmap speculation.
- Re-explaining jj internals. Link to the matching `/jj/<slug>` page instead (`/jj/backends`,
  `/jj/operations`, `/jj/view`, `/jj/commits`, `/jj/trees`, `/jj/protobufs`, `/jj/cli`),
  noting that `/jj` describes its own pinned jj version, which can differ from the `jj-lib`
  version this project depends on.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime call
   to GitHub or any other service, no client-side fetching, no JavaScript framework.
2. **$0 incremental cost.** No new paid service, no new hosting, no new runtime dependency
   in `backend/requirements.txt`.
3. **Every claim is sourced.** Each message, RPC, trait implementation, flow and algorithm
   links to the exact upstream file, pinned to the analyzed commit
   (`https://github.com/jj-vcs/jj-commit-cloud-poc/blob/<sha>/<path>#L<start>-L<end>`).
   Claims about jj-lib or jj-cli APIs link to `github.com/jj-vcs/jj` at the tag matching
   the `jj-lib` version in the workspace's `Cargo.toml` files (`v<version>`), never `main`.
4. **Pinned to one upstream commit.** The whole section describes exactly one commit,
   recorded in code (§7.3) and shown on every page.
5. **Never fabricate.** Message, field and RPC names, field numbers, CLI flags and defaults
   are copied from source. When unsure, omit and log the gap in the progress file.
6. **PoC honesty.** Upstream promises no completeness or stability. `todo!()` or
   `unimplemented!()` trait methods, TODO comments that change behaviour (such as streaming
   `WriteFile`), storage engines that are declared but not implemented, and failing or
   ignored tests are stated plainly, with source links.
7. **Licensing.** Apache-2.0 (Google LLC). Every page footer credits the upstream authors and
   links the license. `.proto` schemas may be reproduced minus their license headers; other
   excerpts stay short.
8. **Section isolation.** Four Routines push to this repo. This section owns only its own
   files (§7). It never edits `jj_docs.py`, `templates/jj/`, `jj.css`, or another section's
   files. Shared files (`app.py`, `home.html`, `app_tests.py`, `CLAUDE.md`) get additive
   edits only.
9. **House rules.** Everything in `CLAUDE.md` applies.

## 4. Information architecture

```
/jj-commit-cloud-poc              Overview: summary, the architecture diagram, page index
/jj-commit-cloud-poc/<slug>       One deep-dive page per topic (§5)
```

- Every page shares one layout: a section nav, a breadcrumb, an on-page table of contents
  built from its `h2`/`h3`, and a footer showing the pinned upstream commit, its date, the
  `jj-lib` version, and the date of the last analysis.
- Pages are reachable from the homepage through a "jj Commit Cloud internals" feature card.
- Unknown slugs return 404. There is no catch-all. Headings have stable `id` anchors.

## 5. Page inventory

Paths are relative to the jj-commit-cloud-poc repo root.

| Slug | Title | Must cover | Source set |
|---|---|---|---|
| *(index)* | Commit Cloud architecture | §6 diagram; one-paragraph tour of each component; crate map (`cli` → binary `jj`, `cc-lib`, `cc-common`, `jj-commit-cloud-server` → binary `jj-cc-server`, `testutils`) with each crate's dependencies; a "status and limitations" summary; links to every page | `README.md`, `Cargo.toml`, `*/Cargo.toml` |
| `protobufs` | Every schema | Both `.proto` files: each service and RPC (request, response, streaming), each message with every field, number, type and meaning, and the jj-lib type it converts to and from (with the conversion code linked); how `common/build.rs` generates the Rust code | `common/proto/*.proto`, `common/build.rs`, `common/src/lib.rs` |
| `client-backend` | The client Backend | `cc_backend.rs`: the commit-cloud `Backend` implementation method by method (which RPC each calls, ID lengths, root commit/change IDs, empty tree, how conflicts, copies and signatures are handled or rejected); the tonic channel; sync/async bridging (`run_async`); `CommitCloudConfig` and how it's loaded from the store | `lib/src/cc_backend.rs`, `lib/src/util.rs`, `lib/src/lib.rs` |
| `client-op-store` | The client OpStore and OpHeadsStore | `cc_op_store.rs` and `cc_op_heads_store.rs` method by method: which RPC each calls, how operations and views are converted, how op heads are read and updated (and whether that update is atomic), how concurrent operations would surface; what is unimplemented | `lib/src/cc_op_store.rs`, `lib/src/cc_op_heads_store.rs` |
| `cli` | The custom jj binary | `CliRunner` customisation in `main.rs` (store factories, the `cc` subcommand); `jj cc init` step by step (`init.rs`), what it writes locally and what it registers on the server; `repo.rs`; how a stock jj command runs unchanged on top of the commit-cloud stores (link `/jj/cli`) | `cli/src/*`, `cli/src/commands/*`, `lib/src/repo.rs` |
| `server` | The server | `server/src/main.rs`: every CLI argument and default, storage-engine selection, tonic setup and health service; `backend.rs` and `op_store.rs` service implementations RPC by RPC (validation, ID computation, `Status` codes via `error_util.rs`); repository registration and repo UUIDs | `server/src/main.rs`, `server/src/backend.rs`, `server/src/op_store.rs`, `server/src/error_util.rs` |
| `storage` | Server storage engines | The `Store` trait method by method; `memorystore.rs` (data structures, locking); any other engine at the pinned commit (for example SQLite) or the fact it is declared but not yet implemented; how op heads are updated atomically (or not) | `server/src/store/*` |
| `object-ids` | Object IDs and hashing | The flagship (§8) | `server/src/hash_utils.rs`, plus the client code that computes or checks IDs |
| `testing` | Tests | `testutils` (how a server is started for tests, how a repo is set up), each integration test under `cli/tests` and `server/tests` and what it asserts, which tests are expected to fail at the pinned commit and why | `testutils/*`, `cli/tests/*`, `server/tests/*` |

**New code upstream.** When the pin moves and a new module, crate, RPC or storage engine
appears, the Routine adds a row to the progress file's queue with a proposed slug, title,
"must cover" and source set, and builds it like any other page. The proposal is recorded as
a deliberate addition until the owner folds it into this table.

## 6. The architecture diagram

The `/jj-commit-cloud-poc` index page centres on one large diagram. Requirements:

- **Hand-authored inline SVG**. No JS rendering library, no external image.
- Shows, left to right or top to bottom: the user's `jj` binary (stock jj-cli commands plus
  `jj cc`) → jj-lib (`ReadonlyRepo`/`Transaction`, `Store`) → `cc-lib`
  (`Backend`, `OpStore`, `OpHeadsStore` implementations) → the network boundary (gRPC,
  `BackendService`, `OpStoreService`) → `jj-cc-server` service impls → `Store` trait →
  storage engines. Show what stays local (the working copy, `.jj/` config) and what lives
  on the server.
- Every box links to the page that explains it (jj-lib boxes link to `/jj` pages).
- Readable at desktop width and scrollable sideways inside its own container on mobile.
- Has `role="img"`, a `<title>`, and a `<desc>`. Uses the site's colour variables.
- `object-ids` needs at least two diagrams; `cli` needs a sequence diagram of a command's
  writes crossing the wire.

## 7. Technical design

### 7.1 Routing

- `app.py` gets `/jj-commit-cloud-poc` and `/jj-commit-cloud-poc/<slug>` and stays
  route-only: it asks `jj_cloud_docs` for the page and renders it, and returns 404 for
  unknown slugs.
- `backend/jj_cloud_docs.py` owns the page registry and upstream pin, and builds the nav,
  breadcrumb and footer context. It must be unit-testable without Flask.

### 7.2 Templates and assets

- `frontend/templates/jj_cloud/base.html` holds the shared layout; each page is a fragment
  `frontend/templates/jj_cloud/<slug>.html`; the index is `jj_cloud/index.html`.
- `frontend/static/jj_cloud.css` holds this section's styles, built on `style.css`
  variables. It may visually match `jj.css` and the page may link `jj.css` too, but never
  edits it.
- Code and schema blocks are plain `<pre><code>`. Field tables: **Field · Type · Proto # ·
  Meaning · jj-lib type · Source**.

### 7.3 Upstream pin

```python
UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-commit-cloud-poc",
    "commit": "<40-char sha>",
    "commit_date": "YYYY-MM-DD",
    "jj_lib_version": "<jj-lib version from the workspace Cargo.toml files>",
    "analyzed_on": "YYYY-MM-DD",
}
```

plus `source_url(path, start=None, end=None)` for this repo and
`jj_lib_url(path, start=None, end=None)` for jj at tag `v<jj_lib_version>`. Every source
link goes through one of them. Never link `blob/main`.

### 7.4 Page registry

An ordered `PAGES` list, each entry with `slug`, `title`, `summary`, `sources` and `ready`.
The nav, index list and slug allowlist derive from it. Not-ready pages show on the index as
"In progress", without a link.

### 7.5 Tests (`backend/tests/jj_cloud_docs_tests.py`, plus `app_tests.py` additions)

- `/jj-commit-cloud-poc` and every ready slug return 200; unknown or not-ready slugs 404.
- Every ready page has a template, a non-empty summary and at least one source.
- Every commit-cloud link is pinned to `UPSTREAM.commit`; every jj link is pinned to
  `v<jj_lib_version>`. No `blob/main` links.
- The pin is well-formed: 40 hex chars, ISO dates, semver version.
- The index includes the architecture SVG with `<title>` and `<desc>` and links to every
  ready page.
- The `protobufs` page names every service, RPC, message and enum in a committed list
  (`PROTO_ITEMS` in `jj_cloud_docs.py`) that the Routine refreshes when it bumps the pin.
- The homepage links to `/jj-commit-cloud-poc`.

## 8. `object-ids` deep dive — requirements

The flagship page. It must explain, with source links:

1. **Which IDs exist.** Commit, tree, file, symlink, operation, view and repo IDs: who
   computes each (client or server), its length and encoding.
2. **Git-compatible hashing.** `compute_git_commit_hash`, `compute_git_tree_hash`,
   `compute_git_blob_hash`: the exact bytes hashed for each, step by step, including how
   jj-only fields (change ID, predecessors, conflicts, signatures) are or aren't
   included, and the `gix` types used.
3. **Operation and view hashing.** `hash_operation`, `hash_view`, the length-prefixing
   helpers, and why that encoding avoids ambiguity.
4. **Agreement with the client.** Where the client relies on the server's IDs (returned in
   write responses) versus computing them itself, and what would break if they disagreed.
5. **Worked example.** A one-file commit: the blob, tree and commit preimages laid out
   byte-group by byte-group as an SVG, ending in the IDs.
6. **Comparison with jj's own backends**, linking `/jj/backends`: where these IDs match what
   `GitBackend` would produce and where they differ.
7. **Edge cases** the code handles or rejects (empty trees, missing signatures, root
   commit), each sourced.

## 9. Keeping it current (the daily Routine)

A Routine ("rayaq.ca/jj-commit-cloud-poc — architecture reference agent") runs once a day.
Each run:

1. Clones `jj-vcs/jj-commit-cloud-poc` at `HEAD` into scratch space (never into this repo).
   Clones `jj-vcs/jj` at tag `v<jj_lib_version>` too, when a page needs to check a jj API.
2. Compares upstream `HEAD` with `UPSTREAM.commit` and lists the pages whose §5 source sets
   changed, plus any new crate, module, RPC or storage engine.
3. **Build phase**: builds the next item from the queue in
   `specs/jj-commit-cloud-poc-progress.md`. Build order: the scaffold (module, routes,
   layout, tests, homepage card, `CLAUDE.md` notes), `protobufs`, the §6 diagram,
   `object-ids`, `client-backend`, `client-op-store`, `server`, `storage`, `cli`,
   `testing`, then any queued additions. The pin isn't bumped while a page is half-built.
4. **Maintenance phase** (always once the build is done; before building while it is still
   going): updates every affected page to match the new `HEAD`, refreshes `PROTO_ITEMS`
   and the jj-lib version, then bumps `UPSTREAM` in the same commit as the content changes.
   If nothing changed, it bumps the pin and dates only.
5. Runs the full test suite and starts the app to check `/jj-commit-cloud-poc` and every
   page return 200, then pushes small commits straight to `main` (merge, never rebase,
   never force).
6. Rewrites `specs/jj-commit-cloud-poc-progress.md`: status, pin, what changed, open gaps,
   queue.

## 10. Acceptance criteria

- [ ] `/jj-commit-cloud-poc` renders the §6 diagram and links to every page in §5.
- [ ] Every §5 page exists, meets its "Must cover" column, and is registered.
- [ ] `object-ids` meets all seven §8 items with at least two SVG diagrams; `cli` has its
      sequence diagram.
- [ ] `protobufs` covers both `.proto` files, every RPC and every field.
- [ ] Every source link is pinned (`UPSTREAM.commit` or `v<jj_lib_version>`).
- [ ] §7.5 tests exist and pass.
- [ ] Homepage card links to `/jj-commit-cloud-poc`.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their container.
- [ ] The daily Routine has run at least once in maintenance mode and either bumped the pin
      or recorded "no relevant upstream change".
