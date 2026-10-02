# Cost optimization log

Maintained by the weekly "rayaq.ca — weekly server cost optimization" Routine. Rewritten
each run; **Considered and rejected** carries forward.

## 2026-10-02

**Verdict:** one low-risk win landed (long-lived static caching); the two bigger levers
need the owner because they touch the VM or change outage behaviour.

### Landed

- `ceba67c` **static: version asset URLs and let browsers cache them for a year.** Static
  files were served `no-cache`, so every page view revalidated each CSS/JS file through
  Caddy to the single gunicorn worker. URLs now carry `?v=<mtime>` with
  `max-age=31536000`. Across `/`, `/weather`, `/flights`, `/assembly-agents`: 8 asset
  requests (53.3 KB) per visit → 0 on repeat views.

### Needs the owner

1. **Turn on compression in Caddy.** Nothing is compressed today. Measured gzip -9:
   `/assembly-agents` 62.0 KB → 19.4 KB, `flights.js` 21.1 KB → 5.4 KB,
   `flights.css` 10.9 KB → 2.7 KB, `/flights` 7.0 KB → 1.8 KB (~70% less egress).
   Change `deploy/Caddyfile` to:
   ```
   rayaq.ca, www.rayaq.ca {
       encode zstd gzip
       reverse_proxy localhost:8000
   }
   ```
   then copy it to `/etc/caddy/Caddyfile` on the VM and `sudo systemctl reload caddy`.
   Not committed, because CI doesn't apply it and the repo copy would drift from the VM.
2. **Weather outage behaviour.** A failed Open-Meteo fetch isn't cached, so while the API
   is down every `/weather` view makes 4 sequential calls with 5 s timeouts. That can
   block the only sync gunicorn worker (and so the whole site) for up to 20 s per view.
   Options: cache failures for ~30 s, and/or fetch all four cities in one Open-Meteo
   request (it accepts comma-separated coordinates), which cuts outbound calls per
   refresh from 4 to 1. Either one changes what visitors see during an outage, and the
   second changes the `_fetch_weather` test seam, so it needs your call.
3. **Observation/event tables grow forever.** `flight_price_observations` and
   `flight_search_events` are never pruned (only the search cache is). Price history only
   reads 30 days back. Growth is tiny at current traffic, but pruning observations
   older than ~60 days would cap it. The spec doesn't set a retention period, so it's
   your decision.

### Considered and rejected

- **Fewer gunicorn workers / different worker type:** the unit already runs gunicorn's
  default of one sync worker, the smallest memory footprint. Nothing to cut.
- **Lazy-loading `airports.json`:** already lazy and indexed once per process (31 KB).
- **Unused dependencies:** `requirements.txt` is flask, gunicorn, requests, all used.

### Already optimal

The SQLite route index, search-cache TTL and pruning, the showcase mtime-gated reload,
and the per-city weather TTL cache.
