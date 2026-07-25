# rayaq.ca

Personal website, live at [rayaq.ca](https://rayaq.ca). Flask backend, server-rendered HTML, no JS framework. Deployed on a single GCP VM behind Caddy, with GitHub Actions handling tests and deploys.

## Pages

- `/` — homepage
- `/weather` — live weather dashboard for four cities, with an hourly forecast chart
- `/resume` — resume, not yet linked from the homepage
- `/health` — health check endpoint

## Stack

- **Backend**: Flask (Python)
- **Frontend**: Jinja2 templates, plain CSS, Chart.js (via CDN) for the weather chart
- **Infra**: GCP `e2-micro` VM, Caddy (reverse proxy + auto-HTTPS), systemd
- **CI/CD**: GitHub Actions — tests run on every push/PR, deploy to the VM on push to `main`

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

## Contributing

See [CLAUDE.md](CLAUDE.md) for architecture details, conventions, and the deploy process.
