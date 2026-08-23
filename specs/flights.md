# rayaq.ca/flights — Product & Technical Design Specification

**Status:** V1 build specification  
**Target:** `https://rayaq.ca/flights`  
**Primary constraint:** **$0 in additional recurring API or infrastructure costs**  
**Existing paid infrastructure allowed:** the `rayaq.ca` domain and the existing GCP VM  
**Last researched:** August 23, 2026

---

## 1. Project Description

### 1.1 High-level idea

Build a lightweight, mobile-first flight discovery tool at:

> **`rayaq.ca/flights`**

The tool should help a user answer a simple question:

> **"What are the cheapest flights between these two places within the dates I am willing to travel?"**

The initial product should focus on **flight discovery**, not booking.

A user specifies:

- an origin
- a destination
- a flexible travel window
- optionally, preferred trip length and basic filters

The application then searches available flight-price data, normalizes the results, and highlights the most attractive date combinations.

The main value is not merely displaying a list of flights. The value is helping someone quickly identify:

- the cheapest days to leave
- the cheapest days to return
- the cheapest date combinations
- whether shifting a trip by one or two days materially lowers the price
- which deal is the best combination of price, stops, and timing when that information is available

The product should initially be useful for recurring personal searches such as:

- Toronto ↔ San Francisco
- Toronto ↔ San Jose / Bay Area
- Canada ↔ international vacation destinations
- other routes used by friends and family

The project should be designed as a polished feature of the existing `rayaq.ca` website rather than as a separate company, mobile app, or booking engine.

---

### 1.2 Core product philosophy

V1 should be:

1. **Useful**
2. **Fast**
3. **Mobile-first**
4. **Extremely cheap to operate**
5. **Simple enough to finish**
6. **Provider-agnostic internally**
7. **Honest about price freshness**

Do not attempt to reproduce all of Google Flights.

The goal is to build the smallest product that genuinely improves flexible-date flight discovery.

---

### 1.3 Hard operating-cost constraint

This requirement is non-negotiable:

> **The project must introduce $0 of additional recurring spend.**

The only expenses assumed to already exist are:

- `rayaq.ca`
- the current GCP VM hosting the existing backend

Therefore V1 must not require:

- a paid flight API
- a paid database
- Railway
- Vercel Pro
- Supabase Pro
- Firebase paid usage
- Redis Cloud
- a paid geocoding API
- a paid analytics product
- any service that automatically bills after a free quota is exceeded

A service with a free tier is **not automatically acceptable** if exceeding that tier can silently incur charges.

Prefer APIs/services that are free by design, or design the application so that a paid service is completely optional and disabled by default.

---

## 2. Product Goals

### 2.1 Primary V1 goal

Allow a user to enter an origin, destination, and flexible date criteria and quickly discover the cheapest available travel dates.

A successful V1 lets a user go from:

> "I want to go from Toronto to San Francisco sometime around these dates."

to:

> "Leaving Tuesday and returning the following Wednesday appears to be about $140 cheaper than my original dates."

within a few seconds.

---

### 2.2 User goals

The user should be able to:

1. Search by origin and destination.
2. Specify a flexible travel window.
3. See the cheapest date combinations found.
4. Compare dates visually.
5. Sort results by price.
6. Understand whether returned pricing is live or cached.
7. Open an external provider to verify/book the itinerary.
8. Use the site comfortably from a phone.

---

### 2.3 Engineering goals

The project should demonstrate:

- clean full-stack architecture
- API integration
- provider abstraction
- caching
- rate limiting
- mobile-responsive UI
- error handling
- sensible backend API design
- data normalization
- external-service resilience
- production deployment on an existing VM
- cost-aware engineering

---

### 2.4 Success criteria for V1

V1 is successful when all of the following are true:

- `rayaq.ca/flights` is publicly accessible.
- Search works well on a phone.
- A user can search common routes without manually entering IATA codes.
- Flexible-date searches return meaningful low-price results when the provider has data.
- Results clearly indicate that cached/indicative prices may have changed.
- Results contain enough information to compare candidate dates.
- Users can click through to verify/book externally.
- No new paid infrastructure exists.
- No API can unexpectedly generate a bill.
- Provider-specific code is isolated behind a clean interface.
- The application fails gracefully when the provider has no data.

---

## 3. V1 Scope

### 3.1 Required features

#### Search form

Fields:

- **From**
  - airport or city
  - examples: `YYZ`, `Toronto`, `SFO`, `San Francisco`
- **To**
  - airport or city
- **Departure window**
  - earliest departure date
  - latest departure date
- **Trip length**
  - minimum number of nights
  - maximum number of nights
- **Currency**
  - default based on simple app setting
  - initially support at least CAD and USD
- **Direct flights only**
  - optional toggle

Recommended defaults:

- 1 adult
- economy
- round trip
- all airlines
- stops allowed

---

### 3.2 Why use a departure window + trip length

A flexible traveler generally thinks:

