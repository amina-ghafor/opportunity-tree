# Opportunity Tree Pipeline

Turn a corpus of unstructured user feedback into a validated opportunity tree: real complaints, clustered into themes, checked against each other, mapped to product opportunities you can act on.

The tree structure follows [Teresa Torres' Opportunity Solution Tree](https://www.producttalk.org/opportunity-solution-tree/): outcome → opportunities → solutions, evidence-backed. This repo is a from-scratch build of the discovery method I use as a PM to populate one: two-pass classification (blind extraction → codebook → classify at scale → spot-check), a validation taxonomy, and an evidence hierarchy for when sources disagree. The method is source-agnostic. This repo demonstrates it on public reviews and Reddit posts about a resale marketplace app, but the pipeline takes any adapter that produces the same record shape.

**Status: early build.** Source adapters are working and pulling real data. Classification, tree-building and the front end are not built yet, in progress. Details below reflect what actually runs today, not the eventual scope.

## What works today

- `src/sources/app_store.py` — pulls App Store reviews via the public iTunes RSS feed, no auth. Single-country feeds are heavily positive-skewed (this platform prompts for a review after a completed transaction, not after a problem), so this pulls multiple storefronts for volume and complaint density.
- `src/sources/reddit.py` — pulls Reddit submissions via [pullpush.io](https://pullpush.io), a public mirror. Reddit's own API blocks unauthenticated requests from some networks; this doesn't.
- `src/schema.py` — the normalised `Record` shape every adapter produces (id, source, text, date, rating, weight, meta). Everything downstream reads this shape and never touches source-specific fields, which is what keeps the pipeline able to take a new source without changing anything else.

Run either adapter directly to see it pull live data:

```bash
python3 -m src.sources.app_store
python3 -m src.sources.reddit
```

## What's next

- Blind extraction pass: sample and hand-code a subset to build the initial codebook.
- Classify the full corpus against the codebook, spot-check a held-out set (this is the eval).
- Map codebook themes onto an opportunity tree, output as structured data.
- Front end (Next.js + TypeScript, React Flow for the tree) reading the tree as static JSON.

## Why this shape

The interesting part of this method isn't any single classification pass, it's the evidence hierarchy: knowing which source to trust when two sources disagree, and being explicit about what's validated versus assumed versus a guess. Two sources of different quality (App Store: short, high-volume, low signal; Reddit: longer, lower-volume, higher signal) exist here specifically to demonstrate that, not just to pad the corpus.
