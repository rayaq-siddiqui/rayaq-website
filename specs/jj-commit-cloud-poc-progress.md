# rayaq.ca/jj-commit-cloud-poc — build progress

Running log for the daily jj-commit-cloud-poc architecture Routine. Read this first, update it last.
The contract is `specs/jj-commit-cloud-poc.md` (spec v1); this file records where the build actually stands.

**Last updated:** 2026-10-03 (first run). Built the scaffold, the `protobufs` page and the §6
architecture diagram.

## Upstream pin

`jj-vcs/jj-commit-cloud-poc@4b1c77b9db365e426e49846669a1626698fd5fa6` (committed 2026-09-01,
`jj-lib`/`jj-cli` 0.43.0), analyzed 2026-10-03. Held in `jj_cloud_docs.UPSTREAM`. jj links point
at the `v0.43.0` tag of `jj-vcs/jj`.

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
4. `object-ids` (flagship, §8; needs at least two diagrams)
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

## Open gaps / questions for the owner

- **No authentication, and client-supplied commit IDs.** `WriteCommit` stores a commit under the
  ID in the request when one is present, without checking it. The stock client always sends an
  empty ID. The index says so plainly. Worth a closer look on the `object-ids` and `server` pages.
- **`StoreFactories::empty()`.** The custom `jj` binary registers only the commit-cloud stores,
  so it can't open ordinary repositories. The index states this from the code. It hasn't been run.
