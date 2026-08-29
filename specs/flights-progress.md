# rayaq.ca/flights — implementation progress

Running log for the flights implementation routine. Read this first, update it last.
The contract is `specs/flights.md`; this file records where the code actually stands.

**Last updated:** 2026-08-29 — remove two more unreachable branches (`service.py`,
`insights.py`) and close the last real test-coverage gaps in `rate_limit.py` and
`insights.py`.

---

## Where things stand

V1 is built end to end and deployed through the normal `main` → CI/CD path. The page,
the API, the provider adapter, the SQLite cache, rate limiting, and the deterministic
insights all exist and are covered by tests (186 passing).

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
4. **Look for more code-cleanliness items,** per the routine's own priority order:
   duplicated logic, functions doing too much, or provider details leaking out of
   `providers/`. Sixteen consecutive full read-throughs of `backend/flights/` (2026-08-24,
   2026-08-25 x4, 2026-08-26 x3, 2026-08-27 x3, 2026-08-28 x3, 2026-08-29 x2) found twelve
   real issues, all now fixed: the `duration` type-check, the uncapped request body, the
   `X-Forwarded-For` trust direction, the dead `with_booking_url` method, the untested
   cheapest-weekday insight, the unpinned month-cap/window-size invariant, the
   all-or-nothing upstream-call failure handling at both the provider layer and the
   `service._search_pairs` fan-out layer, the degenerate same-airport pairs the
   nearby fan-out could synthesize, non-string `origin`/`destination`/`currency`
   values in the request body crashing validation with a 500 instead of a clean 400, and
   (this run) two more genuinely unreachable defensive branches (`service._place`,
   `insights._neighbour_saving`). The most recent pass found its remaining two issues not
   by reading but by running `coverage` and chasing every non-defensive gap it reported —
   that method is now clearly outperforming another blind read-through of the same
   ~1,450 lines; `flight_search_events` grows without pruning; at this site's traffic
   that's years away from mattering, so leave it be unless real growth numbers say
   otherwise.
5. **Watch how often the new price-history line actually appears.** It requires
   observations spanning at least 3 distinct days for the same real origin/destination
   pair and currency, so it will stay silent in production until the VM's traffic
   history (only ~1 day deep as of the token going live 2026-08-24) grows past that. No
   agent action needed — just note it in a future run once it's had time to accumulate.

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

