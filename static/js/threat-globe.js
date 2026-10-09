/* CyberGrind threat globe. Data:
 *   /data/globe.json       honeypot export (country level, no IPs), committed daily by the analyst
 *   /data/centroids.json   ISO2 -> [lat, lng, name]
 *   /data/land-110m.json   land outlines (Natural Earth 110m via world-atlas)
 *   AbuseIPDB / OSINT Workers for the two community layers
 */
(function () {
  "use strict";
  const ABUSEIPDB_WORKER = "https://cybergrind-threatmap-worker.wacker-jason.workers.dev";
  const OSINT_WORKER = "https://cybergrind-osint-worker.wacker-jason.workers.dev";

  const root = document.getElementById("tg");
  if (!root) return;
  if (typeof Globe === "undefined") window.Globe = function () { throw new Error("globe.gl did not load"); };
  const $ = (id) => document.getElementById(id);
  const css = (n) => getComputedStyle(root).getPropertyValue(n).trim();
  const COL = { use: css("--tg-use"), fetch: css("--tg-fetch"), scan: css("--tg-scan"), land: css("--tg-land"),
                warn: css("--tg-warn"), abuse: css("--tg-abuse"), osint: css("--tg-osint") };
  const rgba = (hex, a) => { const v = parseInt(hex.slice(1), 16); return `rgba(${v >> 16},${(v >> 8) & 255},${v & 255},${a})`; };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (n) => Number(n || 0).toLocaleString();
  const size = (n, base, k) => base + k * Math.log2(1 + n);
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  let C = {}, HP = null, mode = "honeypot";
  const cache = {};
  const name = (cc) => (C[cc] ? C[cc][2] : cc);
  const lag = (h) => (h == null ? "" : h < 1 ? `${Math.round(h * 60)}m` : h < 48 ? `${h.toFixed(1)}h` : `${(h / 24).toFixed(1)} days`);
  const tip = (title, lines) => `<div class="tg-tip"><b>${esc(title)}</b>${lines.filter(Boolean).map((l) => "<br>" + l).join("")}</div>`;

  // ---- globe (if WebGL is unavailable, keep the panel working and say why)
  const el = $("tg-globe");
  const noop = new Proxy(function () {}, { get: (t, k) => (k === "color" || k === "emissive" ? { set() {} } : noop), apply: () => noop });
  function webgl() {
    try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); }
    catch (e) { return false; }
  }
  let g = noop;
  if (webgl()) {
    try { g = makeGlobe(); } catch (e) { console.error("threat globe:", e); g = noop; }
  }
  if (g === noop) {
    el.innerHTML = '<p class="tg-nogl">The globe needs WebGL, which is turned off or unavailable in this browser. The numbers and lists still update.</p>';
  }
  function makeGlobe() { return new Globe(el, { animateIn: !reduce })
    .backgroundColor("rgba(0,0,0,0)")
    .showAtmosphere(true).atmosphereColor(COL.fetch).atmosphereAltitude(0.15)
    .hexPolygonResolution(3).hexPolygonMargin(0.45).hexPolygonUseDots(true).hexPolygonColor(() => COL.land)
    .pointLat("lat").pointLng("lng").pointRadius("r").pointAltitude("alt").pointColor("color").pointLabel("label")
    .arcStartLat("sLat").arcStartLng("sLng").arcEndLat("eLat").arcEndLng("eLng").arcLabel("label")
    .arcColor((d) => d.colors).arcStroke("stroke").arcDashLength(0.5).arcDashGap(0.25)
    .arcDashAnimateTime(reduce ? 0 : 2600).arcAltitudeAutoScale(0.45)
    .ringLat("lat").ringLng("lng").ringColor((d) => (t) => rgba(d.hot ? COL.warn : COL.use, 1 - t))
    .ringMaxRadius(4).ringPropagationSpeed(1.6).ringRepeatPeriod(reduce ? 0 : 1400); }
  if (g !== noop) {
    const mat = g.globeMaterial(); mat.color.set("#0b1524"); if (mat.emissive) mat.emissive.set("#05090f");
    const ctl = g.controls(); ctl.autoRotate = !reduce; ctl.autoRotateSpeed = 0.4;
    g.pointOfView({ lat: 30, lng: 15, altitude: 2.3 }, 0);
    const fit = () => g.width(el.clientWidth).height(el.clientHeight);
    new ResizeObserver(fit).observe(el); fit();
    el.addEventListener("pointerdown", () => { ctl.autoRotate = false; }, { once: true });
  }

  // ---- honeypot layer
  function honeypot() {
    const on = (id) => $(id).checked;
    const pts = [], rings = [], arcs = [];
    for (const [cc, c] of Object.entries(HP.countries || {})) {
      const at = C[cc]; if (!at) continue;
      const [lat, lng] = at;
      const svc = Object.entries(c.services || {}).map(([k, v]) => `${esc(k)} ×${v}`).join(", ");
      const net = { hosting: "Hosting networks", isp: "Home and mobile ISPs", mixed: "Hosting and home ISPs" }[c.network] || "";
      if (c.uses && on("tg-l-use")) {
        pts.push({ lat, lng, r: size(c.uses, 0.25, 0.14), alt: 0.012, color: COL.use,
          label: tip(name(cc), [`${num(c.uses)} key and bait use${c.uses > 1 ? "s" : ""}`, net && `<em>${net}</em>`,
            svc && `<em>${svc}</em>`, c.writes && c.writes.length && `<span class="tg-w">Tried: ${c.writes.map(esc).join(", ")}</span>`]) });
        if (!reduce) rings.push({ lat, lng, hot: !!(c.writes && c.writes.length) });
      }
      if (c.fetches && on("tg-l-fetch"))
        pts.push({ lat: lat + 1.1, lng: lng + 1.1, r: size(c.fetches, 0.2, 0.1), alt: 0.008, color: COL.fetch,
          label: tip(name(cc), [`${num(c.fetches)} key fetch${c.fetches > 1 ? "es" : ""}`]) });
      if (c.scanners && on("tg-l-scan"))
        pts.push({ lat: lat - 1.1, lng: lng - 1.1, r: size(c.scanners, 0.15, 0.08), alt: 0.004, color: COL.scan,
          label: tip(name(cc), [`${num(c.scanners)} scanner${c.scanners > 1 ? "s" : ""}, no key use`]) });
    }
    if (on("tg-l-arc"))
      for (const h of HP.handoffs || []) {
        const a = C[h.from], b = C[h.to]; if (!a || !b || h.from === h.to) continue;
        arcs.push({ sLat: a[0], sLng: a[1], eLat: b[0], eLng: b[1], stroke: Math.min(0.35 + 0.15 * h.count, 1),
          colors: [rgba(COL.fetch, 0.9), rgba(COL.use, 0.9)],
          label: tip(`${name(h.from)} → ${name(h.to)}`, [h.kind === "git" ? "Git credential" : "AWS key",
            h.count > 1 && `${h.count} uses`, h.lag_h != null && `<em>Fetch to first use: ${lag(h.lag_h)}</em>`]) });
      }
    g.pointsData(pts).arcsData(arcs).ringsData(rings);
  }

  // ---- community layers (AbuseIPDB / OSINT Workers)
  async function community(kind) {
    if (!cache[kind]) {
      const res = await fetch(kind === "abuse" ? ABUSEIPDB_WORKER : OSINT_WORKER);
      if (!res.ok) throw new Error("HTTP " + res.status);
      const d = await res.json(); if (d.error) throw new Error(d.error);
      cache[kind] = d;
    }
    const d = cache[kind], color = kind === "abuse" ? COL.abuse : COL.osint;
    g.arcsData([]).ringsData([]).pointsData((d.points || []).map((p) => ({
      lat: p.lat, lng: p.lng, r: size(p.count, 0.15, 0.12), alt: 0.006, color,
      label: tip(p.country, [`${num(p.count)} reported IPs`, p.avgScore != null && `<em>Avg abuse score ${p.avgScore}%</em>`]) })));
    return d;
  }

  // ---- side panel
  function stats(rows) {
    $("tg-stats").innerHTML = rows.map(([v, l]) => `<div><b>${esc(v)}</b><span>${esc(l)}</span></div>`).join("");
  }
  function list(items, empty) {
    $("tg-list").innerHTML = items.length ? items.map((i) =>
      `<li><span class="tg-k">${esc(i.k)}</span><span>${i.t}</span>${i.w ? `<span class="tg-w">${esc(i.w)}</span>` : ""}</li>`).join("")
      : `<li class="tg-empty">${esc(empty)}</li>`;
  }
  function panelHoneypot() {
    const t = HP.totals || {};
    stats([[num(t.uses), "key uses"], [num(t.handoffs), "hand-offs"], [num(t.countries), "countries"]]);
    const top = Object.entries(HP.countries || {}).filter(([, c]) => c.uses).sort((a, b) => b[1].uses - a[1].uses).slice(0, 6)
      .map(([cc, c]) => ({ k: name(cc), t: esc(Object.keys(c.services || {}).join(", ") || "Bait use") + ` · ${num(c.uses)}`,
                          w: c.writes && c.writes.length ? "Tried " + c.writes.join(", ") : "" }));
    const arcs = (HP.handoffs || []).filter((h) => h.from !== h.to).slice(0, 4)
      .map((h) => ({ k: `${name(h.from)} → ${name(h.to)}`, t: (h.kind === "git" ? "Git credential" : "AWS key") +
                     (h.lag_h != null ? ` · used ${lag(h.lag_h)} after fetch` : "") }));
    $("tg-list-h").textContent = "Where the keys went";
    list([...arcs, ...top], "No key use in this window.");
    $("tg-updated").textContent = HP.generated ? `Updated ${HP.generated.replace("T", " ").replace("Z", " UTC")} · last ${HP.window_hours}h` : "";
  }
  function panelCommunity(kind, d) {
    stats([[num(d.totalIPs), "reported IPs"], [num((d.points || []).length), "countries"], [d.topCountries ? d.topCountries[0] : "-", "top source"]]);
    $("tg-list-h").textContent = "Top countries";
    list((d.points || []).slice(0, 8).map((p) => ({ k: p.country, t: `${num(p.count)} IPs` })), "No data.");
    $("tg-updated").textContent = d.generatedAt ? "Updated " + new Date(d.generatedAt).toLocaleString() : "";
  }

  async function show(m) {
    mode = m;
    root.querySelectorAll("[data-mode]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === m)));
    $("tg-hp-layers").hidden = m !== "honeypot";
    $("tg-note-hp").hidden = m !== "honeypot";
    $("tg-note-cm").hidden = m === "honeypot";
    if (m === "honeypot") {
      if (!HP) { stats([["-", "key uses"], ["-", "hand-offs"], ["-", "countries"]]); list([], "Honeypot data is not available right now."); g.pointsData([]).arcsData([]).ringsData([]); return; }
      honeypot(); panelHoneypot(); return;
    }
    try { const d = await community(m); if (mode === m) panelCommunity(m, d); }
    catch (e) { if (mode === m) { stats([["-", "reported IPs"], ["-", "countries"], ["-", "top source"]]); list([], "This feed is unavailable right now."); g.pointsData([]); } }
  }

  root.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => show(b.dataset.mode)));
  ["tg-l-use", "tg-l-arc", "tg-l-fetch", "tg-l-scan"].forEach((id) => $(id).addEventListener("change", () => HP && honeypot()));

  const get = (u) => fetch(u, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status))));
  Promise.all([get("/data/centroids.json"), get("/data/land-110m.json")]).then(([cen, land]) => {
    C = cen; g.hexPolygonsData(land.features || []);
    return get("/data/globe.json").then((d) => { HP = d; }).catch(() => { HP = null; });
  }).then(() => show(mode)).catch(() => list([], "The map data failed to load."));
})();
