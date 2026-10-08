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
- `/ml-models`: a reference for learning or refreshing anything in machine learning, from the math through classical models, neural networks, Transformers and language models to the systems that train and serve them. It has a seven-step learning path for beginners, 93 planned pages in 12 areas, each marked intro, core or advanced, and a tiered list of notable models. Every code link is pinned to one release of PyTorch, scikit-learn or XGBoost.
- `/ml-models/<page>`: deep-dive pages, starting with an interactive walk through the Transformer (`/ml-models/transformer`): a clickable architecture diagram, a live attention table and a parameter calculator. Planned pages show on `/ml-models` until they are ready.
- `/leetcode`: every algorithmic pattern behind coding interviews, one page per pattern, organized by the [NeetCode roadmap](https://neetcode.io/roadmap) and measured against Blind 75, Grind 169 and NeetCode 150. Each page covers the signals that point to the pattern, why it works, a traced example, a Python template and the list problems it unlocks. 58 pages are planned in 20 topics; a progress meter on `/leetcode` shows how much of each list is covered.
- `/leetcode/<page>`: pattern pages (e.g. `/leetcode/two-pointers`). Planned pages show on `/leetcode` until they are ready.
- `/resume`: resume
- `/health`: health check endpoint

## Stack

- **Backend**: Flask (Python), served by gunicorn
- **Frontend**: Jinja2 templates and plain CSS. Chart.js (via CDN) is used only for the weather chart; the diagrams in the `/jj*`, `/ml-models` and `/leetcode` sections are hand-written inline SVG. `/ml-models` adds a small vanilla JS file for its interactive figures; every page reads in full without it.
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
| rayaq.ca/ml-models build run | Daily | Builds the next `/ml-models` page from the queue in [`specs/ml-models-progress.md`](specs/ml-models-progress.md), then keeps pages in step with new PyTorch, scikit-learn and XGBoost releases |
| rayaq.ca/leetcode pattern reference agent | Every 5 hours | Researches the three problem lists, then builds the next `/leetcode` page from the queue in [`specs/leetcode-progress.md`](specs/leetcode-progress.md) until every list problem has a finished home page |
| Weekly server cost optimization | Weekly (Sunday) | Looks for measurable savings in the application code and logs each run in [`docs/COST_OPTIMIZATION.md`](docs/COST_OPTIMIZATION.md) |
| Sync Assembly showcase | Every 6 hours | Copies the latest project digest from Assembly into `backend/showcase.json` |

## Repository layout

```
backend/     Flask app, business logic, and the test suite (backend/tests/)
frontend/    Jinja2 templates and static assets
deploy/      Caddyfile and systemd unit mirrored from the VM
specs/       Product and technical specs (jj.md, jj-dojo.md, jj-vfs-poc.md,
             jj-commit-cloud-poc.md, ml-models.md, leetcode.md), each with a
             build-progress file
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

See [AGENTS.md](AGENTS.md) (which [CLAUDE.md](CLAUDE.md) points to) for architecture details, conventions, and the deploy process, and the matching spec in [`specs/`](specs/) before changing anything under `/jj`, `/jj-dojo`, `/jj-vfs-poc`, `/jj-commit-cloud-poc`, `/ml-models` or `/leetcode`.