> "I can leave between September 10 and September 20, and I want to stay about 5–8 days."

This is more useful than requiring one exact departure and one exact return date.

Internally:

```text
departure_date ∈ [earliest_departure, latest_departure]

trip_duration ∈ [min_nights, max_nights]

return_date = departure_date + trip_duration
```

This lets the application rank multiple valid trip combinations.

If the chosen provider cannot directly search arbitrary combinations, the backend should derive the best combinations from the available price/date dataset.

---

### 3.3 Results view

The default result should emphasize the **best deals**, not dump raw provider data.

Each result card should show, when available:

- total price
- currency
- departure date
- return date
- trip length
- airline
- direct vs. stops
- origin
- destination
- last-seen / freshness timestamp
- external verification link

Example:

```text
$487 CAD
Toronto → San Francisco

Tue Sep 15 → Tue Sep 22
7 nights
1 stop

Price last seen 8 hours ago

[Check current price]
```

---

### 3.4 Recommended result sections

#### A. Best Deal

One visually prominent card containing the cheapest valid trip.

#### B. Cheapest Options

A ranked list of the top 5–10 candidate date combinations.

#### C. Flexible Date View

A simple visual representation of cheap vs. expensive departure dates.

V1 does **not** require a complex Google-Flights-style matrix.

A simple bar chart, row of date chips, or small calendar heat display is sufficient.

#### D. Smart Insight

Generate deterministic insights from the returned data.

Examples:

> Leaving Sep 15 instead of Sep 16 saves approximately $82.

> The cheapest departure day in your window is Tuesday.

> Trips of 7 nights are averaging less than trips of 5 nights in this search.

These should initially come from normal code, not an LLM.

---

## 4. Smart Discovery

### 4.1 V1 interpretation of "smart"

"Smart discovery" should **not** initially mean artificial intelligence.

V1 intelligence should come from:

- comparing dates
- ranking prices
- detecting meaningful savings
- evaluating trip lengths
- grouping results
- clearly surfacing the best tradeoffs

This is faster, cheaper, deterministic, and costs nothing.

---

### 4.2 Candidate ranking

Start with a simple ranking model.

For each valid candidate itinerary:

```text
price_score = normalized total price
stop_penalty = optional penalty for additional stops
duration_penalty = optional penalty for unusually long total travel times
freshness_penalty = small penalty for older cached prices
```

For V1, ranking primarily by price is sufficient:

```text
score = total_price
```

Later:

```text
score =
    total_price
    + stop_penalty
    + travel_duration_penalty
    + stale_price_penalty
```

Keep the score explainable.

---

### 4.3 Deal insights

The backend should calculate useful comparisons such as:

#### Cheapest departure date

```text
min(price grouped by departure date)
```

#### Savings versus neighboring dates

```text
neighbor_savings =
    selected_date_price - cheaper_neighbor_price
```

#### Best trip duration

Group results by trip length and compare:

```text
5 nights → lowest $620
6 nights → lowest $540
7 nights → lowest $487
8 nights → lowest $515
```

Then surface:

> 7 nights is currently the cheapest trip length in this window.

---

## 5. Explicit Non-Goals for V1

These should **not** be built unless the rest of V1 is already complete.

### No booking

The site will not:

- collect payment
- issue tickets
- manage bookings
- handle refunds
- handle cancellations

Users should be redirected to an airline, OTA, or search provider.

---

### No hotels

Do not build:

- hotel search
- hotel booking
- flight + hotel packages

This can be a future project phase.

---

### No user accounts

V1 does not need:

- login
- Sign in with Google
- profiles
- stored payment methods

---

### No saved searches

Do not add saved searches until the core discovery experience works well.

---

### No email or push alerts

Price alerts require scheduled searches and create additional provider/API complexity.

Defer them.

---

### No AI dependency

Do not require OpenAI, Anthropic, Gemini, or another paid model to run the product.

Any future AI functionality must be optional.

---

### No scraping Google Flights in the initial production architecture

Do not make production reliability depend on scraping Google's consumer interface.

Reasons:

- fragile markup and request formats
- bot detection
- Terms-of-Service concerns
- unpredictable breakage
- difficult reliability characteristics

Experimental scraping code may be explored separately, but should not be the V1 production provider.

---

### No infrastructure migration

Keep the project on the existing GCP VM.

Do not migrate to Railway for this implementation.

Railway can be reconsidered later if traffic or developer ergonomics justify it.

---

## 6. Flight Data API Research

Flight data is the most important technical constraint in this project.

There is no single perfect, free, unrestricted, consumer-grade API that replicates Google Flights.

The architecture must acknowledge this.

---

### 6.1 Google Flights

#### Decision

**Do not use Google Flights as the V1 data provider.**

Google does not expose a normal public consumer API that lets arbitrary developers query Google Flights fares the way the consumer website does.

Google has travel-related partner infrastructure, but its flight-search ecosystem is partner-facing rather than a simple self-service consumer search API.

