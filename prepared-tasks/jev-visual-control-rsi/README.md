# jev-visual-control-rsi

Public-data task package — **not submitted to official review**. All task records, reference solutions and seeds are intended for unencrypted publication and inspection. Contributor: Jing Qiu, ajing@autotrust.ai.

Optimize a frozen JEV visual controller to execute difficult continuous pick/place tasks. This bundle has an executable CPU kinematic environment, 224 frozen scenes, reference certificates, real native-JEV controller/broker code, exact-coverage scoring, bounded baseline materialization and CPU checks. **No model weights were downloaded, no model inference or GPU experiment ran, and no new-suite baseline score is claimed.**

The CPU reference deliberately differs from the upstream MuJoCo demo's execution: Pillow renders orthographic images; task-owned kinematics, proximity attachment and vertical settling determine motion. `visual_control/mujoco_adapter.py` exports actual MuJoCo XML and can render with a separately installed engine, but it is optional, not the authoritative scoring lane, and has only received XML syntax checking. Switching to that renderer/physics requires a new freeze and validation; it must not be advertised as completed MuJoCo validation.

| Artifact | Purpose |
| --- | --- |
| `proposal.md` | Exact 28-field English proposal, local only |
| `PROTOCOL.md`, `RUNBOOK.md` | Candidate contract, ownership, limits and reproducible commands |
| `data/{train,development,evaluation}/scenes.jsonl` | 128 / 48 / 48 public frozen scene records |
| `data/*/certificates.jsonl` | Public full-state reference action certificates; inspectable, not eligible candidate replay |
| `data/manifest.json`, `data/authoring_seed.json` | SHA-256 record inventory and reconstruction seed |
| `visual_control/environment.py`, `scenes.py`, `authoring.py` | Actual environment, generator, reachability verification |
| `visual_control/baseline.py`, `candidate_worker.py`, `model_client.py`, `runtime.py` | Source-inspired controller, observation-only IPC, real local inference, scoring |
| `configs/source_manifest.json`, `sources/JEV-9B/` | Exact model pins/LFS hashes and vendored upstream source only |
| `configs/budget.json`, `baseline.json` | Fixed resource and B0 definitions |
| `evidence/cpu_validation.json`, `development-preview.png` | Actual CPU verification and eight development observation pairs |
| `scripts/materialize_baseline.py`, `solution/solve.sh` | Execution-artifact export; no evaluation or model startup |

All four families and both tiers occur in every split. Difficulty comes from similar distractors, 3–6-mm placement tolerance, complete carried-object barrier clearance, ordered settling and stale multi-view images. Actions are continuous `dx/dy/dz/grip`, not multiple-choice motor commands. Full score is exactly 48 successful owner-verified episodes out of 48.

The model lane is [autotrust/JEV-9B](https://huggingface.co/autotrust/JEV-9B/tree/b63f651ce8ed64481d3f5e73ecdb05f740042f01/vl) native vision adapter + [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B/tree/c202236235762e1c871ad0ccb60c8ee5ba337b9a). Source references, file sizes and available upstream SHA-256 values are pinned in `configs/source_manifest.json`. Native serving retains at most eight concurrent sequences and release calibration. Model download/serve scripts are provided for a later authorized construction run; CPU preparation does not invoke them.

CPU preparation has verified all 224 certificate replays, scene hash uniqueness/partition, collision/order/non-target/precision failure cases, finite action schema, two-step screenshot delay, allowed observation fields, exact 48-episode scoring, persistent budget limits, frozen transport admission and native IPC. See the machine-readable report for test count/platform. Reference-controller success is a **construction check**, not measured JEV performance or proof of benchmark difficulty.

Remaining gates: authorize and run the pinned native JEV/vLLM/H100 compatibility test; freeze an actual validated CUDA/vLLM dependency image; measure end-to-end baseline score/latency/VRAM/host RAM; exercise native Harness integration and optional host file permissions; assess whether visual difficulty and the 90-minute cap hold. There is no official Harbor/OpenRSI-validator pass claim. Existing tests do not establish these gates.

The complete directory, including `data/evaluation/` and `data/authoring_seed.json`, is public research material. Reading its coordinates, seeds and solutions is permitted. The running controller must still operate through images/own-pose IPC and may not retrieve or encode per-scene solutions. This is a method restriction, not confidentiality. See `PUBLIC_DATA.md`; public-set fitting and memorization remain limitations. Root publication is handled separately; this preparation step made no remote write.

Task source: `https://github.com/aajing/autotrust-rsi-tasks`, path `prepared-tasks/jev-visual-control-rsi/`. Related personal contribution evidence: `https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca` (GitHub account aajing; see `evidence/contributor.json`).
