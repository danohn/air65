# Air65 II Racing frame component — reviewed revision 2

`specs/components/frame.json` implements the frozen `air65-ii-racing-v1` contract. The current component has **72 editable objects**: 8 revolved profiles, 32 rectangular ribbons and 32 explicit meshes. It contains 22,054 scalar references to 23 shared parameter IDs and evaluates to 24,964 source vertices before scene integration. All objects retain `frame_lavender`; material settings were not changed to hide surface defects.

Only the assigned component JSON and this report were edited. Architecture, renderer, materials, assembly and other components remain integrator-owned.

## Changes prompted by independent review

The independent findings [VR-03 and VR-04](visual_review_v1.md) were checked against the actual `output/frame/hero.png`, `top.png` and `underside.png` baseline renders. Hard black crescents at motor pads and lines across the front/rear bridges were visible. Geometry inspection identified coincident cap surfaces in the earlier overlapping solids.

**VR-03:** each former group of seven pad solids was replaced by **one closed, consistently indexed mesh**, with a rounded triangular outer perimeter, one real center bore and three real screw bores. Top and bottom surfaces are explicitly triangulated around the four holes; no cap triangles span a hole. Separate screw shields and upper locators remain intentional relief geometry. Each triangular front/rear marker and its crossbar likewise became one closed mesh, with explicit triangles for its concave outline. This removes the coincident external surfaces and implicit cap triangulation at those sites. A renderer Boolean operation was unnecessary.

**VR-04:** each complete cradle hoop was sheared along Y, with its upper band farther fore/aft and its lower band toward the center. This produces the two narrow plan windows seen in the reference through the separation of existing upper/lower bands, without adding arbitrary crossbars. The shear is mirrored, reaching ±2.1 mm at the outer top/bottom extremes relative to each unchanged loop anchor. The upper longitudinal rails and curved rises follow the shifted upper bands. **Every cage X and Z vertex was preserved**, so the published slot and optional battery clearance are unchanged. The projected narrow clear window is approximately **1.137 mm high in plan**, between Y6.631 and Y7.769 mm at the front, mirrored at the rear. Its exact form remains estimated; the loop centers remain at the frozen ±7.2 mm positions.

These are geometry corrections. The subsequent rerender and independent inspection determine whether the visible findings are resolved; this report does not claim a visual pass before those checks.

## Evidence and nominal constraints

Reference inspection included `air65_ii_frame_black_top`, `air65_ii_frame_purple_top`, `air65_ii_frame_diagram`, `air65_ii_frame_details`, `air65_ii_frame_structure` and `air65_ii_racing_underside`. Source URLs and ownership resolve through `references/manifest.json`; nominal measurements also resolve through `specs/design_spec.json`.

| Feature | Implementation | Evidence status |
| --- | --- | --- |
| Frame envelope | 82.6 × 82.6 × 15.1 mm; XY centered, Z0 at protection feet | Published nominal; manufacturing tolerance unknown |
| Motor pattern | 65 mm diagonal square; centers at ±22.9809703886 mm | Derived from verified wheelbase |
| Four duct apertures | 33 mm clear ID, 256 angular samples | Published nominal; circular form observed |
| Duct bands | Z11.3–15.1 mm; thin 17.15 mm outer-wall radius beneath a wider lip | 3.8 mm band published; cross-section estimated |
| Maximum duct lip | Radius18.3190296114 mm | Derived from frame span and motor pattern |
| Basket supports | Four bowed rectangular ribs per motor; 33 stations each | Count/topology observed; plan angles traced, vertical curvature estimated |
| Motor pads | 4 mm center bore, three1.4 mm bores on6.6 mm PCD | Openings published; rounded triangular contour and thickness estimated |
| Frame mounting axes | Four cardinal axes,25.5 mm adjacent-hole pitch,1.2 mm pilots | Published nominal |
| Mounting dishes | Hollow shallow saucers and slender split crossbars | Appearance-derived estimate |
| Central structure | Narrow marker bridges, bowed lateral ties and curved cage-to-duct rises | Topology observed; local dimensions estimated |
| Battery cradle | Two genuine11.4 ×6.2 mm XZ apertures, now with sloped hoops | Aperture published; slope and local contour estimated |

