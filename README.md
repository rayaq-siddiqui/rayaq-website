# rayaq.ca

Personal website, live at [rayaq.ca](https://rayaq.ca). Flask backend, server-rendered HTML, no JS framework. Deployed on a single GCP VM behind Caddy, with GitHub Actions handling tests and deploys.

## Pages

- `/`: homepage
- `/weather`: live weather dashboard for four cities, with an hourly forecast chart
- `/assembly-agents`: project page for [Assembly](https://github.com/rayaq-siddiqui/assembly-agents), rendered from a digest synced from that repo
- `/jj`: a detailed, source-linked reference to the internal architecture of [Jujutsu (jj)](https://github.com/jj-vcs/jj), with an architecture diagram on the overview page
- `/jj/<page>`: deep-dive pages, either architecture topics (e.g. `/jj/operations`, `/jj/protobufs`) or individual commands (e.g. `/jj/fix`). Pages still being written return 404 and show as "In progress" on `/jj`.
- `/jj-dojo`: the same kind of reference for [Jujutsu Dojo](https://github.com/jj-vcs/jj-dojo), Google's VS Code extension for jj, starting with its commit graph layout (`/jj-dojo/graph-layout`)
- `/jj-vfs-poc`: the same for [jj-vfs-poc](https://github.com/jj-vcs/jj-vfs-poc), a read-only FUSE file system over a jj repository, starting with its namespace (`/jj-vfs-poc/namespace`)
- `/jj-commit-cloud-poc`: the same for [jj-commit-cloud-poc](https://github.com/jj-vcs/jj-commit-cloud-poc), a gRPC commit cloud for jj, starting with its protobuf schemas (`/jj-commit-cloud-poc/protobufs`)
- `/ml-models`: a reference to how large ML models are built, with a model-family map and a tiered list of models every ML engineer should know, from linear regression to current frontier models. Every code link is pinned to a PyTorch release.
- `/ml-models/<page>`: deep-dive pages, starting with an interactive walk through the Transformer (`/ml-models/transformer`): a clickable architecture diagram, a live attention table and a parameter calculator. Planned pages show on `/ml-models` until they are ready.
- `/resume`: resume
- `/health`: health check endpoint

## Stack

- **Backend**: Flask (Python), served by gunicorn
- **Frontend**: Jinja2 templates and plain CSS. Chart.js (via CDN) is used only for the weather chart; the diagrams in the `/jj*` and `/ml-models` sections are hand-written inline SVG. `/ml-models` adds a small vanilla JS file for its interactive figures; every page reads in full without it.
- **Infra**: GCP `e2-micro` VM, Caddy (reverse proxy and auto-HTTPS), systemd
- **CI/CD**: GitHub Actions. Tests run on every push and PR; pushes to `main` that pass deploy to the VM.

## Automation

Several scheduled Claude Code routines push straight to `main`, which deploys through the normal CI/CD path:

| Routine | Schedule | What it does |
|---|---|---|
| rayaq.ca/jj architecture reference agent | Daily | The `/jj` build is complete; keeps every page in sync with upstream jj, tracked in [`specs/jj-progress.md`](specs/jj-progress.md) |
| rayaq.ca/jj-dojo architecture reference agent | Weekly (Thursday) | The same maintenance for `/jj-dojo`, tracked in [`specs/jj-dojo-progress.md`](specs/jj-dojo-progress.md) |
| rayaq.ca/jj-vfs-poc architecture reference agent | Weekly (Monday) | The same for `/jj-vfs-poc`, tracked in [`specs/jj-vfs-poc-progress.md`](specs/jj-vfs-poc-progress.md) |
| rayaq.ca/jj-commit-cloud-poc architecture reference agent | Weekly (Wednesday) | The same for `/jj-commit-cloud-poc`, tracked in [`specs/jj-commit-cloud-poc-progress.md`](specs/jj-commit-cloud-poc-progress.md) |
| rayaq.ca/ml-models build run | Daily | Builds the next `/ml-models` page from the queue in [`specs/ml-models-progress.md`](specs/ml-models-progress.md), then keeps pages in step with new PyTorch releases |
| Weekly server cost optimization | Weekly (Sunday) | Looks for measurable savings in the application code and logs each run in [`docs/COST_OPTIMIZATION.md`](docs/COST_OPTIMIZATION.md) |
| Sync Assembly showcase | Every 6 hours | Copies the latest project digest from Assembly into `backend/showcase.json` |

## Repository layout

```
backend/     Flask app, business logic, and the test suite (backend/tests/)
frontend/    Jinja2 templates and static assets
deploy/      Caddyfile and systemd unit mirrored from the VM
specs/       Product and technical specs (jj.md, jj-dojo.md, jj-vfs-poc.md,
             jj-commit-cloud-poc.md, ml-models.md), each with a build-progress file
docs/        Run logs (cost optimization)
```

## Getting started

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/python3 app.py          # http://127.0.0.1:8000
```

## Testing

```bash
cd backend
./venv/bin/pytest -v
```

Test files use the `*_tests.py` naming convention (configured in `pytest.ini`), and no test touches the network.

## Contributing

See [AGENTS.md](AGENTS.md) (which [CLAUDE.md](CLAUDE.md) points to) for architecture details, conventions, and the deploy process, and the matching spec in [`specs/`](specs/) before changing anything under `/jj`, `/jj-dojo`, `/jj-vfs-poc`, `/jj-commit-cloud-poc` or `/ml-models`.