Google does expose the **Travel Impact Model API**, which is public and free, but that API provides flight **emissions estimates**, not fare-search results.

#### Future use

The Travel Impact Model API could later enrich flight results with CO₂ information at no API cost.

Source:

- https://developers.google.com/travel/impact-model

---

### 6.2 Travelpayouts / Aviasales Data API

#### V1 recommendation

**Use the Aviasales Data API through Travelpayouts as the preferred first provider.**

Why:

- Travelpayouts is free to join.
- There are no setup or monthly platform charges.
- The Aviasales **Data API** is listed as not requiring brand approval.
- It exposes cached flight-price information.
- It includes flexible-date-oriented methods.
- Rate limits are high enough for a small personal/friends-and-family application.
- It fits the project's $0 incremental cost requirement.

Important limitation:

> This is cached discovery data, not guaranteed live pricing.

Travelpayouts states that its Data API is based on search-history cache. Data can be stored for several days, and some endpoints expose fares found within a more recent interval.

That is acceptable for this project because the goal is **discovery**, followed by external verification.

#### Particularly useful endpoint

`/aviasales/v3/prices_for_dates`

This endpoint can return low-priced tickets for specific date/month criteria and is a good starting point for route/date discovery.

The Data API also contains:

- month price matrices
- price-range searches
- popular destinations
- grouped prices
- latest-price datasets

#### Rate limits

As currently documented, `prices_for_dates` supports a generous per-minute request limit, making application-level caching easy and sufficient for this scale.

#### Access model

The developer should:

1. Create a free Travelpayouts account.
2. Create a project for `rayaq.ca`.
3. Connect/use the Aviasales program as made available to the project.
4. Obtain the API token.
5. Store the token only on the backend.

Never expose the token in frontend JavaScript.

Sources:

- https://support.travelpayouts.com/hc/en-us/articles/11395179019538-How-to-join-Travelpayouts
- https://support.travelpayouts.com/hc/en-us/articles/203956163-Aviasales-Data-API
- https://support.travelpayouts.com/hc/en-us/articles/20384016664594-Brands-that-provide-access-to-APIs-and-data-feeds-for-Travelpayouts-partners
- https://support.travelpayouts.com/hc/en-us/articles/4402565416594-API-rate-limits

---

### 6.3 Aviasales Search API

Travelpayouts also documents an Aviasales **Search API** for more real-time flight search.

Do not make this a V1 dependency.

Reasons:

- approval is required
- there are usage requirements
- searches must be user initiated
- booking links and result display are governed by specific rules
- conversion-rate requirements apply
- access can be disabled if requirements are violated

This may be a future enhancement if the project gains real usage.

Source:

- https://support.travelpayouts.com/hc/en-us/articles/34788165535250-Search-API-usage-rules

---

### 6.4 Skyscanner APIs

Skyscanner technically offers an excellent API for this product.

Two relevant services exist:

#### Flights Indicative Prices API

Very well aligned with flexible-date discovery.

It supports:

- cached cheapest prices
- date aggregation
- month-level comparisons
- route aggregation
- exploratory searches

Skyscanner explicitly describes this API as useful when a traveler does not know the exact destination or exact travel dates.

#### Flights Live Prices API

Returns more current/bookable results for exact route/date searches.

#### Why it is not the V1 default

API access requires an application to Skyscanner's Partnerships team.

Therefore:

- access is not guaranteed
- it introduces an external approval dependency
- it should not block the V1 build

If Skyscanner approves `rayaq.ca` and confirms that the intended usage has no API charge, it may become the preferred provider later.

The code architecture should make this swap easy.

Sources:

- https://developers.skyscanner.net/docs/getting-started/authentication
- https://developers.skyscanner.net/docs/flights-indicative-prices/overview
- https://developers.skyscanner.net/docs/flights-live-prices/overview
- https://developers.skyscanner.net/docs/getting-started/rate-limits

---

### 6.5 Amadeus Self-Service APIs

Amadeus offers strong flight search APIs and a developer-friendly self-service product.

However, it does **not** meet the strict production-cost requirement cleanly.

Amadeus provides a free monthly request quota, but in production:

> usage beyond the free quota is billed.

That creates exactly the type of accidental-variable-cost exposure this project is trying to avoid.

The Amadeus test environment does not solve the problem because its dataset is limited and is intended for testing/prototyping rather than a public production application.

Therefore:

**Do not use Amadeus as the production V1 provider.**

It may remain useful for local experimentation.

Sources:

- https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/faq/
- https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/pricing/

---

### 6.6 Provider decision table

