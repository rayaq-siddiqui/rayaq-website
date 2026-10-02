# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md` (spec v2); this file records where the build actually stands.

**Last updated:** 2026-10-02 (second run) — maintenance found no upstream change; built the
`cli`, `commits` and `view` pages.

## Upstream pin

`jj-vcs/jj@0cb02a837f28459cd698734264c9fcd3712ec0d1` (committed 2026-10-01, version
0.45.1), analyzed 2026-10-02. Held in `jj_docs.UPSTREAM`. The second run's maintenance check
found upstream `HEAD` still at the pin, so nothing changed and the pin stayed.

## §10 acceptance criteria

- [x] `/jj` renders the §6 diagram and links to every page in §5 (boxes for unbuilt
      pages link to pinned source until the page exists).
- [ ] Every §5 page exists and is registered: `protobufs`, `cli`, `commits`, `view` done;
      9 to go (`operations`, `transactions`, `working-copy`, `trees`, `conflicts`,
      `storage`, `index`, `revsets`, `backends`).
- [x] The `fix` page meets all ten §8 items, with three SVG diagrams.
- [x] The `protobufs` page covers all seven `.proto` files, every field.
- [x] Every source link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass (75 tests in the suite).
- [x] Homepage card links to `/jj`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj` and every ready page
      (checked in headless Chromium).
- [x] The `cli` lifecycle page exists.
- [ ] Every §8A.1 command has a page that meets its tier's bar: 1 of 105 (`fix`).
- [x] The daily Routine has run once in maintenance mode (second run: no upstream change).

## Second run (2026-10-02)

| Commit | What |
|---|---|
| `0c1aa97` | `cli` page: startup and config, dispatch, loading and op-head merging, snapshot and stale working copies, transactions, finish/write/publish, global flags, exit codes |
| `99b521c` | `commits` page: stored and in-memory commits, commit vs change IDs, root commit, `CommitBuilder`, predecessors, signing |
| `34ed812` | `view` page: `View` fields, `RefTarget` conflicts and merging, remote refs and tracking, `view::View` rules, merging views |

## First run

| Commit | What |
|---|---|
| `1124529` | Scaffold: `jj_docs.py` (pin, registry, pinned-link helper, `PROTO_MESSAGES`), `/jj` + `/jj/<slug>`, `jj/base.html`, `jj.css`, homepage card, tests, CLAUDE.md |
| `39751dc` | Spec v2 (owner request): every command gets a page (§8A) |
| `98a7058` | `fix` page (§8) |
| `5ca3f93` | `protobufs` page; header renders before the on-page TOC |
| `46c7640` | §6 architecture diagram on `/jj` |
| `1d27034` | `COMMANDS` (105 entries from upstream clap definitions), `kind`/`category`/`tier`, `cli` topic stub, grouped nav and index |

## How to maintain the command list

`python3 specs/jj-tools/gen_commands.py <jj checkout>` prints `COMMAND_CATEGORIES` and
`COMMANDS` for `backend/jj_docs.py`. It takes each summary verbatim from the command's
doc comment and pins its source line. It exits non-zero if upstream has a command its
`CATEGORIES` table doesn't list, or the table lists one upstream removed. Add new commands
to that table (category and tier per §8A.2), regenerate, and paste the output over the
existing block. On this run its output matched the committed block exactly.

## Queue (build in this order, per spec §9)

1. Remaining topic pages that command pages lean on: `operations`, `transactions`,
   `working-copy`.
2. Tier A commands, alternating with the remaining topics (`trees`, `conflicts`,
   `storage`, `index`, `revsets`, `backends`): `new`, `edit`, `describe`, `commit`,
   `squash`, `rebase`, `abandon`, `undo`, then the rest of Tier A.
3. Tier B commands.
4. Tier C commands (`debug` and `bench` each as one shared page).

To mark a command page ready, add its slug to `COMMAND_PAGE_OVERRIDES` with
`"ready": True` and any extra `sources`.

## Deliberate deviations

- **Colours.** The site is dark-only with hard-coded colours and no CSS variables, so
  `jj.css` defines its own `--jj-*` variables from the site palette, and diagrams use those
  (§6 asks for "the site's colour variables").
- **Templates.** Page templates are fragments rendered into `jj/base.html` instead of
  extending it (§7.2), so `jj_docs.render` can build the on-page table of contents from
  the rendered headings.
- **Nested subcommands.** `git colocation`, `git remote` and `util backend` each get one
  page covering their own subcommands, and `debug`/`bench` are one page each (§8A.2 allows
  shared pages for Tier C; the first three are a judgment call to keep slugs to two levels).

## Open gaps / questions for the owner

- On `/jj/fix`, I chose not to mention that `fix_files`' `paths.extend(...)` lookup of
  base commits in `commit_paths` appears unable to match: base commits are by definition
  outside the fixed set, and `commit_paths` only holds commits inside it. The page explains
  the actual carry-forward mechanism (the cumulative diff against out-of-set bases)
  instead. Worth a closer read before stating it publicly.
