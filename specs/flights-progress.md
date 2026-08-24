# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-24 — merged in /v2/prices/latest and added a proactive
unconfigured-provider banner.

---

## Where things stand

V1 is built end to end and deployed through the normal `main` → CI/CD path. The page,
the API, the provider adapter, the SQLite cache, rate limiting, and the deterministic
insights all exist and are covered by tests (135 passing).

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
4. **Two upstream endpoints feed the provider, not one.** `/v3/prices_for_dates` is
   grouped by calendar month, so a lightly-searched route can show almost nothing for a
   given month even when Aviasales has more data elsewhere. Confirmed by hand on
   2026-08-24: YTO-SFO for October 2026 alone returned 1 ticket at limit=1000, while
   LON-NYC returned 23 and MOW-LED returned 367 for the same window — real cache
   scarcity for this specific corridor, not a bad parameter. `/v2/prices/latest` isn't
   month-bound and its cache outlives the endpoint's own 48-hour claim (observed
   `found_at` values spanning multiple weeks), so the provider now queries both and
   merges the results. One more upstream call per search either way.
5. **Cross-endpoint duplicates aren't deduplicated.** `ranking.dedupe` keys on
   `(origin, destination, departure_date, return_date, airline_code, price)`.
   `/v2/latest` tickets carry no `airline_code`, so a fare seen through both endpoints
   in the same window can render as two near-identical cards rather than collapsing
   into one. Not incorrect, just slightly redundant — worth widening the dedupe key
   (or falling back to price+dates when either candidate lacks an airline code) if it
   turns out to happen often in practice.
6. **Rate limits are per gunicorn worker.** The counters live in process memory, so the
   real limit is roughly `workers × 10/min`. Acceptable at this scale; §17 explicitly
   allows in-memory. Move to SQLite only if it actually matters.
7. **Search parameters are not encoded in the URL.** That is §27's V1.4, not V1.

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

1. **`cache.prune()` is written but never called.** Either call it (opportunistically
   after a write, or on a low-frequency path) or delete it. Dead code either way today.
2. **Widen `ranking.dedupe`'s key** so a fare seen through both Aviasales endpoints in
   the same search doesn't render as two cards (see deviation 5 above).
3. **Re-check thin-route coverage on real traffic.** The `/v2/latest` merge roughly
   doubled usable candidates for YTO-SFO in manual testing (1 -> ~3). Once the token is
   live on the VM, watch `flight_search_events` for a week and see whether personal
   routes named in the spec (§1.1: Toronto <-> Bay Area, Toronto <-> international
   vacation spots) return enough candidates for the insights to say anything useful. If
   a route still comes back thin, the honest move per §30 is UI copy that says so, not a
   third provider.
4. **V1.4 saved URLs** (§27) — encode search criteria in the query string so a search is
   bookmarkable/shareable without accounts. Deliberately deferred past V1 already; worth
   picking up now that the core experience is stable.

---

## Run log

### 2026-08-23 — initial build
Built the whole V1 stack: airport dataset, domain layer, Aviasales adapter, SQLite cache,
rate limiter, service orchestration, JSON endpoints, and the mobile-first page. Verified
in a real browser at 390px and 1280px against a stubbed provider; fixed a horizontal
overflow caused by grid children defaulting to `min-width: auto`, and replaced `fieldset`
/`legend` with labelled groups so the field headings stop colliding.

### 2026-08-24 — proactive unconfigured-provider banner
The provider token still isn't set on the VM (see **Open owner actions**), so every real
visitor to the live site was filling out the form, watching the loading skeleton, and
only then learning search wasn't available. Added a client-side check of
`/api/flights/health` on page load: when `providerConfigured` is false, an informational
banner (`#provider-notice` in `flights.html`, populated by `checkProviderStatus()` in
`flights.js`) appears above the form immediately, saying plainly that live search isn't
switched on yet rather than implying an outage. When the provider is configured the
banner stays hidden. Verified both states in a real browser (Playwright against the dev
server, dependency not added to the project). Added
`test_flights_page_includes_a_hook_for_the_provider_status_banner` to
`backend/tests/app_tests.py`.

### 2026-08-24 — merge in /v2/prices/latest
The site owner tested the token by hand and found /v3/prices_for_dates returning only 1
ticket for YTO-SFO across all of October, versus 23 for LON-NYC and 367 for MOW-LED on
the same query shape — real cache scarcity for this corridor, confirmed rather than
assumed. /v2/prices/latest (not month-bound, longer-lived cache, and it actually carries
found_at, which /v3 doesn't) found 2 more fares for the same route spanning September
and October. Added it as a second call inside AviasalesDataProvider, filtered on
show_to_affiliates and actual per the provider's own signals, normalized through a new
fixture built from the real (already anonymized) response the owner captured by hand.
Full suite (134 tests) passes. Provider token is still not on the VM; that's the one
remaining manual step, tracked in specs/flights-setup.md.
