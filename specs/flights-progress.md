# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-24 — dedupe widened across provider endpoints, cache pruning wired up.

---

## Where things stand

V1 is built end to end and deployed through the normal `main` → CI/CD path. The page,
the API, the provider adapter, the SQLite cache, rate limiting, and the deterministic
insights all exist and are covered by tests (135 passing).

The provider token is live on the VM — the site owner confirmed
`GET https://rayaq.ca/api/flights/health` returns `{"providerConfigured": true}` on
2026-08-24. Real search is working in production. There are no more owner-side setup
steps; `specs/flights-setup.md` is kept for reference (rotating the token, rolling back)
but nothing in it is currently outstanding.

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
5. **Rate limits are per gunicorn worker.** The counters live in process memory, so the
   real limit is roughly `workers × 10/min`. Acceptable at this scale; §17 explicitly
   allows in-memory. Move to SQLite only if it actually matters.
6. **Search parameters are not encoded in the URL.** That is §27's V1.4, not V1.

---

## Open owner actions (not agent work)

None outstanding. The Travelpayouts token is live on the VM (confirmed 2026-08-24);
see `specs/flights-setup.md` if it ever needs rotating or rolling back.

---

## Next candidate increments

1. **Re-check thin-route coverage on real traffic.** The token is live as of 2026-08-24.
   The `/v2/latest` merge roughly doubled usable candidates for YTO-SFO in manual testing
   (1 -> ~3), but that was one manual check, not real usage. Watch `flight_search_events`
   for a week and see whether personal routes named in the spec (§1.1: Toronto <-> Bay
   Area, Toronto <-> international vacation spots) return enough candidates for the
   insights to say anything useful. If a route still comes back thin, the honest move
   per §30 is UI copy that says so, not a third provider.
2. **V1.4 saved URLs** (§27) — encode search criteria in the query string so a search is
   bookmarkable/shareable without accounts. Deliberately deferred past V1 already; worth
   picking up now that the core experience is stable.
3. **Look for more code-cleanliness items.** The two dead-code/dedupe items previously
   listed here are done (see run log below); next sweep should look for duplicated
   logic, functions doing too much, or provider details leaking out of `providers/`,
   per the routine's own priority order.

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

### 2026-08-24 — provider token confirmed live
The site owner set `TRAVELPAYOUTS_API_TOKEN` in `/etc/rayaq-website.env` on the VM and
restarted the service. `GET https://rayaq.ca/api/flights/health` now returns
`{"providerConfigured": true}`. No agent session verified this directly — the remote
sandbox's egress proxy blocks both `rayaq.ca` and `travelpayouts.com` outright, so
production reachability has to be confirmed by the site owner or something outside this
environment. V1 is feature-complete and live end to end. Cleared the **Open owner
actions** section accordingly; remaining work is the cleanup items below, not blockers.

### 2026-08-24 — wire up cache pruning, widen cross-endpoint dedupe
Two cleanup items from the previous run's candidate list, both code-cleanliness rather
than user-facing behaviour changes:
- `cache.prune()` existed and was tested but never called in the request path, so the
  `flight_search_cache` table only ever grew. Now called from `service.search()` right
  after a live (non-cache-hit) write, so pruning happens on the same cadence as real
  traffic without adding a scheduler or extra process. Added
  `test_a_live_search_prunes_cache_entries_past_the_stale_grace_period`.
- `FlightCandidate.dedupe_key` included `airline_code` in its fallback tuple, but
  `/v2/prices/latest` tickets never carry one (see the now-removed deviation 5), so the
  same fare seen through both Aviasales endpoints in one search rendered as two
  near-identical cards instead of collapsing into one. Dropped `airline_code` from the
  key — `raw_provider_id` is still tried first when a provider supplies one, and the
  remaining fields (route, dates, price) are specific enough that two genuinely
  different fares are vanishingly unlikely to collide. Added
  `test_dedupe_collapses_the_same_fare_seen_with_and_without_an_airline_code`.

Full suite (137 tests, up from 135) passes. Removed the corresponding items from
**Next candidate increments** and the now-resolved deviation from the deviations list.
