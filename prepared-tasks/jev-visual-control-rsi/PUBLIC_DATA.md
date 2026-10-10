# Public evaluation and reference solutions

All task-specific source, train/development/evaluation records, coordinates, goal definitions, full reference trajectories and reconstruction seeds are publicly distributable without encryption. Researcher inspection and reproduction are explicitly allowed. The source repository is `https://github.com/aajing/autotrust-rsi-tasks`, code path `prepared-tasks/jev-visual-control-rsi/`; the publication manifest identifies the immutable revision.

| Public path | Content |
| --- | --- |
| `data/train/{scenes,certificates}.jsonl` | 128 scenes and complete full-state reference solutions |
| `data/development/{scenes,certificates}.jsonl` | 48 scenes and complete reference solutions |
| `data/evaluation/{scenes,certificates}.jsonl` | 48 scored scenes and complete reference solutions |
| `data/authoring_seed.json` | Reconstruction master seed, not a credential |
| `data/manifest.json` | Counts, per-file SHA-256 and geometry partition |
| `visual_control/scenes.py`, `authoring.py`, `environment.py` | Generator, executable reference controller, physics, rendering and goal checks |
| `ARTIFACT_MANIFEST.json` | Full public package inventory and hashes |

The public evaluation namespace replaces the earlier `judge` dataset directory. Train and development geometries retain their frozen seed namespaces; evaluation is reconstructed in its explicitly named namespace and re-certified. All three splits have the same four families and two tiers; their disjointness separates development roles and geometric instances, not visibility. No inaccessible holdout is used.

The research workspace may include the complete package. `scripts/export_research.py` copies it from the explicit artifact inventory. The running controller uses a smaller execution artifact made by `scripts/materialize_baseline.py`, or a reviewed candidate with the same worker interface. It receives images, own pose, calibration, goal text and native JEV responses. It must not load published per-scene coordinates or action tables, regenerate the current scene from its seed, embed instance-indexed references, or match an image to a known solution. Inspecting a reference to understand the rules is allowed; submitting its per-scene replay as a learned visual controller is not.

These are transparent method restrictions, not secrecy claims. Public solution knowledge can influence optimization, and source review/ordinary permissions cannot prove that arbitrary code contains no encoded answer. The resulting score measures conformity and success on the public benchmark. It does not establish unseen-scene generalization, contamination-free evaluation or protection against arbitrary root access. Disclose use of public evaluation information in the candidate report; keep episode-specific references out of the executable artifact.

The full-state reference controller is only a reachability certificate. Its successful CPU replay does not measure JEV, does not count as B0 performance and cannot be used to claim H100 or MuJoCo validation. The exact score remains 100 only for 48 successful, newly executed conforming controller episodes, with ordinary failures scoring zero and invalid/incomplete attempts unscored.
