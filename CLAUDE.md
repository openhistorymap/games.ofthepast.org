# games.ofthepast.org

A catalogue of the **great games of human history** — the board, sowing, dice and
guessing games people across every continent and five thousand years actually
played, each with its rules, its history, and a **live shared table you can play
with friends**. Senet by the Nile, Go on its grid, tigers hunting goats, seeds
sown round a mancala, a dreidel spun at Hanukkah.

Sibling, in machinery and house style, to **`games.ofancientrome.org`** (the same
*curated-seed → harvester → static-data → GitHub-Pages* shape, the same OHM
footer, the same "never fabricate history" discipline) and to
**`rulers.ofthepast.org`** (the same *broadening of a single-culture sibling into
the whole world*). Where games.ofancientrome is one city's shelf of boards, this
is the **world's gaming table**.

## How it fits together (two repos)

1. **This repo** is the catalogue + the data. The harvester turns a hand-authored
   roster into machine-owned `data/`: a compact index, a per-game detail record,
   and — the key artefact — a **`boardgame/1.1` pack** per game under
   `data/packs/<id>.json`.
2. **The launcher** is `JustPlayBo/launcher` (the JustPlay shared-board engine,
   working tree at `/srv/justplay-sy`). Each game's **▶ Play with friends** button
   deep-links into it:
   `https://justplaybo.github.io/launcher/?game=<absolute pack URL>&room=<code>`.
   The launcher fetches the pack (GitHub Pages serves it CORS-`*`), renders the
   board + pieces, and syncs moves over MQTT. Because the pack carries `rules`,
   `context`, `dice` and `turns`, players land at the table already knowing **how
   to play and what the game is** — a rules drawer, a synced dice roller and a
   "whose turn" chip travel with the pack.

The `boardgame/1.1` blocks (`rules`/`context`/`dice`/`turns`) are documented in
`/srv/justplay-sy/packs/SCHEMA.md`. They are additive; the engine enforces nothing.

## Scope (decided up front)

- **~28 world classics, the core playable set**, grouped into **seven mechanic
  categories** (the lanes): *war & strategy* (Go, Chaturanga, Xiangqi, latrunculi,
  petteia, alquerque), *hunt & siege* (hnefatafl, bagh-chal, fox-and-geese),
  *race & tables* (senet, royal game of Ur, tabula, backgammon, pachisi, patolli,
  game of the goose), *sowing* (oware, bao, toguz korgool), *alignment* (nine /
  three men's morris, mū tōrere, rota), *dice & lots* (tali, hazard, dreidel),
  *hand & guess* (morra, par impar). The mechanic is the lane; **culture/origin
  and region are per-game facets** (a pill + a "Where" filter) — that is where the
  broadening from the Rome sibling lives. The nine Roman games are one strand
  among many.
- **Honesty about lost rules.** Several games' rules were never written down (or
  only partly recovered). Where we give a playable set for a game whose rules are
  unrecorded, the game is flagged `reconstruction: True`; the frontend shows a
  banner and the rules say so plainly. The Royal Game of Ur (recovered by Finkel
  from a clay tablet) and tablut/hnefatafl (recorded by Linnaeus) are flagged but
  explained. **Never present a reconstruction as recovered fact.**
- **Zero binary assets.** Every board is a self-contained inline **SVG**
  (generated in `build_seed.py`, embedded as a `data:` URI in the pack); every
  piece is a unicode/emoji glyph or a coloured chip. The repo ships no images.
- **Curated text is authoritative.** The blurb, rules and sources are
  hand-written; the Wikipedia/Wikidata enrichers only *add* (an illustration, an
  encyclopedic extract, external links). They never overwrite curated content.

## Layout

```
harvester/        Python pipeline (stdlib only for the offline path).
  build_seed.py   THE CURATED CORE — the ~28 games, their boardgame/1.1 packs
                  (SVG board generators + glyph pieces), rules, history, and
                  per-game origin/region/era. `python -m harvester.build_seed`
                  writes harvester/data/seed.json.
  wikipedia.py    MediaWiki client: lead extract, lead image, page URL (lazy `requests`).
  wikidata.py     wbgetentities client: QID + P18 image fallback (lazy `requests`).
  harvest.py      orchestrator -> data/ (packs, details, index, manifest + region table).
  sources/
    base.py       the Enricher contract (run(games, ctx) -> status; failures isolated).
    seed.py       loads the spine (not an enricher).
    wikipedia_enrich.py   illustration + encyclopedic extract + Wikipedia link.
    wikidata_enrich.py    QID + image fallback + Wikidata link.
  data/seed.json  the canonical spine the harvester reads (committed).
web/              static frontend (no build step, relative paths only).
  index.html  style.css  app.js
data/             GENERATED, machine-owned. Committed; published by Deploy.
  games.json             compact index for the catalogue grid (+ board thumbnails, regions)
  games/<id>.json        full per-game detail (rules, context, pack, pieces)
  packs/<id>.json        the boardgame/1.1 pack the JustPlay launcher loads
  manifest.json          totals, categories, regions, per-source status, launcher, footer
.github/workflows/  harvest.yml + deploy.yml (two independent manual workflows)
CNAME             games.ofthepast.org
```

