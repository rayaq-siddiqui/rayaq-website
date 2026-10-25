# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward. Scope is application code only —
server configuration (Caddy, gunicorn, systemd, the VM) is out of scope by the owner's choice.

## 2026-10-25

**Verdict:** one fix landed: the slowest cold render on the site (`/leetcode/segment-trees`)
went from 5.6 s to 0.47 s with byte-identical output. `/assembly-agents` and
`showcase.json` still don't exist in the app, so the smoke list's 404 there is expected.

### Landed

- **`e3bfcef` perf: build each segment tree once when sizing queries.**
  `segment_tree_sizes` traced every (left, right) range through `segment_query_trace`, and
  each trace rebuilt the tree: ~33k rebuilds for n = 256. The first render blocked the only
  sync worker for **5587 ms → 465 ms**. The HTML is byte-identical, and a new test checks
  the shared tree against per-range tracing for n = 1..16.

Warm requests are unchanged: `/` 0.22 ms, `/resume` 0.35 ms, and cached reference pages
(310 ready, `/rml` included) and `/health` about 0.12 ms.

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
3. **Slow first renders of simulation pages in `/ml-models`.** Four pages run real
   simulations at render time: random-forests 1292 ms, distillation 1085 ms,
   vector-indexes 912 ms, diffusion-models 759 ms (about 1M `random.gauss` calls). Each costs
   that once per worker start. Making them faster means precomputing their figures offline
   into committed data, the way torch figures already are, or changing the simulations,
   and either risks float-level changes to the pages. That is the ml-models Routine's call.

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
reference page cache (bytes, bounded by the number of ready pages, 310 today, `/rml`
included).
