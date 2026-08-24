# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-24 — empty-state suggestions now reflect the filters actually
used in the search.

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
6. ~~Search parameters are not encoded in the URL.~~ Resolved 2026-08-24 (§27 V1.4).

---

## Open owner actions (not agent work)

None outstanding. The Travelpayouts token is live on the VM (confirmed 2026-08-24);
see `specs/flights-setup.md` if it ever needs rotating or rolling back.

---

## Next candidate increments

1. **Re-check thin-route coverage on real traffic, now that nearby-airport search
   exists.** Watch `flight_search_events` for a week and see how often `includeNearby`
   searches actually turn up a genuinely different (non-exact) airport, and whether
   personal routes named in the spec (§1.1: Toronto <-> Bay Area, Toronto <->
   international vacation spots) return enough candidates for the insights to say
   anything useful once nearby search is in the mix. If a route still comes back thin
   even with it on, the honest move per §30 is UI copy that says so, not a third
   provider.
2. **Consider defaulting `includeNearby` to on.** It's opt-in today, matching how the
   spec describes it (§27 V1.1: "Allow: Include nearby airports"). Once there's a sense
   of how often it changes the outcome, it may be worth defaulting it on for routes with
   known-sparse coverage, or simply always-on, rather than asking a casual user to find
   the checkbox.
3. **Apply for Skyscanner's Indicative Prices API** (§6.4, §27 V1.5). Free if approved,
   purpose-built for flexible-date discovery per Skyscanner's own docs, and the provider
   abstraction means adding it later is a new file in `providers/`, not a rewrite. This
   needs the site owner to apply — not something an agent session can do — but it's the
   spec-sanctioned path to denser data if nearby-airport search still isn't enough.
4. **§27 V1.3, local price history.** `flight_price_observations` has been recording
   every result card since the token went live on 2026-08-24, but nothing reads it back
   yet. Once a route has accumulated a few weeks of observations, surface "Lowest price
   we've observed in the last 30 days" per the spec's own wording — precise that it's
   this site's own observed history, not full market history. Worth waiting for real
   data to accumulate first; the table is nearly empty right now (live only since
   today), so the insight would have nothing to say.
5. **Look for more code-cleanliness items,** per the routine's own priority order:
   duplicated logic, functions doing too much, or provider details leaking out of
   `providers/`. A full read-through this run (`service.py`, `ranking.py`, `insights.py`,
   `models.py`, `cache.py`, `validation.py`, `providers/aviasales.py`, `airports.py`,
   `rate_limit.py`, `api.py`, `errors.py`, `app.py`) found nothing worth changing — the
   backend stays small and each module does one thing.

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

### 2026-08-24 — nearby-airport search (§27 V1.1, pulled forward)
The site owner ran a real search (Toronto -> San Francisco, a 2-day departure window, a
12-15 night trip) and got "no fares found" — a legitimate complaint, not a bug report to
dismiss. Discussed three ways to get denser data: SerpApi's Google Flights engine (250
free searches/month *total across all visitors*, then $25/mo — dies under exactly the
"some real load" this site expects, per spec §1.3), an MCP flight-search marketplace
(every listing there wraps a provider already evaluated and rejected — Amadeus, SerpApi,
or a plain unmaintained Google Flights scraper with no flexible-date support at all), and
a legacy Aviasales calendar endpoint (`min-prices.aviasales.ru/calendar_preload`,
untested — same underlying cache, unclear payoff). All three were set aside in favor of
the thing the spec itself already named as the real fix: §27 V1.1, nearby airports.

Added `airports.nearby(code)` — a haversine lookup over the bundled dataset's lat/lon,
not a hardcoded route list, so it generalizes past the two examples the spec names
(Toronto: YYZ/YTZ; Bay Area: SFO/SJC/OAK — both reproduced exactly by the real distance
calculation). A metro code like YTO returns nothing on purpose, since Aviasales already
aggregates real airports under those codes. `SearchRequest` gained `include_nearby`
(part of the cache key, so an exact search and a nearby one never collide). When it's
set, `service.py` fans out to the searched pair plus up to one real alternate on each
side — bounded at 3 upstream provider calls total, not a full cross-product — and merges
the candidates. Every result carries `airportNote` (e.g. "from Toronto (YTZ)") whenever
its actual origin or destination differs from what was searched, rendered as a distinct
amber tag in the UI, so a fare from a real-but-different airport is never shown as if it
departed the one the user picked. Opt-in checkbox next to "Direct flights only", default
off, matching how the spec itself describes this as something to allow, not force.

