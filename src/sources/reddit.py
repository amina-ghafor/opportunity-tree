"""Reddit adapter, via pullpush.io (a Pushshift-style mirror).

Reddit's own API and old.reddit.com both hard-block unauthenticated requests
from some networks (403, not a rate limit). pullpush.io indexes the same
public data without that restriction. Pulls submissions; comments are a
richer follow-up source not yet wired in (see README known gaps).
"""

import json
import urllib.request

from src.schema import Record

BASE_URL = "https://api.pullpush.io/reddit/search/submission/"


def fetch(subreddit: str, size: int = 100, sort_type: str = "score") -> list[Record]:
    url = f"{BASE_URL}?subreddit={subreddit}&size={size}&sort=desc&sort_type={sort_type}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)

    records: list[Record] = []
    for post in data.get("data", []):
        body = post.get("selftext", "") or ""
        title = post.get("title", "")
        text = f"{title}. {body}".strip()
        records.append(
            Record(
                id=f"reddit:{post['id']}",
                source="reddit",
                text=text,
                date=None,  # pullpush returns created_utc; convert if needed downstream
                rating=None,
                weight=max(1, post.get("score", 1)),
                meta={
                    "num_comments": post.get("num_comments", 0),
                    "score": post.get("score", 0),
                    "permalink": post.get("permalink"),
                    "created_utc": post.get("created_utc"),
                },
            )
        )
    return records


if __name__ == "__main__":
    recs = fetch("vinted", size=100)
    substantial = [r for r in recs if r.is_substantial()]
    print(f"fetched {len(recs)} posts, {len(substantial)} with substantial text")
