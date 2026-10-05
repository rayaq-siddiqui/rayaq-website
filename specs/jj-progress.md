# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md` (spec v2); this file records where the build actually stands.

**Last updated:** 2026-10-05 (forty-sixth run): no upstream change since `4df5265`; built
`root` and `operation diff`. `operation log` is next.

## Upstream pin

`jj-vcs/jj@4df526513289fdee58eb7e8351c2ff87aac099ff` (committed 2026-10-04, version
0.45.1), analyzed 2026-10-04. Held in `jj_docs.UPSTREAM`. Previous pin: `03db8d1`.

## §10 acceptance criteria

- [x] `/jj` renders the §6 diagram and links to every page in §5 (boxes for unbuilt
      pages link to pinned source until the page exists).
- [x] Every §5 page exists and is registered: `protobufs`, `cli`, `commits`, `view`,
      `operations`, `transactions`, `working-copy`, `trees`, `conflicts`, `storage`, `index`,
      `revsets`, `backends`.
- [x] The `fix` page meets all ten §8 items, with three SVG diagrams.
- [x] The `protobufs` page covers all seven `.proto` files, every field.
- [x] Every source link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass (142 tests in the suite, including the other sections').
- [x] Homepage card links to `/jj`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj` and every ready page
      (checked in headless Chromium).
- [x] The `cli` lifecycle page exists.
- [ ] Every §8A.1 command has a page that meets its tier's bar: 78 of 105: Tier A 65 of 65 (complete),
      Tier B 13 of 27 (`file annotate`/`list`/`search`/`show`, `sparse list`, `log`, `show`, `diff`, `interdiff`, `status`, `evolog`, `root`, `operation diff`), Tier C 0 of 13. Done: `fix`, `new`, `edit`, `describe`, `commit`, `squash`,
      `rebase`, `abandon`, `undo`, `redo`, `restore`, `split`, `absorb`, `duplicate`,
      `bookmark create`/`set`/`move`, `git fetch`, `git push`, `metaedit`, `next`, `prev`,
      `parallelize`, `simplify-parents`, `arrange`, `converge`, `revert`, `diffedit`, `run`,
      `resolve`, `file chmod`/`track`/`untrack`, `sparse edit`/`reset`/`set`, `bisect run`,
      `op abandon`/`integrate`/`restore`/`revert`, `bookmark advance`/`delete`/`forget`/`rename`/
      `track`/`untrack`, `tag delete`/`set`/`track`/`untrack`, `git clone`/`colocation`/`export`/
      `import`/`init`/`remote`, `sign`, `unsign`, `workspace add`/`forget`/`remove`/`rename`/`update-stale`, `gerrit upload`.
- [x] The daily Routine has run in maintenance mode (second and third runs: no change; fourth
      run: pin bumped).

## Thirty-ninth to forty-sixth runs (2026-10-05)

Pin unchanged (`4df5265`). Forty-sixth run: `c38a690`, `root`; `05206c7`, `operation diff`
(merged from-ops, commit classification by predecessors and change ids, elision). Forty-fifth:
`048ddfc`, `status`; `64544ef`, `evolog`. Forty-fourth: `2c09138`, `diff` (`--from`/`--to` vs.
`-r`, merged parents, flow and range SVGs); `b4b1576`, `interdiff`. Forty-third: `44f5c36`,
`show` (format flags, merge-parent tree SVG). Forty-second: `8401046`, `log` (topo-grouped
ordering, edge kinds, elided nodes; two SVGs). Forty-first: `98f13eb`, `file search`;
`1b18f74`, `file show`; `c338d03`, `sparse list`. Fortieth: `e3d0baa`, `file list`.
Thirty-ninth: `72c938f`, `file annotate`, plus a test that every ready Tier B page has all eight
sections (§8A.3 item 5 is `reads`; see deviations).

## Thirty-fourth to thirty-eighth runs (2026-10-04)

Pin unchanged (`4df5265`). Topic pages: `backends` `f862a0b`, `revsets` `7a715c9`, `index` `4c1e053` (template
`jj/commit-index.html`, see deviations), `storage` `3b6b9ff`, `conflicts` `0f9c64e`.
`44cd877`/`4fbf569` linked 16 "page planned" cells to `revsets`/`index` (their bodies cite "§6"
for §8A.3 item 4). `c805986` added `.claude/settings.json` (`autoCompactWindow`), per the owner.

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

## First to twenty-sixth runs (2026-10-02 to 2026-10-04)

- Scaffold `1124529`, spec v2 `39751dc`, `fix` `98a7058`, `protobufs` `5ca3f93`, §6 diagram `46c7640`,
  `COMMANDS` `1d27034`. Topics: `cli` `0c1aa97`, `commits` `99b521c`, `view` `34ed812`, `operations`
  `8b6d256`, `transactions` `04f092e`, `working-copy` `5279499`, `trees` `a760e3f`.
- Maintenance: `0cb02a8..69abfbe` (`2cebd0f`), `69abfbe..55921f5` (`c9c1103`), `55921f5..c16d378`
  (`4ca0bdc`), `c16d378..03db8d1` (`197de77`).
- Command pages `new` through `revert` (see the criteria list); later commits are in `git log`.
- Core types (`CommitId`, `id_type!`, `Signer`, `create_or_reuse_dir`) live in `core/src/`, not
  `lib/src/`, so cite them there.

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
2. Remaining topic pages: ~~`conflicts`~~, ~~`storage`~~, ~~`index`~~, ~~`revsets`~~, ~~`backends`~~.
   All topics done.
3. **Next.** Tier B commands, in registry order: ~~`file annotate`~~, ~~`file list`~~, ~~`file search`~~, ~~`file show`~~,
   ~~`sparse list`~~, ~~`log`~~, ~~`show`~~, ~~`diff`~~, ~~`interdiff`~~, ~~`status`~~, ~~`evolog`~~, ~~`root`~~, ~~`operation diff`~~,
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

- **Tier B section 5.** §8A.2 renames item 5 for read-only commands, so Tier B pages use
  `<h2 id="reads">` ("What it reads, and snapshotting") instead of `transaction`, and need one SVG
  (the flow) rather than two; `test_ready_tier_b_command_pages_cover_every_section` checks this.
- **The `index` page's template.** The slug `index` would map to `jj/index.html`, the `/jj` landing
  page, so a registry entry can set `"template"` (read through `jj_docs.page_template`), and the
  `index` topic uses `jj/commit-index.html`. Its URL is still `/jj/index`, as §5 names it.

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
- **`jj file annotate` on conflicts and merges.** The page explains, from the code, why the
  conflict markers in `test_annotate_conflicted` are credited to the empty child commit: `files()`
  compares a merge with the merge of its parents, so the unresolved merge doesn't count as modifying
  the file. It also says that on a merge the first parent holding a line gets it. Both are read from
  `has_diff_from_parent` and `process_commit` and agree with upstream's snapshots, but weren't run here.
- **`jj file list`/`search`/`show` vs help text.** The positional help says "matching these prefixes",
  but each argument is a full fileset. `file show`'s single-path fast path returns before the
  unmatched-path check, so one missing path is an error but two give a warning. Pages state the code.
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
- On `/jj/fix`, I left out that `fix_files`' `paths.extend(...)` lookup of base commits in
  `commit_paths` appears unable to match (bases are outside the fixed set). The page explains the
  cumulative-diff carry-forward instead. Worth a closer read before stating it publicly.
