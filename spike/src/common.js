import { feature } from 'topojson-client';
import topo110 from 'world-atlas/countries-110m.json';

// Deterministic pseudo-random so both options render identical data.
function rng(seed) { return () => (seed = (seed * 16807) % 2147483647) / 2147483647; }

export async function loadCountries(res = '110m') {
  const topo = res === '50m' ? (await import('world-atlas/countries-50m.json')).default : topo110;
  const fc = feature(topo, topo.objects.countries);
  const r = rng(42);
  fc.features.forEach((f) => { f.properties.value = r(); f.properties.value2 = r(); });
  return fc;
}

export function centroid(f) {
  // cheap bbox-centre of the largest ring; fine for a spike
  let best = null, area = -1;
  const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const p of polys) { const ring = p[0]; const a = ring.length; if (a > area) { area = a; best = ring; } }
  let [x0, y0, x1, y1] = [180, 90, -180, -90];
  for (const [x, y] of best) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
  return [(x0 + x1) / 2, (y0 + y1) / 2];
}

export function makeArcs(fc, n = 300) {
  const r = rng(7); const cs = fc.features.map(centroid); const out = [];
  for (let i = 0; i < n; i++) {
    const a = cs[Math.floor(r() * cs.length)], b = cs[Math.floor(r() * cs.length)];
    out.push({ source: a, target: b, value: r() });
  }
  return out;
}

export function color(v) { // simple sequential ramp
  const t = Math.max(0, Math.min(1, v));
  return [Math.round(255 * (1 - t) + 20 * t), Math.round(240 * (1 - t) + 80 * t), Math.round(200 * (1 - t) + 160 * t)];
}

// FPS probe exposed for the Playwright harness
export function startFpsProbe() {
  window.__frames = []; let last = performance.now();
  const tick = (t) => { window.__frames.push(t - last); last = t; requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
  window.__fps = (sinceMs) => {
    const f = window.__frames.slice(-Math.max(5, Math.round(sinceMs / 16)));
    const avg = f.reduce((s, x) => s + x, 0) / f.length; const sorted = [...f].sort((a, b) => a - b);
    return { fps: +(1000 / avg).toFixed(1), p95ms: +sorted[Math.floor(sorted.length * 0.95)].toFixed(1) };
  };
}
