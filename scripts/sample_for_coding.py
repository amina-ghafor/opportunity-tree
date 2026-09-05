"""Blind-coding sample: pulls a seeded random slice of AIID records for
hand-reading, with all taxonomy fields (meta) stripped out.

This is the "blind" half of the two-pass method - the point is naming
themes from the text alone, before ever looking at the MIT labels. So this
script never prints or writes meta; only description, date, and id.

Usage:
    python3 -m scripts.sample_for_coding [N]

Output goes to data/processed/coding_sample.md (gitignored), formatted so
you can write your theme directly under each record.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.sources.ai_incident_db import fetch

SEED = 42  # fixed, so re-running gives the same sample - not a fresh draw each time
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "coding_sample.md"


def main(n: int = 25) -> None:
    records = fetch()
    rng = random.Random(SEED)
    sample = rng.sample(records, n)

    lines = [
        f"# Blind coding sample (seed {SEED}, n={n})",
        "",
        "No MIT labels here on purpose. Read each one, write your own theme",
        "underneath it, don't look anything up until you're done.",
        "",
    ]
    for i, rec in enumerate(sample, start=1):
        lines += [
            f"## {i}. {rec.date or 'undated'}",
            rec.text,
            "",
            "**My theme:** ",
            "",
            "---",
            "",
        ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines))
    print(f"wrote {n} records to {OUT_PATH}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    main(n)
