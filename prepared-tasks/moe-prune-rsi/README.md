# moe-prune-rsi

Public, inspectable benchmark package. Every task input, answer, executable gold, PNG, source seed and evaluator is public and unencrypted. Scores describe this disclosed benchmark; they do not establish unseen-task generalization.

## Baseline and optional research controls

The sole Solution reference **B0** is the existing [AutoTrust GEV-26B-Decide BF16 release](https://huggingface.co/autotrust/GEV-26B-Decide/tree/7c89590ead085bf77630b4bf68264ea30b6ddc78). It is publicly downloadable today. It has not been downloaded or run in this local preparation. Missing task-specific measurements are distinct from the existing upstream checkpoint.

Author setup downloads this pinned upstream snapshot; Solution verifies its cached content hashes, pinned config/index and complete backbone payloads, copies the files and writes provenance. It performs no training, profiling, compression or evaluation and requires no future task-specific checkpoint or prepared-artifact wrapper. See [RUNBOOK.md](RUNBOOK.md) for the exact interface.

**B96 is an optional Work-produced control**, not the reference baseline and not an activation/scoring prerequisite. Its recipe remains available for informative ablations. All control construction, repeated/discarded invocations and evaluation use the same Work budgets; submitting it to Judge consumes an attempt. Its artifact and measurements may remain absent without blocking B0 materialization or the primary reward.

## Score and scope

`100 * clip((3840 - retained_experts) / 1440, 0, 1)`. Full score requires at most 2,400 retained experts (64–128 per layer) and every quality/resource gate. The unchanged B0 is a valid zero-score identity artifact. Optional B96 retains 2,880 and scores at most 66.67 if its gates pass.

All families retain the overall accuracy loss limit of 0.01, per-family loss of 0.03 and Brier increase of 0.01 relative to B0. Latency is at most 1.10 times B0; actual peak GPU allocation is capped at 64 GiB. Complete gate failures score zero; invalid, crashed, timed-out or incomplete runs are unscored. `task.json` and `taskkit/scoring.py` define the contract.

Fit only on practice records; development selects. The entire evaluation is inspectable, but fitting its records, answer lookup, output replacement and evaluator tampering remain prohibited. Source-derived declarative tensors, a task-owned runtime and provenance checks reduce ordinary bypasses. Public answers remain a contamination limitation; no cryptographic proof of training ancestry or clean-Base isolation is claimed.

The CPU implementation includes deterministic six-family data, PNGs, objective oracles, coverage scoring, budgets, tensor/admission utilities and the B0 materializer. Five families require free System 2 outputs; confidence is the sixth. `scripts/stage_work.py` copies evaluation gold and seed into Work. Run the CPU checks in [RUNBOOK.md](RUNBOOK.md).

No GPU run or model-score measurement occurred. `public-authoring/reference_cache.json` deliberately contains null B0 measurements and assessment rejects it until real task-author measurements exist. [INTEGRATION.md](INTEGRATION.md) lists ordinary post-acceptance runtime integration. CPU oracle fixtures are not model scores. Contributor context: [CONTRIBUTOR.md](CONTRIBUTOR.md); licensing: [LICENSES.md](LICENSES.md).
