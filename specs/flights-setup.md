# rayaq.ca/flights — provider setup runbook

Everything in this file has to run **locally** (a machine with an authenticated
`gcloud`, or a shell on the VM). The Claude Code web/remote sandbox cannot do any of it:
it has no `gcloud`, no `ssh` client, no GCP credentials, and its egress proxy blocks
`travelpayouts.com`. The 6-hourly implementation routine runs in that same sandbox, so it
can write and test code but can never reach the VM or the live provider.

Until step 3 is done, `/flights` renders normally and reports that search is unavailable.
Nothing here is urgent or destructive; step 6 is a one-command rollback.

---

## 1. Get the Travelpayouts token (browser, not scriptable)

The Aviasales **Data API** is the V1 provider. It is free, and per the spec (§6.2) it does
not require brand approval — unlike the Search API, which does.

1. Sign up free at <https://www.travelpayouts.com> (no card, no plan).
2. Add `rayaq.ca` as a website/project in the dashboard.
3. Join the **Aviasales** program.
4. Copy two values from your account settings:
   - **API token** — account-level, used for every Data API endpoint.
   - **Marker** — your affiliate ID. Optional; it is only appended to outbound booking
     links so click-throughs are attributed. The app works fine without it.

Their dashboard layout changes from time to time, so navigate by those names rather than
by a fixed menu path. Step 2 below is the authoritative check that you got the right value.

---

## 2. Verify the token before it goes anywhere near the VM

Raw call — expect `"success": true` and a non-empty `data` array:

```sh
export TRAVELPAYOUTS_API_TOKEN='paste-token-here'

curl -sS "https://api.travelpayouts.com/aviasales/v3/prices_for_dates\
?origin=YTO&destination=SFO&departure_at=2026-10&currency=cad\
&sorting=price&direct=false&one_way=false&limit=5&token=$TRAVELPAYOUTS_API_TOKEN" \
  | python3 -m json.tool | head -40
```

`401`/`403` means the token is not active yet — usually the Aviasales program has not
finished connecting to your project. Wait and retry rather than switching providers.

Then run the real adapter against live data. This is the check that matters: it proves the
normalizer handles the actual payload, not just the fixture it was written against.

```sh
cd backend
[ -d venv ] || (python3 -m venv venv && ./venv/bin/pip install -r requirements-dev.txt)

TRAVELPAYOUTS_API_TOKEN="$TRAVELPAYOUTS_API_TOKEN" ./venv/bin/python3 -c "
from datetime import date, timedelta
from flights.models import SearchRequest
from flights.providers import get_provider

today = date.today()
request = SearchRequest(
    origin='YTO', destination='SFO',
    earliest_departure=today + timedelta(days=30),
    latest_departure=today + timedelta(days=44),
    min_nights=5, max_nights=8, currency='CAD', direct_only=False,
)
result = get_provider().search_flexible_dates(request)
print(result.provider, len(result.candidates), 'candidates', result.provider_requests, 'upstream calls')
for candidate in result.candidates[:5]:
    print(candidate.departure_date, candidate.return_date, candidate.total_price,
          candidate.currency, candidate.airline_code, 'stops=', candidate.stops,
          candidate.booking_url)
"
```

**If any field comes back empty or wrong** (prices `None`, `return_date` missing, stops
always `None`, booking URLs that 404): the live schema has drifted from
`backend/tests/fixtures/aviasales_prices_for_dates.json`. Update the fixture *and*
`backend/flights/providers/aviasales.py` together, in one commit, so the contract test
keeps pinning reality. Do not paper over it in the UI.

---

## 3. Put the token on the VM

Write the secret **interactively**, so it never lands in shell history, in a `ps` listing
on the VM, or in this repo:

```sh
gcloud compute ssh rayaq-server --project=rayaq-website --zone=us-central1-a
```

then, on the VM:

```sh
sudo install -d -o rayaq -g rayaq -m 755 /var/lib/rayaq-website
sudo touch /etc/rayaq-website.env
sudo chmod 600 /etc/rayaq-website.env      # systemd reads it as root before dropping to rayaq
sudo nano /etc/rayaq-website.env
```

Contents (template: `deploy/rayaq-website.env.example`):

```
TRAVELPAYOUTS_API_TOKEN=paste-token-here
TRAVELPAYOUTS_MARKER=paste-marker-or-leave-empty
```

Exit the SSH session.

---

## 4. Install the updated systemd unit

CI/CD deploys code, but it does not install unit files — same manual pattern as the
Caddyfile. The unit gained `EnvironmentFile=` and `FLIGHTS_DB_PATH`, so it needs copying
into place **once**:

```sh
./vmrun.sh 'cd /opt/rayaq-website && git pull'
./vmrun.sh 'sudo cp /opt/rayaq-website/deploy/rayaq-website.service /etc/systemd/system/rayaq-website.service'
./vmrun.sh 'sudo systemctl daemon-reload'
./vmrun.sh 'sudo systemctl restart rayaq-website'
```

---

## 5. Verify the deploy

```sh
./vmrun.sh 'curl -sS http://127.0.0.1:8000/api/flights/health'
```

Expect `{"status":"ok","providerConfigured":true}`. Then from anywhere:

```sh
curl -sS https://rayaq.ca/api/flights/health; echo
curl -sS -o /dev/null -w '%{http_code}\n' https://rayaq.ca/flights

curl -sS -X POST https://rayaq.ca/api/flights/search \
  -H 'Content-Type: application/json' \
  -d '{"origin":"YTO","destination":"SFO","earliestDeparture":"2026-10-01","latestDeparture":"2026-10-14","minNights":5,"maxNights":8,"currency":"CAD","directOnly":false}' \
  | python3 -m json.tool | head -40
```

Then confirm the supporting state and that the secret is not leaking:

```sh
./vmrun.sh 'ls -l /var/lib/rayaq-website/'                        # flights.db should appear after the first search
./vmrun.sh 'sudo journalctl -u rayaq-website -n 30 --no-pager'    # structured flight_search lines, no token
./vmrun.sh 'sudo journalctl -u rayaq-website --no-pager | grep -c TRAVELPAYOUTS'   # expect 0
curl -sS https://rayaq.ca/flights | grep -c TRAVELPAYOUTS         # expect 0
```

Finally open `https://rayaq.ca/flights` on a phone and run one real search. §22.4 asks for
mobile Safari and mobile Chrome; the automated pass only covered headless Chromium.

---

## 6. Rollback

```sh
./vmrun.sh 'sudo rm -f /etc/rayaq-website.env && sudo systemctl restart rayaq-website'
```

The page returns to reporting search as unavailable. The SQLite file is a cache and an
observation log — deleting `/var/lib/rayaq-website/flights.db` is harmless.

---

## 7. When it works

Update `specs/flights-progress.md`: drop the **Open owner actions** section, and record in
the run log whether the live payload matched the fixture. The routine reads that file every
six hours and will otherwise keep treating live verification as outstanding.
