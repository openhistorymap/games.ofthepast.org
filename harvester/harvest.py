"""Orchestrator for games.ofthepast.org.

Loads the spine (the curated games table, seed.json), runs each enricher in
`sources.REGISTRY` in isolation (a failing or disabled enricher is recorded in the
manifest; the spine and the other enrichers survive), then writes:

  - data/packs/<id>.json    the `boardgame/1.1` pack the JustPlay launcher loads
  - data/games/<id>.json    full per-game detail for the website (rules, context, pack)
  - data/games.json         compact index for the catalogue grid
  - data/manifest.json      generated_at, totals, categories, regions, per-source status

The curated content is authoritative; enrichers only add (an image, a link, an
encyclopedic extract). Run the whole thing offline — no network, curated content
only — with:

    GAMES_DISABLE=wikipedia,wikidata python -m harvester

Environment:
  GAMES_DISABLE=wikipedia,wikidata   skip these enrichers (comma-separated)
"""

import datetime
import json
import os
import time
import traceback
from collections import OrderedDict
from pathlib import Path

from . import sources
from .sources import seed

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
GAMES_DIR = DATA_DIR / "games"
PACKS_DIR = DATA_DIR / "packs"

LAUNCHER = "https://justplaybo.github.io/whitechapel/"
PACK_SCHEMA = "boardgame/1.1"
TITLE = "Games of the Past"

# fields promoted into the compact index (data/games.json)
INDEX_FIELDS = [
    "id", "name", "native", "category", "category_label", "origin", "region", "era",
    "players", "duration", "tagline", "reconstruction", "wp", "qid",
]


def _disabled():
    raw = os.environ.get("GAMES_DISABLE", "").strip()
    return {s.strip() for s in raw.split(",") if s.strip()}


def _pack_for(game):
    """Assemble the boardgame/1.1 pack the launcher consumes."""
    pack = {
        "schema": PACK_SCHEMA,
        "id": game["id"],
        "name": game["name"],
        "description": game.get("tagline", ""),
        "board": game["board"],
        "pieces": game.get("pieces", []),
    }
    if game.get("setup"):
        pack["setup"] = game["setup"]
    if game.get("dice"):
        pack["dice"] = game["dice"]
    if game.get("turns"):
        pack["turns"] = game["turns"]
    pack["rules"] = game.get("rules", {})
    pack["context"] = game.get("context", {})
    return pack


def main():
    started = time.time()
    spine = seed.load()
    games = spine["games"]
    categories = spine["categories"]
    disabled = _disabled()

    print(f"games.ofthepast.org harvest — {len(games)} games, "
          f"enrichers {[s.name for s in sources.REGISTRY]} "
          f"(disabled: {sorted(disabled) or 'none'})")

    ctx = {}
    source_status = {}
    for src in sources.REGISTRY:
        if src.name in disabled:
            source_status[src.name] = {"status": "disabled"}
            print(f"  · {src.name}: disabled")
            continue
        t0 = time.time()
        try:
            st = src.run(games, ctx)
            st["elapsed_seconds"] = round(time.time() - t0, 1)
            source_status[src.name] = st
            print(f"  · {src.name}: {st.get('status')} "
                  f"(matched {st.get('matched', '—')}/{st.get('total', '—')}, "
                  f"{st['elapsed_seconds']}s)")
        except Exception as exc:  # isolate per-enricher failure
            source_status[src.name] = {"status": "stale", "error": str(exc),
                                       "elapsed_seconds": round(time.time() - t0, 1)}
            print(f"  · {src.name}: STALE — {exc}")
            traceback.print_exc()

    # ---- write outputs ----
    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    PACKS_DIR.mkdir(parents=True, exist_ok=True)

    cat_counts = {c["key"]: 0 for c in categories}
    region_counts = OrderedDict()
    index_games = []
    for g in games:
        cat_counts[g["category"]] = cat_counts.get(g["category"], 0) + 1
        reg = g.get("region")
        if reg:
            region_counts[reg] = region_counts.get(reg, 0) + 1

        # the launcher pack
        pack = _pack_for(g)
        (PACKS_DIR / f"{g['id']}.json").write_text(
            json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

        # the website detail record (a superset of the pack)
        detail = {k: v for k, v in g.items() if k != "_nodes"}
        detail["schema"] = PACK_SCHEMA
        detail["pack_path"] = f"data/packs/{g['id']}.json"
        (GAMES_DIR / f"{g['id']}.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

        # compact index row (+ a board thumbnail so the grid needs no extra fetch)
        rowrec = {k: g.get(k) for k in INDEX_FIELDS}
        rowrec["pigment"] = next((c["pigment"] for c in categories if c["key"] == g["category"]), None)
        rowrec["thumb"] = (g.get("board") or {}).get("image")
        rowrec["has_dice"] = bool(g.get("dice"))
        index_games.append(rowrec)

    generated = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    regions = [{"key": r, "count": n} for r, n in sorted(region_counts.items(), key=lambda kv: -kv[1])]

    index = {
        "generated_at": generated,
        "title": spine.get("title", TITLE),
        "categories": [dict(c, count=cat_counts.get(c["key"], 0)) for c in categories],
        "regions": regions,
        "games": index_games,
    }
    (DATA_DIR / "games.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "generated_at": generated,
        "title": spine.get("title", TITLE),
        "totals": {
            "games": len(games),
            "regions": len(regions),
            "reconstructions": sum(1 for g in games if g.get("reconstruction")),
            "with_image": sum(1 for g in games if (g.get("context") or {}).get("image")),
            "with_dice": sum(1 for g in games if g.get("dice")),
        },
        "categories": [dict(c, count=cat_counts.get(c["key"], 0)) for c in categories],
        "regions": regions,
        "launcher": {
            "base": LAUNCHER,
            "note": "Play link = <base>?game=<absolute pack URL>&room=<code>. "
                    "The pack is a boardgame/1.1 file under data/packs/.",
        },
        "sources": source_status,
        "footer": spine.get("footer", "Made with <3 in Bologna by OpenHistoryMap"),
    }
    (DATA_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"done in {round(time.time() - started, 1)}s → "
          f"{len(games)} packs + details, games.json, manifest.json")


if __name__ == "__main__":
    main()
