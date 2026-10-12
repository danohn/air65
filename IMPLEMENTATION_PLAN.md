# BETAFPV Air65 II — implementation plan

Target selected by the user: **Air65 II**. The current manufacturer **Racing** configuration was locked from coherent evidence before component modelling.

## Ordered workflow

1. **Three independent research tasks (parallel).** Technical dimensions; visual references and proportions; deterministic parametric modelling and JSON techniques. Each researcher owns separate outputs in `research/`; the visual researcher owns `references/`.
2. **Consolidate a sourced design specification.** Main agent resolves variant conflicts, distinguishes verified values from estimates, records provenance and confidence, and defines the component schema.
3. **Spatial architecture review.** A dedicated agent establishes axes, origins, mount coordinates, vertical layers, shared dimensions, and constraints. Main agent integrates and freezes these decisions before delegating component modelling.
4. **Minimal working prototype.** A small assembly proves JSON parsing, reference resolution, editable geometry, headless `.blend` generation, multiview rendering, and numerical validation. Inspect this before adding detail.
5. **Independent component modelling.** Assign disjoint JSON files for frame, propulsion, and canopy/electronics. Shared dimensions can only be referenced, never independently redefined. Requests for architecture changes return to the main agent.
6. **Integrate and render.** A deterministic Python build resolves component instances and procedural geometry into named, editable Blender collections. Produce orthographic and perspective reference views.
7. **Independent visual review.** A separate agent compares the actual rendered images against manufacturer photos. Record mismatches with evidence, impact, and uncertainty.
8. **Improve and validate.** Fix major silhouette/proportion errors first; rerender and verify dimensions, constraints, schema, reproducibility, and editability. Preserve review history and report remaining uncertainty honestly.

## Deliverables

- `specs/`: consolidated design, spatial architecture, materials, shared schema, assembly, component JSON.
- `research/` and `references/`: source records and local reference images with provenance.
- `scripts/`: Python command line builder, Blender renderer, validators, and meaningful tests.
- `output/`: editable Blender project, multiview PNG renders, resolved assembly and numerical metrics.
- `reports/`: independent visual review, revision notes, and final validation report.
- `README.md`: reproduction commands, file guide, coordinate system, limitations.

## Architecture rules

- Millimetres in all JSON. Conversion to Blender scene scale occurs in one place.
- A single shared parameter registry controls important dimensions and mounting points.
- Every important parameter records source, verification status, confidence, and uncertainty.
- JSON is data: no arbitrary Python expressions, shell commands, or executable code.
- Stable names, ordered construction, fixed mesh sampling and render settings, no random geometry.
- Keep procedural objects, materials, and useful modifiers editable in the `.blend`.
- Agents edit only their assigned paths; main agent owns schema, scripts, integration, and final deliverables.
- Images constrain appearance; perspective photos do not establish verified physical dimensions.
- This is a visual/dimensional recreation, not a certified manufacturing model. Unknown dimensions remain explicitly estimated.

## Validation gates

1. JSON schema and safe parameter-reference validation.
2. Recomputed motor diagonal, duct/prop clearance, mount spacing, overall envelope and vertical stack checks.
3. Successful background Blender execution and reopening of the saved project.
4. Mesh/material/collection presence, finite coordinates, sensible bounds, and repeatable geometry fingerprint.
5. All required renders exist and are inspected against actual reference photos.
6. Review findings either resolved or carried into the final report as limitations.

## Execution record

- 2026-10-12: Empty workspace inspected. Three researchers dispatched independently. User selected Air65 II. Local Blender 5.2.2 LTS and uv 0.11.15 verified.
- Research completed in three separate JSON/Markdown handoffs. Main consolidated the current Racing variant, schema and source hierarchy.
- Spatial architect established the shared 119-parameter registry, anchors and constraints before component delegation. Both distinct frame/FC mounting pitches were retained.
- Minimal prototype built, rendered, numerically checked and retained under `output/prototype/` before detailed component work.
- Three component modelling agents authored separate frame, propulsion and canopy/electronics JSON files. Main integrated the shared renderer and assembly.
- Independent visual review identified important canopy, propeller, frame-surface and camera-finish errors. Assigned modellers corrected their own files; main controlled shared-parameter and material changes.
- Second visual review accepted the major shape corrections with residual estimates documented. A separate spatial audit found screw engagement and a canopy dependency defect; main fixed both and added regression checks.
- Final deliverables completed: editable Blender project, eight 1400px renders, isolated frame, optional battery, JSON/contracts, scripts, portable archive and validation report.
- All 87 numerical checks and 12 software tests pass. Saved-project reopening and separate regeneration have matching geometry fingerprints; all eight final PNG hashes are verified. Optional battery targeted fit passes. Independent spatial and final visual closure reports are complete.
