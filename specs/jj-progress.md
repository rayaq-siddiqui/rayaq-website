# rayaq.ca/jj — build progress

Running log for the daily jj architecture Routine. Read this first, update it last.
The contract is `specs/jj.md` (spec v2); this file records where the build actually stands.

**Last updated:** 2026-10-10 (fifty-fourth run): bumped the pin `da1d234..889e5a6` (0.46.0). **The
build is complete: every §8A.1 command and every §5 topic has a page.** Later runs are maintenance only.

## Upstream pin

`jj-vcs/jj@889e5a68fc24f00b9dfa0fe58dc140c9f064f902` (committed 2026-10-10, version
0.46.0), analyzed 2026-10-10. Held in `jj_docs.UPSTREAM`. Previous pin: `da1d234`.

## §10 acceptance criteria

- [x] `/jj` renders the §6 diagram and links to every page in §5 (boxes for unbuilt
      pages link to pinned source until the page exists).
- [x] Every §5 page exists and is registered: `protobufs`, `cli`, `commits`, `view`,
      `operations`, `transactions`, `working-copy`, `trees`, `conflicts`, `storage`, `index`,
      `revsets`, `backends`.
- [x] The `fix` page meets all ten §8 items, with three SVG diagrams.
- [x] The `protobufs` page covers all seven `.proto` files, every field.
- [x] Every source link is pinned to `UPSTREAM.commit` (tested).
- [x] §7.5 tests exist and pass (143 tests in the suite, including the other sections').
- [x] Homepage card links to `/jj`.
- [x] Mobile at 390px: no horizontal page scroll on `/jj` and every ready page
      (checked in headless Chromium).
- [x] The `cli` lifecycle page exists.
- [x] Every §8A.1 command has a page that meets its tier's bar: 107 of 107. Tier A 67 of 67 (the
      spec's 65 plus `file delete`/`edit`), Tier B 27 of 27, Tier C 13 of 13 (`help`, `version`,
      `util completion`/`config-schema`/`exec`/`gc`/`install-man-pages`/`markdown-help`/`snapshot`/
      `diff`/`backend`, `debug`, `bench`). Per-command lists are in the registry and `git log`.
- [x] The daily Routine has run in maintenance mode (second and third runs: no change; fourth
      run: pin bumped; fiftieth to fifty-fourth runs: pin bumped).

## Fifty-fourth run (2026-10-10)

- `b4bc7c5` maintenance `da1d234..889e5a6` (17 commits, a refactor wave). `files.rs` moved to `core/src/`,
  `template_parser.rs`/`template.pest` to `dsl/src/`, `IndexStore` to `lib/src/index_store.rs`, revset and
  fileset backend types to `lib/src/revset_backend.rs` and `core/src/fileset_backend.rs`; page source
  sets now list them. `MergeOptions` is now built by `UserSettings::merge_options`;
  `parent_tree`/`is_empty`/`is_discardable` take an index; `is_hidden` was inlined into the `hidden()`
  template method (`commits`, `show`, `conflicts` updated). `git fetch` now prints "Fetching from Git
  remotes: …" and joins remotes with ", " (`git-fetch` and the `bookmark-forget` snapshot updated).
  About 570 ranges were remapped, and 10 command source lines shifted in the regenerated registry. Protos
  are unchanged. A `gerrit-upload` range that ran one line past EOF was fixed.
- A link check rendered all 121 pages: 5,480 pinned links, every path and range inside the checkout.
  0px overflow at 390px on the changed pages.

## Fifty-third run (2026-10-09)

- `c3d8c40` maintenance `26bcd69..da1d234` (tag-name completion): ranges re-pinned on 10 pages, no prose change.

## Fifty-first and fifty-second runs (2026-10-08)

- `d7ebdbf` maintenance `320f7e6..3935c0f` (release 0.46.0): revset/fileset parsers and grammars moved to
  the new `jj-dsl` crate (`dsl/src/`); `revsets` says so; `git init` help remapped. Held a day by a
  permission denial until the owner allowed pushes to `main`.
- `7eafa56` pin-only `3935c0f..26bcd69` (unused `pest` deps dropped from `lib/Cargo.toml`).

## Fiftieth run (2026-10-06)