### 2026-08-25 — local price history (§27 V1.3, pulled forward)
A fifth full read-through of `backend/flights/` found nothing new (same conclusion as
the last four), and both data-dependent items from the previous run's candidate list
(thin-route re-check, price history) still need more real traffic than the ~1 day the
token has accumulated. Rather than wait idle, built the read side of V1.3 now, gated so
it only activates once there is actually enough data behind it — the honest failure mode
the spec asks for (§30: "implement the subset supported by the free source, surface the
limitation honestly") applied to a feature waiting on its own data rather than a provider
gap.

Added `cache.price_history(origin, destination, currency, now=None)`: queries
`flight_price_observations` for the given real origin/destination/currency over the
trailing 30 days (`PRICE_HISTORY_WINDOW_DAYS`), and returns `None` unless the rows span
at least 3 distinct calendar days (`PRICE_HISTORY_MIN_OBSERVED_DAYS`) — otherwise a
same-day search would just echo its own live price back as "history". `service.py` wires
it into the response as `priceHistory`, keyed off the **Best Deal** card's own
origin/destination (`best.origin`/`best.destination`, the real airport pair actually
shown), not the searched request codes — the two differ whenever the searched code is a
metro code (`YTO`) or nearby-airport search substituted a real alternate, and observations
are themselves recorded against the real candidate airports, so querying by request code
would silently never match. Computed before the current search's own observation is
written, so a fresh route's very first search correctly shows nothing rather than
comparing today's price to itself.

`flights.js` renders `payload.priceHistory` as a muted line under the Best Deal card's
meta tags ("Our own search history shows a low of $540 CAD for this route in the last 30
days.") when present, and renders nothing when it is `null`. Verified in a real browser
(Playwright against the dev server, dependency not added to the project) at 390px with a
stubbed `/api/flights/search` response: the line renders with the expected text when
`priceHistory` is set, no `.price-history` node is added when it's `null`, no horizontal
overflow, no console errors beyond the pre-existing missing-favicon 404. Added 3 tests to
`flights_cache_tests.py` (withheld under 3 days, reported at 3 days, ignores stale/other-
currency rows) and 2 to `flights_service_tests.py` (absent, then correct once 3 prior
days exist). Full suite (162 tests, up from 157) passes.

This will stay silent on the live site until real traffic accumulates 3 distinct days of
observations for a given route/currency — expected soon given the token went live
2026-08-24, but not verifiable from this sandbox (egress to `rayaq.ca` is blocked here,
per the 2026-08-24 note).

### 2026-08-26 — cap the incoming request body size

A sixth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) found nothing
new — the package stays small and each module still does one thing. The two
data-dependent roadmap items (thin-route re-check, watching price history appear) both
still need more real traffic than this sandbox can observe (egress to `rayaq.ca` is
blocked here).

Widened the read to `app.py` itself and found a real gap against §18 Security's "cap
response payload sizes" requirement: the outbound side was already covered
(`aviasales.py`'s `MAX_RESPONSE_BYTES` refuses an oversized *provider* response, tested
by `test_oversized_payloads_are_refused`), but nothing capped the *inbound* side —
`POST /api/flights/search` read `request.get_json(silent=True)` with no limit on the
request body Werkzeug buffers into memory first. On an e2-micro VM with ~1 GB of RAM,
an arbitrarily large POST body to that one endpoint (the only route in this app that
accepts a body at all) is a real, cheap way to pressure the process before validation
ever gets a chance to reject the input on its merits.

Added `app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BODY_BYTES` (16 KiB — generous for
a search payload of a handful of short strings, dates, ints, and booleans) plus a `413`
error handler that returns the same `{"error": ...}` JSON shape as every other flights
error, rather than Flask's default HTML error page, since this is a JSON API. Added
`test_flights_search_rejects_an_oversized_request_body` to `app_tests.py`. Full suite
(163 tests, up from 162) passes.

No UI-facing change — a legitimate search body is a few hundred bytes at most, nowhere
near the new limit.

### 2026-08-26 — trust the rightmost `X-Forwarded-For` hop

A seventh full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) plus `app.py`
found one real issue in `flights_api.client_id()`, which decides the identity the §17
rate limiter counts against. It took `forwarded_for.split(",")[0]` — the leftmost entry.
`deploy/Caddyfile` has no `trusted_proxies` configured, and `rayaq.ca` sits behind exactly
one hop (Caddy, no CDN in front of it per the infra notes in `CLAUDE.md`), so the only
entry in that header a client cannot control is the one the trusted hop itself appends —
the rightmost one. Depending on the exact Caddy version's default handling of an
already-present client-supplied header (verified against Caddy's own docs was not
possible from this sandbox — `caddyserver.com` is on the egress blocklist), trusting the
leftmost entry ranges from a no-op (if Caddy discards/overwrites inbound values, which
recent Caddy versions do by default) to a free rate-limit bypass (if it appends, since a
client can put anything before Caddy's own value). There is no version of this
single-proxy deployment where trusting the leftmost entry over the rightmost one is more
correct, so switched `client_id()` to `split(",")[-1]` — behavior-identical when the
header only ever has one entry (which is likely already the case in production), strictly
safer otherwise. Updated the existing convention test (it modeled a two-hop chain and
was itself asserting the vulnerable behavior) and added
`test_the_forwarded_client_address_ignores_a_client_supplied_leftmost_hop`. Full suite
(164 tests, up from 163) passes.

Also confirmed this session's designated branch (`claude/adoring-newton-lsce8k`) had
already been fast-forward-merged into `main` in full (through "cap the incoming request
body size") with no open PR — `origin/main` and the branch tip were identical commits.
Restarted the branch from `origin/main` per this routine's standing instructions before
starting work, rather than stacking on top of already-merged history.

### 2026-08-26 — remove the dead `with_booking_url` method

This session's designated branch (`claude/adoring-newton-w217j6`) was also already
fast-forward-merged into `main` in full (through the previous entry above) with no open
PR — restarted it from `origin/main` before starting work, same as the prior run.

Confirmed no VM/production access exists from this sandbox this run either (no `gcloud`
CLI installed at all, so `vmrun.sh` cannot run here), so the two data-dependent roadmap
items (thin-route re-check, watching price history appear) still cannot be checked from
an agent session — no change from prior runs' notes.

An eighth full read-through of `backend/flights/`, this time also reading
`frontend/templates/flights.html` and `frontend/static/flights.js` line by line rather
than only spot-checking them in a browser, found one real issue:
`FlightCandidate.with_booking_url()` in `models.py` was dead code — added in the very
first commit of the domain layer (`2873b34`) and never called by `service.py`,
`providers/aviasales.py` (which sets `booking_url` directly via the constructor instead),
or any test. Removed the method and the now-unused `replace` import it was the only user
of. No behavior change; full suite (164 tests) still passes. Frontend files themselves
had no issues worth changing.

### 2026-08-27 — cover the untested cheapest-weekday insight

Confirmed this session's designated branch (`claude/adoring-newton-91zsdm`) was already
identical to `origin/main` (no unmerged commits) — no restart needed, just continued from
`origin/main`'s tip.

A ninth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) plus `app.py`
and the frontend (`flights.html`, `flights.js`) found the modules themselves unchanged
from the last several passes — no new logic bug. But cross-checking module logic against
`backend/tests/` surfaced a real coverage gap: `insights._cheapest_weekday` (the fourth
insight type, `"weekday"`, live in `insights.build()` on every real search) had zero test
coverage anywhere in the suite — no test asserted it fires, stays silent below the
`MIN_MEANINGFUL_SAVING` threshold, or produces the expected message. `date_prices`'s
`weekday` field was tested; the separate weekday insight was not. This is exactly the gap
CLAUDE.md's testing rule exists to catch ("write a test for every ... new piece of logic").

Added `test_insights_report_the_cheapest_weekday` (three candidates split across three
different weekdays with a >$15 average-price gap, asserting the `weekday` insight type and
its exact message) and `test_insights_stay_silent_on_a_weekday_split_too_small_to_act_on`
(same shape, gap under $15, asserting it does not fire) to `flights_domain_tests.py`. No
production code changed — this run confirmed existing behavior matches intent rather than
fixing a bug. Full suite (166 tests, up from 164) passes.

### 2026-08-27 — pin the month-cap/window-size invariant with a test

The designated branch (`claude/adoring-newton-uet06z`) had a stale local `origin/main`
ref pointing at an old commit (pre-dating the entire flights build); a fresh
`git fetch origin main` confirmed GitHub's actual `main` was already at this branch's
tip (`ba487bc`) with no divergence — a local caching artifact, not a real gap between
the branch and production.

A tenth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) plus `app.py`
and, for the first time this run, a complete line-by-line pass of `flights.html`,
`flights.js`, and `flights.css` found no new logic bug and no UI/mobile issue.

