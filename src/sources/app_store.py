"""App Store review adapter (iTunes RSS, no auth required).

Reviews are heavily skewed positive (this app scored ~90% 5-star in
single-country testing) because the platform prompts for a review after a
completed transaction, not after a problem. Pulling multiple countries is
the fix for volume: each storefront is a separate 500-review cap.
"""

import json
import time
import urllib.request

from src.schema import Record

PAGE_SIZE = 50
MAX_PAGES_PER_COUNTRY = 10  # iTunes RSS caps at 500 reviews/country


def fetch(app_id: int, countries: list[str], delay: float = 0.15) -> list[Record]:
    records: list[Record] = []
    for country in countries:
        for page in range(1, MAX_PAGES_PER_COUNTRY + 1):
            url = (
                f"https://itunes.apple.com/{country}/rss/customerreviews/"
                f"page={page}/id={app_id}/sortby=mostrecent/json"
            )
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    data = json.load(resp)
            except Exception:
                break

            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                break

            for entry in entries:
                if "im:rating" not in entry:
                    continue  # first entry on page 1 is the app metadata, not a review
                records.append(
                    Record(
                        id=f"app_store:{country}:{entry['id']['label']}",
                        source="app_store",
                        text=f"{entry['title']['label']}. {entry['content']['label']}",
                        date=entry.get("updated", {}).get("label"),
                        rating=int(entry["im:rating"]["label"]),
                        meta={"country": country, "version": entry.get("im:version", {}).get("label")},
                    )
                )
            time.sleep(delay)
    return records


if __name__ == "__main__":
    VINTED_APP_ID = 632064380
    COUNTRIES = ["gb", "us", "fr", "de", "es", "it", "nl", "pl", "be", "pt"]
    recs = fetch(VINTED_APP_ID, COUNTRIES)
    print(f"fetched {len(recs)} records across {len(COUNTRIES)} storefronts")
