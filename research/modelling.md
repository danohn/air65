# Parametric modelling research for BETAFPV Air65 II

Use a small, deterministic JSON-to-Blender interpreter built on the installed Blender Python API. It is sufficient for editable geometry, curves, modifiers, materials, cameras and renders, and avoids making the first prototype depend on an add-on or a remote service. This research establishes techniques only. The consolidated specification and spatial architect must decide every important dimension, target configuration and assembly coordinate.

The local environment has `/Users/daniel/.local/bin/uv` version 0.11.15 and `/Applications/Blender.app/Contents/MacOS/Blender` version 5.2.2 LTS, build `d13f752e3b9c`. Blender is not on PATH. A read-only factory-startup headless invocation succeeded, confirmed `bpy.app.background`, and confirmed `Mesh.from_pydata` is available. Blender embeds Python 3.13.13. A uv-managed Python 3.14 wrapper can validate and launch Blender, while the renderer runs inside Blender's own Python; do not assume wrapper dependencies exist there. No environment changes were made.

## Shared representation

Use [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12), reject unknown properties, and validate each operation with a discriminated schema. Keep the format deliberately small: allow literal finite numbers or `{ "param": "canonical_id", "scale": 1, "offset": 0 }` references. Precompute anything more complicated in the central parameter registry, with its derivation recorded. Do not accept free-form Python, expression strings, imports or arbitrary file paths.

The main agent owns a central parameter registry and the spatial contract. Each important value records its unit, evidence status, confidence basis, source IDs and uncertainty where justified. Manufacturer specification, image-derived measurement, arithmetic derivation, visual estimate and modelling assumption are distinct statuses. A stated nominal manufacturer dimension is not a verified tolerance. Image confidence also depends on projection, lens distortion, occlusion and whether the photographed component is the exact revision being modelled.

Every component document carries `component_id`, schema version, contract version/hash, declared parameter dependencies, source IDs, geometry nodes, named local anchors and explicit uncertainties. The assembly places component instances at the architect's shared anchors. Component authors may propose corrections, but must not silently replace locked dimensions. Stable IDs become object names and validation-report keys.

Each geometry node has `id`, `op`, strictly validated `args`, a canonical `material` reference and a documented transform. Useful optional modifiers are bevel, solidify, subdivision and mirror. Define transform order and angle convention once; generate sizes in mesh coordinates before applying modifiers whose widths depend on local scale.

## Compact geometry operation set

| Operation | Role | Important implementation detail |
|---|---|---|
| `box` | Electronics, connector blocks, prototype battery | Bevel only after final local dimensions are established. |
| `cylinder` | Motors, shafts, lens barrels and screws | Bore holes require annular geometry or explicit apertures. |
| `annulus` | Ducts and rings | Explicit outer/inner loops with bridged rims; extend to a radial-z cross section for taper and moulded lips. |
| `polyline_tube` | Wires, antenna lead, simple struts | Editable curves are suitable for round wire; shaped struts need a swept nonround profile. |
| `polygon_extrusion` | PCB outline, tabs and flat braces | Support concave outlines and holes with deterministic triangulation. |
| `loft_shell` | Hollow curved canopy | Matching samples between sections, explicit openings and uncapped underside; retain useful thickness modifier. |
| `prop_blade` | Propeller chord, sweep and twist | Spanwise stations define planform and foil surfaces; centrally supplied blade count and handedness. |
| `mesh` | Explicit original topology fallback | Vertices and indexed faces remain data, with provenance and the same validation gates. |

For thin ducts, explicit inner and outer surfaces are more controllable than repeatedly subtracting cylinders. A radial-z profile provides thickness, taper and top/bottom lips without fragile coplanar booleans. Angular samples, profile order and face winding stay fixed. Duct rings and motor-support arms can remain separate editable objects for visual reconstruction; the final report should say if this is not a unified watertight printable part.