Chased one near-miss that turned out to be correct-but-unpinned: `aviasales.py`'s
`_months_in_window` caps at `MAX_MONTHS_PER_SEARCH = 3` months per search, while
`validation.MAX_WINDOW_DAYS = 60` lives in a different file. If a maximal-length window
could span 4 calendar months, the cap would silently drop the last month's dates from
every search touching it — no error, just quietly incomplete results, exactly the kind
of gap §12.2 warns against papering over. Worked the calendar math by hand: touching 4
months in a 60-day window needs two full consecutive months in the middle (minimum 59
days, achieved only by Jan+Feb or Feb+Mar) plus at least one day on each end (2 more),
i.e. 61 days minimum — one more than `MAX_WINDOW_DAYS` allows. So today's constants are
correct, but the relationship is implicit across two files with no test enforcing it;
bumping `MAX_WINDOW_DAYS` alone in a future run would silently reintroduce exactly this
bug. Added `test_the_month_cap_never_truncates_a_maximum_length_window` to
`flights_provider_tests.py`: it walks every possible start date across a leap and a
non-leap year and asserts `_months_in_window`'s output always matches the naturally
occurring (uncapped) month count for a `MAX_WINDOW_DAYS`-long window. Verified the test
actually catches a regression by temporarily lowering `MAX_MONTHS_PER_SEARCH` to 2 in a
throwaway REPL check (685 mismatches), then confirmed the real code has none. Full suite
(167 tests, up from 166) passes.

### 2026-08-27 — tolerate a single failed upstream call within one pair search

