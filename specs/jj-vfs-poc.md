# rayaq.ca/jj-vfs-poc — jj VFS proof-of-concept architecture reference

**Status:** approved for build · **Owner:** Rayaq Siddiqui · **Spec version:** 1 (2026-10-03)

This is the product and technical contract for `rayaq.ca/jj-vfs-poc`. The daily
implementation Routine builds and maintains the section against it. Build progress lives in
`specs/jj-vfs-poc-progress.md`. Don't edit this spec without the owner's say-so. If the code
and the spec disagree, fix the code or record a deliberate deviation in the progress file.

---

## 1. Goal

`rayaq.ca/jj-vfs-poc` is a very detailed, always-current reference to the internal
architecture of [jj-vfs-poc](https://github.com/jj-vcs/jj-vfs-poc) (crate `jjfsd`), a
proof-of-concept read-only FUSE file system that exposes a jj repository's commits and
workspaces as directories. Someone who has read it should be able to:

- draw the layers from the kernel's FUSE request down to jj-lib's `Store`, and say which
  type and file owns each responsibility;
- name every trait (`VirtualFilesystem`, `VirtualFile`, `PathMapper`) and every implementor,
  method by method;
- explain the mount's namespace (what lives at each path, and why) and how a path is
  resolved to a `VirtualFile`;
- trace a `lookup`, `getattr`, `readdir`, `read` and `readlink` request end to end, including
  inode allocation and the async/sync bridge;
- say exactly how jj objects (commits, trees, files, symlinks, conflicts, workspaces) become
  files and directories, and what the PoC does not support yet.

It's a reference, not a tutorial. Every page opens with a short plain-language summary.

## 2. Non-goals

- Usage documentation beyond what is needed to explain the code.
- Opinion, comparison with other VCS file systems, or roadmap speculation.
- Re-explaining jj internals. Link to the matching `/jj/<slug>` page instead (for example
  `/jj/trees`, `/jj/commits`, `/jj/conflicts`, `/jj/working-copy`), noting that `/jj`
  describes its own pinned jj version, which can differ from the `jj-lib` version this crate
  depends on.

## 3. Hard constraints

1. **Static content.** Pages are server-rendered from committed templates. No runtime call
   to GitHub or any other service, no client-side fetching, no JavaScript framework.
2. **$0 incremental cost.** No new paid service, no new hosting, no new runtime dependency
   in `backend/requirements.txt`.
3. **Every claim is sourced.** Each type, method table, flow and algorithm links to the
   exact upstream file, pinned to the analyzed commit
   (`https://github.com/jj-vcs/jj-vfs-poc/blob/<sha>/<path>#L<start>-L<end>`). Claims about
   jj-lib APIs the crate calls link to `github.com/jj-vcs/jj` at the tag matching the
   `jj-lib` version in `Cargo.toml` (`v<version>`), never `main`.
4. **Pinned to one upstream commit.** The whole section describes exactly one jj-vfs-poc
   commit, recorded in code (§7.3) and shown on every page.
5. **Never fabricate.** Type, trait, method, FUSE op and error names, mount options and
   defaults are copied from source, not paraphrased from memory. When unsure, omit and log
   the gap in the progress file.
6. **PoC honesty.** Upstream promises no completeness or stability. Unsupported operations,
   `todo!()`/`unimplemented!()` paths, known limitations and failing or ignored tests are
   stated plainly, with source links, rather than glossed over.
7. **Licensing.** jj-vfs-poc is Apache-2.0 (Google LLC). Every page footer credits the
   upstream authors and links the license. Code excerpts stay short.
8. **Section isolation.** Four Routines push to this repo. This section owns only its own
   files (§7). It never edits `jj_docs.py`, `templates/jj/`, `jj.css`, or another section's
   files. Shared files (`app.py`, `home.html`, `app_tests.py`, `CLAUDE.md`) get additive
   edits only.
9. **House rules.** Everything in `CLAUDE.md` applies.

## 4. Information architecture

```
/jj-vfs-poc              Overview: summary, the architecture diagram, page index
/jj-vfs-poc/<slug>       One deep-dive page per topic (§5)
```

- Every page shares one layout: a section nav, a breadcrumb, an on-page table of contents
  built from its `h2`/`h3`, and a footer showing the pinned upstream commit, its date, the
  crate version and the `jj-lib` version from `Cargo.toml`, and the date of the last
  analysis.
- Pages are reachable from the homepage through a "jj VFS internals" feature card.
- Unknown slugs return 404. There is no catch-all. Headings have stable `id` anchors.

## 5. Page inventory

Each page lists the upstream files it is responsible for (its "source set"). Paths are
relative to the jj-vfs-poc repo root.

| Slug | Title | Must cover | Source set |
|---|---|---|---|
| *(index)* | jj-vfs-poc architecture | §6 diagram; one-paragraph tour of each layer; module map (every `pub mod` in `lib.rs`); dependency table from `Cargo.toml` with what each is used for; a "status and limitations" summary; links to every page | `README.md`, `Cargo.toml`, `src/lib.rs` |
| `mounting` | Starting and mounting | `main.rs` step by step: arguments, tracing setup, `fuser::Config` and every mount option, the tokio runtime, loading settings, the workspace and the repo at head, choosing the path mapper, `spawn_mount`, signal handling and unmount | `src/main.rs` |
| `fuse` | The FUSE adapter | `JjFuse`: every `Filesystem` method it implements and every one it leaves to `fuser`'s defaults; how each op maps to a `VirtualFilesystem` call; the async bridge onto the tokio runtime and the reply macro; `FileAttributes` → `FileAttr` (every field, TTLs, permissions, timestamps); `FileType` conversion; `JjError` → errno table | `src/fuse.rs`, `src/jj_error.rs` |
| `inodes` | Inodes | `InodeMap`: its entries, how inode numbers are allocated and looked up, the root inode, path ↔ inode mapping, lifetime (is anything ever forgotten?), concurrency | `src/inode_map.rs` |
| `vfs-layer` | The virtual file layer | The `VirtualFilesystem`, `VirtualFile` and `PathMapper` traits method by method, default methods included; `PathMappedVfs`; `DirectoryEntry`/`DirectoryStream`; how `read(offset, size)` is served from an `AsyncRead` | `src/vfs.rs`, `src/virtual_file.rs`, `src/path_mapper.rs` |
| `namespace` | The mount's namespace | The flagship (§8) | `src/path_mapper_all_commits.rs`, `src/static_directory.rs`, `src/commits_directory.rs`, `src/workspaces_directory.rs` |
| `commit-trees` | Commits as directory trees | `CommitTreeFile`: how a commit's `MergedTree` is walked; how each `TreeValue` kind (file, executable file, symlink, tree, submodule) and each conflicted path is presented; how file content is streamed from the `Store`; sizes and attributes; links to `/jj/trees` and `/jj/conflicts` | `src/commit_tree_file.rs` |
| `testing` | Tests and CI | `test_helpers` (how a throwaway repo and commit are built), the unit tests per module and what each pins down, `tests/vfs_integration.rs` (what is mounted and asserted), the CI workflow and rustfmt settings | `src/test_helpers.rs`, `tests/*`, `.github/workflows/*`, `rustfmt.toml` |

**New code upstream.** When the pin moves and a new module appears (for example a writable
working-copy layer or another path mapper), the Routine adds a row to the progress file's
queue with a proposed slug, title, "must cover" and source set, and builds it like any other
page. The proposal is recorded as a deliberate addition until the owner folds it into this
table.

## 6. The architecture diagram

The `/jj-vfs-poc` index page centres on one large diagram. Requirements:

- **Hand-authored inline SVG**. No JS rendering library, no external image.
- Shows, top to bottom: a process calling `open`/`read` → the kernel FUSE driver → `fuser`
  → `JjFuse` (with `InodeMap`) → `VirtualFilesystem` / `PathMappedVfs` → `PathMapper`
  (`AllCommitsPathMapper`) → the `VirtualFile` implementors (`StaticDirectory`,
  `CommitsDirectory`, `WorkspacesDirectory`, `CommitTreeFile`) → jj-lib (`ReadonlyRepo`,
  `Store`, `MergedTree`) → the repository on disk. Show the tokio runtime boundary.
- Beside it, the mount's directory tree as the namespace page describes it.
- Every box links to the page that explains it (jj-lib boxes link to `/jj` pages).
- Readable at desktop width and scrollable sideways inside its own container on mobile.
- Has `role="img"`, a `<title>`, and a `<desc>`. Uses the site's colour variables.
- `fuse` needs a sequence diagram for one `read`; `namespace` needs at least two diagrams.

## 7. Technical design

### 7.1 Routing

- `app.py` gets `/jj-vfs-poc` and `/jj-vfs-poc/<slug>` and stays route-only: it asks
  `jj_vfs_docs` for the page and renders it, and returns 404 for unknown slugs.
- `backend/jj_vfs_docs.py` owns the page registry and upstream pin, and builds the nav,
  breadcrumb and footer context. It must be unit-testable without Flask.

### 7.2 Templates and assets

- `frontend/templates/jj_vfs/base.html` holds the shared layout; each page is a fragment
  `frontend/templates/jj_vfs/<slug>.html`; the index is `jj_vfs/index.html`.
- `frontend/static/jj_vfs.css` holds this section's styles, built on `style.css` variables.
  It may visually match `jj.css` and the page may link `jj.css` too, but never edits it.
- Code blocks are plain `<pre><code>`. Tables: **Item · Type/Signature · Meaning · Source**.

### 7.3 Upstream pin

```python
UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-vfs-poc",
    "commit": "<40-char sha>",
    "commit_date": "YYYY-MM-DD",
    "version": "<package.version from Cargo.toml>",
    "jj_lib_version": "<jj-lib version from Cargo.toml>",
    "analyzed_on": "YYYY-MM-DD",
}
```

plus `source_url(path, start=None, end=None)` for this repo and
`jj_lib_url(path, start=None, end=None)` for jj-lib at tag `v<jj_lib_version>`. Every source
link goes through one of them. Never link `blob/main`.

### 7.4 Page registry

An ordered `PAGES` list, each entry with `slug`, `title`, `summary`, `sources` and `ready`.
The nav, index list and slug allowlist derive from it. Not-ready pages show on the index as
"In progress", without a link.

### 7.5 Tests (`backend/tests/jj_vfs_docs_tests.py`, plus `app_tests.py` additions)

- `/jj-vfs-poc` and every ready slug return 200; unknown or not-ready slugs return 404.
- Every ready page has a template, a non-empty summary and at least one source.
- Every jj-vfs-poc link is pinned to `UPSTREAM.commit`; every jj-lib link is pinned to
  `v<jj_lib_version>`. No `blob/main` links.
- The pin is well-formed: 40 hex chars, ISO dates, semver versions.
- The index includes the architecture SVG with `<title>` and `<desc>` and links to every
  ready page.
- The `fuse` page names every `Filesystem` method in a committed list (`FUSE_OPS` in
  `jj_vfs_docs.py`) that the Routine refreshes from `src/fuse.rs` when it bumps the pin.
- The homepage links to `/jj-vfs-poc`.

## 8. `namespace` deep dive — requirements

The flagship page. It must explain, with source links:

1. **The tree.** The full directory layout of a mounted repository as `AllCommitsPathMapper`
   builds it (the root, `commits/`, `workspaces/`, and anything else at the pinned commit),
   drawn as an SVG tree.
2. **Path resolution.** `get_entry` step by step: how a path is split, which component
   selects which `VirtualFile`, how commit IDs (full or prefix?) and workspace names are
   resolved, and what error each failure returns.
3. **Each directory type.** `StaticDirectory`, `CommitsDirectory`, `WorkspacesDirectory`:
   what `list`, `attributes` and `file_type` return, and how entries are produced.
4. **Repo snapshot semantics.** Which `ReadonlyRepo` (loaded when) every lookup sees, and
   what that means for commits created after mount.
5. **Worked example.** A three-commit repo with two workspaces: the exact paths that appear,
   and the call chain for `cat <mount>/commits/<id>/<file>`, as a sequence diagram.
6. **Limitations** the code makes visible (read-only mount, missing ops, unsupported value
   kinds), each sourced.

## 9. Keeping it current (the daily Routine)

A Routine ("rayaq.ca/jj-vfs-poc — architecture reference agent") runs once a day. Each run:

1. Clones `jj-vcs/jj-vfs-poc` at `HEAD` into scratch space (never into this repo). Clones
   `jj-vcs/jj` at tag `v<jj_lib_version>` too, when a page needs to check a jj-lib API.
2. Compares upstream `HEAD` with `UPSTREAM.commit` and lists the pages whose §5 source sets
   changed, plus any new module.
3. **Build phase**: builds the next item from the queue in `specs/jj-vfs-poc-progress.md`.
   Build order: the scaffold (module, routes, layout, tests, homepage card, `CLAUDE.md`
   notes), `namespace`, the §6 diagram, `vfs-layer`, `fuse`, `inodes`, `commit-trees`,
   `mounting`, `testing`, then any queued additions. The pin isn't bumped while a page is
   half-built.
4. **Maintenance phase** (always once the build is done; before building while it is still
   going): updates every affected page to match the new `HEAD`, refreshes `FUSE_OPS` and the
   jj-lib version, then bumps `UPSTREAM` in the same commit as the content changes. If
   nothing changed, it bumps the pin and dates only.
5. Runs the full test suite and starts the app to check `/jj-vfs-poc` and every page return
   200, then pushes small commits straight to `main` (merge, never rebase, never force).
6. Rewrites `specs/jj-vfs-poc-progress.md`: status, pin, what changed, open gaps, queue.

## 10. Acceptance criteria

- [ ] `/jj-vfs-poc` renders the §6 diagram and links to every page in §5.
- [ ] Every §5 page exists, meets its "Must cover" column, and is registered.
- [ ] `namespace` meets all six §8 items with at least two SVG diagrams; `fuse` has its
      sequence diagram.
- [ ] Every source link is pinned (`UPSTREAM.commit` or `v<jj_lib_version>`).
- [ ] §7.5 tests exist and pass.
- [ ] Homepage card links to `/jj-vfs-poc`.
- [ ] Mobile at 390px: no horizontal page scroll; diagrams scroll inside their container.
- [ ] The daily Routine has run at least once in maintenance mode and either bumped the pin
      or recorded "no relevant upstream change".
