# Air65 II — handoff from Sketchfab comparison

## Purpose

Please incorporate these findings into the Air65 II project and use them to guide the next refinement pass. Preserve the project's original emphasis on visual and dimensional accuracy, shared JSON specifications, deterministic Blender generation and independent review.

Check the current main-thread state first: the website work may have progressed while this side conversation was running. This comparison did not modify any project files or model assets.

## What was inspected

The following model was inspected interactively in Chrome:

https://sketchfab.com/3d-models/tiny-whoop-fpv-drone-15dd7ffce5724af0afcc62b00545c401

- Title: Tiny Whoop FPV drone
- Author: Mallfroex
- Description identifies it as a BetaFPV Air65 Racing.
- Inspection included oblique, top and underside views, plus Sketchfab's Base Color, Matcap and Wireframe modes.
- The model-information panel was also inspected.

It was compared with our current Air65 II renders, optional-battery renders, manufacturer reference image and physical review photograph.

Important: the Sketchfab model represents an Air65 configuration, not our selected Air65 II Racing configuration. Its canopy, frame details, motors, antenna and battery must not be copied indiscriminately. It is a benchmark for visual craftsmanship, not verified dimensional ground truth.

## Overall assessment

The Sketchfab model currently looks more convincing as a finished physical object.

Our model has documented dimensions, explicit estimates, reproducible construction and an editable source. Those strengths do not establish equivalent visual fidelity.

Our earlier visual signoff should be interpreted as closure of the defects found during that review. This comparison exposes additional opportunities for substantial improvement; the signoff should not be treated as proof that the model is already a highly faithful finished reconstruction.

The comparison was qualitative. Camera poses and lighting were not calibrated, and no dimensional error percentage was established.

## Main findings

### 1. Canopy shape remains the highest-priority geometry issue

The Sketchfab canopy reads as a continuous moulded part, with flowing transitions between the lens housing and mounting legs.

Our canopy still reads more like strips, arches and a separate collar assembled together. The canopy generations differ, so the corrective target must be the actual Air II canopy photographs.

Review:
- Lens collar and brow.
- Shoulder transitions around the camera.
- Upper openings and rear arch.
- Mounting-leg transitions.
- Local thickness and cross-sections.
- Relationship between the canopy, camera PCB and lens.

Use matched views against Air65 II references before changing the geometry. Do not change a verified dimension merely to resemble the Sketchfab model.

### 2. PCB surface detail is a major visual gap

The Sketchfab PCB has dense visible detail: silkscreen, chip markings, pads and varied component surfaces.

Our PCB has the main components but substantial plain areas and sparse markings, giving it a schematic appearance.

Improve the Matrix II board using its own references. Distinguish actual component geometry from printed surface detail. Do not invent precise electronics markings or copy the older board's layout.

### 3. Materials need refinement against the Air65 II photographs

Our frame and canopy look too uniform, and the clear propellers become difficult to read in some views.

Review:
- Milky/translucent frame plastic.
- Canopy translucency and roughness.
- Propeller reflections and transmission.
- Motor metal, paint and winding appearance.
- Lens optical appearance.

The Sketchfab prop reflections are strong and are not automatically a physically correct target. Use the real reference photographs to decide the material response.

### 4. The optional battery looks unfinished

The Sketchfab battery benefits from wrapper graphics, metallic pouch edges and surface detail.

Our battery has documented nominal dimensions but a box-like appearance and simple label treatment.

Preserve the selected 280 mAh configuration and improve its own pouch shape, wrapper and connector details. Do not copy the other model's battery dimensions or graphics.

### 5. Geometry is not being used efficiently for the browser asset

The Sketchfab model achieves convincing detail with a much lower triangle count and substantial texture use.

Verified figures:

| Metric | Sketchfab information panel | Our current GLB export |
|---|---:|---:|
| Triangles | Approximately 33,000 | 534,490 |
| Vertices | Approximately 18,000 | 357,745 |
| Texture images | 20 | 0 |
| Materials | 9 | 27 |
| Asset size | 42 MB reported | 11,850,856 bytes / 11.30 MiB |

Our asset has roughly 16 times as many triangles. Each of our four motors contains 54,752 triangles—more than the entire Sketchfab model.

These counts do not establish comparative frame rate or loading speed. The Sketchfab asset is larger despite its lower polygon count, and its delivery/compression characteristics were not benchmarked.

## Recommended order of work

1. Reassess the canopy and other major visible contours against Air65 II references.
2. Correct the largest shape/proportion problems while preserving verified dimensional anchors.
3. Improve the PCB and battery surface detail.
4. Refine materials and lighting, checking both Blender and Three.js.
5. Produce an optimised web representation while retaining the detailed editable Blender source.
6. Perform a fresh independent visual review using comparable views and preserved before/after images.

For the web representation:
- Reduce excessive subdivisions where they do not affect the visible silhouette.
- Consider textures and normal maps for fine surface detail.
- Preserve component visibility controls and assembly transforms.
- Verify bounds, component alignment and important dimensions after optimisation.
- Measure actual browser performance before claiming an improvement.

Do not simply increase polygon counts.

## Relevant local files

Workspace:
`/Users/daniel/Code/air65`

Current model and renders:
- `output/final/air65_ii.blend`
- `output/final/hero.png`
- `output/final/multiview.png`
- `output/final/top.png`
- `output/final/front.png`
- `output/final/right.png`
- `output/final/underside.png`
- `output/with_battery/air65_ii.blend`
- `output/with_battery/hero.png`
- `output/with_battery/underside.png`

Web export:
- `output/web/air65-ii.glb`
- `output/web/model-metadata.json`
- `scripts/export_web_model.py`
- `reports/web_model_export.md`

Reference images:
- `references/photo_racing_oblique.webp`
- `references/air65_ii_racing_oblique.webp`
- `references/air_ii_canopy_structure.webp`
- `references/air_ii_canopy_side.webp`
- `references/air_ii_canopy_black.webp`
- `references/air65_ii_electronics.webp`

Specification and validation:
- `specs/design_spec.json`
- `specs/spatial_architecture.json`
- `specs/component.schema.json`
- `specs/components/`
- `reports/validation_report.md`
- `reports/final_visual_signoff.md`

## Coordination and acceptance

Keep the main agent responsible for integration and the shared measurement registry. If delegating refinements, assign separate component files and prohibit independent changes to shared dimensions.

Continue recording sources, confidence and the distinction between verified, derived and estimated measurements. Any justified change to an estimated parameter should be made centrally and documented.

The next review should assess both:
- Whether the model still satisfies its dimensional constraints.
- Whether it looks more like the actual Air65 II in comparable views.

Successful schema checks, render completion or a high triangle count must not substitute for that visual assessment.