Confirmed this session's designated branch (`claude/adoring-newton-xbml0r`) was identical
to `origin/main`'s tip (`ed64839`) — no restart needed. A stale local `origin/main` cache
from an earlier failed compound `git fetch` briefly looked like `main` was missing the
entire flights feature; re-fetching `origin/main` on its own confirmed it was current and
matched `HEAD` exactly. No real divergence, just a local caching artifact from the failed
fetch command, noted here so a future run isn't alarmed by the same false signal.

An eleventh full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors), plus `app.py`
and the frontend (`flights.html`, `flights.js`), found one real robustness gap:
`AviasalesDataProvider.search_flexible_dates()` makes up to 4 upstream calls per pair
search (up to `MAX_MONTHS_PER_SEARCH` month calls plus one `/v2/prices/latest` call, per
the 2026-08-24 two-endpoint deviation), and a failure in any single one of them, a network
error, a 429, a malformed body, propagated immediately and discarded every candidate
already gathered from the calls that did succeed. The two-endpoint design exists
specifically because the endpoints are complementary for thin routes (deviation 4 in this
file); throwing away one endpoint's good data because the other endpoint hiccupped
defeats that purpose and contradicts the spec's "fails gracefully when the provider has
no data" — the provider often did have data, and the code discarded it anyway.

Changed `search_flexible_dates()` to catch `ProviderError` around each month call and the
latest-tickets call individually, keeping whatever candidates each successful call
contributed. Only when every call in a given pair search fails does it re-raise, the most
recently seen error, so a search where every call gets rate-limited still surfaces
`ProviderRateLimitedError` rather than a generic unavailable message, preserving the
existing distinction the two error types exist for. Verified against the existing
uniform-failure tests (`test_rate_limited_responses_raise_a_rate_limit_error`,
`test_error_responses_raise_provider_unavailable`, and friends), unchanged, since when
every call fails identically the new code still raises the same exception type as before.
Added `test_a_failed_latest_prices_call_does_not_discard_successful_month_data` and
`test_a_failed_month_call_does_not_discard_successful_latest_data`, each stubbing one
endpoint to 500 and the other to a real fixture, asserting the successful endpoint's
candidates still come through. Full suite (169 tests, up from 167) passes.

Also found, but did not fix, the same failure shape one layer up in `service.py`'s
nearby-airport pair fan-out, recorded as the next candidate increment below rather than
bundled into this commit, since it is opt-in (`includeNearby`) and a separate,
independent fix.

### 2026-08-28 — tolerate a single failed pair within a nearby-airport fan-out

Confirmed this session's designated branch (`claude/adoring-newton-veddej`) was identical
to `origin/main`'s tip (`6fd4791`) — no restart needed.

Picked up the increment flagged, but deliberately not fixed, at the end of the previous
run: `service._search_pairs`'s nearby-airport fan-out had the same all-or-nothing failure
shape that `AviasalesDataProvider.search_flexible_dates()` was fixed for one layer down.
When `includeNearby` is on, `service.search()` loops over up to 3 origin/destination pairs
(exact, nearby-origin, nearby-destination) calling `provider.search_flexible_dates()` for
each with no per-pair try/except; since the provider-level fix means that call now only
raises when *every* one of its own upstream calls failed, a single pair that was
completely unavailable (provider outage on just that route, or every one of its own
upstream calls rate-limited) still discarded whatever candidates the other, successful
pairs had already gathered.

Wrapped each pair's `provider.search_flexible_dates()` call in its own
`try`/`except ProviderError`, accumulating candidates from every pair that succeeds and
remembering the most recent error from any pair that fails. Only re-raises (preserving the
existing stale-cache-fallback/error-propagation behavior in `search()`) when literally
every pair failed, mirroring the fix shape used one layer down. For the common
`includeNearby=False` case there is exactly one pair, so behavior is unchanged: a single
failure still raises exactly as before.

Added `test_a_failed_nearby_pair_does_not_discard_the_other_pairs_candidates` (one pair
fails, two succeed, asserts both successful pairs' candidates are present) and
`test_nearby_search_only_fails_when_every_pair_fails` (all three pairs fail with different
error types, asserts the error from the last-attempted pair propagates, matching the
existing distinction between rate-limit and generic-unavailable errors). Extended the
existing `FakeProvider` test double with an `errors_by_pair` option rather than adding a
new fake, since `by_pair` already existed for per-pair candidates. Full suite (171 tests,
up from 169) passes.

### 2026-08-28 — skip degenerate same-airport pairs in the nearby fan-out

Confirmed this session's designated branch (`claude/adoring-newton-wn5lky`) was identical
to `origin/main`'s tip (`ab3ce25`) — no restart needed. (A first `git fetch origin main`
returned a stale cached ref pointing at an older commit, the same false-alarm pattern
noted in the 2026-08-27 entries; a forced re-fetch confirmed the real state matched.)