The Air II canopy needs its actual hollow structure and open spaces, not a generic solid blob. Start with a few controlled cross sections or boundary curves, bridge them into a shell, and add the camera opening, cap aperture and visible braces. The manufacturer explicitly describes the revised brace, cap vent and curved profile, so those are revision-specific modelling priorities. [BETAFPV Air II Canopy](https://betafpv.com/products/air-ii-canopy).

An editable Solidify modifier is useful for the canopy, but thickness on complex curved topology is approximate. Validate the evaluated geometry where clearance or wall thickness matters; a modifier setting is not proof of physical thickness. Keep openings as boundary topology where possible; retain any necessary boolean cutters in a named hidden collection. [Blender Solidify documentation](https://docs.blender.org/manual/en/5.3/modeling/modifiers/generate/solidify.html).

For propellers, use spanwise stations containing radius, chord, sweep, height, twist angle and thickness. Build a thin closed upper/lower surface with a rounded tip, then instance the blade around its hub. The product contract must supply diameter, blade count, hub fit and variant. Photographs can constrain planform but do not verify an airfoil or exact pitch distribution. Never silently infer a generic two-blade propeller solely from the original task's modelling suggestion.

Curves with bevel remain easy to edit for wires and antenna leads. Round wire and a flat moulded strut should not share a geometry assumption simply because both are elongated. Blender supports bevelled curves and custom profile objects, with cross sections defined in the profile object's local XY plane. [Blender curve geometry](https://docs.blender.org/manual/de/4.5/modeling/curves/properties/geometry.html).

## Deterministic builds and editability

A suitable invocation pattern is `Blender --background --factory-startup --python-exit-code 1 --python renderer.py -- --assembly assembly.json`. Arguments after `--` belong to the script. The command was checked locally; Blender's documentation also describes these flags and the significance of argument order. [Blender command-line arguments](https://docs.blender.org/manual/en/3.6/advanced/command_line/arguments.html).

Prefer `bpy.data` and direct mesh/curve construction to UI-state-dependent operators. Sort component files and IDs, fix sample counts and tessellation, avoid random geometry, and make all material and camera settings explicit. Store each component in a named collection under a parent Empty. Keep editable curves and useful modifiers, and embed the source specification or a manifest in Blender Text datablocks/custom properties. Manual `.blend` changes remain editable but do not automatically update JSON; document regeneration as a one-way process.

Record the Blender build, renderer/device, input hashes, seed, resolution, sample count, color transform, lights and world. For regeneration, compare stable semantic metadata and rounded geometry-coordinate hashes. Byte-identical `.blend` files are not a sensible default promise, and pixel identity is only testable for a pinned Blender build, device and render configuration. A CPU Cycles configuration with fixed seed and explicitly chosen sampling settings is a conservative comparison baseline.

Start the minimal prototype with four thin ducts, a central board, motor envelopes and a hollow canopy envelope, all using the frozen architecture. Prove the schema, parameter references, scene naming, save step and multiview rendering before adding curved braces, exact canopy apertures, blade twist and small components. This is an implementation milestone, not a claim that its geometry is accurate.

## Validation and review

JSON Schema handles structure; the wrapper must separately check references, units, unique IDs, stale contract hashes, geometry constraints and ownership of shared dimensions. After building, measure evaluated bounds, motor/duct/prop coaxiality, wheelbase, rotor-to-duct clearance, board mount alignment and camera direction. Report acceptable nonmanifold or disconnected-geometry exceptions explicitly.

Produce top, bottom, front, rear, left, right and three-quarter views. Orthographic neutral clay renders expose geometry; material renders assess appearance. Match the photo's camera before comparing apparent proportions. Silhouette overlap or landmark pixel errors are useful only when view/projection and object configuration are aligned. Rank frame layout and duct size first, then canopy silhouette and camera placement, motor height and propeller shape, followed by materials, cables and labels. Unseen surfaces and uncertain measurements remain labelled estimates after review.

## Open-source tools and skills investigated

| Candidate | Verified role/license statement | Decision |
|---|---|---|
| [Sverchok](https://github.com/nortikin/sverchok) | Blender parametric node system; repository declares GPL-3.0 | Useful reference for profiles, surfaces and indexed geometry; unnecessary dependency for the initial pipeline. |
| [build123d](https://github.com/gumyr/build123d) | Python parametric BREP on Open Cascade; Apache-2.0 | Possible later route for manufacturing-grade solid geometry; does not remove photographic shape uncertainty. |
| [TerminalSkills Blender scripting](https://github.com/TerminalSkills/skills/blob/main/skills/blender-scripting/SKILL.md) | Public skill, Apache-2.0 declared in metadata | Headless and mesh/curve examples are relevant; read as research only, with API recipes verified against installed Blender. |
| [pinion05 Blender headless skill](https://github.com/pinion05/blender-headless-skill) | Blender 4.2 headless examples/tests; README declares CC0 | Useful older reference; Blender 5.2 compatibility must be checked independently. |

No skill or add-on was installed, no external skill was adopted as a governing instruction, and no third-party modelling code was copied into the project. The direct Blender interpreter is the smallest architecture aligned with the experiment.

The Air II and original Air Canopy manufacturer pages and targeted BETAFPV support search did not establish an official downloadable Air65 II STL. This does not prove one is unavailable. If one is subsequently found, record its exact revision, units, hash, source and license, and identify it explicitly as a measurement/comparison reference. Do not silently substitute an asset for generated component JSON or assume that a downloadable asset has an open reuse license.

The companion `modelling.json` contains the machine-readable operation recommendations, suggested field contract, validation gates, evidence links and runtime facts.
