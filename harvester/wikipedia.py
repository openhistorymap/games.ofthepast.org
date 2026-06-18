"""Minimal MediaWiki (en.wikipedia.org) client — resolve titles, lead extracts,
lead images, and the canonical page URL. `requests` is imported lazily so the
offline build never needs it.
"""

API = "https://en.wikipedia.org/w/api.php"
UA = "games.ofthepast.org harvester (OpenHistoryMap; +https://games.ofthepast.org)"


def _get(params):
    import requests
    params = dict(params)
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.json()


def pages(titles, thumb_px=640):
    """Return {requested_title: {title, extract, url, thumb, qid}} for a batch of titles."""
    if not titles:
        return {}
    data = _get({
        "action": "query",
        "titles": "|".join(titles),
        "prop": "extracts|pageimages|pageprops|info",
        "exintro": 1, "explaintext": 1,
        "piprop": "thumbnail", "pithumbsize": thumb_px,
        "ppprop": "wikibase_item",
        "inprop": "url",
        "redirects": 1,
    })
    # map any redirect/normalisation back to the title we asked for
    back = {}
    q = data.get("query", {})
    for n in q.get("normalized", []):
        back[n["to"]] = n["from"]
    for n in q.get("redirects", []):
        back[n["to"]] = back.get(n["from"], n["from"])

    out = {}
    for p in q.get("pages", []):
        if p.get("missing"):
            continue
        title = p.get("title")
        asked = back.get(title, title)
        out[asked] = {
            "title": title,
            "extract": (p.get("extract") or "").strip(),
            "url": p.get("canonicalurl") or p.get("fullurl"),
            "thumb": (p.get("thumbnail") or {}).get("source"),
            "qid": (p.get("pageprops") or {}).get("wikibase_item"),
        }
    return out