A thirteenth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors), `app.py`, and
the frontend (`flights.html`, `flights.js`, `flights.css`) found the modules themselves
still consistent with the last several passes — no new logic bug on inspection alone. Ran
`pyflakes` over `backend/flights/` and `app.py` (clean) and `coverage` over the full suite
(94% on the flights package, the gaps being defensive `except sqlite3.Error` branches and
a couple of untested `airports._match_rank` tiers — no real gap) to sanity-check that
manual read-throughs weren't missing something a tool would catch.

Manual reasoning about `service._search_pairs` turned up a real bug, not a proactive
check: with `includeNearby` on, it builds a pair from each of the *searched* origin/
destination plus every real nearby alternate on each side, but never checks whether the
resulting synthesized pair collapses origin and destination onto the same airport. The
bundled dataset makes this a live scenario, not a theoretical one — Toronto's two airports
are each other's only nearby alternate (`airports.nearby("YYZ") == [YTZ]` and
`airports.nearby("YTZ") == [YYZ]`, confirmed by hand), so a search from YYZ to YTZ (a
plausible real search: Pearson to the island airport, or vice versa) with nearby search on
synthesizes `_search_pairs` = `[("YYZ", "YTZ"), ("YTZ", "YTZ"), ("YYZ", "YYZ")]` — two of
the three pairs ask the provider to search an airport against itself. `_search_pairs`
builds these sub-requests with `dataclasses.replace()` directly, bypassing
`validation.parse()`'s existing origin != destination check entirely, so nothing catches
it before it reaches the provider. Best case this wastes two of the three upstream calls
on a query Aviasales has no meaningful answer for; worst case a same-airport query returns
provider-side error or garbage data folded into the results as if it were a real nearby
alternate.

Fixed by having `_search_pairs` skip any synthesized pair where the resulting origin
equals the resulting destination, and (cheaply, since the guard was already there) dedupe
against pairs already queued — a defensive measure for airport data denser than today's
`NEARBY_LIMIT = 1` might later produce duplicate pairs, not something reachable today.
Verified the fix against the same YYZ/YTZ scenario by hand
(`service._search_pairs(...)` now returns exactly `[("YYZ", "YTZ")]`) and added
`test_nearby_fan_out_skips_a_pair_that_would_search_an_airport_against_itself`, which
asserts the provider is called exactly once for that route pair rather than three times.
Confirmed the existing three-pair nearby tests (SFO/OAK, none of whose synthesized pairs
collapse) are unaffected. Full suite (172 tests, up from 171) passes.

### 2026-08-28 — reject non-string origin/destination/currency instead of crashing

Confirmed this session's designated branch (`claude/adoring-newton-thhg0f`) was identical
to `origin/main`'s tip (`44b40f9`) — no restart needed.

A fourteenth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) plus `app.py`
found a real gap in `validation.py`, the one module that turns an untyped JSON body into a
typed `SearchRequest`. `_require_code` computed `(payload.get(field) or "").strip().upper()`
and the currency line did the same with `DEFAULT_CURRENCY` as the fallback — both assume
the raw value is either falsy or already a string. Neither holds for a JSON body a client
fully controls: `{"origin": 123, ...}` is valid JSON, passes the existing
`isinstance(payload, dict)` check and the `MAX_CONTENT_LENGTH` cap, and then hits
`123 .strip()`, an `AttributeError` that nothing in `flights_api.search_response` catches
(it only handles `FlightSearchError`, `TooManyRequestsError`, `ProviderError`), so it
propagates as an unhandled 500. §16 of the spec lists "unknown airport" and "unsupported
currency" as clean 400s; a non-string value for the same fields should be no different, and
should certainly not crash the process. Confirmed the crash by hand before fixing it
(`validation.parse({"origin": 123, ...})` raised `AttributeError: 'int' object has no
attribute 'strip'`). `_require_date` and `_require_nights` were already safe — the former
type-checks before touching the value, the latter's `int()` conversion already raises a
caught `TypeError`/`ValueError` for a non-numeric type. Checked every other `.strip()`/
`.upper()`/`.lower()` call in the package: `airports.py` and `service.py`'s copies all
operate on values already known to be strings (Flask's `request.args` query-string values,
or a value already validated by `validation.parse`), so this was the only reachable gap.

