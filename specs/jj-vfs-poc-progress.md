# rayaq.ca/jj-vfs-poc — build progress

Running log for the daily jj-vfs-poc architecture Routine. Read this first, update it last.
The contract is `specs/jj-vfs-poc.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-05 (fourth run). Upstream unchanged since the pin; built the
last four pages (`inodes`, `commit-trees`, `mounting`, `testing`), so every §5 page is live.
From the next run on, the Routine is in maintenance mode only.

## Upstream pin

`jj-vcs/jj-vfs-poc@37b8f8625556778f5ce41cbb2d5220bcea245675` (committed 2026-09-03, crate
`jjfsd` 0.1.0, `jj-lib` 0.43.0), analyzed 2026-10-03. Held in `jj_vfs_docs.UPSTREAM`.
jj-lib links point at the `v0.43.0` tag of `jj-vcs/jj`.

## §10 acceptance criteria

- [x] `/jj-vfs-poc` renders the §6 diagram and links to every page in §5 (boxes for unbuilt
      pages link to pinned source until the page exists).
- [x] Every §5 page exists, meets its "Must cover" column, and is registered (all seven
      ready as of the fourth run).
- [x] `namespace` meets all six §8 items with at least two SVG diagrams; `fuse` has its sequence
      diagram.
- [x] Every source link is pinned (`UPSTREAM.commit` or `v<jj_lib_version>`; tested).
- [x] §7.5 tests exist and pass (142 tests in the suite, all sections).
- [x] Homepage card links to `/jj-vfs-poc`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj-vfs-poc` and every ready page (checked
      in headless Chromium this run).
- [x] The daily Routine has run in maintenance mode (second and third runs: no relevant upstream
      change).

## Fourth run (2026-10-05)

| Commit | What |
|---|---|
| `a277e85` | `inodes` page: `InodeMap`, inode allocation and path resolution, its locking, and what it never forgets |
| `14c61ac` | `commit-trees` page: `CommitTreeFile`, how each tree value kind is shown, conflicts, and streamed reads |
| `1b7a76c` | `mounting` page: `main.rs` step by step, mount options, repo loading, `spawn_mount` internals, threads diagram, shutdown |
| `a425e51` | `testing` page: `setup_test_repo`, unit tests per module, both integration tests, CI jobs, rustfmt, coverage diagram |

Maintenance: upstream `HEAD` still at `37b8f86`, so the pin stayed. Upstream's own suite
(`cargo test --all-targets`) was run at the pin in a scratch clone: 30 unit and 2 integration
tests pass, including the mounted `test_vfs_mount` (this container has FUSE).

## Third run (2026-10-04)

| Commit | What |
|---|---|
| `d4de924` | `fuse` page: `JjFuse`, the six implemented methods, the `fuser` defaults for the rest, the `reply_async!` bridge, a sequence diagram of one `read`, `FileAttr` field by field, `FileType`, and the errno table |

Maintenance: upstream `HEAD` still at `37b8f86`, so the pin stayed. The `fuser` defaults were read
from the `fuser` 0.18.0 crate source and link to it on docs.rs, like `namespace` does.

## Second run (2026-10-03)

| Commit | What |
|---|---|
| `8f5ba16` | `vfs-layer` page: the three traits, the four implementors, the data types, `PathMappedVfs` and how reads at an offset are served, the unit tests |

Maintenance: upstream `HEAD` still at `37b8f86`, so the pin stayed.

## First run (2026-10-03)

| Commit | What |
|---|---|
| `87f0491` | Scaffold: `jj_vfs_docs.py` (pin, registry, `FUSE_OPS`, `source_url`, `jj_lib_url`), `/jj-vfs-poc` + `/jj-vfs-poc/<slug>`, `jj_vfs/` layout and index, `jj_vfs.css`, §7.5 tests, homepage card, `CLAUDE.md` |
| `0f8f364` | `namespace` page (§8): tree SVG, path resolution, directory types, snapshot semantics, worked example with sequence diagram, limitations |
| `64abea0` | §6 diagram, layer tour, module map, dependency table, status and limitations on the index |

The commit-ID error behaviour on `namespace` was checked by running the pinned code
(`cargo test` in a scratch clone, with a temporary probe test that was then reverted). With a
Git-backed repo, a prefix fails with `InvalidHashLength` and an unknown full ID with
`ObjectNotFound`, and both reach the user as `EIO`. Non-hex or odd-length names fail with
`NotFound` (`ENOENT`). `commits/` lists newest first with the root last. The upstream test helper
uses the local backend (128-hex IDs), where a prefix gives `ObjectNotFound` instead.

## Queue

1. ~~Scaffold~~
2. ~~`namespace` (flagship, §8)~~
3. ~~§6 architecture diagram on the index~~
4. ~~`vfs-layer`~~
5. ~~`fuse`~~
6. ~~`inodes`~~
7. ~~`commit-trees`~~
8. ~~`mounting`~~
9. ~~`testing`~~

The queue is empty. Later runs diff upstream against the pin and update affected pages.

## Deliberate deviations

- **Worked example IDs.** §8 item 5 asks for "the exact paths that appear". The page uses
  placeholders (`<A>`, `<B>`, `<C>`) for the three commits' 40-digit IDs, since any real
  example's IDs depend on author, time and content. The root's all-zero ID is shown exactly.
- **Diagram colours.** As on `/jj`, diagrams use the `--jj-*` variables from `jj.css` (the site
  is dark-only).
- **fuser links.** Claims about `fuser`'s default methods link to docs.rs at the exact crate
  version (0.18.0), since `fuser` isn't covered by either pinned helper.

## Open gaps / questions for the owner

- **`InvalidPath` reports `EIO`.** The errno mapping's fallback arm sends `InvalidPath` (a
  non-UTF-8 name in `lookup`) to `EIO`, not `ENOENT` or `EINVAL`, and discards a wrapped
  `io::Error`'s own errno. The `fuse` page states this as the code does. It may be unintended.
- **`readdir` re-lists every batch.** Each `readdir` call lists the whole directory and then skips
  to the offset, so a large directory read in several batches is listed several times. The page
  states this. It wasn't measured.

- **Commits created after mounting.** Lookup by ID goes straight to the store, so hidden
  commits that existed at mount time resolve. Whether a commit written *after* mounting resolves
  depends on the Git backend's caches (its extras table and object lookup). The page doesn't
  claim either way.
- **Misnamed upstream test.** `test_all_commit_trees_mapper_invalid_commit_id` exercises the
  unknown-top-level-name path, not commit-ID parsing. `namespace` and `testing` say so.
- **Conflicted tree root gives `EIO` (derived).** `commit-trees` derives this from the code
  path rather than from a run with a conflicted commit.
- **Entry types in conflicted directories.** How listing types a path whose value is
  conflicted was read from the code, not exercised. The page keeps to what the code shows.
- **Executable bit dropped.** Files never report an executable mode. The page states it as a
  PoC limitation.
- **Submodules give `EISDIR`.** A git submodule entry is not readable as a file or directory.
  The page states it as the code does.
- **`load_at_head` can write an operation.** If the op heads have diverged, jj-lib merges them
  and writes the merged operation without publishing it, so starting `jjfsd` is not strictly
  read-only on the repo store. `mounting` says so.
- **Mounted test on CI unverified.** `test_vfs_mount` needs `/dev/fuse` and mount permission.
  `ci.yml` installs nothing for FUSE, and whether GitHub's hosted runners allow the mount
  wasn't checked. It passes locally here.
- **CI only on PRs and merge groups.** `ci.yml` has no `push` trigger, so direct pushes to the
  default branch are never checked. `testing` states it.