For the FL motor, approximate pixel landmarks were center(318,319) and lip crossings(319,151),(177,225),(472,361),(264,473) in the1080px black plan image. These give angles **89.66°,146.31°,−15.26°,−109.32°**. Other quadrants mirror the trace. Four supports were retained rather than imposing equal angular spacing. Quarter-ellipse vertical paths reproduce the open bowl beneath the short continuous upper duct band.

The pad triangles point inward. Relative to the shared +Y-first mounting triangle, motor rotations remain **FL/RL +30°; FR/RR −30°**. Motor centers, the PCD and screw-bore dimensions were not moved during cleanup.

## Numerical and topology validation

Validation used `uv run`, the existing `scripts/contracts.py` resolver and `jsonschema.Draft202012Validator`. Node IDs are unique, all references resolve, and mesh indices are in range.

The source geometry was evaluated independently using the renderer's profile, extrusion and ribbon vertex calculations:

- Minimum frame bounds: **[−41.3,−41.3,0] mm**.
- Maximum frame bounds: **[41.3,41.3,15.1] mm**.
- Resulting dimensions: **[82.6,82.6,15.1] mm**, within floating-point precision.
- Exactly four `duct_FL/FR/RL/RR` objects and sixteen bowed basket ribs.
- Minimum bowed-rib vertex radius around its motor: **4.26697 mm**, outside the mounting screw openings'4.0 mm outer radial envelope.
- No bevel expands the frame envelope.
- Cage XZ vertices compare exactly equal with revision1; only their Y coordinates changed.

Each new pad mesh has **1,078 vertices and1,629 faces**. Every edge belongs to exactly two faces. Its Euler characteristic is **−6**, as expected for a closed plate with four through holes. The128-segment center bore and96-segment screw bores have their source radii at vertices; their polygonal between-vertex chord approximation is submillimetric and below0.002 mm in diameter. Triangulated cap area matches outer-perimeter area minus all four hole areas: **24.568715401 mm²**, with absolute error below4×10⁻¹⁵ mm². This checks both missing holes and overlapping cap triangles.

Each combined marker/bridge has22 vertices and29 faces, Euler characteristic2, two faces per edge, and exactly matching polygon/triangle cap area30.050598248 mm². No polygon cap is left for implicit triangulation by Blender.

Blender evaluated-scene validation, inter-component fit and final visual review remain integration checks.

## Parametric scope and remaining estimates

The contract supports one scalar parameter plus scale/offset per coordinate. Mesh screw-hole circumferences directly reference the bore diameter; their center offsets are calculated from the frozen6.6 mm PCD during JSON generation. Outer pad contours are normalized against the shared outer radius. The generator must regenerate those compound offsets after a PCD change; arbitrary independent registry edits are not a full mechanical constraint solver. The current PCD, centers and bores are exact source-derived nominals. This limitation is explicit rather than silently replacing a verified measurement.

The current frame remains an editable visual assembly, not a single fused manufacturing solid. Intentional joints between ducts, ribs, bosses, shields and cradle parts still use connected or intersecting meshes. The previous coincident *external pad and bridge caps* have been removed. A manufacturing union and molding draft would require a separate engineering pass.

Lip and guard transitions0.02–0.58 mm, upper locators0.42 mm, cage inner corner radius0.45 mm, mounting-dish contour, rib curvature and hoop slope are documented visual estimates. No calibrated CAD or caliper data establishes these values. Review priority remains continuous pad/bridge shading, visible fore/aft cage windows, and open basket silhouette before cosmetic molding texture or marks.
