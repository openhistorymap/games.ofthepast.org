"""Minimal Wikidata client — fetch entities and pull the image (P18) and a label.
`requests` is imported lazily so the offline build never needs it.
"""

API = "https://www.wikidata.org/w/api.php"
COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/"
UA = "games.ofthepast.org harvester (OpenHistoryMap; +https://games.ofthepast.org)"


def _get(params):
    import requests
    params = dict(params)
    params.setdefault("format", "json")
    r = requests.get(API, params=params, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.json()


def entities(qids):
    """Return {qid: entity-json} for a batch of QIDs."""
    qids = [q for q in qids if q]
    if not qids:
        return {}
    out = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i:i + 50]
        data = _get({"action": "wbgetentities", "ids": "|".join(chunk),
                     "props": "claims|labels|sitelinks", "languages": "en"})
        out.update(data.get("entities", {}))
    return out


def _claim_value(entity, prop):
    claims = (entity.get("claims") or {}).get(prop) or []
    for c in claims:
        try:
            return c["mainsnak"]["datavalue"]["value"]
        except (KeyError, TypeError):
            continue
    return None


def image_url(entity, width=640):
    fname = _claim_value(entity, "P18")
    if not fname:
        return None
    return COMMONS + fname.replace(" ", "_") + f"?width={width}"
