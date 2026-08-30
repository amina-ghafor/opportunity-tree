# Opportunity Tree Pipeline

Turn a corpus of unstructured user feedback into a validated opportunity tree: real complaints, clustered into themes, checked against each other, mapped to product opportunities you can act on.

The tree structure follows [Teresa Torres' Opportunity Solution Tree](https://www.producttalk.org/opportunity-solution-tree/): outcome → opportunities → solutions, evidence-backed. This repo is a from-scratch build of the discovery method I use as a PM to populate one: two-pass classification (blind extraction → codebook → classify at scale → spot-check), a validation taxonomy, and an evidence hierarchy for when sources disagree. The method is source-agnostic. The worked example here is a corpus of AI-failure-mode feedback: curated incident reports plus first-hand accounts from AI-tool communities. The pipeline takes any adapter that produces the same record shape.

**Status: early build.** The source adapters currently pull a resale-marketplace corpus and are being repointed to AI-failure feedback (see [What's next](#whats-next)). `src/schema.py` does not change in that move — that is the point of the normalised shape. Classification, tree-building and the front end are not built yet. Details below reflect what actually runs today, not the eventual scope.

## What works today

- `src/sources/reddit.py` — pulls Reddit submissions. Currently via [pullpush.io](https://pullpush.io) against resale subreddits; being migrated to the official Reddit API (OAuth) against AI-tool communities (see [What's next](#whats-next)).
- `src/sources/app_store.py` — pulls App Store reviews via the public iTunes RSS feed. Part of the resale corpus; being removed in the migration.
- `src/schema.py` — the normalised `Record` shape every adapter produces (id, source, text, date, rating, weight, meta). Everything downstream reads this shape and never touches source-specific fields, which is what keeps the pipeline able to take a new source without changing anything else.

Run an adapter directly to see it pull live data:

```bash
python3 -m src.sources.reddit
```

## What's next

- Repoint the corpus to AI-failure-mode feedback:
  - `src/sources/ai_incident_db.py` — new adapter for the [AI Incident Database](https://incidentdatabase.ai/) (CC-BY, curated and structured incident reports).
  - `src/sources/reddit.py` — move to the official Reddit API (OAuth) and to r/ClaudeAI, r/ChatGPT, r/OpenAI, r/GeminiAI, r/LocalLLaMA. Usernames stripped on ingest; raw corpus not committed.
- Blind extraction pass: sample and hand-code a subset to build the initial codebook.
- Classify the full corpus against the codebook, spot-check a held-out set (this is the eval).
- Map codebook themes onto an opportunity tree, output as structured data.
- Front end (Next.js + TypeScript, React Flow for the tree) reading the tree as static JSON.

## Why this shape

The interesting part of this method isn't any single classification pass, it's the evidence hierarchy: knowing which source to trust when two sources disagree, and being explicit about what's validated versus assumed versus a guess. Two sources of different quality (AI Incident Database: curated, verified, structured, low-volume; Reddit: raw, unverified, high-volume, variable signal) exist here specifically to demonstrate that, not just to pad the corpus.
