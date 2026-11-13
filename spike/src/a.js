import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapboxOverlay } from '@deck.gl/mapbox';
import { ArcLayer, ColumnLayer } from '@deck.gl/layers';
import { loadCountries, makeArcs, centroid, color, startFpsProbe } from './common.js';

const fc = await loadCountries('110m');
const arcs = makeArcs(fc);
const cols = fc.features.map((f) => ({ pos: centroid(f), v: f.properties.value2 }));

const map = new maplibregl.Map({
  container: 'map', center: [20, 20], zoom: 1.3, attributionControl: false,
  style: { version: 8, projection: { type: 'globe' }, sources: {}, layers: [{ id: 'bg', type: 'background', paint: { 'background-color': '#0b1020' } }] },
});
map.addControl(new maplibregl.NavigationControl(), 'top-right');
map.on('load', () => {
  map.addSource('c', { type: 'geojson', data: fc });
  map.addLayer({ id: 'fill', type: 'fill', source: 'c', paint: {
    'fill-color': ['interpolate', ['linear'], ['get', 'value'], 0, '#fff0c8', 1, '#1450a0'] } });
  map.addLayer({ id: 'line', type: 'line', source: 'c', paint: { 'line-color': '#334', 'line-width': 0.5 } });
  const overlay = new MapboxOverlay({ interleaved: true, layers: [
    new ColumnLayer({ id: 'cols', data: cols, getPosition: (d) => d.pos, getElevation: (d) => d.v * 800000,
      radius: 60000, getFillColor: [255, 140, 0, 220], pickable: true }),
    new ArcLayer({ id: 'arcs', data: arcs, getSourcePosition: (d) => d.source, getTargetPosition: (d) => d.target,
      getWidth: (d) => 1 + d.value * 4, getSourceColor: [0, 200, 120], getTargetColor: [220, 60, 60], greatCircle: true }),
  ]});
  map.addControl(overlay);
  map.on('click', 'fill', (e) => { window.__clicked = e.features[0].properties.name; });
  // 110m -> 50m swap on zoom
  let hi = false;
  map.on('zoomend', async () => {
    if (!hi && map.getZoom() > 3) { hi = true; map.getSource('c').setData(await loadCountries('50m')); window.__swapped = true; }
  });
  startFpsProbe();
  window.__rotate = () => { const step = () => { map.setCenter([map.getCenter().lng + 0.3, 20]); window.__raf = requestAnimationFrame(step); }; step(); };
  window.__stop = () => cancelAnimationFrame(window.__raf);
  window.__flyToCountry = () => map.flyTo({ center: [10.4, 51.1], zoom: 5, duration: 3000 });
  window.__ready = true;
});
