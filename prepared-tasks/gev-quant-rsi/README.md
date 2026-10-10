# gev-quant-rsi

Public, inspectable benchmark package. Every task input, answer, executable gold, PNG, source seed and evaluator is public and unencrypted. Scores describe this disclosed benchmark; they do not establish unseen-task generalization.

## Baseline and optional research controls

The sole Solution reference **B0** is the existing [AutoTrust GEV-26B-Decide BF16 release](https://huggingface.co/autotrust/GEV-26B-Decide/tree/7c89590ead085bf77630b4bf68264ea30b6ddc78). It is publicly downloadable today. It has not been downloaded or run in this local preparation. Missing task-specific measurements are distinct from the existing upstream checkpoint.

Author setup downloads this pinned upstream snapshot; Solution verifies its cached content hashes, pinned config/index and complete backbone payloads, copies the files and writes provenance. It performs no training, profiling, compression or evaluation and requires no future task-specific checkpoint or prepared-artifact wrapper. See [RUNBOOK.md](RUNBOOK.md) for the exact interface.

**BQ is an optional Work-produced control**, not the reference baseline and not an activation/scoring prerequisite. Its recipe remains available for informative ablations. All control construction, repeated/discarded invocations and evaluation use the same Work budgets; submitting it to Judge consumes an attempt. Its artifact and measurements may remain absent without blocking B0 materialization or the primary reward.

## Score and scope

`100 * clip((1 - delivered_bytes / B0_bytes) / 0.60, 0, 1)`. Full score requires at most 40% of B0 delivered inference weight bytes and every quality/resource gate. The unchanged B0 has zero score. The 40% ratio is now the full-score target rather than an eligibility gate; intermediate reductions receive graded credit. B0 distribution distortion is reported, not BQ-normalized.

All families retain the overall accuracy loss limit of 0.01, per-family loss of 0.03 and Brier increase of 0.01 relative to B0. Latency is at most 1.10 times B0; actual peak GPU allocation is capped at 64 GiB. Complete gate failures score zero; invalid, crashed, timed-out or incomplete runs are unscored. `task.json` and `taskkit/scoring.py` define the contract.

Fit only on practice records; development selects. The entire evaluation is inspectable, but fitting its records, answer lookup, output replacement and evaluator tampering remain prohibited. Source-derived declarative tensors, a task-owned runtime and provenance checks reduce ordinary bypasses. Public answers remain a contamination limitation; no cryptographic proof of training ancestry or clean-Base isolation is claimed.

The CPU implementation includes deterministic six-family data, PNGs, objective oracles, coverage scoring, budgets, tensor/admission utilities and the B0 materializer. Five families require free System 2 outputs; confidence is the sixth. `scripts/stage_work.py` copies evaluation gold and seed into Work. Run the CPU checks in [RUNBOOK.md](RUNBOOK.md).

No GPU run or model-score measurement occurred. `public-authoring/reference_cache.json` deliberately contains null B0 measurements and assessment rejects it until real task-author measurements exist. [INTEGRATION.md](INTEGRATION.md) lists ordinary post-acceptance runtime integration. CPU oracle fixtures are not model scores. Contributor context: [CONTRIBUTOR.md](CONTRIBUTOR.md); licensing: [LICENSES.md](LICENSES.md).

Quantized candidates reconstruct to BF16 on CPU using the supplied arithmetic and then use the same ordinary backbone runtime as B0. The target is delivered storage, not native INT4 execution, lower resident GPU memory or speedup. Reconstructed BF16 tensors are ephemeral derivatives, excluded from delivered bytes; their reconstruction time and actual memory remain charged.
