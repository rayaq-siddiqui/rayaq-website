# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md`; this file records where the build actually stands.

**Last updated:** 2026-10-02 — spec v2: every jj command now gets a page (§8A).

## Upstream

- Scoping was done against `jj-vcs/jj` at `0cb02a837f28459cd698734264c9fcd3712ec0d1`
  (2026-10-01, version 0.45.1). The first build run should pin to the upstream `HEAD`
  it clones (§7.3), not necessarily this commit.

## Where things stand

Nothing is built. No route, template, registry or test exists yet.

## Queue (build in this order, per spec §9)

1. Scaffold (registry, pin, routes, layout, tests, homepage card).
2. `fix` page (§8).
3. `protobufs` page.
4. Index architecture diagram (§6).
5. `cli` lifecycle page; add `kind`/`COMMANDS` to the registry (§7.4, §8A.1) and group the
   nav and index into Architecture and Commands.
6. Topic pages that command pages lean on: `commits`, `view`, `operations`,
   `transactions`, `working-copy`.
7. Tier A commands, alternating with the remaining topics (`trees`, `conflicts`,
   `storage`, `index`, `revsets`, `backends`): `new`, `edit`, `describe`, `commit`,
   `squash`, `rebase`, `abandon`, `undo`, then the rest of Tier A.
8. Tier B commands.
9. Tier C commands.

## Deliberate deviations

None.

## Open gaps / questions for the owner

None yet.
