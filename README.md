# rayaq.ca

Personal website, live at [rayaq.ca](https://rayaq.ca). Flask backend, server-rendered HTML, no JS framework. Deployed on a single GCP VM behind Caddy, with GitHub Actions handling tests and deploys.

## Pages

- `/`: homepage
- `/weather`: live weather dashboard for four cities, with an hourly forecast chart
- `/assembly-agents`: project page for [Assembly](https://github.com/rayaq-siddiqui/assembly-agents), rendered from a digest synced from that repo
- `/jj`: a detailed, source-linked reference to the internal architecture of [Jujutsu (jj)](https://github.com/jj-vcs/jj), with an architecture diagram on the overview page
- `/jj/<page>`: deep-dive pages, either architecture topics (e.g. `/jj/operations`, `/jj/protobufs`) or individual commands (e.g. `/jj/fix`). Pages still being written return 404 and show as "In progress" on `/jj`.
- `/resume`: resume, not yet linked from the homepage
- `/health`: health check endpoint

## Stack

- **Backend**: Flask (Python), served by gunicorn
- **Frontend**: Jinja2 templates and plain CSS. Chart.js (via CDN) is used only for the weather chart; the `/jj` diagrams are hand-written inline SVG.
- **Infra**: GCP `e2-micro` VM, Caddy (reverse proxy and auto-HTTPS), systemd
- **CI/CD**: GitHub Actions. Tests run on every push and PR; pushes to `main` that pass deploy to the VM.

## Automation

Several scheduled Claude Code routines push straight to `main`, which deploys through the normal CI/CD path:

| Routine | Schedule | What it does |
|---|---|---|
| rayaq.ca/jj architecture reference agent | Daily | Builds the next `/jj` page from the queue in [`specs/jj-progress.md`](specs/jj-progress.md) and keeps existing pages in sync with upstream jj |
| Weekly server cost optimization | Weekly (Sunday) | Looks for measurable savings in the application code and logs each run in [`docs/COST_OPTIMIZATION.md`](docs/COST_OPTIMIZATION.md) |
| Sync Assembly showcase | Every 6 hours | Copies the latest project digest from Assembly into `backend/showcase.json` |

## Repository layout

```
backend/     Flask app, business logic, and the test suite (backend/tests/)
frontend/    Jinja2 templates and static assets
deploy/      Caddyfile and systemd unit mirrored from the VM
specs/       Product and technical specs (jj.md) and build progress
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

See [CLAUDE.md](CLAUDE.md) for architecture details, conventions, and the deploy process, and [`specs/jj.md`](specs/jj.md) before changing anything under `/jj`.
