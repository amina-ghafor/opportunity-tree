# Opportunity Tree Pipeline

I built this to run my own product-discovery method end to end, not as a one-off exercise. As a PM, I take a corpus of user feedback and turn it into an [opportunity tree](https://www.producttalk.org/opportunity-solution-tree/): Teresa Torres' framework of an outcome, the opportunities underneath it, and the solutions underneath those, each one backed by evidence.

The method runs in two passes. First, I read a sample of the corpus blind, without looking at any existing taxonomy, and build my own list of recurring themes: a codebook. Second, I classify the full corpus against that codebook, then spot-check a slice by hand to see how well it held up. That spot-check is the eval.

Any source can feed this pipeline, as long as it produces the same shape of record (see `schema.py` below). I'm demonstrating it here on AI-failure-mode feedback: real incident reports plus first-hand posts from people describing problems with AI tools.

## Where it stands

Sources are working. Classification and the front end aren't built yet.

- `ai_incident_db.py`: reads a public database of documented AI-harm incidents.
- `reddit.py`: pulls Reddit posts.
- `app_store.py`: pulls App Store reviews. I'm dropping this one as I move off resale-marketplace data.
- `schema.py`: the one record shape every source has to produce (id, source, text, date, rating, weight, meta). Nothing downstream needs to know which source a record came from.

Run any adapter directly to see it pull live data, e.g. `python3 -m src.sources.ai_incident_db`.

## Why two sources

The interesting part of this method isn't any single classification pass. It's deciding which source to trust when two disagree, and being honest about what's actually validated versus assumed versus guessed: an evidence hierarchy. I picked two sources of very different quality on purpose, one curated and verified, one raw and high-volume, because that contrast is what actually tests the method.

## Next

- Finish moving the Reddit adapter onto its official API. Blocked for now on registering the API app, see the commit log.
- Retire the App Store adapter.
- Read a sample blind and build the codebook.
- Classify the full corpus, then spot-check.
- Map the codebook onto the tree.
- Front end: Next.js, TypeScript, React Flow, static data, deployed on Vercel.
