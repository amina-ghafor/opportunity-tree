"""AI Incident Database adapter (weekly snapshot, no auth required).

AIID publishes no documented API, but does publish a weekly Excel export
that has already joined each incident to its taxonomy classifications. That
is the better source anyway: one download, no rate limits, and identical
results on every re-run, so anyone can reproduce the numbers in this repo.

The snapshot date is pinned deliberately. Always fetching "latest" would let
the corpus shift under the codebook between runs, which would quietly
invalidate any comparison built on it.
"""

import datetime
import urllib.request
from pathlib import Path

import openpyxl

from src.schema import Record

SNAPSHOT_DATE = "20260831"  # pinned; bump deliberately, not automatically
SNAPSHOT_URL = (
    "https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/"
    f"AIID_Excel_Export-{SNAPSHOT_DATE}.xlsx"
)

# repo root is three levels up from this file (src/sources/ai_incident_db.py)
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# The CDN rejects urllib's default Python-urllib UA with a 403.
USER_AGENT = "opportunity-tree/0.1 (research pipeline; contact via github.com/amina-ghafor)"

# Cuts the corpus to the generative-AI era. Measured 4 Sep 2026: this drops
# the corpus from 1,654 to 951 incidents but *raises* MIT label coverage
# from 77.1% to 84.3%, since recent incidents get labelled faster. Trade-off
# worth knowing: the domain mix shifts hard toward Malicious Actors & Misuse
# (46% of the recent set vs. 34% overall), and Socioeconomic & Environmental
# Harms drops to 9 incidents - thin for the codebook to still recognise.
SINCE_DATE = datetime.datetime(2024, 1, 1)


def ensure_snapshot() -> Path:
    """Return the local path to the pinned snapshot, downloading it if absent.

    The file is cached in data/raw/ (gitignored) so repeated runs do no
    network traffic. Delete the file to force a re-download.
    """
    local_path = RAW_DIR / f"aiid-{SNAPSHOT_DATE}.xlsx"
    if local_path.exists():
        return local_path

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(SNAPSHOT_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        local_path.write_bytes(resp.read())
    return local_path


def fetch(since: datetime.datetime = SINCE_DATE) -> list[Record]:
    """Read the snapshot and return one Record per incident on/after `since`.

    The Incidents sheet has two banner rows before the real header (a title
    row, then a column-group row), so data starts at row 4 - openpyxl's
    values_only iterator makes skipping them a plain next() twice.

    MIT Risk Domain/Subdomain are ground truth for the eval and go in meta,
    never in text. They must not reach the classifier - see the schema.py
    docstring on why the shape stays source-agnostic.
    """
    path = ensure_snapshot()
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Incidents"]

    rows = ws.iter_rows(values_only=True)
    next(rows)  # row 1: title banner
    next(rows)  # row 2: column-group banner
    headers = next(rows)  # row 3: real headers
    col = {h: i for i, h in enumerate(headers)}

    records: list[Record] = []
    for row in rows:
        date = row[col["date"]]
        if not isinstance(date, datetime.datetime) or date < since:
            continue
        description = row[col["description"]]
        if not description:
            continue  # a handful of rows have every field but this one

        records.append(
            Record(
                id=f"aiid:{row[col['Incident ID']]}",
                source="ai_incident_db",
                text=description,
                date=date.date().isoformat(),
                rating=None,
                weight=max(1, row[col["report_count"]] or 1),
                meta={
                    "title": row[col["title"]],
                    "deployer": row[col["deployer"]],
                    "harmed": row[col["harmed"]],
                    "mit_risk_domain": row[col["Risk Domain"]],
                    "mit_risk_subdomain": row[col["Risk Subdomain"]],
                },
            )
        )
    return records


if __name__ == "__main__":
    recs = fetch()
    print(f"fetched {len(recs)} incidents since {SINCE_DATE.date()}")
    labeled = sum(1 for r in recs if r.meta["mit_risk_domain"])
    print(f"{labeled} carry an MIT risk domain ({labeled / len(recs) * 100:.1f}%)")