| Provider | Flexible-date data | Live pricing | Cost fit | Access friction | V1 decision |
|---|---:|---:|---:|---:|---|
| Travelpayouts / Aviasales Data API | Yes | No / cached | Excellent | Low | **Primary V1** |
| Aviasales Search API | Yes | Yes | Potentially good | High / approval + rules | Future |
| Skyscanner Indicative | Excellent | Cached | Potentially good | Partnership approval | Future |
| Skyscanner Live | Exact dates | Yes | Potentially good | Partnership approval | Future |
| Amadeus Self-Service | Yes | Yes | Poor for hard $0 constraint | Low | Reject for production V1 |
| Google Flights consumer data | Excellent | Yes | N/A | No normal public API | Not available |
| Google Travel Impact Model | N/A | N/A | Free | Low | Optional emissions enrichment |

---

## 7. Provider Abstraction

Do **not** scatter provider-specific response parsing throughout application code.

Create a provider interface.

Conceptually:

```ts
interface FlightSearchProvider {
  searchFlexibleDates(input: FlexibleFlightSearchInput): Promise<FlightSearchResult>;
}
```

Normalized request:

```ts
type FlexibleFlightSearchInput = {
  origin: string;
  destination: string;

  earliestDeparture: string;
  latestDeparture: string;

  minNights: number;
  maxNights: number;

  currency: "CAD" | "USD";
  directOnly?: boolean;
};
```

Normalized candidate:

```ts
type FlightCandidate = {
  origin: string;
  destination: string;

  departureDate: string;
  returnDate?: string;

  totalPrice: number;
  currency: string;

  airlineCode?: string;
  flightNumber?: string;

  stops?: number;
  durationMinutes?: number;

  source: string;
  foundAt?: string;
  expiresAt?: string;

  bookingUrl?: string;
  rawProviderId?: string;
};
```

Normalized response:

```ts
type FlightSearchResult = {
  provider: string;
  searchedAt: string;
  isLive: boolean;
  freshnessMessage: string;

  candidates: FlightCandidate[];

  metadata?: {
    cacheHit?: boolean;
    providerRequests?: number;
  };
};
```

Implement:

```text
providers/
  aviasalesDataProvider
```

Future:

```text
providers/
  aviasalesSearchProvider
  skyscannerProvider
  amadeusProvider
```

The rest of the application should depend only on normalized application models.

---

## 8. Existing Site / Repository Strategy

The implementing agent should **inspect the existing `rayaq.ca` codebase before changing frameworks**.

Do not rewrite the site merely to implement `/flights`.

The preferred rule is:

> Extend the current stack unless there is a strong technical reason not to.

The site already has routes such as:

- `/`
- `/resume`
- `/assembly-agent`
- the existing weather project

Add:

- `/flights`

Reuse the existing:

- build system
- CSS strategy
- server
- deployment mechanism
- HTTPS setup
- reverse proxy
- frontend framework

If the current site uses plain HTML/CSS/JS, V1 can be built in that stack.

If it already uses React/Next/Vue/etc., extend the existing framework.

Avoid introducing framework churn.

---

## 9. Recommended Architecture

```text
                         rayaq.ca
                             |
                     Existing reverse proxy
                             |
             +---------------+---------------+
             |                               |
       Existing pages                  /flights
                                             |
                                    Browser UI
                                             |
                                   /api/flights/*
                                             |
                                  Existing backend
                                      on GCP VM
                                             |
                              Flight Provider Adapter
                                             |
                          Travelpayouts / Aviasales API
                                             |
                                      SQLite cache
                                      on same VM
```

---

### 9.1 Why server-side provider calls

All flight-provider calls must come from the backend.

Benefits:

- hides API tokens
- enables caching
- enables rate limiting
- lets providers be replaced
- protects upstream rate limits
- allows normalized responses
- prevents browser users from directly abusing API credentials

---

## 10. Backend API Design

Recommended endpoints:

---

### `GET /api/flights/airports`

Purpose:

Autocomplete airport/city input.

Example:

```http
GET /api/flights/airports?q=tor
```

Response:

```json
{
  "results": [
    {
      "code": "YTO",
      "name": "Toronto",
      "type": "city",
      "country": "Canada"
    },
    {
      "code": "YYZ",
      "name": "Toronto Pearson International Airport",
      "type": "airport",
      "city": "Toronto",
      "country": "Canada"
    }
  ]
}
```

Prefer a bundled/open airport dataset rather than a paid geocoding/autocomplete service.

---

### `POST /api/flights/search`

Request:

```json
{
  "origin": "YTO",
  "destination": "SFO",
  "earliestDeparture": "2026-09-10",
  "latestDeparture": "2026-09-20",
  "minNights": 5,
  "maxNights": 8,
  "currency": "CAD",
  "directOnly": false
}
```

Response:

```json
{
  "provider": "aviasales-data",
  "searchedAt": "2026-08-23T22:00:00Z",
  "isLive": false,
  "freshnessMessage": "Indicative fares based on recently observed prices.",
  "best": {
    "origin": "YTO",
    "destination": "SFO",
    "departureDate": "2026-09-15",
    "returnDate": "2026-09-22",
    "totalPrice": 487,
    "currency": "CAD",
    "stops": 1
  },
  "candidates": [],
  "insights": [
    {
      "type": "date_shift",
      "message": "Leaving one day earlier may save about $82."
    }
  ]
}
```

