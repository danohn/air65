# Integration and revision record

The frozen target is Air65 II Racing, contract `air65-ii-racing-v1`. That identifier names the shared interface; exact versions are identified by the source hashes in each build. Earlier rendered baselines remain available and their reviews have not been rewritten to describe the final result.

| Stage | Work and evidence | Ownership |
| --- | --- | --- |
| Research | Three parallel studies of dimensions, appearance and modelling methods; user clarification to Air65 II propagated before consolidation | Three separate research agents |
| Architecture | Consolidated design, source/confidence registry, shared schema; spatial architect established axes, anchors and constraints | Main integrator plus dedicated architect |
| Prototype | Four simple duct rings, motor/prop envelopes and central board proved JSON resolution, headless rendering, source embedding and editable save | Main integrator; `output/prototype/` |
| Initial component construction | Frame; motors/props; canopy/camera/electronics authored in disjoint component JSON files | Three component specialists |
| First integrated review | Seven assembly views, frame and propulsion inspections exposed canopy, prop, surface and finish errors despite 31 passing numerical checks | Independent visual reviewer; `visual_review_v1.*` |
| Propeller correction | Retained chord toward the tips, widened terminal cap, revised estimated hub radius centrally from 2.2 to 2.4 mm; preserved 31 mm sweep, 6.8 mm max chord and 3.3 mm hub height | Propulsion modeller; sole shared-parameter edit by main |
| Canopy correction | Replaced ladder-like topology with continuous rounded perforated strap, formed shoulders/vent and protective brow; shared anchors and nominal clamp unchanged | Canopy modeller |
| Frame correction | Replaced overlapping motor-pad and bridge caps with explicitly triangulated bored meshes; sheared existing cradle hoops to recover narrow plan windows while preserving X/Z slot geometry | Frame modeller |
| Camera/finish correction | Corrected buried solder masks; recessed optical stack; increased prop transmission and reduced roughness | Mask fix by canopy/electronics modeller; optics/material integration by main |
| Second visual review | Eight integrated views plus isolated components accepted with low-priority residual contour/material/electronic-detail limits | Independent visual reviewer; `visual_review_v2.*` |
| Spatial audit | Found floating/protruding screw shanks and unrelated aperture-to-leg parameter coupling beyond the original checks | Spatial architect acting as independent component auditor |
| Final fit/dependency correction | Screw beams now span shared-anchor offsets Z11.8–17.98; legs reference mounting width rather than antenna opening; added regression and evaluated engagement tests | Main integrator |
| Final validation | Expanded to 87 checks including evaluated motor/body dimensions, motor/prop/duct concentricity, FC thickness and camera depth. Added per-render source/checksum manifest. Saved reopen, independent rebuild and battery fit checks pass | Main plus independent spatial closure |
| Final delivery review | Hero, eight-view contact sheet and optional battery inspected. Missing multiplication glyph in contact sheet corrected to ASCII x and verified | Main presentation fix plus independent visual signoff |

No verified source dimension was changed to force photographic agreement. The only changed shared scalar was the explicitly estimated prop hub radius, within its documented uncertainty range. Local image-derived contour refinements retain their estimated status.

The first complete review build and its review are in `output/review_v1/` and `reports/visual_review_v1.*`. Its isolated frame is `output/frame/`. Revision 2 is preserved in `output/review_v2/`, `output/frame_v2/` and `output/propulsion_v2/`. The final geometry differs from accepted revision 2 mainly in screw shank extent; the canopy reference repair preserves its default shape to floating-point precision. Orthographic delivery views now share a 99 mm scale.

The final geometry fingerprint is `b7717341231c9fe97b6481735403833f0324cb75c8719d1c625e16cca6ba50c1`; revision 2 was `9276066d5dffff0725766bd5028cfa7f20804a0b37115b33b6252470bb9dd409`. Historical source hashes are expected to differ from the final interpreter and JSON. Rebuilding an old output directory from current files creates a new result; the preserved resolved JSON and metrics describe the original snapshots.
