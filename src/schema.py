"""Normalised record shape every source adapter must produce.

One schema, many sources. This is what lets the pipeline stay source-agnostic:
extraction, classification and tree-building never see App Store or Reddit
specifics, only Record objects.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Record:
    id: str
    source: str          # "app_store" | "reddit" | ...
    text: str             # the primary text to classify
    date: str | None       # ISO 8601 if known
    rating: int | None     # 1-5 if the source has one, else None
    weight: int = 1        # signal strength proxy (e.g. upvotes), default 1
    meta: dict[str, Any] = field(default_factory=dict)  # source-specific extras

    def is_substantial(self, min_chars: int = 40) -> bool:
        return len(self.text.strip()) >= min_chars
