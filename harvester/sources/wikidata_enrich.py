"""Wikidata enricher — resolves a QID per game (from the curated `qid`, or the one
Wikipedia found via its sitelink), adds a Wikidata link, and supplies a P18 image
only if Wikipedia did not already provide one. Curated text is never touched.
"""

from .base import Enricher
from .. import wikidata


def _ensure_link(ctx_block, label, url):
    if not url:
        return
    links = ctx_block.setdefault("links", [])
    if not any((l.get("url") == url) for l in links if isinstance(l, dict)):
        links.append({"label": label, "url": url})


def run(games, ctx):
    qmap = ctx.get("qids", {})
    wanted = {}
    for g in games:
        qid = g.get("qid") or qmap.get(g["id"])
        if qid:
            wanted[g["id"]] = qid
    ents = wikidata.entities(list(wanted.values()))
    matched, no_image = 0, []
    for g in games:
        qid = wanted.get(g["id"])
        if not qid:
            continue
        matched += 1
        g["qid"] = qid
        block = g.setdefault("context", {})
        _ensure_link(block, "Wikidata", f"https://www.wikidata.org/wiki/{qid}")
        ent = ents.get(qid)
        if ent and not block.get("image"):
            img = wikidata.image_url(ent)
            if img:
                block["image"] = img
                block.setdefault("credit", "Image via Wikimedia Commons")
            else:
                no_image.append(g["id"])
    return {"status": "ok", "matched": matched, "total": len(wanted), "no_image": no_image}


SOURCE = Enricher(name="wikidata", title="Wikidata QID + image fallback", run=run)
