# Current web model exports

Both files are deterministic local exports of the refined optional-battery Blender project. The source `.blend` remains unchanged and editable. The browser defaults to hiding the optional battery.

| Representation | Triangles | Exported vertices | Materials | Embedded images | Bytes / binary size |
| --- | ---: | ---: | ---: | ---: | ---: |
| Preserved original | 534,490 | 357,745 | 27 | 0 | 11,850,856 / 11.30 MiB |
| Refined full export | 488,054 | 338,478 | 30 | 5 | 14,935,792 / 14.24 MiB |
| Refined public web asset | 262,810 | 206,782 | 30 | 5 | 10,417,808 / 9.94 MiB |

`output/web/air65-ii.glb` retains the full evaluated surfaces. `output/web_optimized/air65-ii.glb` is the separately optimized public asset, copied exactly to `site/dist/assets/air65-ii.glb`. Each directory contains source identity, serialized component bounds and validation metadata. Five PNG images are embedded unchanged from the authored assets; no reference photograph is embedded.

Both pass Khronos validation with 0 errors and 0 warnings. Informational notices are retained in their JSON reports. Optimized serialization is byte-identical on repetition. Group transforms and all 13 component controls remain intact. Coordinates map `(x, y, z)` millimetres in the source to `(x, z, -y)` metres in glTF.

Detailed current optimization statistics, measured browser timings, material limits, source fingerprints and accuracy limits are in [refinement_validation.md](refinement_validation.md). The initial optimization experiment on the preserved original model is documented in [web_optimization.md](web_optimization.md); its numbers are historical and do not describe the final refined asset.

Full GLB SHA-256: `6ea007a2a37bfabe00bc9904472eed24b80cefa485f8d6b97213a1246f8768b8`.

Optimized GLB SHA-256: `8ddbc0195e22c59bc8dcf6de34885021e5cc099aea5b33a08817a11a7b6395a7`.

The source studio lights and Cycles/AgX pipeline are not glTF model data. Web transmission, tone mapping and lighting produce a different material response; final browser screenshots and independent review assess that representation directly.
