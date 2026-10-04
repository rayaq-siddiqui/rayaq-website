# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward. Scope is application code only —
server configuration (Caddy, gunicorn, systemd, the VM) is out of scope by the owner's choice.

## 2026-10-04

**Verdict:** one clear win landed (the four reference sections no longer re-render static
pages on every hit); the weather outage item from last run still needs the owner.

### Landed

- `810e3dc` **perf: cache rendered reference pages after the first request.** Every hit
  on `/jj`, `/jj-dojo`, `/jj-vfs-poc` and `/jj-commit-cloud-poc` rendered the fragment and
  the layout again, rebuilt the registry lists and re-parsed headings for the table of
  contents, although the output only changes on a deploy. `rendered_pages.py` now keeps
  each page's HTML after its first successful render (unknown slugs are never stored, so
  the cache is bounded by the number of ready pages). Median of 50 requests:
  `/jj` 2.11 → 0.14 ms, `/jj/fix` 1.26 → 0.15 ms, `/jj-dojo/graph-layout` 0.86 → 0.16 ms,
  `/jj-commit-cloud-poc` 0.71 → 0.13 ms. Cost: 1.8 MB of HTML once all 43 ready pages are
  warm, growing roughly 40–60 KB per new page. All 43 responses are byte-identical before
  and after (sha256). The test suite also dropped from ~2.9 s to ~1.2 s.

### Needs the owner

1. **Weather outage behaviour** (carried from 2026-10-02, unchanged). A failed Open-Meteo
   fetch isn't cached, so while the API is down every `/weather` view makes 4 sequential
   calls with 5 s timeouts, which can block the only sync worker for up to 20 s per view.
   Options: cache failures for ~30 s, and/or fetch all four cities in one Open-Meteo
   request (it accepts comma-separated coordinates), cutting outbound calls per refresh
   from 4 to 1. Either changes what visitors see during an outage, and the second changes
   the `_fetch_weather` test seam.

### Considered and rejected

- **Minifying the reference pages' HTML.** They are 26–87 KB each with indentation
  whitespace, but the routine requires their output to stay byte-identical, and compression
  in transit is server config (out of scope).
- **Caching `/`, `/resume` and `/assembly-agents` output.** They already render in
  0.2–0.5 ms; `/assembly-agents` already reuses its parsed view until `showcase.json`'s mtime
  changes. Not worth the extra state.
- **Import time.** `import app` takes ~150 ms, almost all Flask/Werkzeug, once per worker
  start. Nothing to trim.
- **Unused dependencies:** `requirements.txt` is flask, gunicorn, requests, all used
  (`requests` by `weather.py`).

### Already optimal

Versioned static assets with year-long caching, the showcase mtime-gated reload, and the
per-city weather TTL cache.
