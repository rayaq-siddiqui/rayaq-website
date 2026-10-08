# AGENTS.md

This file provides shared guidance to Claude Code, Codex, and other coding agents when working with code in this repository.

## What this is

`rayaq.ca` — a personal website. Flask backend, server-rendered HTML frontend (no JS framework, no build step). Deployed on a single GCP VM behind Caddy, with GitHub Actions handling CI (tests) and CD (deploy).

## Architecture

```
backend/            Flask app (Python) — all server-side logic
  app.py            Route definitions only. Keep business logic out of here.
  weather.py        Open-Meteo API client + in-memory cache for the /weather page
  resume_data.py    Plain Python data (dicts/lists) that _resume.html renders — this
                     is the single source of truth for resume content, not the template
  static_assets.py  Appends ?v=<mtime> to static URLs so they can be cached for a year
  rendered_pages.py Keeps each /jj* reference page's HTML after its first render; pages only
                     change on a deploy, which restarts the process
  jj_docs.py        The /jj section: upstream pin, page registry, pinned source-link
                     helper, protobuf message list, and page rendering (see "jj" below)
  jj_dojo_docs.py   The /jj-dojo section: the same shape for the Jujutsu Dojo VS Code
                     extension (see "jj-dojo" below)
  jj_vfs_docs.py    The /jj-vfs-poc section: the same shape for the jj-vfs-poc FUSE file
                     system, plus a jj-lib link helper and the FUSE op list (see "jj-vfs-poc" below)
  jj_cloud_docs.py  The /jj-commit-cloud-poc section: the same shape for the commit cloud,
                     with the protobuf item list (see "jj-commit-cloud-poc" below)
  ml_models_docs.py The /ml-models section: PyTorch/scikit-learn/XGBoost release pins, areas,
                     page registry, learning path, pinned source-link helpers, and page
                     rendering (see "ml-models" below)
  leetcode_docs.py  The /leetcode section: problem lists, areas, page registry, learning path,
                     the PROBLEMS table (every Blind 75 / Grind 169 / NeetCode 150 / NeetCode 250 problem and
                     its home page), coverage, and page rendering (see "leetcode" below)
  requirements.txt       Runtime deps
  requirements-dev.txt   Runtime + pytest, for local dev / CI
  pytest.ini         Configures pytest to discover *_tests.py (not the pytest default
                     test_*.py — this project intentionally uses the *_tests.py suffix)
  tests/
    conftest.py      Adds backend/ to sys.path so tests can `import app`, `import weather`
    app_tests.py     Route-level tests (Flask test client), weather calls are monkeypatched
    weather_tests.py Tests for weather.py logic, with requests calls monkeypatched — no
                     real network calls in the test suite
    rendered_pages_tests.py Tests the page cache and that each /jj* page renders once
    jj_docs_tests.py Tests the jj registry, pin, pinned links, and every /jj page
    jj_dojo_docs_tests.py Same checks for /jj-dojo
    jj_vfs_docs_tests.py  Same checks for /jj-vfs-poc, plus jj-lib link pinning
    jj_cloud_docs_tests.py Same checks for /jj-commit-cloud-poc
    ml_models_docs_tests.py Same checks for /ml-models, plus the spec inventory, learning
                     path, page format, build-queue order, and that no ML package
                     becomes a server dependency
    leetcode_docs_tests.py Same checks for /leetcode, plus the PROBLEMS table, list sizes,
                     build-queue order and marks, and the page format

specs/
  jj.md               The rayaq.ca/jj product & technical spec — the contract the
                      section is held to. Don't edit without the owner's say-so.
  jj-progress.md      Running status of that build: queue, pin, deviations, gaps.
  jj-dojo.md / jj-dojo-progress.md   The same pair for /jj-dojo.
  jj-vfs-poc.md / jj-vfs-poc-progress.md   The same pair for /jj-vfs-poc.
  jj-commit-cloud-poc.md / jj-commit-cloud-poc-progress.md   The same pair for
                      /jj-commit-cloud-poc.
  ml-models.md / ml-models-progress.md   The same pair for /ml-models.
  leetcode.md / leetcode-progress.md   The same pair for /leetcode.

frontend/
  templates/         Jinja2 templates. One per route: home.html, weather.html,
                     resume.html; _resume.html holds the resume sections that
                     resume.html includes; jj/ holds the /jj layout
                     (base.html), index.html, and one fragment per /jj/<slug> page;
                     jj_dojo/, jj_vfs/ and jj_cloud/ are the same for /jj-dojo,
                     /jj-vfs-poc and /jj-commit-cloud-poc; ml_models/ and leetcode/
                     are the same for /ml-models and /leetcode
  static/            style.css (shared/global, plus the light/dark `--site-*` tokens and
                     homepage and /weather styles for pages with `<body class="site">`), resume.css, jj.css, jj_dojo.css,
                     jj_vfs.css, jj_cloud.css, ml_models.css, leetcode.css,
                     ml_models.js (optional step-through for /ml-models figures),
                     script.js (weather chart only)

deploy/
  Caddyfile           Reverse proxy config — proxies rayaq.ca/www.rayaq.ca to
                      localhost:8000, auto-provisions HTTPS via Let's Encrypt
  rayaq-website.service   systemd unit that runs gunicorn from backend/venv

.github/workflows/ci-cd.yml   GitHub Actions: test job (every push/PR) + deploy job
                               (push to main only, after tests pass)
.github/CODEOWNERS            Makes the owner the required reviewer for every path

vmrun.sh            Convenience wrapper: `./vmrun.sh '<command>'` runs a single command
                    on the production VM over SSH. Use this instead of writing raw
                    `gcloud compute ssh` invocations — keeps commands short and auditable.
```