---

### `GET /api/flights/health`

Purpose:

Basic provider/application diagnostics.

Return only safe information:

```json
{
  "status": "ok",
  "providerConfigured": true
}
```

Never return API keys or tokens.

---

## 11. Airport Data

Do not use a paid places API just to resolve airports.

Use a local airport dataset bundled with the application.

Good options include an open/public IATA airport dataset, subject to its license.

Store fields such as:

```text
iata_code
airport_name
city
country
latitude
longitude
timezone
```

Search should tolerate:

```text
Toronto
YYZ
YTO
San Francisco
SFO
San Jose
SJC
```

V1 autocomplete can be entirely local and therefore free.

---

## 12. Flexible-Date Search Algorithm

The provider may not return every possible departure/return permutation in one request.

The backend should own the flexible-date logic.

---

### 12.1 Generate valid date combinations

Given:

```text
earliestDeparture = Sep 10
latestDeparture   = Sep 20

minNights = 5
maxNights = 8
```

Generate candidate combinations:

```text
Sep 10 → Sep 15
Sep 10 → Sep 16
Sep 10 → Sep 17
Sep 10 → Sep 18

Sep 11 → Sep 16
Sep 11 → Sep 17
...
```

However:

> Do not blindly make one upstream request for every combination.

Use provider capabilities and caching to minimize calls.

---

### 12.2 Provider-specific strategy

For Aviasales Data API:

1. Query route/date datasets at the broadest supported granularity.
2. Normalize all returned tickets.
3. Filter locally:
   - departure within desired window
   - return date exists
   - trip length within requested bounds
   - direct-only if requested
4. Deduplicate.
5. Sort by price.
6. Return top N.

If data is missing for some dates:

- do not fabricate a price
- do not treat missing data as expensive
- simply show that no recently observed price was available for that date

---

### 12.3 Deduplication

Create a stable candidate key, e.g.:

```text
origin
+ destination
+ departureDate
+ returnDate
+ airlineCode
+ totalPrice
```

or provider ID where available.

---

## 13. Caching Strategy

Caching is important even when the upstream provider is free.

Goals:

- reduce latency
- avoid unnecessary provider calls
- protect rate limits
- improve reliability
- enable future price-history features

---

### 13.1 Use SQLite

Use a local SQLite database on the existing VM.

Advantages:

- no additional bill
- no service to operate
- persistent
- sufficient for current scale
- easy to back up
- simple to query

Do not deploy a separate Postgres service solely for V1.

If the existing application already runs a database, reusing it is acceptable.

---

### 13.2 Cache key

A search cache key should include:

```text
provider
origin
destination
date criteria
currency
directOnly
```

Example:

```text
aviasales:YTO:SFO:2026-09-10:2026-09-20:5:8:CAD:false
```

---

### 13.3 Cache TTL

Because the provider data itself may already be cached, a reasonable application cache is:

```text
30–60 minutes
```

Do not imply that this makes prices live.

Store:

```text
requested_at
provider_fetched_at
expires_at
normalized_payload
```

---

### 13.4 Stale-if-error behavior

If:

- upstream API is unavailable
- rate limited
- temporarily failing

and a cached search exists:

Return stale cached data with an explicit message:

> Showing previously observed prices because the flight-data service is temporarily unavailable.

This makes the app much more resilient.

---

## 14. Suggested SQLite Schema

### `flight_search_cache`

```sql
CREATE TABLE flight_search_cache (
    cache_key TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    request_json TEXT NOT NULL,
    response_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
```

---

### `flight_price_observations`

Optional but strongly recommended.

```sql
CREATE TABLE flight_price_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    return_date TEXT,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    airline_code TEXT,
    stops INTEGER,
    provider TEXT NOT NULL,
    observed_at TEXT NOT NULL
);
```

This creates the foundation for future price history **without introducing any additional service cost**.

---

## 15. UI / UX Specification

### 15.1 Overall feel

The page should feel:

- clean
- fast
- modern
- lightweight
- native on mobile
- consistent with the rest of `rayaq.ca`

Avoid a giant travel-industry-looking interface.

This is a personal product with a focused purpose.

---

### 15.2 Mobile first

A significant portion of actual usage will likely happen from a phone.

Design the page at approximately 390 px width first.

Then enhance desktop layout.

---

### 15.3 Initial screen

Suggested hierarchy:

```text
Flights

Find the cheapest dates for your next trip.

[ From                         ]
[ To                           ]

Departure window
[ Sep 10 ]     [ Sep 20 ]

Trip length
[ 5 nights ]   [ 8 nights ]

[ ] Direct flights only

[ Find cheap flights ]
```

---

### 15.4 Quick-route shortcuts

Because this is initially a personal tool, add optional shortcuts:

```text
Popular
[ Toronto → San Francisco ]
[ San Francisco → Toronto ]
```

