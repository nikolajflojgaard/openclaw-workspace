# Rolex Denmark dealer monitor

Goal: track official Rolex authorized dealers in Denmark, store the latest snapshot, overwrite it on every run, and notify Nikolaj here only when something changes.

## Source strategy
Use web search results from rolex.com because Rolex blocks simple HTTP scraping from this environment.

Run these searches:
1. `site:rolex.com/rolex-dealers/ denmark rolex`
2. `site:rolex.com "Official Rolex Retailer" Denmark rolex.com`
3. `site:rolex.com/store-locator/denmark rolex`

## What counts as a dealer
Keep only rolex.com URLs that clearly represent a Denmark dealer page.

Include URLs that match patterns like:
- `https://www.rolex.com/rolex-dealers/...-denmark`
- `https://www.rolex.com/en-gb/rolex-dealers/...-denmark`
- `https://www.rolex.com/en-us/rolex-dealers/...-denmark`

Exclude:
- `.../service/...`
- `.../watch-care-and-service/...`
- `.../store-locator/...`
- subpages like `buying-a-rolex`, `buy-a-rolex-watch`, `purchasing-a-rolex`, `servicing-your-rolex`, `the-rolex-guarantee`, `rolex-certified-pre-owned`

Normalize each dealer to this shape:
```json
{
  "name": "store name from title or snippet",
  "city": "city inferred from URL/snippet/title",
  "url": "canonical rolex dealer URL"
}
```

Sort by `city`, then `name`, then `url`.

## State files
- Snapshot: `state/rolex-denmark-dealers.json`
- Audit log: `state/rolex-denmark-dealers-history.jsonl`

## Run steps
1. Read this file.
2. Search using the queries above.
3. Build the normalized dealer list.
4. Read `state/rolex-denmark-dealers.json` if it exists.
5. Compare old vs new by normalized URL set and by dealer objects.
6. Overwrite `state/rolex-denmark-dealers.json` with:
```json
{
  "updatedAt": "ISO timestamp",
  "source": "web_search rolex.com result aggregation",
  "dealers": []
}
```
7. Append one JSON line to `state/rolex-denmark-dealers-history.jsonl` with timestamp, count, and change summary.

## Notification rules
- First-ever run: create baseline and reply exactly `NO_REPLY`.
- No change: reply exactly `NO_REPLY`.
- Change detected: send a short Telegram-friendly alert.

Alert format:
```text
Rolex Denmark dealer change detected.

Added:
- ...

Removed:
- ...

Current dealers:
- City — Name
- City — Name
```

If only metadata looks different but the dealer set is materially the same, do not alert.

## Quality bar
Be conservative. False alerts are worse than missing minor wording differences.