## The harvester

Spine-then-enrich, identical machinery to the siblings. `harvest.py` loads the
**spine** (`seed.json`, built by `build_seed.py`) and runs each **Enricher** in
`sources.REGISTRY` over the shared games list, in isolation: a failing enricher is
recorded `stale` in the manifest and the spine + the other enrichers survive.

- **Offline build (no network):** `GAMES_DISABLE=wikipedia,wikidata python -m
  harvester` — produces a complete `data/` from the curated content alone. This is
  how the committed `data/` is cut; the site is fully functional without ever
  hitting the network.
- **Full build (network):** `python -m harvester` — additionally fetches an
  illustration, an encyclopedic extract and external links per game.
- Editing the roster = edit `GAMES` / `CATEGORIES` (and the SVG board generators)
  in `build_seed.py`, re-run `python -m harvester.build_seed`, eyeball the printed
  roster (grouped by category, with origins), then re-harvest. **Never hand-edit
  `data/`** — it is machine output.

## Frontend

Plain HTML/CSS/JS, **no build step**, **relative paths only** (custom domain + any
`/staging/` subpath both work). Loads `data/manifest.json` + `data/games.json`,
renders category **lanes** of cards (each card shows the board as a thumbnail and
its culture of origin), offers a **"Where" region filter** alongside the category
chips, and lazy-loads `data/games/<id>.json` into a detail overlay on click. The
overlay shows origin/region, history & context, the rules, the pieces legend and
the dice — and the **▶ Play with friends** button that opens the launcher. Theme
(light/parchment vs dark) persists in `localStorage` (`gotp-theme`). Design is the
**world's gaming table**: warm boxwood/parchment, inked lines, a pigment per
game-family; Cormorant Garamond + Spectral (the `ofthepast` family face). Full
design context in `.impeccable.md`.

## Local preview

`web/` and `data/` are separate trees that Deploy merges. To preview them together:

```bash
GAMES_DISABLE=wikipedia,wikidata python -m harvester      # (re)cut data/
mkdir -p _site/data && cp -r web/. _site/ && cp -r data/. _site/data/
python3 -m http.server -d _site 8799   # open http://localhost:8799
```

`_site/` is git-ignored.

## Deploy

**GitHub Pages**, custom domain via `CNAME`. Two independent **manual** workflows
(same discipline as the siblings):

- **Harvest** — rebuild the seed, re-pull `data/` (optionally with enrichers),
  commit to `main`. Does *not* publish.
- **Deploy** — stage `web/` to the root + `data/` to `_site/data/` + `CNAME` →
  Pages (`actions/deploy-pages`). Does *not* harvest. Pages source = "GitHub
  Actions".

Typical: *frontend change → push → Deploy*; *roster change → edit `build_seed.py`
→ Harvest → eyeball the manifest → Deploy*.

## House rules

- `data/` is machine-owned harvester output — never hand-edit it.
- The roster lives in `build_seed.py`. That is the one file to edit to add,
  remove, or re-rule a game; everything downstream is generated.
- **Never fabricate history.** Games with lost rules are `reconstruction: True`
  and say so. Cite real sources (Murray 1952; Bell 1979; Parlett 1999; Finkel for
  Ur; Kendall for senet; Linnaeus for tablut; Alfonso X for alquerque/tables).
- No hard-coded credentials; this repo holds no keys.
- No tests. Don't claim a change is "tested" because nothing broke at import —
  but you *can* validate packs by normalising them with the launcher's
  `js/gamedef.js` (see `/srv/justplay-sy`), and validate the SVG boards by
  decoding the `data:` URIs and parsing them as XML.
- The footer always reads "Made with <3 in Bologna by OpenHistoryMap" (OHM line).
- Host runtime is old — run one-off tooling under Docker if the host Python
  chokes (`docker run --rm -v "$PWD":/w -w /w python:3-slim …`).