Verified in a real browser: unchecked, behavior is byte-for-byte the same as before;
checked, a stubbed provider whose fares vary by which pair was actually queried produced
results correctly tagged "from Toronto (YTZ)" / "to Oakland (OAK)" alongside untagged
exact-match fares, no console errors. Full suite (148 tests, up from 137) passes.

### 2026-08-24 — saved/shareable search URLs (§27 V1.4, pulled forward)
Implemented the last deferred-from-V1 deviation. `service.form_defaults()` now takes an
optional `query` mapping (raw query-string values from Flask's `request.args`, passed
through by `app.py`'s `/flights` route) and folds it into the computed defaults:
`from`/`to` (validated against the airport dataset, silently dropped if unknown),
`departStart`/`departEnd` (clamped to today and to the existing 60-day window limit),
`minNights`/`maxNights`, `currency`, and `direct`/`nearby` flags. Every value is
best-effort — a malformed or out-of-range query parameter falls back to the ordinary
default rather than erroring, since this path renders a page, not the search API (which
still does full `validation.parse` on submit). `page_context()` adds a computed
`autoSearch` flag (true only when both origin and destination resolved to known
airports) so the template doesn't need its own duplicate logic.

On the client, `flights.js` now: prefills the origin/destination combo boxes from
`defaults.origin`/`defaults.destination` on load (reusing the same `combo.set()` path the
popular-route chips already used), applies `defaults.includeNearby` alongside the
existing `defaults.directOnly` (previously the nearby checkbox had no server-driven
default at all), auto-submits the form when `defaults.autoSearch` is true, and calls
`history.replaceState` with the full form state as query parameters on every submit
(manual or chip-triggered) so the address bar always reflects the last search — no new
history entries are pushed, matching the "bookmarkable/shareable" goal without adding
back-button semantics the spec doesn't ask for.

Verified in a real browser (Playwright against the dev server): a URL carrying a full
saved search (`?from=YYZ&to=SFO&departStart=...&direct=1&nearby=1`) prefilled every field
correctly and auto-ran the search with no console errors (only the expected 503 from the
unconfigured dev provider); a manual search from a bare `/flights` load correctly updated
the URL after submit. An unknown airport code in `from`/`to` is dropped rather than
surfaced as an error, since a stale or hand-edited URL shouldn't look broken. Added 7
tests to `flights_service_tests.py` (query overrides, unknown-code handling, malformed
values, window clamping, the `autoSearch` flag) and 2 to `app_tests.py` (end-to-end
query-string rendering). Full suite (155 tests, up from 148) passes.

### 2026-08-24 — honest empty-state suggestions
Read through the entire `backend/flights/` package this run (all modules) looking for
cleanliness items per the routine's priority order; found nothing worth changing — no
duplicated logic, no oversized functions, no provider details leaking above
`providers/`. Full suite (155 tests) already green with no changes needed there.

Did find one small UI honesty gap: the "No fares found" empty state
(`frontend/static/flights.js`) always suggested "Widen the departure window / Allow more
trip lengths / Try a nearby airport" verbatim, even when the search that came back empty
already had "Include nearby airports" checked — recommending an option the user had
already tried. `emptyState()` now takes the full response payload instead of just the
message string, and builds suggestions from the search's own `request.directOnly` /
`request.includeNearby` flags: "Allow flights with stops" only when direct-only was on,
"Try a nearby airport" only when nearby wasn't already included. Matches §15/§28's intent
that copy should be honest about what the search actually did.

Verified in a real browser (Playwright against the dev server, dependency not added to
the project) at 390px: a no-filters search shows all three original suggestions; a
search with both `directOnly` and `includeNearby` checked shows "Allow flights with
stops" in place of "Try a nearby airport", no console errors. No backend change, so the
existing 155 tests stand unchanged (this project has no frontend JS test harness — see
CLAUDE.md — so verification here is manual/Playwright, matching how prior JS-only
changes in this log were checked).
