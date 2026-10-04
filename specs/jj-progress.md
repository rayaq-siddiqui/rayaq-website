# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md` (spec v2); this file records where the build actually stands.

**Last updated:** 2026-10-04 (thirty-fifth run): no upstream change since `4df5265`; built the
`storage` topic page. `index`, `revsets` and `backends` come next, then Tier B (spec §9).

## Upstream pin

`jj-vcs/jj@4df526513289fdee58eb7e8351c2ff87aac099ff` (committed 2026-10-04, version
0.45.1), analyzed 2026-10-04. Held in `jj_docs.UPSTREAM`. Previous pin: `03db8d1`.

## §10 acceptance criteria

- [x] `/jj` renders the §6 diagram and links to every page in §5 (boxes for unbuilt
      pages link to pinned source until the page exists).
- [ ] Every §5 page exists and is registered: `protobufs`, `cli`, `commits`, `view`,
      `operations`, `transactions`, `working-copy`, `trees`, `conflicts`, `storage` done; 3 to go
      (`index`, `revsets`, `backends`).
- [x] The `fix` page meets all ten §8 items, with three SVG diagrams.
- [x] The `protobufs` page covers all seven `.proto` files, every field.
- [x] Every source link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass (138 tests in the suite, including the other sections').
- [x] Homepage card links to `/jj`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj` and every ready page
      (checked in headless Chromium).
- [x] The `cli` lifecycle page exists.
- [ ] Every §8A.1 command has a page that meets its tier's bar: 65 of 105, all Tier A (65 of 65, complete;
      Tier B 0 of 27, Tier C 0 of 13). Done: `fix`, `new`, `edit`, `describe`, `commit`, `squash`,
      `rebase`, `abandon`, `undo`, `redo`, `restore`, `split`, `absorb`, `duplicate`,
      `bookmark create`/`set`/`move`, `git fetch`, `git push`, `metaedit`, `next`, `prev`,
      `parallelize`, `simplify-parents`, `arrange`, `converge`, `revert`, `diffedit`, `run`,
      `resolve`, `file chmod`/`track`/`untrack`, `sparse edit`/`reset`/`set`, `bisect run`,
      `op abandon`/`integrate`/`restore`/`revert`, `bookmark advance`/`delete`/`forget`/`rename`/
      `track`/`untrack`, `tag delete`/`set`/`track`/`untrack`, `git clone`/`colocation`/`export`/
      `import`/`init`/`remote`, `sign`, `unsign`, `workspace add`/`forget`/`remove`/`rename`/`update-stale`, `gerrit upload`.
- [x] The daily Routine has run in maintenance mode (second and third runs: no change; fourth
      run: pin bumped).

## Thirty-fourth and thirty-fifth runs (2026-10-04)

Pin unchanged (`4df5265`). `3b6b9ff`: `storage` topic page (every `.jj/` path with owner and format,
linked tree diagram, `type` files and factory dispatch, the `.jj/repo` pointer file, Git backend
`git_target`/`extra/`, content-addressed op store writes, op heads and lock files, index
`segments`/`op_links`/`changed_paths`, `checkout`/`tree_state`). `0f9c64e`: `conflicts` topic page (`Merge<T>`, trivial merge, flatten/simplify,
labels, `tree_merge.rs`, Git/simple storage, materialization and parsing; example from upstream's
`test_materialize_conflict_three_sides`; four diagrams); `resolve` now links to it. The queue had put
Tier B before the remaining topic pages, against §9; fixed below. Separately, at the owner's request,
`c805986` added `.claude/settings.json` (`autoCompactWindow: 200000`).

## Twenty-seventh to thirty-third runs (2026-10-04)

- `d4fc639`: maintenance `03db8d1..4df5265` (signature-only code changes; `docs/config.md` grew 6
  lines, shifting config-doc ranges on 5 pages; fixed `git-push`: sign-on-push signs only *your* commits).
- Pages: `diffedit` `d12cd80`, `run` `71e79fb`, `resolve` `0da010f`, `file chmod` `a199333`,
  `file track`/`untrack` `c473761`, `sparse set`/`edit`/`reset` `81ce853`, `bisect run` `292581a`,
  `op restore`/`revert`/`abandon`/`integrate` `30dcf98`, `bookmark advance` `5c2f4de`, `bookmark
  delete`/`forget` `40fcace`, `bookmark rename`/`track`/`untrack` `b241000`, `tag *` `e4557a0`,
  `git clone` `ca130e3`, `git export`/`import` `5b40048`, `git init` `f3b79f6`, `git remote` `77f4574`,
  `git colocation` `b40cb83`, `sign`/`unsign` `56f3709`, `workspace *` `283ba7c`, `gerrit upload` `32f055e`.
- `create_or_reuse_dir` and `Signer` live in `core/src/` (`file_util.rs`, `signing.rs`).

## Twelfth to twenty-sixth runs (2026-10-03 to 2026-10-04)

- Maintenance: `69abfbe..55921f5` (`c9c1103`), `55921f5..c16d378` (`4ca0bdc`), and `c16d378..03db8d1`
  (`197de77`, pin only; all 72 citations into changed files checked with a diff-based line map).
- Pages: `redo` `261b4f6`, `restore` `86bb02b`, `split` `ffb1b60`, `absorb` `1e58788`, `duplicate`
  `1733c66`, `git fetch` `f8530a8`, `bookmark create`/`set`/`move` `6bf55c1`, `git push` `f156028`,
  `metaedit` `afb1c31`, `next`/`prev` `e62dc52`, `parallelize` `fe97413`, `simplify-parents` `ab334a4`,
  `arrange` `c3348ce`, `converge` `c993b6f` (plus a test that SVG `<title>`/`<desc>` hold no markup),
  `revert` `cd1593a`.

## Fifth to eleventh runs (2026-10-03)

Pin unchanged (`69abfbe`). Pages: `trees` topic `a760e3f`, `edit` `42d2f3d`, `commit` `a25d7eb`,
`describe` `0e29d5e` (plus a test that every ready Tier A page except `fix` has the eight section
anchors and at least two diagrams), `squash` `b95d84e`, `rebase` `6dfaf93`, `abandon` `b859736`,
`undo` `f332523` (example drawn as an operation log). Core types such as `CommitId` and `id_type!`
live in the `core/` crate (`core/src/`), not `lib/src/`, so cite them there.

## Second to fourth runs (2026-10-02 to 2026-10-03)

- Topic pages: `cli` (`0c1aa97`, fix `5b20712`), `commits` (`99b521c`), `view` (`34ed812`),
  `operations` (`8b6d256`), `transactions` (`04f092e`), `working-copy` (`5279499`).
- `2cebd0f`: maintenance `0cb02a8..69abfbe` (undo/redo gained `--allow-cross-workspace`;
  `operations` page and catalogue updated). `bac9988`: `new` command page.

## First run

Scaffold `1124529` (`jj_docs.py` pin/registry/link helper/`PROTO_MESSAGES`, routes, `jj/base.html`,
`jj.css`, homepage card, tests, CLAUDE.md); spec v2 `39751dc` (every command gets a page, §8A);
`fix` `98a7058`; `protobufs` `5ca3f93`; §6 diagram `46c7640`; `COMMANDS` (105 entries) `1d27034`.

## How to maintain the command list

`python3 specs/jj-tools/gen_commands.py <jj checkout>` prints `COMMAND_CATEGORIES` and
`COMMANDS` for `backend/jj_docs.py`. It takes each summary verbatim from the command's
doc comment and pins its source line. It exits non-zero if upstream has a command its
`CATEGORIES` table doesn't list, or the table lists one upstream removed. Add new commands
to that table (category and tier per §8A.2), regenerate, and paste the output over the
existing block. On the fourth run it moved only the `undo` and `redo` source lines.

## Queue (build in this order, per spec §9)

1. Tier A commands, alternating with the remaining topics (`trees`, `conflicts`,
   `storage`, `index`, `revsets`, `backends`): ~~`new`~~, ~~`trees`~~, ~~`edit`~~, ~~`describe`~~, ~~`commit`~~,
   ~~`squash`~~, ~~`rebase`~~, ~~`abandon`~~, ~~`undo`~~, then the rest of Tier A. Next, in this order:
   ~~`redo`~~, ~~`restore`~~, ~~`split`~~, ~~`absorb`~~, ~~`duplicate`~~, ~~`bookmark-create`/`-set`/`-move`~~, ~~`git-fetch`~~,
   ~~`git-push`~~, then the remaining Tier A commands in registry order: ~~`diffedit`~~, ~~`run`~~,
   ~~`resolve`~~, ~~`file-chmod`~~, ~~`file-track`~~, ~~`file-untrack`~~, ~~`sparse-edit`~~,
   ~~`sparse-reset`~~, ~~`sparse-set`~~, ~~`bisect-run`~~, ~~`operation-abandon`~~,
   ~~`operation-integrate`~~, ~~`operation-restore`~~, ~~`operation-revert`~~, ~~`bookmark-advance`~~,
   ~~`bookmark-delete`~~, ~~`bookmark-forget`~~, ~~`bookmark-rename`~~, ~~`bookmark-track`~~,
   ~~`bookmark-untrack`~~, ~~`tag-*`~~, ~~`git-clone`/`-colocation`/`-export`/`-import`/`-init`/
   `-remote`~~, ~~`sign`~~, ~~`unsign`~~, ~~`workspace-*`~~, ~~`gerrit-upload`~~. Tier A complete.
2. Remaining topic pages: ~~`conflicts`~~, ~~`storage`~~, `index`, `revsets`, `backends`. When `index` and
   `revsets` ship, link them from the `bookmark set`/`move` touchpoint tables (see gaps).
3. Tier B commands, in registry order: `file annotate`, `file list`, `file search`, `file show`,
   `sparse list`, `log`, `show`, `diff`, `interdiff`, `status`, `evolog`, `root`, `operation diff`,
   `operation log`, `operation show`, `bookmark list`, `tag list`, `git root`, `workspace list`,
   `workspace root`, `config edit`/`gc`/`get`/`list`/`path`/`set`/`unset`.
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

- **`workspace_store/` location in spec §5.** The spec lists `workspace_store/` directly under `.jj/`,
  but `ReadonlyRepo::init` creates it at `.jj/repo/workspace_store/` (shared by all workspaces). The
  `storage` page describes the code; the spec may want updating.
- **`jj gerrit upload` help text vs code.** `--remote` says it "can be a full SSH URL", but only
  configured remote names work; `--merged` is parsed but never sent. The page describes the code.
- **`jj git remote` doc string.** `RemoteCommand`'s doc comment says "The Git repo will be a bare git
  repo stored inside the `.jj/` directory", which is only true for non-colocated workspaces (the
  default is colocated). The page says so.
- **`jj bisect run` help text vs code.** The `COMMAND` help says each revision "will be directly
  edited (will become the current working copy)", but `evaluate_commit` calls `tx.check_out`, which
  creates a new empty commit on top of the revision, as upstream's own test output shows. The page
  describes the code.
- **`jj file track` couldn't be run.** The page's claim that the working-copy commit changes only at
  the next command comes from the code (the command never rewrites `@`) and upstream's
  `test_track_ignored`, whose `Rebased … onto updated working copy` appears on the following
  `jj file list`. No jj binary could be built or downloaded here to confirm it in an op log.
- **`jj run` new-file size limit.** Slots snapshot with `max_new_file_size: 64_000_u64`, next to a
  comment saying "64 MB for now"; 64,000 bytes is about 64 kB, so larger new files a command creates
  stay untracked. The page states the value in the code and notes the comment.
- **`jj converge` base-commit comment.** A source comment in `lib/src/converge.rs` says the tree
  merge base F is "any of those producer commits (we pick the first one)", but
  `get_value_producer` picks by change offset, then input order, then committer time, then ID. The
  page describes the code.
- **`jj arrange` worked example.** The interactive UI can't be driven from upstream's CLI tests, so
  the page's example is a unit test of the plan executor (`test_execute_plan_abandon`), not a
  user-level session. A recorded TUI session would be a better example if upstream adds one.
- **`jj next 0`.** Without `--edit`, `next` computes `descendants_at(offset - 1)` on a `u64`, so an
  offset of 0 would underflow. No upstream test covers it and it couldn't be run here (toolchain), so
  the page doesn't describe it.
- **`jj git push` help text vs code.** The command's help says "There is no option to push to
  multiple remotes", but `--remote` is repeatable, takes patterns, and the code pushes to every
  matching remote (and `git.push` accepts a list). The page describes the code.
- **Links to unbuilt topics.** The `bookmark set`/`move` touchpoint tables name the `index` and
  `revsets` topics as plain text ("page planned"), because a link to an unready page fails
  `test_every_internal_jj_link_resolves`. Link them when those topic pages ship.
- **`jj split` help text vs code.** The help text says splitting an empty commit "is not supported",
  but the code has no such check, and upstream's `test_split_empty` splits one successfully. The page
  states both.
- **Worked example for `undo`.** No commits change, so the page draws the *operation log* from
  `test_jump_over_old_undo_stack` instead (§8A.3 item 8). Same for `redo` and the `op` commands.
- **`jj undo` with unrecorded edits.** From the code, the snapshot taken on load is committed as its
  own operation before `undo` reads the current operation, so that snapshot is what gets undone.
  The page states only this. It couldn't be run, because the pinned jj needs rustc 1.97.1 and the
  sandbox has an older toolchain.
- **Monospace text in diagrams.** Several `/jj` diagrams set `font-family="monospace"` on SVG
  text, but `jj.css`'s `.jj-diagram svg text` rule overrides presentation attributes, so that
  text renders in the sans font. It's cosmetic only. A small `jj.css` class (as `/jj-commit-cloud-poc`
  now uses) would fix it in a later run.
- **`jj commit` and immutability.** `cmd_commit` makes no `check_rewritable` call of its own,
  unlike `describe`. The page states only that, without claiming what happens if `@` is
  immutable, since that wasn't traced.
- On `/jj/fix`, I chose not to mention that `fix_files`' `paths.extend(...)` lookup of
  base commits in `commit_paths` appears unable to match: base commits are by definition
  outside the fixed set, and `commit_paths` only holds commits inside it. The page explains
  the actual carry-forward mechanism (the cumulative diff against out-of-set bases)
  instead. Worth a closer read before stating it publicly.
