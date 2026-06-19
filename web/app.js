/* app.js — Games of the Past catalogue.
 *
 * No build step, relative paths only (custom domain + any /staging/ subpath both
 * work). Loads data/manifest.json + data/games.json, renders category lanes of
 * cards, lazy-loads data/games/<id>.json on click, and deep-links each game into
 * the JustPlay launcher pre-loaded with that game's boardgame/1.1 pack.
 */
(function () {
  "use strict";

  const $ = (s, r) => (r || document).querySelector(s);
  const state = {
    manifest: null, games: [], byId: {}, categories: [], regions: [],
    cat: "all", region: "all", q: "", detailCache: {},
  };

  /* ---------- tiny DOM helpers ---------- */
  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function setVar(node, name, val) { if (val) node.style.setProperty(name, val); }

  /* ---------- room codes (world-of-games flavour) ---------- */
  const WORDS = ["agora", "souk", "tavern", "teahouse", "bazaar", "forum", "longhouse",
    "caravanserai", "plaza", "veranda", "courtyard", "cloister", "wharf", "stoa"];
  const rnd = (n) => (Math.random() * n) | 0;
  const room = () => `${WORDS[rnd(WORDS.length)]}-${WORDS[rnd(WORDS.length)]}-${rnd(90) + 10}`;

  /* ---------- launcher deep link ---------- */
  function launcherBase() {
    return (state.manifest && state.manifest.launcher && state.manifest.launcher.base)
      || "https://justplaybo.github.io/launcher/";
  }
  function playUrl(packPath, withRoom) {
    const packAbs = new URL(packPath, location.href).href;       // absolute, CORS-readable on Pages
    const u = new URL(launcherBase());
    u.searchParams.set("game", packAbs);
    if (withRoom) u.searchParams.set("room", withRoom);
    return u.toString();
  }

  /* ---------- boot ---------- */
  (async function init() {
    document.documentElement.dataset.theme = localStorage.getItem("gotp-theme") || "light";
    $("#themeBtn").onclick = toggleTheme;
    try {
      const [manifest, index] = await Promise.all([
        fetch("data/manifest.json").then((r) => r.json()),
        fetch("data/games.json").then((r) => r.json()),
      ]);
      state.manifest = manifest;
      state.games = index.games || [];
      state.games.forEach((g) => (state.byId[g.id] = g));
      state.categories = index.categories || manifest.categories || [];
      state.regions = index.regions || manifest.regions || [];
      renderStats();
      renderCatFilter();
      renderRegionFilter();
      renderLanes();
      if (manifest.footer) $("#footLine").textContent = manifest.footer;
      wireSearch();
      openFromHash();
      window.addEventListener("hashchange", openFromHash);
    } catch (e) {
      $("#lanes").innerHTML =
        '<p class="empty">The catalogue could not be loaded. Run <code>python -m harvester</code> to cut <code>data/</code>.</p>';
      console.error(e);
    }
  })();

  function toggleTheme() {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("gotp-theme", next);
  }

  function renderStats() {
    const t = (state.manifest && state.manifest.totals) || {};
    const dl = $("#stats");
    dl.innerHTML = "";
    const add = (n, label) => {
      const d = el("div");
      d.appendChild(el("dt", null, String(n)));
      d.appendChild(el("dd", null, label));
      dl.appendChild(d);
    };
    add(t.games != null ? t.games : state.games.length, "games");
    if (t.regions) add(t.regions, "regions");
    if (t.reconstructions) add(t.reconstructions, "reconstructed");
  }

  function renderCatFilter() {
    const nav = $("#cats");
    nav.innerHTML = "";
    const mk = (key, label, pigment) => {
      const b = el("button", "cat-chip", label);
      if (pigment) setVar(b, "--p", pigment);
      if (key === state.cat) b.classList.add("active");
      b.onclick = () => { state.cat = key; renderCatFilter(); renderLanes(); };
      return b;
    };
    nav.appendChild(mk("all", "All games", null));
    state.categories.forEach((c) => nav.appendChild(mk(c.key, c.label, c.pigment)));
  }

  function renderRegionFilter() {
    const nav = $("#regions");
    if (!nav) return;
    nav.innerHTML = "";
    const mk = (key, label) => {
      const b = el("button", "region-chip", label);
      if (key === state.region) b.classList.add("active");
      b.onclick = () => { state.region = key; renderRegionFilter(); renderLanes(); };
      return b;
    };
    nav.appendChild(mk("all", "Everywhere"));
    state.regions.forEach((r) => nav.appendChild(mk(r.key, `${r.key} · ${r.count}`)));
  }

  function wireSearch() {
    const inp = $("#search");
    inp.oninput = () => { state.q = inp.value.trim().toLowerCase(); renderLanes(); };
  }

  function matches(g) {
    if (state.cat !== "all" && g.category !== state.cat) return false;
    if (state.region !== "all" && g.region !== state.region) return false;
    if (!state.q) return true;
    const hay = [g.name, g.native, g.tagline, g.category_label, g.origin, g.region, g.era,
      (g.aka || []).join(" ")].join(" ").toLowerCase();
    return hay.includes(state.q);
  }

  function renderLanes() {
    const wrap = $("#lanes");
    wrap.innerHTML = "";
    let shown = 0;
    state.categories.forEach((c) => {
      const games = state.games.filter((g) => g.category === c.key && matches(g));
      if (!games.length) return;
      shown += games.length;
      const lane = el("section", "lane");
      const head = el("div", "lane-head");
      setVar(head, "--p", c.pigment);
      head.appendChild(el("h2", null, c.label));
      if (c.note) head.appendChild(el("span", "lane-note", c.note));
      head.appendChild(el("span", "lane-count", games.length + (games.length === 1 ? " game" : " games")));
      lane.appendChild(head);
      const grid = el("div", "grid");
      games.forEach((g) => grid.appendChild(card(g, c.pigment)));
      lane.appendChild(grid);
      wrap.appendChild(lane);
    });
    $("#empty").classList.toggle("hidden", shown > 0);
  }

  function card(g, pigment) {
    const c = el("button", "card");
    setVar(c, "--p", g.pigment || pigment);
    const niche = el("div", "card-niche");
    if (g.thumb) { const img = el("img"); img.src = g.thumb; img.alt = g.name + " board"; img.loading = "lazy"; niche.appendChild(img); }
    c.appendChild(niche);
    const body = el("div", "card-body");
    const top = el("div", "card-top");
    top.appendChild(el("span", "card-cat", g.category_label || g.category));
    if (g.origin) top.appendChild(el("span", "card-origin", g.origin));
    body.appendChild(top);
    body.appendChild(el("h3", null, g.name));
    if (g.native && g.native !== g.name) body.appendChild(el("div", "native", g.native));
    body.appendChild(el("p", "card-tag", g.tagline || ""));
    const meta = el("div", "card-meta");
    if (g.era) meta.appendChild(el("span", "pill era", g.era));
    if (g.has_dice) meta.appendChild(el("span", "pill dice", "dice"));
    if (g.reconstruction) meta.appendChild(el("span", "pill recon", "reconstruction"));
    body.appendChild(meta);
    c.appendChild(body);
    c.onclick = () => openDetail(g.id);
    return c;
  }

  /* ---------- detail overlay ---------- */
  async function openDetail(id) {
    let g = state.detailCache[id];
    if (!g) {
      try { g = await fetch(`data/games/${id}.json`).then((r) => r.json()); }
      catch (e) { g = state.byId[id]; }                 // fall back to the index row
      state.detailCache[id] = g;
    }
    renderDetail(g);
    const ov = $("#overlay");
    ov.classList.remove("hidden");
    ov.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    if (location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
  }
  function closeDetail() {
    $("#overlay").classList.add("hidden");
    document.body.style.overflow = "";
    if (location.hash) history.replaceState(null, "", location.pathname + location.search);
  }
  function openFromHash() {
    const id = decodeURIComponent(location.hash.replace(/^#/, ""));
    if (id && state.byId[id]) openDetail(id);
    else if (!id) closeDetail();
  }

  $("#overlay").addEventListener("click", (e) => { if (e.target.dataset.close != null) closeDetail(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDetail(); });

  function renderDetail(g) {
    const pigment = (g.pigment) || (state.byId[g.id] && state.byId[g.id].pigment);
    const d = $("#detail");
    d.innerHTML = "";
    setVar(d, "--p", pigment);
    const board = g.board || {};
    const ctx = g.context || {};
    const rules = g.rules || {};

    // ---- top: board + heading + play ----
    const top = el("div", "detail-top");
    const bwrap = el("div", "detail-board");
    if (board.image) { const img = el("img"); img.src = board.image; img.alt = g.name + " board"; bwrap.appendChild(img); }
    top.appendChild(bwrap);

    const head = el("div", "detail-head");
    const close = el("button", "detail-close", "✕"); close.onclick = closeDetail; head.appendChild(close);
    head.appendChild(el("div", "detail-cat", g.category_label || g.category));
    head.appendChild(el("h2", null, g.name));
    if (g.native && g.native !== g.name) head.appendChild(el("p", "detail-native", g.native));
    if (g.aka && g.aka.length) head.appendChild(el("p", "detail-aka", "also: " + g.aka.join(" · ")));

    const prov = el("div", "detail-prov");
    if (g.origin) prov.appendChild(el("span", "prov-origin", g.origin));
    if (g.region) prov.appendChild(el("span", "prov-region", g.region));
    head.appendChild(prov);

    const meta = el("div", "detail-meta");
    if (g.era) meta.appendChild(el("span", "pill era", g.era));
    if (rules.players || g.players) meta.appendChild(el("span", "pill", (rules.players || g.players) + " players"));
    if (rules.duration || g.duration) meta.appendChild(el("span", "pill", rules.duration || g.duration));
    if (g.has_dice || (g.dice && g.dice.length)) meta.appendChild(el("span", "pill dice", "dice"));
    if (g.reconstruction) meta.appendChild(el("span", "pill recon", "reconstruction"));
    head.appendChild(meta);

    const playrow = el("div", "play-row");
    const play = el("button", "play-btn", "▶ Play with friends");
    play.onclick = () => { window.open(playUrl(g.pack_path || `data/packs/${g.id}.json`, room()), "_blank", "noopener"); };
    playrow.appendChild(play);
    const copy = el("button", "copy-btn", "Copy invite link");
    copy.onclick = async () => {
      const link = playUrl(g.pack_path || `data/packs/${g.id}.json`, room());
      try { await navigator.clipboard.writeText(link); toast("Invite link copied — share it to play together"); }
      catch (e) { prompt("Copy this invite link:", link); }
    };
    playrow.appendChild(copy);
    head.appendChild(playrow);
    head.appendChild(el("span", "play-sub", "Opens the JustPlay shared table in a new tab with this game loaded. Send the invite link and you’re both at the same board — the rules, dice and turn order travel with it."));
    top.appendChild(head);
    d.appendChild(top);

    // ---- body ----
    const body = el("div", "detail-body");

    if (g.reconstruction) {
      const note = el("div", "recon-note");
      note.appendChild(el("b", null, "Reconstruction. "));
      note.appendChild(document.createTextNode("No source records how this game was played in full. The rules below are a modern, plausible reconstruction — offered so the board can be enjoyed, not presented as recovered fact."));
      body.appendChild(note);
    }

    // context
    if (ctx.period || ctx.blurb || ctx.encyclopedia || (ctx.sources && ctx.sources.length) || (ctx.links && ctx.links.length)) {
      const sec = el("section");
      sec.appendChild(el("h3", "sec-h", "History & context"));
      if (ctx.image) {
        const fig = el("figure", "fig");
        const img = el("img"); img.src = ctx.image; img.alt = g.name; img.loading = "lazy"; fig.appendChild(img);
        if (ctx.credit) fig.appendChild(el("figcaption", null, ctx.credit));
        sec.appendChild(fig);
      }
      if (ctx.period) sec.appendChild(el("span", "period-pill", ctx.period));
      if (ctx.blurb) sec.appendChild(el("p", null, ctx.blurb));
      if (ctx.encyclopedia) { sec.appendChild(el("div", "sub-h", "From Wikipedia")); sec.appendChild(el("p", null, ctx.encyclopedia)); }
      if (ctx.links && ctx.links.length) {
        const nav = el("div", "links");
        ctx.links.forEach((l) => { if (!l || !l.url) return; const a = el("a", null, l.label || l.url); a.href = l.url; a.target = "_blank"; a.rel = "noopener"; nav.appendChild(a); });
        sec.appendChild(nav);
      }
      if (ctx.sources && ctx.sources.length) {
        sec.appendChild(el("div", "sub-h", "Sources"));
        const ul = el("ul", "bul sources");
        ctx.sources.forEach((s) => ul.appendChild(el("li", null, s)));
        sec.appendChild(ul);
      }
      body.appendChild(sec);
    }

    // rules
    const sec = el("section");
    sec.appendChild(el("h3", "sec-h", "How to play"));
    if (rules.objective) sec.appendChild(el("p", "objective", rules.objective));
    if (rules.setup) { sec.appendChild(el("div", "sub-h", "Setup")); sec.appendChild(el("p", null, rules.setup)); }
    if (rules.howToPlay && rules.howToPlay.length) {
      sec.appendChild(el("div", "sub-h", "Play"));
      const ol = el("ol", "steps");
      rules.howToPlay.forEach((s) => ol.appendChild(el("li", null, s)));
      sec.appendChild(ol);
    }
    if (rules.winning) { sec.appendChild(el("div", "sub-h", "Winning")); sec.appendChild(el("p", null, rules.winning)); }
    if (rules.variants && rules.variants.length) {
      sec.appendChild(el("div", "sub-h", "Variants"));
      const ul = el("ul", "bul");
      rules.variants.forEach((v) => ul.appendChild(el("li", null, v)));
      sec.appendChild(ul);
    }
    body.appendChild(sec);

    // pieces legend
    if (g.pieces && g.pieces.length) {
      const ps = el("section");
      ps.appendChild(el("h3", "sec-h", "Pieces"));
      const leg = el("div", "legend");
      g.pieces.forEach((p) => {
        const item = el("div", "legend-item");
        const chip = el("span", "chip", p.glyph || "");
        if (p.bg) chip.style.background = p.bg;
        if (p.color) chip.style.color = p.color;
        if (!p.bg && !p.glyph) chip.style.background = "var(--stone-3)";
        item.appendChild(chip);
        item.appendChild(el("span", null, p.label || p.type));
        leg.appendChild(item);
      });
      ps.appendChild(leg);
      body.appendChild(ps);
    }

    if (g.dice && g.dice.length) {
      const ds = el("section");
      ds.appendChild(el("h3", "sec-h", "Dice & lots"));
      g.dice.forEach((die) => {
        const faces = die.faces && die.faces.length
          ? die.faces.map((f) => (f && f.label != null ? f.label : f)).join(" · ")
          : "1–" + (die.sides || 6);
        ds.appendChild(el("p", null, `${die.count || 1} × ${die.label} — faces ${faces}. Rolled live in the shared table.`));
      });
      body.appendChild(ds);
    }

    d.appendChild(body);
    d.scrollTop = 0;
  }

  /* ---------- toast ---------- */
  let toastTimer = 0;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg; t.classList.remove("hidden");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.add("hidden"), 2600);
  }
})();
