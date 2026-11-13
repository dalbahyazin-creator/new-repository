import Globe from 'globe.gl';
import { loadCountries, makeArcs, centroid, color, startFpsProbe } from './common.js';

const fc = await loadCountries('110m');
const arcs = makeArcs(fc);
const rgb = (c) => `rgb(${c.join(',')})`;
const g = new Globe(document.getElementById('globe'))
  .backgroundColor('#0b1020').showAtmosphere(true)
  .polygonsData(fc.features)
  .polygonCapColor((f) => rgb(color(f.properties.value)))
  .polygonSideColor(() => 'rgba(255,140,0,0.6)').polygonStrokeColor(() => '#334')
  .polygonAltitude((f) => 0.005 + f.properties.value2 * 0.08) // extrusion of a 2nd metric
  .arcsData(arcs).arcStartLat((d) => d.source[1]).arcStartLng((d) => d.source[0])
  .arcEndLat((d) => d.target[1]).arcEndLng((d) => d.target[0])
  .arcStroke((d) => 0.2 + d.value * 0.8).arcColor(() => ['#00c878', '#dc3c3c'])
  .onPolygonClick((f) => { window.__clicked = f.properties.name; });
g.globeMaterial().color.set('#0f1a33');
g.controls().autoRotate = false;
startFpsProbe();
window.__rotate = () => { g.controls().autoRotate = true; g.controls().autoRotateSpeed = 2; };
window.__stop = () => { g.controls().autoRotate = false; };
window.__flyToCountry = () => g.pointOfView({ lat: 51.1, lng: 10.4, altitude: 0.15 }, 3000);
window.__ready = true;
