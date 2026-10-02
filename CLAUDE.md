# CLAUDE.md

This file provides guidance to Claude Code (or any coding agent) when working with code in this repository.

## What this is

`rayaq.ca` — a personal website. Flask backend, server-rendered HTML frontend (no JS framework, no build step). Deployed on a single GCP VM behind Caddy, with GitHub Actions handling CI (tests) and CD (deploy).

## Architecture

```
backend/            Flask app (Python) — all server-side logic
  app.py            Route definitions only. Keep business logic out of here.
  weather.py        Open-Meteo API client + in-memory cache for the /weather page
  resume_data.py    Plain Python data (dicts/lists) that resume.html renders — this
                     is the single source of truth for resume content, not the template
  assembly.py       Reads showcase.json and builds the view assembly.html renders,
                     re-reading only when the file's mtime changes
  showcase.json     The Assembly project digest. SYNCED FROM UPSTREAM — do not
                     hand-edit (see "Assembly" under Feature-specific notes)
  sync_showcase.py  Copies that digest out of an assembly-agents checkout
  static_assets.py  Appends ?v=<mtime> to static URLs so they can be cached for a year
  requirements.txt       Runtime deps
  requirements-dev.txt   Runtime + pytest, for local dev / CI
  pytest.ini         Configures pytest to discover *_tests.py (not the pytest default
                     test_*.py — this project intentionally uses the *_tests.py suffix)
  tests/
    conftest.py      Adds backend/ to sys.path so tests can `import app`, `import weather`
    app_tests.py     Route-level tests (Flask test client), weather calls are monkeypatched
    weather_tests.py Tests for weather.py logic, with requests calls monkeypatched — no
                     real network calls in the test suite
    assembly_tests.py     Tests for assembly.py against a fabricated digest, plus one
                     test that the committed showcase.json actually renders
    sync_showcase_tests.py Tests the sync refuses anything the page cannot render

frontend/
  templates/         Jinja2 templates. One per route: home.html, weather.html,
                     resume.html, assembly.html
  static/            style.css (shared/global), resume.css, assembly.css,
                     script.js (weather chart only)

deploy/
  Caddyfile           Reverse proxy config — proxies rayaq.ca/www.rayaq.ca to
                      localhost:8000, auto-provisions HTTPS via Let's Encrypt
  rayaq-website.service   systemd unit that runs gunicorn from backend/venv

.github/workflows/ci-cd.yml   GitHub Actions: test job (every push/PR) + deploy job
                               (push to main only, after tests pass)

vmrun.sh            Convenience wrapper: `./vmrun.sh '<command>'` runs a single command
                    on the production VM over SSH. Use this instead of writing raw
                    `gcloud compute ssh` invocations — keeps commands short and auditable.
```

### Routes

| Route | Purpose |
|---|---|
| `/` | Homepage — name, tagline, feature cards linking to other pages |
| `/weather` | Live weather dashboard for 4 fixed cities, click a card for an hourly chart |
| `/resume` | Resume page, **not currently linked from `/`** (disabled "Coming soon" card on homepage — ask before enabling, it's an intentional choice by the site owner) |
| `/assembly-agents` | Project page for Assembly, rendered from `backend/showcase.json` |
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
- **Resume** (`resume_data.py` + `resume.html`): all content lives in `resume_data.py` as plain data — edit that file, not the template, to change resume content. Company/project logos: `cdn.simpleicons.org` for brands that have an icon there (checked availability before using — not every brand does), fallback to a colored initials badge (`{"type": "initials", ...}`) otherwise. Bullets that need an inline link are pre-authored as HTML strings and rendered with Jinja's `| safe` filter — this is safe because the content is fully author-controlled, not user input; don't apply `| safe` to anything that isn't.
- **Assembly** (`assembly.py` + `showcase.json` + `assembly.html`): `backend/showcase.json` is **not authored here**. The upstream project, `rayaq-siddiqui/assembly-agents` (private), writes `docs/showcase.json` as its published contract with this page, and that file is copied in verbatim — so a hand-edit here is lost on the next sync. To change what the page says, change the digest upstream.
  - Sync manually with `./venv/bin/python3 sync_showcase.py <path-to-assembly-agents-checkout>` from `backend/`; it prints `updated` or `unchanged`, and refuses to write anything `assembly.build_view` can't render, so upstream schema drift fails the sync instead of the live page.
  - A Routine ("Sync Assembly showcase to rayaq.ca") runs that sync every 6 hours and pushes the result straight to `main`, which deploys via the normal CI/CD path. If the digest gains fields the page should show, the website is what adapts — keep the copy verbatim.
  - Upstream also has `.github/workflows/publish-showcase.yml`, which does the same copy on every push to its `main`. It has never actually published: it skips unless a `SHOWCASE_PUBLISH_TOKEN` secret (a fine-grained PAT scoped to this repo, Contents: read+write) exists on assembly-agents. Creating that secret makes syncing instant and the Routine redundant.
- Phone number is intentionally omitted from the public resume page (privacy choice, since the repo is public). Don't add it back without checking with the site owner first.

## Conventions

- No code comments unless explaining a non-obvious "why" (matches the general house style this project was built under) — identifiers and structure should be self-explanatory otherwise.
- Keep `backend/` free of anything that touches the terminal/HTML rendering beyond Flask's own templating — business logic (like `weather.py`) should stay easily unit-testable without spinning up the Flask app.
- When adding a new page: add the route in `app.py`, the template in `frontend/templates/`, any new static assets in `frontend/static/`, and a test in `backend/tests/app_tests.py` — all four, every time.
