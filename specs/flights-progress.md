# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-25 — trip-length preset chips now show which one is active.

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
   this site's own observed history, not full market history. Still worth waiting: the
   table has only ~1 day of real traffic behind it as of this run.
5. **Look for more code-cleanliness items,** per the routine's own priority order:
   duplicated logic, functions doing too much, or provider details leaking out of
   `providers/`. Four consecutive full read-throughs (2026-08-24, 2026-08-25 x3) found
   only one backend issue, now fixed (the `duration` type-check) — the backend stays small
   and each module does one thing. `flight_price_observations` and `flight_search_events`
   grow without pruning; at this site's traffic that's years away from mattering and
   `flight_price_observations` is explicitly the substrate for V1.3, so leave it be unless
   real growth numbers say otherwise.

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

### 2026-08-25 — type-check provider `duration` before it reaches ranking
Read through the whole `backend/flights/` package again this run, then verified the live
page in a real browser at 390px (Playwright against the dev server, unconfigured
provider) — no horizontal overflow, no console errors, tap targets already correct
(`.toggle` labels are `min-height: 44px`, so the whole row is the target, not just the
checkbox glyph). No UI gap found.

Did find one real robustness gap in `providers/aviasales.py`: `price` and `stops` are
both validated/coerced before becoming a `FlightCandidate` (`_price` catches conversion
failures, `_stops` filters to `isinstance(leg, int)`), but `duration` was passed straight
through as `ticket.get("duration")` with no check. `ranking.score()` sorts on
`(price, stops, duration_minutes or 10**6)` — confirmed by hand that when two candidates
tie on price and stops, a string `duration` on one and the `10**6` int fallback on the
other raises `TypeError: '<' not supported between instances of 'int' and 'str'` inside
`sorted()`, which would 500 the whole search from one malformed upstream field. Added
`_duration()`, mirroring the existing `_price`/`_stops` pattern, and used it in both
`_to_candidate` and `_to_candidate_from_latest`. Added
`test_malformed_durations_normalize_to_none_instead_of_crashing_sort`. Full suite (156
tests, up from 155) passes.

### 2026-08-25 — trip-length preset chips (§27 V1.2, pulled forward)
§26 acceptance criteria are still all met and a fresh read-through of `backend/flights/`
found no new cleanliness issue, so picked up the next unbuilt roadmap item instead:
§27 V1.2, search presets ("Weekend trip", "5–8 days", "7–14 days", "Long weekend").
Added a row of chip buttons under the trip-length fields in `flights.html`
(`#trip-length-presets`), each carrying `data-min-nights`/`data-max-nights`. Numeric
mapping (the spec names the presets but not their bounds): Weekend trip 2–3, Long
weekend 3–4, 5–8 days 5–8, 7–14 days 7–14 — read as nights, matching how the two fields
next to them are already labelled.

Reused the existing `.chip` visual style rather than adding new CSS. That meant fixing a
latent selector bug rather than just adding a listener: `flights.js` previously wired
click handlers with a bare `document.querySelectorAll(".chip")`, assuming every `.chip`
on the page was a popular-route chip with `data-origin`/`data-destination`. Adding a
second kind of chip would have made that handler call `origin.set(null)` on click and
silently clear whatever was selected. Scoped the existing handler to `.popular .chip`
and added a second one scoped to `#trip-length-presets .chip` that just writes into
`#min-nights`/`#max-nights` (no auto-submit, unlike the route chips — trip length is one
of several inputs, not a complete search on its own).

Verified in a real browser (Playwright against the dev server) at 390px: all 4 presets
render with the right labels and bounds, clicking one updates both fields, no horizontal
overflow (`scrollWidth` == `clientWidth` == 390), and the popular-route chips still set
origin/destination and auto-submit correctly after the selector change. Added
`test_flights_page_offers_trip_length_presets` to `app_tests.py`. Full suite (157 tests,
up from 156) passes.

### 2026-08-25 — preset chips show which one is active
A fourth full read-through of `backend/flights/` this run (models, service, cache,
validation, ranking, insights, airports, rate_limit, providers/aviasales, api, errors)
found nothing new — same conclusion as the last three passes. §26 is still fully met, and
the two data-dependent roadmap items (thin-route re-check, V1.3 price history) both still
need more than the ~1 day of real traffic the token has accumulated since going live
2026-08-24, so neither is ready yet.

Did find one real UI gap in last run's own addition: the trip-length preset chips
(`#trip-length-presets`) updated the min/max nights fields on click but gave no visual
confirmation afterwards — unlike the popular-route chips, which auto-submit and so make
their effect obvious immediately, a preset click's only feedback was two number inputs
changing value, easy to miss on a small screen. Added `aria-pressed` tracking: a chip
shows as selected (new `.chip[aria-pressed="true"]` style, reusing the site's existing
`#4da3ff` accent) exactly when the current min/max nights values match its bounds, kept in
sync via `syncPresetSelection()` on preset click, on manual edits to either nights field
(so hand-typing a value that no longer matches clears the selected state, and typing one
that does match highlights it), and on page load (so a saved-search URL or the plain
5–8-night default shows its matching preset as already selected).

Verified in a real browser (Playwright against the dev server) at 390px: page load shows
"5–8 days" pre-selected (matches the default 5/8 night values); clicking "Weekend trip"
selects it and deselects the others while setting the fields to 2/3; manually editing
minimum nights to a value with no matching preset clears every chip's selected state; no
horizontal overflow; no console errors beyond the pre-existing missing-favicon 404. Added
an `aria-pressed="false"` assertion to `test_flights_page_offers_trip_length_presets`.
Full suite (157 tests) passes.