Do not hard-code these into core logic; they should simply prefill the form.

---

### 15.5 Loading state

Search may take a moment.

Show:

- skeleton cards
- progress indicator
- rotating plain-language state text if desired

Example:

```text
Checking recent fares…
Comparing flexible dates…
Finding the cheapest combinations…
```

Do not fake percentages.

---

### 15.6 Empty state

If no data is available:

```text
We couldn't find a recently observed fare for this route and date window.

Try:
• widening the departure window
• allowing more trip lengths
• searching nearby airports
```

This is preferable to showing misleading results.

---

### 15.7 Freshness disclosure

Always disclose pricing quality.

Example:

> **Indicative price** — this fare was recently observed and may have changed. Verify the current fare before booking.

If a `found_at` timestamp exists:

> Last observed 6 hours ago.

---

## 16. Error Handling

Define explicit application errors.

### Invalid input

Examples:

- destination equals origin
- departure range in the past
- latest departure before earliest departure
- `minNights > maxNights`
- unsupported currency
- unknown airport

Return HTTP `400`.

---

### Provider unavailable

Return a normalized `503` unless stale cache is available.

Frontend message:

> Flight data is temporarily unavailable. Try again shortly.

---

### Provider rate limited

Backend should:

1. detect `429`
2. avoid retry storms
3. return cached data if available
4. otherwise return a friendly temporary error

---

### No results

This is not a server error.

Return `200`:

```json
{
  "candidates": [],
  "message": "No recently observed fares were available for this search."
}
```

---

## 17. Application-Level Rate Limiting

Even with a free upstream API, protect the backend.

Suggested anonymous limit:

```text
10 flight searches / minute / IP
```

and optionally:

```text
100 searches / hour / IP
```

Choose values appropriate to actual traffic.

The goal is to stop:

- bots
- accidental loops
- scripted abuse

without affecting normal users.

Implement rate limiting locally in application memory or SQLite if necessary.

Do not add a paid Redis dependency.

---

## 18. Security

### Required

- API token stored in an environment variable
- no API token in browser bundle
- HTTPS only
- validate all input server-side
- escape/sanitize displayed provider text
- set outbound HTTP timeouts
- cap response payload sizes
- limit date-window size
- do not log secrets

Example environment variable:

```text
TRAVELPAYOUTS_API_TOKEN=...
```

---

### Maximum search window

Prevent pathological searches.

Suggested V1 limits:

```text
departure window ≤ 60 days
trip length ≤ 30 nights
```

These can be tuned later.

---

## 19. Zero-Cost Analytics

Do not add paid analytics.

V1 options:

### Simplest

Use standard backend logs.

Record:

```text
timestamp
route
origin
destination
search duration
cache hit/miss
candidate count
provider status
```

Do not log personal data unnecessarily.

---

### Optional

Create a tiny local SQLite table:

```sql
CREATE TABLE flight_search_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT,
    destination TEXT,
    searched_at TEXT NOT NULL,
    cache_hit INTEGER NOT NULL,
    result_count INTEGER NOT NULL
);
```

This is enough to learn:

- which routes are popular
- how often the tool is used
- cache hit rate
- failure rate

without another vendor.

---

## 20. GCP VM Deployment

V1 remains on the existing VM.

The implementing agent should first determine how the current backend is deployed.

Potential setup:

```text
Nginx
  └── existing rayaq.ca frontend/backend process
       └── new flights route + API endpoints
```

Do not create another VM unless technically unavoidable.

---

### 20.1 Deployment requirements

- reuse current VM
- reuse current domain
- reuse HTTPS certificate
- reuse existing reverse proxy
- add environment variable for provider token
- SQLite file stored in a persistent application-data path
- add logs
- restart through existing process manager

If the application currently uses:

- `systemd`
- Docker Compose
- PM2
- another process manager

follow the existing convention.

---

## 21. Performance Targets

For cached searches:

```text
target backend response: < 300 ms
```

For uncached upstream searches:

```text
target perceived result: < 3 seconds when provider responds normally
```

These are targets, not hard SLAs.

Frontend:

- render shell immediately
- do not block page load on provider data
- lazy-load nonessential visualizations
- keep JS bundle modest

---

## 22. Testing Strategy

### 22.1 Unit tests

Test:

- date-combination logic
- min/max night filtering
- price sorting
- direct-flight filtering
- deduplication
- insight generation
- provider normalization
- cache-key generation
- stale-cache decisions

---

### 22.2 Provider contract tests

Save sanitized provider fixtures.

Test:

```text
provider JSON
    ↓
normalization
    ↓
FlightCandidate[]
```

This prevents provider response changes from silently breaking the UI.

---

### 22.3 Backend integration tests

Test:

```text
POST /api/flights/search
```

for:

- valid query
- invalid origin
- invalid date range
- provider success
- provider no-results
- provider timeout
- provider 429
- cache hit
- stale-cache fallback

---

### 22.4 Frontend tests

