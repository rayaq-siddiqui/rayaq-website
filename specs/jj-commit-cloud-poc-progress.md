# rayaq.ca/jj-commit-cloud-poc — build progress

Running log for the daily jj-commit-cloud-poc architecture Routine. Read this first, update it last.
The contract is `specs/jj-commit-cloud-poc.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-03 (second run). Upstream unchanged since the pin; built the
`object-ids` flagship page.

## Upstream pin

`jj-vcs/jj-commit-cloud-poc@4b1c77b9db365e426e49846669a1626698fd5fa6` (committed 2026-09-01,
`jj-lib`/`jj-cli` 0.43.0), analyzed 2026-10-03. Held in `jj_cloud_docs.UPSTREAM`. jj links point
at the `v0.43.0` tag of `jj-vcs/jj`.

## Second run (2026-10-03)

| Commit | What |
|---|---|
| `d67c1dd` | `object-ids` page (§8): ID table, Git blob/tree/commit preimages, operation and view encodings, client agreement, worked example, `GitBackend` comparison, edge cases; three SVGs |

Maintenance: upstream `HEAD` still at `4b1c77b`, so the pin stayed.

The worked example's IDs come from a scratch crate that makes the same `gix` 0.68.0 calls as
`hash_utils.rs` (the server itself wasn't built, since `protoc` isn't available), and were
checked with `git hash-object`. The `GitBackend` comparison ID used jj's reverse-hex
`change-id` value in the same preimage. The operation and view collisions were found and
checked with a byte-for-byte Python reimplementation of `hash_operation` and `hash_view`.
Redo all of this if the pin moves and `hash_utils.rs` changes.

## First run (2026-10-03)

| Commit | What |
|---|---|
| `a0dd969` | Scaffold: `jj_cloud_docs.py` (pin, registry, `PROTO_ITEMS` with 60 entries, `source_url`, `jj_lib_url`), `/jj-commit-cloud-poc` + `/jj-commit-cloud-poc/<slug>`, `jj_cloud/` layout and index, `jj_cloud.css`, §7.5 tests, homepage card, `CLAUDE.md` |
| `c6a34cf` | `protobufs` page: codegen and constants, both services RPC by RPC, all 43 messages field by field, what the wire loses |
| `7204579` | §6 diagram, component tour, crate map, status and limitations on the index |

The `protobufs` field tables were generated from the `.proto` files by a scratch script that
parses every message and field with its line number, and fails if a field has no description.
Regenerate the same way when the schemas change, so names, numbers and line links stay exact.

## Queue

1. ~~Scaffold~~
2. ~~`protobufs`~~
3. ~~§6 architecture diagram on the index~~
4. ~~`object-ids` (flagship, §8)~~
5. `client-backend`
6. `client-op-store`
7. `server`
8. `storage`
9. `cli` (needs a sequence diagram of a command's writes crossing the wire)
10. `testing`

## Deliberate deviations

- **Diagram colours.** As on `/jj`, diagrams use the `--jj-*` variables from `jj.css` (the site
  is dark-only).
- **Table column for services.** §7.2's field-table columns are used for every message. The
  two service tables use RPC · Request · Response · Client caller · Server handler instead,
  since RPCs have no field numbers or jj-lib types.
- **"Why that encoding avoids ambiguity" (§8 item 3).** It only partly does. The page explains
  what the length prefixes prevent (field-boundary collisions), then shows, with verified
  examples, the collisions they don't prevent, rather than claiming the encoding is unambiguous.
- **`/jj/backends` link (§8 item 6).** That `/jj` page isn't built yet, so the link falls back to
  `/jj` until it is marked ready (the templates now get `jj_ready_slugs`). The comparison itself
  links jj-lib's `git_backend.rs` at `v0.43.0` directly.

## Open gaps / questions for the owner

- **No authentication, and client-supplied commit IDs.** `WriteCommit` stores a commit under the
  ID in the request when one is present, without checking it. The stock client always sends an
  empty ID. The index and `object-ids` say so plainly; still to cover on the `server` page.
- **Commit IDs ignore jj-only fields.** The commit hash covers only the first tree term, and leaves
  out predecessors, conflict labels, signatures and sub-second time. Two different jj commits can
  share an ID, and the memory store's insert silently replaces the first. jj's `GitBackend`
  detects this and nudges the committer time instead.
- **`change-id` header differs from `GitBackend`.** The cloud writes the change ID's bytes
  reversed as plain hex, while jj writes them in order in its `z`–`k` alphabet. So no commit ID
  matches what `GitBackend` would produce, though file and tree IDs do. Possibly unintended.
- **Operation and view encodings aren't injective.** There are no counts and no presence flag for
  `workspace_name`, and `commit_predecessors_set` isn't hashed. The page shows two verified
  collisions; both need unusual inputs.
- **`StoreFactories::empty()`.** The custom `jj` binary registers only the commit-cloud stores,
  so it can't open ordinary repositories. The index states this from the code. It hasn't been run.
