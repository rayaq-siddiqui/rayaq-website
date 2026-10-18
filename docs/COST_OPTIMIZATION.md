# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward. Scope is application code only —
server configuration (Caddy, gunicorn, systemd, the VM) is out of scope by the owner's choice.

## 2026-10-18

**Verdict:** no change landed. The hot paths haven't changed since last week, and nothing
measured is big enough to justify new code. The weather outage item still needs the owner.
`/assembly-agents` and `showcase.json` still don't exist in the app, so the smoke list's
404 there is expected.

### Landed

Nothing this run. Last week's `13982b3` (cached reference pages kept as UTF-8 bytes) is
still the most recent optimization. With 302 ready pages the cache now holds **15.2 MB**
of bytes; as a str cache it would hold about 30 MB.

### Needs the owner

1. **Weather outage behaviour** (carried from 2026-10-02, unchanged). A failed Open-Meteo
   fetch isn't cached, so while the API is down every `/weather` view makes 4 sequential
   calls with 5 s timeouts. That can block the only sync worker for up to 20 s per view.
   Options: cache failures for ~30 s, and/or fetch all four cities in one Open-Meteo
   request (it accepts comma-separated coordinates), cutting outbound calls per refresh
   from 4 to 1. Either changes what visitors see during an outage, and the second changes
   the `_fetch_weather` test seam.
2. **Stray screenshots in `backend/`.** `tf_arch.png`, `tf_attn.png`, `tf_calc.png` and
   `tf_tier.png` (231 KB) came in with `e476f70`. Nothing references them and Flask doesn't
   serve `backend/`, so they cost nothing at runtime, only clone and pull size. They came
   from another Routine's commit, so they're left for the owner to delete.

### Considered and rejected

- **Caching the formatted weather rows.** On a warm cache, `get_weather_for_cities`
  re-parses and re-formats 4 × 24 hourly timestamps on every view: 125 µs of `/weather`'s
  0.44 ms p50. Caching the rows next to the raw fetch would save ~0.12 ms per view, but it
  adds state that has to expire with the 1-hour TTL. At this site's traffic it isn't worth
  it (same call as caching `/` and `/resume`).
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
reference page cache (bytes, bounded by the number of ready pages, 302 today).