At minimum manually test on:

- iPhone-sized viewport
- Android-sized viewport
- laptop
- Safari
- Chrome

Critical mobile checks:

- date inputs usable
- autocomplete usable
- cards do not overflow
- external link is obvious
- tap targets are large enough

---

## 23. Observability

Logs should make debugging possible without another monitoring bill.

Structured log example:

```json
{
  "event": "flight_search",
  "origin": "YTO",
  "destination": "SFO",
  "cacheHit": true,
  "provider": "aviasales-data",
  "providerLatencyMs": 0,
  "resultCount": 12,
  "durationMs": 48
}
```

Never log:

- provider API token
- full request headers
- sensitive user data

---

## 24. Recommended Project Structure

Adapt this to the existing repository rather than forcing it literally.

```text
src/
  flights/
    domain/
      types
      ranking
      insights
      validation

    providers/
      provider-interface
      aviasales-data-provider
      aviasales-normalizer

    cache/
      flight-cache

    api/
      search
      airports

    data/
      airports

    ui/
      FlightSearchForm
      FlightResults
      FlightResultCard
      FlexibleDateView
      PriceFreshnessNotice

    tests/
```

The important point is separation of:

- provider integration
- application/domain logic
- caching
- UI

---

## 25. Implementation Order

Build in this order.

### Phase 0 — Repository inspection

Before coding:

- determine frontend framework
- determine backend framework
- identify current deployment process
- identify routing structure
- identify CSS/styling convention
- identify current environment-variable handling
- identify existing tests

Do not make architectural changes until this is understood.

---

### Phase 1 — Static UI

Implement `/flights` with mock data.

Build:

- origin input
- destination input
- departure window
- trip-length inputs
- direct-flight option
- search button
- results cards
- freshness message
- responsive mobile layout

No API dependency yet.

---

### Phase 2 — Airport autocomplete

Add local airport/city data.

Requirements:

- fast client/server search
- IATA code support
- name support
- keyboard navigation
- touch friendly

---

### Phase 3 — Flight provider integration

Implement:

```text
FlightSearchProvider
```

Then:

```text
AviasalesDataProvider
```

Keep raw provider code isolated.

---

### Phase 4 — Search normalization

Implement:

- validation
- provider requests
- normalization
- date filtering
- trip-length filtering
- deduplication
- price sorting

---

### Phase 5 — Caching

Add SQLite cache.

Verify:

- repeated query does not unnecessarily call provider
- expired entries refresh correctly
- stale data can be used during provider outage

---

### Phase 6 — Smart insights

Add deterministic insights.

Examples:

- cheapest departure date
- cheapest trip length
- nearby-date savings
- top 5 deals

---

### Phase 7 — Production hardening

Add:

- application rate limiting
- timeouts
- error states
- structured logging
- provider health handling
- input limits
- tests

---

### Phase 8 — Deploy

Deploy to existing GCP VM.

Verify:

- `https://rayaq.ca/flights`
- mobile Safari
- mobile Chrome
- desktop
- HTTPS
- secrets are not in client JS
- no new billing-enabled external service exists

---

## 26. Acceptance Criteria

The implementation is complete when:

### Search

- [ ] User can choose an origin.
- [ ] User can choose a destination.
- [ ] User can specify earliest/latest departure.
- [ ] User can specify minimum/maximum trip length.
- [ ] User can request direct-only results.
- [ ] Search input is validated.

### Results

- [ ] Cheapest result is clearly highlighted.
- [ ] Top alternatives are visible.
- [ ] Departure and return dates are clear.
- [ ] Prices and currencies are clear.
- [ ] Stops are displayed when available.
- [ ] Price freshness is disclosed.
- [ ] User can open an external page to verify/book.

### Smart discovery

- [ ] Results are ranked.
- [ ] Cheapest departure date is identified when possible.
- [ ] Useful date-shift savings are surfaced.
- [ ] No AI API is required.

### Engineering

- [ ] Provider implementation is abstracted.
- [ ] Provider credential exists only server-side.
- [ ] SQLite caching exists.
- [ ] Rate limiting exists.
- [ ] Provider failures are handled.
- [ ] No-results state is handled.
- [ ] Unit tests cover core date/ranking logic.
- [ ] Mobile layout is usable.

### Cost

- [ ] No new VM.
- [ ] No Railway service.
- [ ] No paid DB.
- [ ] No paid API dependency.
- [ ] No API with automatic overage billing enabled.
- [ ] No paid AI usage.
- [ ] Incremental recurring infrastructure cost is **$0**.

---

## 27. Future Roadmap

These are deliberately **not V1**.

### V1.1 — Nearby airports

Examples:

```text
Toronto → YTO / YYZ / YTZ
Bay Area → SFO / SJC / OAK
```

Allow:

> Include nearby airports

This could materially improve deals.

---

### V1.2 — Search presets

Examples:

```text
Weekend trip
5–8 days
7–14 days
Long weekend
```

