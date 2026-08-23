# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-23 — initial V1 build.

---

## Where things stand

V1 is built end to end and deployed through the normal `main` → CI/CD path. The page,
the API, the provider adapter, the SQLite cache, rate limiting, and the deterministic
insights all exist and are covered by tests (131 passing).

The one thing standing between this and a working public search is the provider token
(see **Open owner actions**). Without it the page renders and honestly reports that
search is unavailable; with it, search works.

### Layout

```
backend/flights/
  models.py       SearchRequest, FlightCandidate, ProviderResult (+ to_api serialization)
  errors.py       FlightSearchError (400), TooManyRequestsError (429), Provider* (503)
  validation.py   raw JSON -> SearchRequest, with the §18 input limits
  ranking.py      filter / dedupe / rank
  insights.py     deterministic insights + cheapest-per-departure-day series
  airports.py     search over the bundled dataset
  cache.py        SQLite: search cache, price observations, search events
  rate_limit.py   in-process per-client sliding window
  service.py      orchestration + structured logging
  api.py          (body, status) mapping, Flask-agnostic
  providers/      base.py (interface), aviasales.py (the only implementation)
  data/airports.json   206 airports and metro city codes
```

Routes live in `backend/app.py`; the page is `frontend/templates/flights.html` with
`frontend/static/flights.{css,js}`.

---

## §26 Acceptance criteria

### Search
- [x] Choose an origin — autocomplete over the bundled dataset, or type an IATA code.
- [x] Choose a destination.
- [x] Earliest / latest departure.
- [x] Minimum / maximum trip length.
- [x] Direct-only toggle (passed through to the provider *and* enforced locally).
- [x] Input validated server-side; the browser only pre-checks emptiness.

### Results
- [x] Cheapest result highlighted in its own Best deal card.
- [x] Top alternatives listed (up to 10 candidates total).
- [x] Departure and return dates shown on every card.
- [x] Price and currency shown on every card.
- [x] Stops shown when the provider reports them.
- [x] Freshness disclosed in a notice, per card when `foundAt` exists, and in the footer.
- [x] Every card links out to verify the fare.

### Smart discovery
- [x] Ranked by price, then stops, then duration.
- [x] Cheapest departure date identified.
- [x] Date-shift savings surfaced when the gap clears $15.
- [x] No AI API involved.

### Engineering
- [x] Provider behind `FlightSearchProvider`; nothing above `providers/` knows Aviasales.
- [x] Credential read from `TRAVELPAYOUTS_API_TOKEN`, server-side only.
- [x] SQLite cache (45-minute TTL, 24-hour stale-if-error window).
- [x] Rate limiting (10/min, 100/hour per client).
- [x] Provider failures handled: outage, 429, malformed body, oversized body, timeout.
- [x] No-results is a 200 with an explanation, not an error.
- [x] Unit tests cover date, ranking, insight, cache, and normalization logic.
- [x] Mobile layout verified at 390px — no horizontal overflow, 44–52px tap targets.

### Cost
- [x] No new VM, no Railway, no paid DB, no paid API, no overage-billed API, no paid AI.
- [x] Incremental recurring cost: $0.

---

## Deliberate deviations from the spec

1. **No `timezone` in the airport dataset.** §11 lists it among "fields such as"; nothing
   in V1 uses it, and hand-authoring it for 206 entries adds error surface. `lat`/`lon`
   are there for the §27 nearby-airports work.
2. **`stops` means the worst leg, not the sum.** Aviasales reports `transfers` and
   `return_transfers` separately; the normalizer takes the max so "Direct" means both
   legs are direct.
3. **`foundAt` is usually absent.** `prices_for_dates` does not reliably return it, so
   the UI falls back to "last checked <when we fetched>" rather than inventing an
   observation time. Do not fabricate a fare age.
4. **Rate limits are per gunicorn worker.** The counters live in process memory, so the
   real limit is roughly `workers × 10/min`. Acceptable at this scale; §17 explicitly
   allows in-memory. Move to SQLite only if it actually matters.
5. **Search parameters are not encoded in the URL.** That is §27's V1.4, not V1.

---

## Open owner actions (not agent work)

- Create a free Travelpayouts account, add a project for `rayaq.ca`, and get the Aviasales
  Data API token.
- On the VM: `sudo install -d -o rayaq /var/lib/rayaq-website`, write the token into
  `/etc/rayaq-website.env` (template: `deploy/rayaq-website.env.example`), copy
  `deploy/rayaq-website.service` to `/etc/systemd/system/`, then
  `sudo systemctl daemon-reload && sudo systemctl restart rayaq-website`.
- Until that happens, `/api/flights/health` reports `providerConfigured: false` and
  searches return 503.

---

## Next candidate increments

1. **Friendlier unconfigured state.** When the provider has no token, the page shows a
   generic "temporarily unavailable" banner. It should say plainly that live search is
   not switched on yet, rather than implying an outage.
2. **`cache.prune()` is written but never called.** Either call it (opportunistically
   after a write, or on a low-frequency path) or delete it. Dead code either way today.
3. **Verify normalization against the real provider** once the token exists. The fixture
   in `backend/tests/fixtures/` was authored from the documented response shape; if the
   live payload differs, update the fixture *and* the normalizer together.

---

## Run log

### 2026-08-23 — initial build
Built the whole V1 stack: airport dataset, domain layer, Aviasales adapter, SQLite cache,
rate limiter, service orchestration, JSON endpoints, and the mobile-first page. Verified
in a real browser at 390px and 1280px against a stubbed provider; fixed a horizontal
overflow caused by grid children defaulting to `min-width: auto`, and replaced `fieldset`
/`legend` with labelled groups so the field headings stop colliding.
