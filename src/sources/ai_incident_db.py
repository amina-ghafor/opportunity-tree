"""AI Incident Database adapter (weekly snapshot, no auth required).

AIID publishes no documented API, but does publish a weekly Excel export
that has already joined each incident to its taxonomy classifications. That
is the better source anyway: one download, no rate limits, and identical
results on every re-run, so anyone can reproduce the numbers in this repo.

The snapshot date is pinned deliberately. Always fetching "latest" would let
the corpus shift under the codebook between runs, which would quietly
invalidate any comparison built on it.
"""

import urllib.request
from pathlib import Path

SNAPSHOT_DATE = "20260831"  # pinned; bump deliberately, not automatically
SNAPSHOT_URL = (
    "https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/"
    f"AIID_Excel_Export-{SNAPSHOT_DATE}.xlsx"
)

# repo root is three levels up from this file (src/sources/ai_incident_db.py)
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# The CDN rejects urllib's default Python-urllib UA with a 403.
USER_AGENT = "opportunity-tree/0.1 (research pipeline; contact via github.com/amina-ghafor)"


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


if __name__ == "__main__":
    path = ensure_snapshot()
    print(f"snapshot at {path} ({path.stat().st_size / 1_000_000:.1f} MB)")
