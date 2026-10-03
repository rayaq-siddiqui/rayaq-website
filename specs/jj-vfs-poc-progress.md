# rayaq.ca/jj-vfs-poc — build progress

Running log for the daily jj-vfs-poc architecture Routine. Read this first, update it last.
The contract is `specs/jj-vfs-poc.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-03 (first run). Built the scaffold, the `namespace` flagship page
and the §6 architecture diagram.

## Upstream pin

`jj-vcs/jj-vfs-poc@37b8f8625556778f5ce41cbb2d5220bcea245675` (committed 2026-09-03, crate
`jjfsd` 0.1.0, `jj-lib` 0.43.0), analyzed 2026-10-03. Held in `jj_vfs_docs.UPSTREAM`.
jj-lib links point at the `v0.43.0` tag of `jj-vcs/jj`.

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
4. `vfs-layer`
5. `fuse` (needs a sequence diagram for one `read`, §6)
6. `inodes`
7. `commit-trees`
8. `mounting`
9. `testing`

## Deliberate deviations

- **Worked example IDs.** §8 item 5 asks for "the exact paths that appear". The page uses
  placeholders (`<A>`, `<B>`, `<C>`) for the three commits' 40-digit IDs, since any real
  example's IDs depend on author, time and content. The root's all-zero ID is shown exactly.
- **Diagram colours.** As on `/jj`, diagrams use the `--jj-*` variables from `jj.css` (the site
  is dark-only).
- **fuser links.** Claims about `fuser`'s default methods link to docs.rs at the exact crate
  version (0.18.0), since `fuser` isn't covered by either pinned helper.

## Open gaps / questions for the owner

- **Commits created after mounting.** Lookup by ID goes straight to the store, so hidden
  commits that existed at mount time resolve. Whether a commit written *after* mounting resolves
  depends on the Git backend's caches (its extras table and object lookup). The page doesn't
  claim either way.
- **Misnamed upstream test.** `test_all_commit_trees_mapper_invalid_commit_id` exercises the
  unknown-top-level-name path, not commit-ID parsing. The page says so.