### Routes

| Route | Purpose |
|---|---|
| `/` | Homepage — name, headline and links (Resume first), a short "About me" intro, then "Fun projects" (a grid linking every section) |
| `/weather` | Live weather dashboard for 4 fixed cities, click a card for an hourly chart |
| `/resume` | Resume page, linked from the top of the homepage |
| `/jj` | jj architecture reference: overview, big diagram, index of deep-dive pages |
| `/jj/<slug>` | One deep-dive page per topic in `jj_docs.PAGES` that is marked ready; 404 otherwise |
| `/jj-dojo` | jj-dojo (VS Code extension) architecture reference: overview and page index |
| `/jj-dojo/<slug>` | One deep-dive page per topic in `jj_dojo_docs.PAGES` that is marked ready; 404 otherwise |
| `/jj-vfs-poc` | jj-vfs-poc (FUSE file system) architecture reference: overview and page index |
| `/jj-vfs-poc/<slug>` | One deep-dive page per topic in `jj_vfs_docs.PAGES` that is marked ready; 404 otherwise |
| `/jj-commit-cloud-poc` | jj-commit-cloud-poc (gRPC commit cloud) architecture reference: overview and page index |
| `/jj-commit-cloud-poc/<slug>` | One deep-dive page per topic in `jj_cloud_docs.PAGES` that is marked ready; 404 otherwise |
| `/ml-models` | Machine learning reference (math to systems, beginner to expert): learning path, area map, vocabulary, pages by area |
| `/ml-models/<slug>` | One deep-dive page per topic in `ml_models_docs.PAGES` that is marked ready; 404 otherwise |
| `/leetcode` | LeetCode interview patterns reference: list coverage, learning path, pages by NeetCode roadmap topic |
| `/leetcode/<slug>` | One pattern page per topic in `leetcode_docs.PAGES` that is marked ready; 404 otherwise |
| `/health` | Returns `{"status": "ok"}`, 200. Used to verify a deploy actually succeeded. |

