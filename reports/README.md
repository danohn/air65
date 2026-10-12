# Evidence index

The current additions are the studio portrait, ten-second spin-up and interactive motor controls. Start with [studio and motion integration](site/studio_motion_validation.md), [independent site review](site/studio_motion_review.md), [motion export validation](web_motion_export.md) and [studio source validation](studio_source_validation.md). The motion GLB preserves the refined static geometry while separating rotating parts.

The underlying Air65 II refinement was published as Site version 2 on 12 October 2026. [refinement_validation.md](refinement_validation.md) and [refinement_independent_visual_review.md](refinement_independent_visual_review.md) remain the shape, proportion and static performance evidence for that version. Its exact static asset hash differs from the new motion hierarchy.

The GitHub source repository intentionally excludes generated `output/` artifacts. [Restore releases v0.1.0 and v0.2.0](../docs/RELEASES.md) to resolve original and studio output links. Reference-photo links point to their original publishers; those photos and `visual_comparison.png` are not distributed here. Selected website and before/after screenshots under this directory are retained as review evidence.

- `refinement_validation.json` contains the numerical, provenance, persistence, export and actual browser measurement evidence.
- `refinement_verified_anchors.json` checks all 35 published scalar values against the preserved original.
- `refinement_canopy_*`, `refinement_pcb_dimension_check.md`, `refinement_surface_audit.md` and `refinement_materials_and_battery.md` explain the current component work and estimates.
- `refinement/` contains comparable before/after sheets and the rejected early optimized lens image.
- `browser_performance.json` contains the measured nine browser runs, including exact asset hashes and GPU identity.
- `site/studio_motion_deployment.json` identifies the studio/motion deployment after publication. `site/deployment.json`, `site/public_asset_validation.json` and `site/published_refinement_*.jpg` retain the preceding Site version 2 evidence.
- `validation_report.md`, `final_visual_signoff.md` and `web_model_export.md` point to or describe the current delivery.

The prototype, component-authoring, spatial-audit, original revision-log and `visual_review_v1/v2` reports retain the earlier workflow history. Their old fingerprints and counts describe those earlier snapshots. The full original delivery is also preserved under `output/refinement_baseline/`. `web_optimization.md` starts with a historical baseline experiment and then records the final corrections. `site/viewer-*.jpg` and `site/deployment_v1.json` describe the previous public viewer; `site/refined_exploded_wireframe.jpg` and `refined_zoom_rotate.jpg` demonstrate controls during refinement, before the final camera-protection export.

No earlier signoff or passing numeric check establishes physical replication accuracy. Use the current independent review's residual findings when assessing fidelity.