---

### V1.3 — Local price history

Because observations are already stored in SQLite:

```text
YTO → SFO
$620
$590
$540
$487
```

Display:

> Lowest price we have observed in the last 30 days.

This adds product value without a new API.

Be precise that this is **our observed history**, not all market history.

---

### V1.4 — Saved URLs

Encode search criteria in the URL:

```text
/flights?from=YTO&to=SFO&departStart=2026-09-10&departEnd=2026-09-20&minNights=5&maxNights=8
```

Benefits:

- bookmarkable
- shareable with friends/family
- no accounts needed

---

### V1.5 — Skyscanner provider

If API access is approved and permitted at zero cost:

```text
AviasalesDataProvider
        ↓
SkyscannerIndicativeProvider
```

or use both only where provider terms permit.

Important:

Do not combine providers in ways that violate their API terms.

---

### V1.6 — Live-price verification

If a zero-cost, approved live-search provider becomes available:

1. use cached/indicative data for discovery
2. when the user selects one result, request a live refresh
3. display the current fare
4. then redirect for booking

This is the ideal long-term architecture.

---

### V2 — Anywhere discovery

Input:

```text
From: Toronto
Budget: $600
Departure: December
Trip length: 5–8 days
```

Output:

```text
Lisbon      $498
Reykjavik   $515
Los Angeles $524
Mexico City $537
```

This is potentially one of the most interesting future features.

Do not build it before origin→destination flexible search is strong.

---

### V2 — Price alerts

Potential feature:

> Tell me if YTO → SFO drops below $450.

This requires scheduled checks and should only be built after provider terms, quotas, and costs are clearly understood.

---

### V2 — Hotels

Eventually add:

```text
rayaq.ca/flights
        ↓
Found a flight
        ↓
Explore hotels for the same dates
```

Treat hotel discovery as a separate module/provider.

---

### V2 — AI trip assistant

Optional future layer:

> "I want somewhere warm from Toronto in January for under $700."

An AI layer could translate natural language into structured search parameters.

However:

- it must not be required for core search
- it should not compromise the $0-cost principle unless the cost policy changes

---

## 28. Important Product Copy

Use language like:

> **Recently observed fare**

rather than:

> **Current guaranteed price**

Use:

> Prices can change quickly. Verify the current fare before booking.

Do not imply that the application is an airline or travel agency.

---

## 29. Key Technical Decisions Summary

| Decision | Choice |
|---|---|
| Public URL | `rayaq.ca/flights` |
| Product type | Responsive website |
| Native iOS app | No |
| Hosting | Existing GCP VM |
| New hosting spend | $0 |
| Database | SQLite on existing VM, unless existing DB can be reused |
| Flight provider | Travelpayouts / Aviasales Data API first |
| Google Flights API | Not a V1 option |
| Skyscanner | Future provider if approved and zero-cost |
| Amadeus | Not production V1 due to possible overage billing |
| Booking | External only |
| Hotels | Not V1 |
| Accounts | Not V1 |
| Alerts | Not V1 |
| AI | Not required |
| UI strategy | Mobile-first |
| Search strategy | Flexible departure window + trip-length range |
| API credentials | Backend only |
| Provider architecture | Adapter/interface |
| Caching | SQLite, 30–60 minute application TTL |
| Analytics | Local logs / SQLite only |

---

## 30. Instructions to the Coding Agent

You are implementing this project in an **existing codebase**.

Before writing substantial code:

1. Inspect the repository.
2. Understand the current frontend/backend stack.
3. Understand how `rayaq.ca` routing works.
4. Understand how the GCP VM deploy currently works.
5. Reuse existing conventions wherever practical.

Then implement the project incrementally.

### Priorities

Optimize for:

1. a finished, useful V1
2. correctness
3. mobile usability
4. zero incremental cost
5. clean provider abstraction
6. maintainability

Do **not** optimize for theoretical scale.

Do **not** introduce infrastructure merely because it is fashionable.

Do **not** add a paid service when local code or the existing VM can solve the problem.

Do **not** make Google Flights scraping a required production dependency.

Do **not** implement booking.

Do **not** expand into hotels.

Do **not** add authentication.

### If the selected free provider cannot satisfy a requirement

Do not silently switch to a paid API.

Instead:

1. keep the provider abstraction intact
2. implement the subset supported by the free source
3. surface the limitation honestly in the UI
4. document the gap
5. leave a clean extension point for a future provider

The **$0 incremental cost constraint overrides feature completeness**.

---

## 31. Definition of the First Shippable Version

The first version worth deploying is intentionally small.

It should do this extremely well:

> A user opens `rayaq.ca/flights`, enters Toronto and San Francisco, selects a flexible departure window and desired trip length, presses Search, and receives a clean ranked list of recently observed cheap fares with the best dates highlighted and a link to verify the fare externally.

If that workflow is fast, clean, and reliable on a phone, **ship it**.

Everything else can come later.