## Local development

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/python3 app.py          # serves on http://127.0.0.1:8000
```

Kill anything already bound to port 8000 before starting: `lsof -ti:8000 | xargs -r kill -9`.

## Testing

```bash
cd backend
./venv/bin/pytest -v
```

- Test files are named `*_tests.py` (not `test_*.py`) — this is configured in `pytest.ini`, don't "fix" it to match pytest's default.
- Never let a test hit the real network. `weather.py`'s `_fetch_weather` and `app.py`'s `get_weather_for_cities` are always monkeypatched in tests — follow that pattern for any new external calls.
- Write a test for every new route and every new piece of logic in `weather.py`/`resume_data.py`-adjacent code before considering a feature done. This project treats the test suite as the regression safety net for a site with no manual QA process.

## CI/CD

Single workflow: `.github/workflows/ci-cd.yml`.

- **`test` job** — runs on every push and PR to `main`. Installs `requirements-dev.txt`, runs `pytest -v` from `backend/`.
- **`deploy` job** — runs only on `push` to `main`, and only `needs: test` (won't run if tests fail). SSHs into the VM using the `VM_HOST`/`VM_USER`/`VM_SSH_KEY` repo secrets, then: `git pull`, reinstall `backend/requirements.txt`, `sudo systemctl restart rayaq-website`.

**In practice: `git push` to `main` *is* the release process.** No manual deploy steps needed for a normal change.

### Branch protection

`main` requires a PR + 1 approval + passing `test` check — for everyone except the repo admin (owner), who can still push directly (`enforce_admins: false`). This is intentional: it protects against accidental force-pushes/bad merges from any future collaborator while keeping the owner's fast workflow.

### Deploy credentials

CI deploys using a **dedicated SSH keypair** (not the owner's personal key), scoped only to this purpose:
- Private key lives only in the `VM_SSH_KEY` GitHub Actions secret.
- Public key is appended to `~/.ssh/authorized_keys` on the VM for user `rayaq`.
- To revoke CI's deploy access without touching the owner's own SSH access: remove that line from `authorized_keys` on the VM and delete the `VM_SSH_KEY` secret.

## Production infrastructure

- **Host**: GCP `e2-micro` VM, project `rayaq-website`, zone `us-central1-a`, instance name `rayaq-server`, static IP reserved (not ephemeral).
- **App**: gunicorn running `app:app`, bound to `127.0.0.1:8000`, managed by systemd (`rayaq-website.service`) — auto-restarts on crash/reboot.
- **Reverse proxy**: Caddy, auto-HTTPS via Let's Encrypt, config at `/etc/caddy/Caddyfile` (mirrored in `deploy/Caddyfile` in this repo — if you edit the Caddyfile, copy it into place on the VM and `sudo systemctl restart caddy`, same pattern as the systemd unit).
- **DNS**: `rayaq.ca` and `www.rayaq.ca` A records point at the VM's static IP, managed at GoDaddy (outside this repo).

### Manual VM access (only needed for infra changes CI/CD doesn't cover, e.g. installing a new system package)

```bash
./vmrun.sh 'whatever single command you need'
```

Each call is one command over SSH — deliberately kept to single, auditable commands rather than chained scripts, so changes to the production VM stay reviewable.

## Feature-specific notes

- **Cost optimization**: a weekly Routine looks for measurable savings in the application code (not server config) and logs each run in `docs/COST_OPTIMIZATION.md`.
- **Weather** (`weather.py`): Open-Meteo API, no API key required. Results are cached in-process per city for 1 hour (`_CACHE_TTL_SECONDS`) to avoid hammering the API — this is a lazy/on-demand cache (only refetches on a request after the TTL expires), not a background poller. Cities are hardcoded in `CITIES` — order matters, it's the display order on the page.
- **Homepage** (`home.html`): the hero and "About me" intro come from `resume_data.py` (headline, location, contact, summary), plus one hand-written sentence from resume facts. The resume is linked from the hero, not inlined — the owner wants the homepage short. "Fun projects" is a static list in the template — when a new section ships, add its card there and its path to `PROJECT_LINKS` in `tests/app_tests.py`. The phone number stays off.
- **Resume** (`resume_data.py` + `_resume.html`, included by `resume.html`): all content lives in `resume_data.py` as plain data — edit that file, not the templates, to change resume content. Colors come from the `--site-*` tokens in `style.css`, so it works in light and dark mode. Company/project logos: `cdn.simpleicons.org` for brands that have an icon there (checked availability before using — not every brand does), fallback to a colored initials badge (`{"type": "initials", ...}`) otherwise. Bullets that need an inline link are pre-authored as HTML strings and rendered with Jinja's `| safe` filter — this is safe because the content is fully author-controlled, not user input; don't apply `| safe` to anything that isn't.
- **jj** (`jj_docs.py` + `templates/jj/` + `jj.css`): a static, source-linked reference to
  Jujutsu's internals at `/jj`. Read `specs/jj.md` before changing anything here, and
  `specs/jj-progress.md` for where the build stands.
  - Pages are static: no runtime network calls, no JS libraries. Diagrams are
    hand-authored inline SVG.
  - Everything describes exactly one upstream commit, `jj_docs.UPSTREAM`. Every source link
    goes through `jj_docs.source_url` so it is pinned to that commit; never link `blob/main`.
  - The registry is `TOPICS` (architecture pages) plus one page per entry in `COMMANDS`,
    which is generated from upstream's clap definitions (names, categories, tiers, and each
    command's own help summary). Command pages live at `/jj/<command>` with spaces turned
    into dashes (`/jj/git-fetch`); `COMMAND_PAGE_OVERRIDES` marks them ready.
  - Page templates are fragments rendered into `jj/base.html`; the on-page table of
    contents is built from their `<h2 id>`/`<h3 id>` headings. A page is routable only
    once its registry entry has `"ready": True`.
  - A Routine ("rayaq.ca/jj — architecture reference agent") runs daily: it builds the
    next queued page, and once the build is done, diffs upstream against the pin and
    updates affected pages. It pushes straight to `main` and keeps
    `specs/jj-progress.md` current, so keep that file accurate if you edit by hand.
- **jj-dojo** (`jj_dojo_docs.py` + `templates/jj_dojo/` + `jj_dojo.css`): a static,
  source-linked reference to Jujutsu Dojo, the VS Code extension for jj, at `/jj-dojo`. Read
  `specs/jj-dojo.md` before changing anything here, and `specs/jj-dojo-progress.md` for where
  the build stands. Same rules as `/jj`: static pages, every link pinned to
  `jj_dojo_docs.UPSTREAM` through `jj_dojo_docs.source_url`, inline SVG diagrams. Anything
  upstream only describes in `docs/intro.md` is marked *planned*, never shown as implemented.
  The section reuses `jj.css` for its layout but never edits `/jj` files. A daily Routine
  ("rayaq.ca/jj-dojo — architecture reference agent") builds and maintains it.
- **jj-vfs-poc** (`jj_vfs_docs.py` + `templates/jj_vfs/` + `jj_vfs.css`): the same kind of
  reference for jj-vfs-poc (crate `jjfsd`), a read-only FUSE file system over a jj repository,
  at `/jj-vfs-poc`. Read `specs/jj-vfs-poc.md` first and `specs/jj-vfs-poc-progress.md` for
  status. Links into the crate go through `jj_vfs_docs.source_url` (pinned commit); links into
  jj-lib go through `jj_vfs_docs.jj_lib_url`, pinned to the `v<jj_lib_version>` tag from the
  crate's `Cargo.toml`, which can differ from the jj version `/jj` describes. `FUSE_OPS` lists
  the `Filesystem` methods `src/fuse.rs` implements. A daily Routine
  ("rayaq.ca/jj-vfs-poc — architecture reference agent") builds and maintains it.
- **jj-commit-cloud-poc** (`jj_cloud_docs.py` + `templates/jj_cloud/` + `jj_cloud.css`): the
  same kind of reference for jj-commit-cloud-poc, a gRPC server storing a jj repository plus
  client store implementations and a custom `jj` binary, at `/jj-commit-cloud-poc`. Read
  `specs/jj-commit-cloud-poc.md` first and `specs/jj-commit-cloud-poc-progress.md` for status.
  Links go through `jj_cloud_docs.source_url` (pinned commit) and `jj_cloud_docs.jj_lib_url`
  (the `v<jj_lib_version>` tag). `PROTO_ITEMS` lists every service, RPC and message in
  `common/proto/*.proto`. A daily Routine ("rayaq.ca/jj-commit-cloud-poc — architecture
  reference agent") builds and maintains it.
- **ml-models** (`ml_models_docs.py` + `templates/ml_models/` + `ml_models.css`/`ml_models.js`):
  a static reference for learning or refreshing anything in machine learning, at `/ml-models`:
  12 areas (math foundations through classical ML, neural networks, architectures, generative
  models, language models, retrieval, training systems, inference and specialized learning),
  93 registered pages with levels and prerequisites, and a seven-step learning path. Read
  `specs/ml-models.md` first and `specs/ml-models-progress.md` for status and the build queue.
  Every page follows the spec's §6 format (problem, intuition, mechanics, worked example,
  implementation, tradeoffs, connections, references). Every code link goes through
  `ml_models_docs.pinned_url` (or its `source_url`/`sklearn_url`/`xgboost_url` shorthands),
  pinned to the commit of one stable release per library in `ml_models_docs.PINS`; ideas no
  library implements cite their papers. Diagrams are inline SVG; `ml_models.js`
  is optional progressive enhancement and every page reads fully without it. Torch-computed
  figures come from offline scripts in `tools/ml_models/` with output committed under
  `frontend/static/ml_models/` — never add `torch` (or scikit-learn, XGBoost or any other ML
  package) to the requirements files or run it in CI or at request time. A Routine
  ("rayaq.ca/ml-models — architecture reference agent", every 5 hours, fresh session per run)
  builds the next queued page and maintains the pins, then becomes a weekly audit (new
  releases, new open-weight models, deeper foundations) once the queue is empty (spec §8.1); before pushing it runs
  `tools/ml_models/check_mobile.js` for the 390px overflow check.
- **leetcode** (`leetcode_docs.py` + `templates/leetcode/` + `leetcode.css`): a static
  reference to every algorithmic pattern behind coding interviews, at `/leetcode`: 20 areas in
  NeetCode roadmap order (plus Foundations first and Beyond the interview last), 58 registered
  pattern pages with levels and prerequisites, and a seven-step learning path. Read
  `specs/leetcode.md` first and `specs/leetcode-progress.md` for status and the build queue.
  Coverage is measured against Blind 75, Grind 169, NeetCode 150 and NeetCode 250: `PROBLEMS` gives every
  problem on those lists exactly one home page, and the tests require each list to be either
  empty (before the research run) or exactly its size. Pages teach patterns, never problems:
  link to `leetcode.com/problems/<slug>/` and never copy LeetCode statements or NeetCode
  explanations or code (spec §3.2). Worked-example values come from stdlib helpers in
  `leetcode_docs.py`; never add a package for this section. A Routine
  ("rayaq.ca/leetcode — pattern reference agent", every 5 hours, fresh session per run, weekly audits once complete)
  researches the lists, then builds three queued pages per run; before pushing it runs
  `tools/leetcode/check_mobile.js` for the 390px overflow check.
- Phone number is intentionally omitted from the public resume and homepage (privacy choice, since the repo is public). Don't add it back without checking with the site owner first.

## Conventions

- No code comments unless explaining a non-obvious "why" (matches the general house style this project was built under) — identifiers and structure should be self-explanatory otherwise.
- Keep `backend/` free of anything that touches the terminal/HTML rendering beyond Flask's own templating — business logic (like `weather.py`) should stay easily unit-testable without spinning up the Flask app.
- When adding a new page: add the route in `app.py`, the template in `frontend/templates/`, any new static assets in `frontend/static/`, and a test in `backend/tests/app_tests.py` — all four, every time.

## Commit and push preferences

- Keep commits small and focused on a single feature or coherent change.
- Use this commit message format: a relevant one-word label (for example,
  `docs`, `fix`, or `weather`), a colon and short description, a blank line,
  then a longer description explaining the change. Choose a label that relates
  to the short or long description; do not use the literal word `title`.

  ```text
  docs: short desc

  long desc...
  ```

- Push changes directly to `main` for this project. A pull request is not required
  for the owner's workflow. Successful pushes deploy through the existing CI/CD
  pipeline.

- Every commit you create and push must include a `Co-Authored-By` trailer naming
  the model that contributed to it, not just the tool name (Claude Code or Codex).
  Use the actual model name and version available in the session and the
  provider's attribution email. For example:

  ```text
  Co-Authored-By: GPT-6 <noreply@openai.com>
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

  Include only models that contributed to the commit; the lines above are
  alternatives, not a list to copy wholesale. Preserve any existing human or
  model co-author trailers. Check the trailers before pushing.
