/* Homepage mini globe: today's honeypot key uses and hand-off arcs, view only.
 * Loads globe.gl and the data only when the card is on screen. Without WebGL the
 * still image stays. Clicking anywhere opens the full map (the card is a link). */
(function () {
  "use strict";
  const box = document.getElementById("hm-globe");
  if (!box) return;
  const still = document.getElementById("hm-still");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const USE = "#ffb347", FETCH = "#5cc8ff", WARN = "#ff6b5e", LAND = "#3a4d66";
  const rgba = (hex, a) => { const v = parseInt(hex.slice(1), 16); return `rgba(${v >> 16},${(v >> 8) & 255},${v & 255},${a})`; };

  function webgl() {
    try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); }
    catch (e) { return false; }
  }
  function script(src) {
    return new Promise((ok, fail) => {
      if (window.Globe) return ok();
      const s = document.createElement("script"); s.src = src; s.onload = ok; s.onerror = fail;
      document.head.appendChild(s);
    });
  }
  const get = (u) => fetch(u, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : Promise.reject(new Error(u))));

  async function start() {
    if (!webgl()) return;
    try {
      const [, C, land, d] = await Promise.all([script("/js/vendor/globe.gl-2.46.2.min.js"),
        get("/data/centroids.json"), get("/data/land-110m.json"), get("/data/globe.json")]);
      const pts = [], rings = [], arcs = [];
      for (const [cc, c] of Object.entries(d.countries || {})) {
        const at = C[cc]; if (!at || !c.uses) continue;
        pts.push({ lat: at[0], lng: at[1], r: 0.3 + 0.16 * Math.log2(1 + c.uses) });
        if (!reduce) rings.push({ lat: at[0], lng: at[1], hot: !!(c.writes && c.writes.length) });
      }
      for (const h of d.handoffs || []) {
        const a = C[h.from], b = C[h.to]; if (!a || !b || h.from === h.to) continue;
        arcs.push({ sLat: a[0], sLng: a[1], eLat: b[0], eLng: b[1] });
      }
      const target = pts.length ? pts.reduce((m, p) => (p.r > m.r ? p : m)) : { lat: 30, lng: 15 };
      const g = new Globe(box, { animateIn: false })
        .width(box.clientWidth).height(box.clientHeight)
        .backgroundColor("rgba(0,0,0,0)").showAtmosphere(true).atmosphereColor(FETCH).atmosphereAltitude(0.14)
        .hexPolygonsData(land.features || []).hexPolygonResolution(3).hexPolygonMargin(0.45)
        .hexPolygonUseDots(true).hexPolygonColor(() => LAND)
        .pointsData(pts).pointLat("lat").pointLng("lng").pointRadius("r").pointAltitude(0.012).pointColor(() => USE)
        .arcsData(arcs).arcStartLat("sLat").arcStartLng("sLng").arcEndLat("eLat").arcEndLng("eLng")
        .arcColor(() => [rgba(FETCH, 0.9), rgba(USE, 0.9)]).arcStroke(0.5)
        .arcDashLength(0.5).arcDashGap(0.25).arcDashAnimateTime(reduce ? 0 : 2600).arcAltitudeAutoScale(0.45)
        .ringsData(rings).ringLat("lat").ringLng("lng").ringColor((r) => (t) => rgba(r.hot ? WARN : USE, 1 - t))
        .ringMaxRadius(4).ringPropagationSpeed(1.6).ringRepeatPeriod(1400)
        .enablePointerInteraction(false);
      const mat = g.globeMaterial(); mat.color.set("#0b1524"); if (mat.emissive) mat.emissive.set("#05090f");
      const ctl = g.controls(); ctl.enableZoom = false; ctl.enableRotate = false; ctl.enablePan = false;
      ctl.autoRotate = !reduce; ctl.autoRotateSpeed = 0.5;
      g.pointOfView({ lat: Math.max(Math.min(target.lat, 45), 10), lng: target.lng, altitude: 1.9 }, 0);
      new ResizeObserver(() => g.width(box.clientWidth).height(box.clientHeight)).observe(box);
      if (still) still.style.opacity = "0";
    } catch (e) {
      console.error("home globe:", e); // still image stays
    }
  }

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); start(); } }, { rootMargin: "200px" });
    io.observe(box);
  } else start();
})();