Fixed by type-checking the raw value before calling any string method: `_require_code` now
raises `FlightSearchError` immediately when the field isn't a `str`, and the currency line
does the same, raising when a non-`None` currency value isn't a string, treating `None`
exactly as before (falls back to `DEFAULT_CURRENCY`). Both reuse the same message students
already see for a missing/unknown value, since "not a string" and "empty" both mean the
field is not something the form could have produced honestly. Added
`test_parse_rejects_a_non_string_origin_instead_of_crashing`,
`test_parse_rejects_a_non_string_destination_instead_of_crashing`, and
`test_parse_rejects_a_non_string_currency_instead_of_crashing` to
`flights_domain_tests.py`. Full suite (175 tests, up from 172) passes.

### 2026-08-29 — remove a dead validation branch, close the last real coverage gaps

Confirmed this session's designated branch (`claude/adoring-newton-bbee3q`) was identical
to `origin/main`'s tip (`47ad3dc`) — no restart needed.

A fifteenth full read-through of `backend/flights/` (models, service, cache, validation,
ranking, insights, airports, rate_limit, providers/aviasales, api, errors) plus `app.py`
found no new logic bug — consistent with the last several passes. Instead of a sixteenth
read-through with the same diminishing returns the previous few runs already flagged, ran
`pyflakes` (clean) and `coverage` over the full suite, same sanity-check tooling the
2026-08-28 run used, and actually chased every non-defensive gap `coverage` reported rather
than treating the 94% headline number as good enough.

Two real findings in `validation.py`, the module that turns an untyped JSON body into a
typed `SearchRequest`:

1. `_require_date`'s `isinstance(value, date)` fast path was dead code. `validation.parse`
   has exactly one caller in the whole repo, `service.search()`, whose `payload` always
   comes from `request.get_json()` — JSON has no native date type, so `earliestDeparture`/
   `latestDeparture` can only ever arrive as strings (or be absent/malformed). No test
   exercised this branch either. Removed it, mirroring the 2026-08-26 removal of the dead
   `with_booking_url` method — same shape of finding, a defensive branch nothing can ever
   reach.
2. The malformed-date, missing-date, negative-nights, non-numeric-nights, and
   whitespace-only-airport-code error paths in `_require_code`/`_require_date`/
   `_require_nights` were all reachable from `POST /api/flights/search` with an ordinary
   malformed request body, and none of them had a test — a real gap against CLAUDE.md's
   "write a test for every ... piece of logic" rule, not a hypothetical one. Added
   `test_parse_rejects_a_whitespace_only_origin`,
   `test_parse_rejects_a_missing_departure_date`,
   `test_parse_rejects_a_malformed_departure_date`,
   `test_parse_rejects_negative_trip_length`, and
   `test_parse_rejects_a_non_numeric_trip_length` to `flights_domain_tests.py`.
   `validation.py` is now at 100% line coverage (was 88%).

