# Public task preparation and runbook

All task source, records, reference solutions and seeds are public research material. Inspection is allowed; the submitted controller must use the declared live observation/model interface rather than per-scene solutions. See `PUBLIC_DATA.md`. This preparation did not submit a task, start a model or run a GPU experiment.

## Reproduce CPU checks

Use Python 3.12 and `Pillow==12.3.0`. The saved platform and actual checks appear in `evidence/cpu_validation.json`.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/cpu_check.py
python3 scripts/build_data.py --check
python3 scripts/render_preview.py
python3 scripts/freeze_manifest.py --check
```

The byte reconstruction check derives all seeds and scenes, replays their full-state reference solutions and compares records/manifests. Do not change the published seed after freeze. The bounded generator rejects duplicate geometry/seed, inadequate cell counts or an infeasible reference. The 224 reference successes prove surrogate reachability, not JEV performance. Preview images use development records.

## Research assets versus the execution artifact

The full package can be placed in the research workspace, read, audited and reproduced. Nothing in `data/evaluation/` is confidential. To copy the exact public inventory:

```bash
python3 scripts/export_research.py --output /tmp/jev-visual-public-research
```

The execution artifact is separate because it defines the submitted method's inputs:

```bash
python3 scripts/materialize_baseline.py --output /tmp/jev-visual-b0
```

`solution/solve.sh /tmp/jev-visual-b0` is equivalent. Both commands only copy files. They do not load weights or run an episode. The fixed B0 artifact contains:

```text
controller.py
candidate_worker.py
baseline.json
budget.json
source_manifest.json
PROTOCOL.md
work_manifest.json
```

A researcher may edit the controller and add allowed prompts/configuration, but must retain the task-owned worker transport or pass its hash check. Review the final artifact for per-instance tables, seed reconstruction, image-to-reference lookup and simulator imports. No evaluation record/solution file is mounted as a controller input. This does not prohibit reading those files during research; it prohibits using them as the action source at execution time. Encoded answers cannot be ruled out by a filename check, ordinary permissions or an IPC subprocess alone. Report public-data fitting and artifact-review limitations explicitly.

## Pinned model construction (not executed)

`configs/source_manifest.json` pins JEV native vision source at `b63f651ce8ed64481d3f5e73ecdb05f740042f01` and Qwen3.5-9B at `c202236235762e1c871ad0ccb60c8ee5ba337b9a`, including API file sizes and available LFS SHA-256 values. Seven source/metadata files are vendored unchanged. Their card licenses declare Apache-2.0; see `NOTICE.md` and `sources/LICENSE-APACHE-2.0`. No weight tensor was downloaded for this preparation.

After model construction/inference is authorized:

```bash
python3 -m pip install huggingface-hub
python3 scripts/download_models.py --output /operator/models
```

The downloader obtains exact native `vl/` assets and verifies listed LFS hashes. The upstream source imports specific vLLM interfaces; a tested CUDA/vLLM image must still be constructed and pinned. No untested pip release is claimed compatible. After that check:

```bash
bash scripts/serve_local.sh /operator/models/JEV-9B /operator/models/Qwen3.5-9B
```

The server script disables System 2, binds loopback, retains at most eight sequences, caps context to 4,096 and images to four. The broker accepts only inline PNGs and native calibrated probabilities; it rejects malformed usage, excess tokens or multiple underlying native requests. It never substitutes a synthetic response. The operator must verify the actual loaded model and source hashes; an endpoint URL is not attestation.

## Native single-container execution

The default lane uses a normal subprocess and observation/model JSONL pipes inside one container. It does not require Bubblewrap, user namespaces, network namespaces, privileged container capabilities or a clean Base environment. The native lane is the compatibility path for the existing Harness.

When the real local model is authorized and running:

```bash
python3 scripts/evaluate.py --work /tmp/jev-visual-b0 --work-id candidate0 --endpoint http://127.0.0.1:8000/v1/decide --split development --output /tmp/jev-visual-development.json
python3 scripts/explore.py --work /tmp/jev-visual-b0 --work-id candidate0 --endpoint http://127.0.0.1:8000/v1/decide --family precision_place --tier harder
python3 scripts/evaluate.py --work /tmp/jev-visual-b0 --endpoint http://127.0.0.1:8000/v1/decide --split evaluation --output /tmp/jev-visual-evaluation-01.json
```

Native execution does not prevent arbitrary candidate code from opening other files in its container. Artifact review and the method contract forbid that behavior for per-scene solutions. On hosts that already support a separate non-root account, `--worker-user NAME` optionally applies an ordinary UID/file-permission boundary. It requires Linux root plus `setpriv` and root-owned mode-0700 runtime data; these are optional host measures, not prerequisites for the standard lane. The public copies remain available for researcher inspection. Do not infer confidentiality or arbitrary-root protection from optional permissions. No Linux UID-separation test has run on this macOS preparation host.

The runner verifies the frozen scene-file hash and worker transport, starts a fresh worker per episode, validates action/call limits and computes score from its own events. It publishes per-episode action/event audit records as well as aggregate results. Existing output files are not overwritten. Ordinary failures continue through all 48 evaluation scenes. A malformed action, scope/cost violation, crash, infrastructure error, timeout or incomplete suite yields `status: unscored`, no score key and exit code 2.

## Accounting and review

A persistent operator-assigned `--work-id` shares the local two-hour and 20,000-call ledger across Work invocations. The exploration script also charges its 160-new-episode cap before sampling and excludes all frozen geometries. Do not reset candidate IDs to evade accounting. Formal Harness Work timing must start with the complete candidate run, including loading/analysis, rather than only this CLI phase.

The evaluation command charges the 12-attempt Judge ledger before admission; controls, invalid attempts and timeouts count. Overall research duration remains 24 hours, with an optional documented extension to 48 hours and no reset of the 12-attempt cap. Work is 2 hours and Judge is 90 minutes on one H100 80 GB, 16 CPU cores, 64 GB RAM and 100 GB storage. Include 15 minutes handling per cycle. The model-serving/runtime estimates remain unmeasured, not promised performance.

The native subprocess, task-owned counters and optional file permissions inherit the standard shared-container/root limitations. Final artifacts may encode public answers; source review cannot prove their complete absence. Report results as optimization on a public benchmark, not an unseen-data claim. Keep the exact 48-case score and all failures; never delete difficult scenes or treat the published full-state oracle as an eligible baseline.

## Remaining empirical gates

The current authoritative environment is the Pillow CPU kinematic surrogate. Optional MuJoCo XML is syntax-checked only and is not a validated alternative renderer or physics engine. No actual JEV request, new-suite B0 score, H100 memory/latency measurement, validated serving image, optional UID execution or official task-validator run is claimed. These limits do not make the task data inaccessible: all files needed to inspect and reconstruct the surrogate are included. If runtime compatibility or feasibility requires protocol changes, revise and freeze before a scored research trajectory.
