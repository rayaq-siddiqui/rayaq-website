# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward. Scope is application code only —
server configuration (Caddy, gunicorn, systemd, the VM) is out of scope by the owner's choice.

## 2026-10-02

**Verdict:** one low-risk win landed (long-lived static caching); the remaining code lever
needs the owner because it changes outage behaviour.

### Landed

- `ceba67c` **static: version asset URLs and let browsers cache them for a year.** Static
  files were served `no-cache`, so every page view revalidated each CSS/JS file through
  Caddy to the single gunicorn worker. URLs now carry `?v=<mtime>` with
  `max-age=31536000`. Across `/`, `/weather`, `/flights`, `/assembly-agents`: 8 asset
  requests (53.3 KB) per visit (measured before `/flights` was removed) → 0 on repeat views.

### Needs the owner

1. **Weather outage behaviour.** A failed Open-Meteo fetch isn't cached, so while the API
   is down every `/weather` view makes 4 sequential calls with 5 s timeouts. That can
   block the only sync gunicorn worker (and so the whole site) for up to 20 s per view.
   Options: cache failures for ~30 s, and/or fetch all four cities in one Open-Meteo
   request (it accepts comma-separated coordinates), which cuts outbound calls per
   refresh from 4 to 1. Either one changes what visitors see during an outage, and the
   second changes the `_fetch_weather` test seam, so it needs your call.

### Considered and rejected

- **Unused dependencies:** `requirements.txt` is flask, gunicorn, requests, all used
  (`requests` by `weather.py`).

### Already optimal

The showcase mtime-gated reload and the per-city weather TTL cache.