Also closed the last two real gaps in `models.py`: `FlightCandidate.nights` returning
`None` for a one-way candidate, and `dedupe_key` preferring `raw_provider_id` when a
provider supplies one (Aviasales never does today — confirmed against both fixtures, which
carry no ticket-level ID field — so this exercises the interface's forward-looking branch
for a future provider, per spec §12.3's "or provider ID where available"). Added
`test_a_candidate_without_a_return_date_has_no_nights` and
`test_dedupe_key_prefers_the_provider_id_when_one_is_supplied`. `models.py` is now at 100%
line coverage (was 96%).

Remaining coverage gaps (86-97% in `cache.py`, `insights.py`, `providers/aviasales.py`,
`providers/base.py`, `rate_limit.py`, `airports.py`) are the same ones the 2026-08-28 run
already characterized as legitimately defensive: `except sqlite3.Error` branches around
every cache operation, `providers/base.py`'s abstract-interface stub, network-error paths
in the provider that would need a real socket failure to hit, and a couple of
`airports._match_rank` tiers below what the bundled 206-airport dataset's real
city/country names happen to trigger. Left those alone — chasing 100% on defensive code
that only exists for a failure mode a fixture can't cheaply fabricate is not what this
project's coverage bar is asking for.

Full suite (182 tests, up from 175) passes. `pyflakes` over `flights/` and `app.py` stays
clean.

### 2026-08-29 — two more dead branches, two more real coverage gaps (via `coverage`, not reading)

Confirmed this session's designated branch (`claude/adoring-newton-2odc8r`) did not exist
on the remote yet, so it started fresh from `origin/main`'s tip (`86a591e`). A first
`git log --oneline origin/main` showed a stale cached ref pointing at a much older,
pre-flights commit — the same false-alarm pattern noted repeatedly in this log's
2026-08-26/27/28 entries. `git ls-remote origin` and a forced `git fetch origin main`
confirmed the real `refs/heads/main` matched this branch's tip exactly; no restart needed.

Rather than a seventeenth full manual read-through of `backend/flights/` — the 2026-08-28
and 2026-08-29 (earlier) entries already flagged diminishing returns from that method —
went straight to `coverage run -m pytest` and chased every line it flagged that wasn't
already characterized as defensive, the same tool-assisted method the previous run used
to close out `validation.py`/`models.py`. Two real findings, both the same dead-branch
shape as `with_booking_url` and the `_require_date` isinstance check:

1. `service._place(code)` had a `if entry is None: return {"code": code, ...}` fallback.
   `_place` is only ever called with `request.origin`/`request.destination`
   (`_build_payload`, lines 157-158), and both are required to satisfy
   `airports.is_known()` by `validation.parse()` before a `SearchRequest` can exist at
   all — `is_known` is defined as exactly `find(code) is not None`, so `airports.find()`
   can never return `None` for a value that already passed `is_known()`. No test reached
   the branch either. Removed it.
2. `insights._neighbour_saving()` had an `if not neighbours: return None` guard after
   building `neighbours` from `ordered[position - 1]`/`ordered[position + 1]`. The
   function already returns early when fewer than two distinct departure dates exist, so
   by the time `neighbours` is built, `len(ordered) >= 2` and `position` is a valid index
   into it — brute-forced every `(length, position)` pair up to 30 to confirm at least one
   of `position - 1`/`position + 1` is always in range whenever `length >= 2`, so
   `neighbours` can never be empty. Removed it.

Also closed two real, non-defensive coverage gaps `coverage` surfaced:

- `rate_limit.check()`'s hour-old-hit pruning loop (`while hits and now - hits[0] > 3600:
  hits.popleft()`) had no test — the existing hourly-cap test never ran long enough for
  any hit to actually expire. Added
  `test_rate_limiting_drops_hourly_history_once_it_expires`, and verified it actually
  catches a regression by temporarily neutering the prune loop and watching the test fail
  before restoring it.
- `insights._best_trip_length()`'s "difference too small to act on" branch had no test,
  unlike the equivalent silence tests already in place for the date-shift and weekday
  insights (`test_insights_stay_silent_on_trivial_differences`,
  `test_insights_stay_silent_on_a_weekday_split_too_small_to_act_on`). Added
  `test_insights_stay_silent_on_a_trip_length_difference_too_small_to_act_on`.

Also added `test_form_defaults_corrects_a_query_window_with_departend_before_departstart`
and `test_form_defaults_swaps_query_nights_given_in_the_wrong_order` to
`flights_service_tests.py` — found by inspection while tracing `_place`'s only callers,
not by `coverage` (both branches execute either way they're taken, so `coverage` can't see
that only one side was ever tested): a saved-search URL's `departStart`/`departEnd` and
`minNights`/`maxNights` query parameters are validated independently, so nothing stopped a
hand-edited or stale link from supplying an end date before its start date, or a minimum
above the maximum. `form_defaults()` already swaps/corrects both cases correctly; only the
tests were missing.

`service.py`, `rate_limit.py`, and `insights.py` are now all at 100% line coverage.
`pyflakes` over `flights/` and `app.py` stays clean. Full suite (186 tests, up from 182)
passes. Pushed as four small commits (two dead-code removals, two test-only additions),
each independently green.

The two data-dependent roadmap items (thin-route re-check on real traffic, watching local
price history appear) remain unverifiable from this sandbox, same as every prior run — no
`gcloud`/VM access and `rayaq.ca`/`travelpayouts.com` are both on the egress blocklist here.
