"""Wikipedia enricher — adds an illustration, an encyclopedic extract, and a
'Wikipedia' link to each game. It NEVER overwrites the curated `blurb` (which is
better written and historically careful); it only fills empty slots and stores
the wiki lead separately as `context.encyclopedia`.
"""

import time

from .base import Enricher
from .. import wikipedia


def _ensure_link(ctx_block, label, url):
    if not url:
        return
    links = ctx_block.setdefault("links", [])
    if not any((l.get("url") == url) for l in links if isinstance(l, dict)):
        links.append({"label": label, "url": url})


def run(games, ctx):
    titles = [g["wp"] for g in games if g.get("wp")]
    pages = wikipedia.pages(titles)
    ctx.setdefault("qids", {})
    matched, no_match = 0, []
    for g in games:
        wp = g.get("wp")
        if not wp:
            continue
        hit = pages.get(wp)
        if not hit:
            no_match.append(g["id"])
            continue
        matched += 1
        block = g.setdefault("context", {})
        if hit.get("thumb") and not block.get("image"):
            block["image"] = hit["thumb"]
            block.setdefault("credit", "Illustration via Wikipedia / Wikimedia Commons")
        if hit.get("extract"):
            block["encyclopedia"] = hit["extract"]
        _ensure_link(block, hit.get("title", wp) + " — Wikipedia", hit.get("url"))
        if hit.get("qid"):
            ctx["qids"][g["id"]] = hit["qid"]
            g["qid"] = g.get("qid") or hit["qid"]
    return {"status": "ok", "matched": matched, "total": len(titles), "no_match": no_match}


SOURCE = Enricher(name="wikipedia", title="Wikipedia lead extract + illustration", run=run)