- `58584d3` maintenance `4df5265..320f7e6` (17 commits, 49 pages re-pinned). New pages: `39e7fb0`
  `file delete`, `8e737cf` `file edit`, and the Tier C pages (`437a375` through `901d340`).

## Thirty-ninth to forty-ninth runs (2026-10-05 to 2026-10-06)

Pin `4df5265`. Tier B: `72c938f` `file annotate` (plus the Tier B sections test) through `bb0eb21`
`config gc`, ending with `git root`, `workspace list`/`root` and `config *` on the forty-ninth run.

## Twenty-seventh to thirty-eighth runs (2026-10-04)

`d4fc639`: maintenance `03db8d1..4df5265` (shifted config-doc ranges on 5 pages; `git-push`: sign-on-
push signs only *your* commits). Topics `backends` `f862a0b`, `revsets` `7a715c9`, `index` `4c1e053`,
`storage` `3b6b9ff`, `conflicts` `0f9c64e`; `44cd877`/`4fbf569` linked "page planned" cells; `c805986`
added `.claude/settings.json` per the owner. Tier A pages `d12cd80` through `32f055e` (`git log`).

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

## Queue

**Build complete; maintenance mode.** Tier A, the topics, Tier B and Tier C are all done. Each run:
diff upstream against the pin, re-run `gen_commands.py`, and update affected pages (§9). A new
upstream command gets a page at its tier before the run records progress.

To mark a command page ready, add its slug to `COMMAND_PAGE_OVERRIDES` with
`"ready": True` and any extra `sources`.

## Deliberate deviations

- **Colours.** The site is dark-only with hard-coded colours and no CSS variables, so
  `jj.css` defines its own `--jj-*` variables from the site palette, and diagrams use those
  (§6 asks for "the site's colour variables").
- **Templates.** Page templates are fragments rendered into `jj/base.html` instead of
  extending it (§7.2), so `jj_docs.render` can build the on-page table of contents from
  the rendered headings.
- **Size of the maintenance commit.** `58584d3` touched 51 files, over the 10-file guideline,
  because one upstream bump shifted line ranges across 49 pages and the pin must move atomically.
- **Tiers for new commands.** Spec §8A.1 predates `file delete` and `file edit`; both mutate the
  working-copy commit, so they were built to Tier A.
- **Nested subcommands.** `git colocation`, `git remote` and `util backend` each get one
  page covering their own subcommands, and `debug`/`bench` are one group page each, while each `util` subcommand has its own page (§8A.2 allows
  shared pages for Tier C; the first three are a judgment call to keep slugs to two levels).

- **Tier B section 5.** §8A.2 renames item 5 for read-only commands, so Tier B pages use
  `<h2 id="reads">` ("What it reads, and snapshotting") instead of `transaction`, and need one SVG
  (the flow) rather than two; `test_ready_tier_b_command_pages_cover_every_section` checks this.
- **The `index` page's template.** The slug `index` would map to `jj/index.html`, the `/jj` landing
  page, so a registry entry can set `"template"` (read through `jj_docs.page_template`), and the
  `index` topic uses `jj/commit-index.html`. Its URL is still `/jj/index`, as §5 names it.

## Open gaps / questions for the owner

- **`jj util diff --tool`.** `show_diff_bytes` has a TODO and prints nothing for a tool format; the
  page says so rather than describing tool output.
- **`jj debug object` help.** The enum's doc comment, "Show information about an operation and its
  view", covers commits, files, symlinks and trees too; the page quotes it as written.

- **This Routine fires hourly, not daily.** On 2026-10-05/06 roughly eighteen firings of this
  "daily" Routine arrived about an hour apart in one session. Worth checking its schedule.
- **`workspace_store/` location in spec §5.** The spec lists `workspace_store/` directly under `.jj/`,
  but `ReadonlyRepo::init` creates it at `.jj/repo/workspace_store/` (shared by all workspaces). The
  `storage` page describes the code; the spec may want updating.
- **`jj git init --git-repo` help text.** As of 0.46.0 it says the option "is mutually exclusive
  with `--collate`" (meant `--colocate`) and spells "Jujutsa". The page describes the clap
  `conflicts_with_all` list instead of quoting it.
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
