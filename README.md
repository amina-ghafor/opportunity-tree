# Opportunity Tree Pipeline

Turns unstructured feedback into a validated [opportunity tree](https://www.producttalk.org/opportunity-solution-tree/): complaints clustered into themes, checked against each other, mapped to product opportunities.

This is my own two-pass method as a PM (blind extraction → codebook → classify at scale → spot-check), built from scratch as a real pipeline rather than a one-off exercise. The method is source-agnostic; any adapter that emits the shared `Record` shape can feed it. Worked example here: AI-failure-mode feedback, mixing curated incident reports with first-hand community accounts.

**Status: early build.** Source adapters only, no classification or front end yet.

## What works

- `src/sources/ai_incident_db.py` — reads the [AI Incident Database](https://incidentdatabase.ai/)'s weekly export: 1,654 curated, taxonomy-labelled incidents.
- `src/sources/reddit.py` — pulls Reddit submissions via [pullpush.io](https://pullpush.io) (currently r/vinted; migrating to official Reddit API + AI-tool subreddits, see below).
- `src/sources/app_store.py` — App Store reviews via iTunes RSS. Being retired as the corpus moves off resale-marketplace data.
- `src/schema.py` — the normalised `Record` shape (id, source, text, date, rating, weight, meta) every adapter produces. Downstream code only ever sees this shape.

Run an adapter directly to pull live data, e.g. `python3 -m src.sources.ai_incident_db`.

## Why this 

The interesting part isn't any single classification pass, it's the evidence hierarchy: knowing which source to trust when two disagree, and being explicit about validated vs. assumed vs. guessed. AIID (curated, verified, low-volume) and Reddit (raw, unverified, high-volume) exist specifically to demonstrate that.

## Next

- Finish repointing Reddit to the official API (OAuth) and AI-tool subreddits — blocked on registering a script app, see the commit log.
- Retire the App Store adapter.
- Blind extraction pass → codebook → classify full corpus → spot-check (the eval).
- Map codebook themes onto the opportunity tree.
- Front end: Next.js + TypeScript, React Flow, static JSON, deployed on Vercel.
