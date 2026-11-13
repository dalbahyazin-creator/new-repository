# Globe spike: MapLibre + deck.gl (A) vs globe.gl (B)

**Recommendation: Option A, MapLibre GL JS 5 (globe projection) with deck.gl 9.4 interleaved.**

## What I built
Both options render the same data, defined in `spike/src/common.js`:
- **Countries:** Natural Earth countries via `world-atlas` 110m TopoJSON, about 177 countries, each colored by a random value.
- **Second metric:** shown as columns in A and as extruded country shapes in B.
- **Arcs:** 300 great-circle arcs.
- **Interaction:** clicking a country selects it.
- **Detail swap:** A swaps the 110m outlines for 50m when zoomed past z3.

To run it: `cd spike && npx vite`, then open `/a.html` or `/b.html`. The harness is `bench.mjs`, which uses Playwright with headless Chromium. It measures load time, then frame rate during 4 s of auto-rotation, then frame rate during a 3 s fly-to from the whole globe down to Germany.

## Results
The sandbox has **no GPU** and renders WebGL in software (SwiftShader), so the frame rates below are far below what real hardware gives. Use them to compare A with B, not as absolute numbers.

| | A desktop | B desktop | A phone 412×915 @2x | B phone |
|---|---|---|---|---|
| Load to first render | 0.53 s | 1.60 s | 0.49 s | 1.66 s |
| Rotate fps (p95 frame time) | **15.7** (200 ms) | 5.7 (1117 ms) | **9.1** (350 ms) | 6.4 (833 ms) |
| Fly-to fps (p95 frame time) | **14.0** (283 ms) | 4.4 (1117 ms) | **9.1** (350 ms) | 4.0 (1767 ms) |
| 110m → 50m swap | works | not built (would rebuild all meshes) | works | – |
| Console errors | 0 | 0 | 0 | 0 |

Screenshots of each run are in `spike/shots/`.

## Assessment against the criteria
| Criterion | A: MapLibre + deck.gl | B: globe.gl |
|---|---|---|
| Smooth zoom from globe to country | Native. The view moves from globe to Mercator as you zoom in, borders stay sharp at country level, and labels and capitals come with the vector-tile stack. | The three.js camera only orbits. At country zoom you see faceted low-poly shapes (see `b-desktop.png`), and there are no tiles, labels or semantic zoom. |
| Choropleth / extrusion / arcs | Choropleth is a MapLibre data-driven fill. Extrusion and arcs are deck.gl `ColumnLayer` and `ArcLayer`. All are GPU-instanced and pickable. | All three are built in, but extruded polygons are rebuilt on the CPU whenever data changes. |
| Performance | About 2.7× B on desktop and 1.4–2.3× on phone. Data updates are cheap because they only change paint expressions and attributes. | Slowest in every test. Changing a color or a slider rebuilds the geometry. |
| Flat projection toggle | One call: `setProjection({type:'mercator'})`. | Not supported; it would need a second library. |
| Fly-to, fit-bounds, zoom controls | `flyTo`, `fitBounds`, `NavigationControl`, and scroll, pinch and double-click zoom all work out of the box. | `pointOfView` only, with no fit-to-bounds. |

**Issues to handle in phase 2 if we pick A:**
- deck.gl and luma.gl versions must match exactly. deck 9.1 failed to build with luma 9.4, so pin both in the lockfile.
- deck columns need their height capped by zoom level, or they lean out of frame when zoomed in (see `a-desktop.png`).
- MapLibre needs a glyphs URL for labels. Self-host the fonts, because the demo tile and glyph servers are blocked in this sandbox and that would be fragile in production too.

**Still to measure:** the 60 fps desktop target and a real mid-range phone. Neither can be tested here without a GPU. I'll run the same harness on real hardware at the start of phase 2, using Chrome's FPS meter on a mid-range Android device.
