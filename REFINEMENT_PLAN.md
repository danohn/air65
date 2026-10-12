# Air65 II refinement pass after the Sketchfab comparison

Started 12 October 2026. The user handoff is preserved verbatim in `research/sketchfab_comparison_handoff.md`. The existing public Site is version 1 at https://air65-ii-explorer.danohn.chatgpt.site, project `appgprj_6acc1dd67ef48191a83f2578cef3428e`. Its public audience and identity must be preserved.

## Evidence and limits

The Sketchfab model depicts an earlier Air65 configuration and is a craftsmanship benchmark, not dimensional evidence for the selected Air65 II Racing. The comparison is qualitative and uncalibrated. Its counts are user-reported observations; the page returned HTTP 403 to the web reader on this pass. No assets from it are imported.

The earlier visual signoff closes the defects identified in that review. It does not establish equivalent visual fidelity or preclude further substantial improvements. All published dimensions remain frozen unless a new primary source contradicts them; any estimated-parameter revision is owned centrally and recorded explicitly.

## Ordered work

1. Preserve source specifications, scripts, reports, final renders, detailed models and web export in `output/refinement_baseline/`; inspect current deployment/source state.
2. Audit the canopy against Air II reference and comparable existing views. Approve specific continuous-surface and transition changes before implementation. Keep camera barrel and collar, mounting axes, mounting pitch and other anchors fixed.
3. Add reference-supported printed PCB detail and the selected 280 mAh battery wrapper, using deterministic authored textures rather than raised lettering or photo projection. Improve battery pouch/connector shape inside its published envelope.
4. Refine material response against Air65 II imagery. Render before and after under the same cameras and lighting so visual improvement is assessable. Keep optical settings labelled as estimates.
5. Export a separate optimized browser mesh while retaining the full editable Blender source. Record measured source-to-export deviations, component transforms/bounds, material/texture counts and repeatability. Benchmark actual browser frame timings before making any performance claim.
6. Run the dimensional checks and an independent visual comparison using preserved images. Correct significant findings, regenerate final outputs, update the existing public viewer and record deployment.

## Ownership

- Main agent: integration, central measurement/material registries, schema and renderer, battery, browser performance measurements, site source and publishing, final validation and packaging.
- Canopy agent: initial audit; canopy JSON and its authoring script/report only after approved scope.
- Surface-detail agent: Matrix II research, electronics JSON and its deterministic texture authoring script/assets, assigned report. No shared dimensions or battery edits.
- Web-export agent: exporter and optimization config, isolated optimized outputs and report. No edits to detailed source, JSON or Site.
- Independent reviewer: new comparison report only; no component or shared-source edits.

Acceptance requires both numerical conformance and an explicit qualitative visual assessment. Reduced triangles, successful rendering, and schema checks are not substitutes for that assessment.
