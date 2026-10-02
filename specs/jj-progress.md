# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md`; this file records where the build actually stands.

**Last updated:** 2026-10-02 — spec written; nothing built yet.

## Upstream

- Scoping was done against `jj-vcs/jj` at `0cb02a837f28459cd698734264c9fcd3712ec0d1`
  (2026-10-01, version 0.45.1). The first build run should pin to the upstream `HEAD`
  it clones (§7.3), not necessarily this commit.

## Where things stand

Nothing is built. No route, template, registry or test exists yet.

## Queue (build in this order)

1. Scaffold: `backend/jj_docs.py` (pin, registry, link helper, `PROTO_MESSAGES`),
   `/jj` + `/jj/<slug>` routes, `jj/base.html`, `jj.css`, index page with the
   "In progress" page list, §7.5 tests, homepage card.
2. `fix` page (§8): the flagship. It may take several runs.
3. `protobufs` page.
4. Index architecture diagram (§6).
5. `commits`, `trees`, `conflicts`.
6. `operations`, `view`, `transactions`.
7. `storage`, `working-copy`, `index`.
8. `revsets`, `backends`.

## Deliberate deviations

None.

## Open gaps / questions for the owner

None yet.
