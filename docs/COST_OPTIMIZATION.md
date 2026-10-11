# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward. Scope is application code only —
server configuration (Caddy, gunicorn, systemd, the VM) is out of scope by the owner's choice.

## 2026-10-11

**Verdict:** one small, measured win landed. The page cache now holds encoded bytes, which
halves its memory and trims per-request time. The weather outage item still needs the owner.
`/assembly-agents` and `showcase.json` no longer exist in the app, so the routine's smoke
list gets a 404 there. That is expected.

### Landed

- `13982b3` **perf: keep cached reference pages as utf-8 bytes.** The six reference sections
  now have 240 ready pages, about 10.8 MB of HTML. Every page holds some non-ASCII text, so
  CPython stored each cached str at 2 bytes per character (21.6 MB), and Flask re-encoded it
  on every response. The cache now keeps the UTF-8 bytes: **21.6 → 10.8 MB** resident in
  the single worker on the 1 GB VM. The saving keeps growing as the ml-models and leetcode
  Routines add pages. Warm p50 over 2000 requests: `/jj` 0.139 → 0.114 ms, `/jj/fix`
  0.144 → 0.119, `/ml-models/cnns` 0.150 → 0.120, `/leetcode` 0.134 → 0.114. Status,
  headers and body sha256 match before and after for all 240 pages plus `/`, `/resume`,
  `/health` and two 404s, each fetched twice.

### Needs the owner

1. **Weather outage behaviour** (carried from 2026-10-02, unchanged). A failed Open-Meteo
   fetch isn't cached, so while the API is down every `/weather` view makes 4 sequential
   calls with 5 s timeouts. That can block the only sync worker for up to 20 s per view.
   Options: cache failures for ~30 s, and/or fetch all four cities in one Open-Meteo
   request (it accepts comma-separated coordinates), cutting outbound calls per refresh
   from 4 to 1. Either changes what visitors see during an outage, and the second changes
   the `_fetch_weather` test seam.

### Considered and rejected

- **Minifying the reference pages' HTML.** It would save whitespace, but the routine
  requires their output to stay byte-identical, and compression in transit is server
  config (out of scope).
- **Pre-rendering every reference page at startup.** Bytes caching already makes a cold
  page a one-off cost of ~1–2 ms. Warming all 240 pages at boot would lengthen restarts and
  hold pages that nobody requests.
- **Caching `/` and `/resume` output.** They already render in 0.2–0.5 ms. Not worth the
  extra state.
- **Import time / module memory.** `import app` is ~150 ms of wall time, mostly
  Flask/Werkzeug, paid once per worker start. The app's own modules account for ~2 MB
  (largest: `leetcode_docs` 0.19 MB, `ml_models_docs` 0.18 MB, `jj_docs` 0.1 MB). Nothing
  worth trimming.
- **Unused dependencies:** `requirements.txt` is flask, gunicorn, requests, all used
  (`requests` by `weather.py`).

### Already optimal

Versioned static assets with year-long caching, the per-city weather TTL cache, and the
reference page cache (now bytes, bounded by the number of ready pages).
