# Task-Agent integration handoff

This package fixes the scientific contract and includes a CPU reward oracle. It is not an implemented H100 evaluator. Implement the native single-container adapter below after proposal acceptance. No baseline/model inference, kernel build or GPU experiment has run here.

## Materialization and command contracts

Check out the exact KIVI commit in task.json, follow its compatible Transformers4.43 installation lane, and build `quant/` for H100. Resolve and record a dependency lock/container digest during Task-Agent packaging. Do not require host Docker sockets, privileged sidecars or remote services. Download the pinned Mistral model/config/tokenizer; preserve its BF16 artifact bytes and apply the same deterministic FP16 runtime cast in B0 and candidates. The source evaluator hardcodes FP16; no BF16 KIVI custom-kernel support is presumed. Verify all192 materialized examples before disabling runtime networking.

Implement these task-owned entrypoints:

```text
python task_adapter.py materialize-reference --task task.json --out baseline/identity.json
python task_adapter.py capture-reference --task task.json --out reference.json
python task_adapter.py evaluate --task task.json --candidate candidate/ --reference reference.json --out candidate-metrics.json
python scoring.py candidate-metrics.json reference.json
```

`task_adapter.py` is a specified implementation API, not an existing executable in this proposal package. `materialize-reference` is Solution: download/resolve the original artifact and write its identity without training, calibration or evaluation. `capture-reference` is a separate trusted evaluator operation during baseline reproduction/task initialization, running the full protocol once. Reference measurements are public, unencrypted and integrity-protected. Normal Judge runs only the complete candidate against that same-device record, not a live paired B0.

## Cache boundary and memory

Bind candidate code only to declared cache-transform/storage/update and attention-consumption hooks. Inputs are current-request Q/K/V/cache tensors, positions, layer/head indices and accumulated tensor statistics. The task-owned runner controls weights, prompts, token IDs, generation and output extraction. No candidate logits/output callback, raw prompt/ID/file path/gold access, auxiliary model, cross-request state, host KV offload or discarded-prefix recomputation is allowed. Source review and immutable component hashes supplement runtime restrictions; arbitrary native code in a shared Work snapshot is not perfectly isolated.

Measure129 persistent-cache samples per cell: immediately after completed prefill and after each128 forced decode updates. Count storage capacity for all KV payloads, scales/zero points, indices, padding, residuals, metadata, backups and shadows across GPU/host; aliased storage once. Host/offload cache is prohibited even if included in byte accounting. Primary R is the maximum over every matching sample in all six performance cells AND every actual quality request's dense-equivalent ratio. For quality requests use131072*(prompt_tokens+decode_update_index) as the dense denominator, and candidate persistent-storage bytes as numerator; never use the candidate-retained length. A policy retaining full caches onquality but compressing synthetic traces cannot score improvement.

Separately record full-trace GPU peak including prefill, temporary dequantization, scratch, graph pools and framework allocations, using consistent allocator/process measurements and the maximum observed measure. Enforce candidate/B0 peak<=1.05. This prevents hiding persistent compression behind unbounded temporary full-cache reconstruction. A full FP16 Mistral cache is `2*32*8*128*2` bytes per sequence token:4GiB at32768tokens forbatch1 and16GiB forbatch4 before overhead. This is shape arithmetic, not measured memory; H10080GB remains an execution-validation requirement.

## CPU metrics interface and integrity bindings

`scoring.py` requires task-owned `status=complete`, `artifact_valid=true`, exact `quality_counts`32perfamily and `quality_total=192`, plus all six0-100 `quality` scores. `data_manifest_sha256` and `runtime_fingerprint` must be identical64-character lowercase SHA256 digests in candidate/reference records. Fingerprint the exact task.json protocol, model/source/runtime revision and lock, fixed prompt/processor policy, GPU SKU, clock/power settings, batch settings and evaluator version. `artifact_sha256` identifies the complete actual artifact manifest. These fields are emitted by Judge, not accepted from candidate assertions.

Cells are `8192x1`, `8192x4`, `16384x1`, `16384x4`, `32256x1`, `32256x4`. Each contains exactly five full-pass `elapsed_seconds`, a `gpu_peak_bytes` value and129 `cache_bytes` values. Public raw repeats accompany the report. `identity_baseline=true` is allowed only after a task-owned identity audit and matching artifact digest; even B0 must complete all cells and counts before receiving0. Missing/nonfinite/failed/incomplete reports are unscored. A valid completed scientific-gate failure scores0. A completed empty answer scores incorrect; a process crash is not a dropped example.

## Budget and residual implementation work

Cycle estimate: Work90min + entire Judge90min +15min overhead. Full Judge includes192 quality generations and42 complete trace passes, not just proxy diagnostics. Hard Judge timeout120min. All edits, compilation, Work, Judge and retries count toward24h/48h wall budget; allow one infrastructure retry of the identical artifact, never a new adaptive loop. One-time setup/reference reserve150min; thirteen complete195min cycles plus195min margin fit48h. This remains an unmeasured estimate.

Remaining implementation: fixed cache-hook loader; full quality and forced-trace runner; exact token-ID cap; robust storage/peak accounting; artifact/source integrity audits; dependency lock; H100 compile/numeric/runtime validation. No new model, private asset, third-party execution service or contributor-owned scientific decision is needed. Target attainability and actual variance are not claimed.

## Mandatory quality-request cache audit

All192real quality requests are included in the primary cache objective, not just synthetic performance traces. For each exact manifest family/ID, record task-owned prompt token count P and generated token count G (including EOS), with1<=G<=thefamilycap. Standard autoregressive generation has a prefill and max(G-1,0) subsequent decoder forwards; record G cache samples after those operations. At decode update j=0..G-1, dense reference KV payload bytes are131072*(P+j), using32layers,8KVheads,128dimensions,2(K/V) and2FP16bytes. Count all candidate persistent storage/metadata/shadows in the numerator. Report the maximum ratio for eachrequest; R takes the maximum over these192ratios and the sixperformance-cell ratios. The scorer requires every exact selectedID, family counts, P+G<=32768, decode_updates=G-1 and sample_count=G. Raw samples are public and task-owned instrumentation computes summaries. Emptydecodedtext still has at least one generatedtoken (for example EOS); a missing generation process is incomplete/unscored. This removes the loophole of retaining full caches on real questions while compressing only recognizable synthetic timing inputs.
