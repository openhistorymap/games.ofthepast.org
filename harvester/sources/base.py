"""Enricher-plugin contract (identical machinery to the rulers siblings).

There is a single, ordered **spine** — the curated games loaded from `seed.json`
(built by `build_seed.py`) — and each plugin *enriches every game in place* from a
different upstream (Wikipedia, Wikidata, …).

So a plugin is an `Enricher`: `run(games, ctx)` walks the shared `games` list,
fills fields (mostly inside each game's `context`), and returns a status dict.
Per-plugin failure is isolated by the orchestrator: an exception in one enricher
is caught and recorded as `stale` in the manifest; the spine and every other
enricher's output survive. The curated content is always authoritative — an
enricher only *adds* (an image, a link, an encyclopedic extract); it never
overwrites a curated blurb or a rule.

`ctx` is a plain dict the orchestrator threads through every enricher, for sharing
cheap derived state (e.g. resolved QIDs) between stages.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Enricher:
    name: str                                   # stable id: "wikidata", "wikipedia"
    title: str                                  # human description (logs/manifest)
    run: Callable[[list, dict], dict]           # (games, ctx) -> status dict
