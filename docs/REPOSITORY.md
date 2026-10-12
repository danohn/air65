# Repository and publishing layout

The GitHub repository is https://github.com/danohn/air65. It versions the JSON model, authoring/build/export scripts, tests, exact authored textures, research provenance, review evidence and a working static website. The single optimized model in `site/dist/assets/air65-ii.glb` is deliberately tracked so the website works without Blender.

`output/` and the root `dist/` are generated local directories. Editable Blender projects, renders, validation artifacts and the original comparison baseline are distributed through [releases](RELEASES.md). The ignore rule is `/dist/`, anchored at the repository root; `site/dist/` contains the website source and must remain tracked. `uv.lock` is also tracked.

Downloaded third-party reference photographs and `reports/visual_comparison.png`, which includes such a photograph, remain local. Their original URLs, hashes and provenance remain in `references/*.json`. The public release packager also excludes them, including the composite inside the preserved baseline. Third-party software notices remain with the vendored code; see [attribution](ATTRIBUTION.md).

## Sites deployment

The existing public viewer is https://air65-ii-explorer.danohn.chatgpt.site. Its identity remains in `site/.openai/hosting.json`.

The GitHub working tree owns ordinary source files under `site/`. It has no nested Git repository. The original Sites publishing repository, including all three original commits and its deployment archive, was preserved in a separate sibling checkout named `air65-site-publish`. On this machine that is `../air65-site-publish` relative to the project root. Moving the local checkout did not change the deployed website.

For future website changes:

1. Edit and verify the tracked files under `site/`.
2. Open the existing Site through the supported Sites source workflow in the separate publishing checkout. Retain its existing project ID and public audience.
3. Copy the reviewed website files to that checkout, excluding Git metadata and generated deployment archives. Preserve the publishing checkout's `.git` directory.
4. Run the Sites helper there to commit/push/package, then save and deploy the returned exact source revision through Sites. Pass short-lived credentials only through the helper's hidden stdin.
5. Record the resulting deployment receipt under `reports/site/` in this GitHub repository.

Do not run the Sites source helper inside the GitHub repository: its Git history and the Sites publishing history are separate. Do not create a replacement Site for routine updates.

## Evidence and local paths

Report navigation uses repository-relative links. Links into `output/` become available after restoring release artifacts. Historical machine-readable execution receipts may retain original local paths as provenance; those paths are not executable configuration. The geometry renderer and generated model inputs are unchanged by this repository preparation.
