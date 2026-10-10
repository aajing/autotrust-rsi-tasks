# Post-acceptance integration contract

No local weights, model inference, H100 adapter or measured GPU results are claimed. The publicly released B0 artifact exists upstream; runtime integration and measurements are ordinary implementation steps after proposal acceptance.

## Lifecycle

1. Author setup runs the exact pinned `hf download` command in RUNBOOK.md, preserving actual source/inherited licenses and recording the downloaded revision. Acquire the complete release: backbone shards/index, original tokenizer/processor, System 1 adapters/head/calibration and source files. Source metadata receipts alone are not weight receipts. The current materializer verifies cache content integrity and pinned config/index binding; the cache directory name alone is not cryptographic proof that every blob belongs to the remote revision. During author setup, fetch exact-revision per-file membership using `python3 scripts/fetch_source_inventory.py --output source/upstream-inventory.json` and use the optional `--inventory source/upstream-inventory.json` materializer argument. The public API was inaccessible during this repair, so no successful inventory fetch or full weight membership verification is claimed here.
2. Solution runs `solution/materialize_baseline.py --source-snapshot SNAPSHOT --output NEW_PATH`. It needs the real existing Hugging Face cache snapshot, not a future BQ/B96 artifact or a pre-created task wrapper. It verifies and copies only; CPU hashing/copying uses zero GPUs. A provenance receipt is created from those real bytes, with no model computation or fabricated measurements.
3. Implement and freeze one task-owned Gemma4-capable BF16 runtime and exact dependency/container hashes. Load B0 first. Preserve the original System 1 interface for confidence, disable its adapter for the five native System 2 families, and preserve vision preprocessing. A different checkpoint or reduced precision is not an implicit fallback.
4. Task-author preparation evaluates B0 under the fixed complete protocol, records actual source inventory, outputs, B0 quality/calibration/bytes/latency, memory, token counts and runtime fingerprint. Bind the cache to source/data/runtime hashes and publish it. Missing measurements currently remain null; never populate them with estimates or oracle fixtures.
5. Judge reloads the materialized Work snapshot through task-owned inference/admission code and evaluates one candidate against the fixed B0 cache. Identity B0 is a valid zero-score artifact. Work pauses during Judge. No research call rebuilds or retrains the reference.
6. Optional compressed controls are created by the agent in Work. Their profiling, export, inference, retries and discarded runs count against ordinary budgets; any Judge submission consumes one of twelve attempts. No optional control checkpoint, routing count, measured distortion or latency is required for activation or primary scoring.

## Fixed evaluation and evidence

Use frozen family templates, greedy generation, thinking disabled, 2,048 text input tokens, one 448×448 image and at most 160 output tokens. System 2 serves free-output math/Python/SQL/tool/visual families; original System 1 serves confidence. Count complete malformed outputs as wrong. Do not accept candidate-written outputs/resource JSON as official measurements; the CPU assessment command alone cannot mint a reward.

Normal inference timings cover the same 24 frozen requests, text/image and batch sizes 1/4. One warmup precedes three timed passes; median total latency is compared with B0. Record clocks, power and software metadata and repeat only if drift can alter a gate. Judge wall time includes integrity, loading/reconstruction, preprocessing, all inference, repeats and finalization. There is no clean-Base verifier: Judge uses the complete shared Work snapshot with task-owned tests injected Judge-only.

All inputs, labels, seeds, outputs and reference measurements remain public and unencrypted. Operator ownership and frozen hashes protect ordinary reference integrity, not answer secrecy or arbitrary-root isolation. The fixed generated-program sandbox must prevent Python/SQL answers from reading host/evaluator/network assets.

## Quantization contract

Only the sixty pinned fused expert tensors may change precision. Their source names are `model.language_model.layers.L.experts.gate_up_proj` and `...down_proj` for L=0..29; each has 128 expert slices. Preserve every other tensor and routing choice.

Use supplied signed symmetric INT4 −7..7 or INT8 −127..127 arithmetic; −8/−128 are invalid. INT4 packs low nibble first in two's complement. Groups 32/64/128 run along the last dimension, trim declared zero padding, use positive float32 scales and ties-to-even rounding. BF16 passthrough preserves exact uint16 payloads. Trusted `taskkit.tensors.dequantize` reconstructs compressed slices on CPU and then the ordinary frozen backbone performs BF16 inference. B0 uses its original BF16 tensors; both routes share final architecture, prompts, decoding and precision. No native packed GPU kernel is required or admitted.

Count all delivered weights/scales/adapters and frozen inference dependencies once. Original compressed expert tensors remain validation-only and cannot be extra inference dependencies. Deterministic BF16 reconstruction is an ephemeral runtime derivative, excluded from delivered bytes but charged for time and actual memory. Document JSON and non-weight source code do not enter model-byte counts.

The score is storage reduction versus B0: `100*clip((1-r)/0.60,0,1)`. Require r≤1 plus existing quality/calibration/64-GiB gates and latency≤1.10×B0. Full score requires r≤0.40 and every gate. B0 yields zero. The storage-bound calculation in `source/storage-bound.json` shows a ~35.72% theoretical backbone payload ratio before adapters/headers for uniform INT4/group128; it establishes arithmetic headroom, not quality or runtime feasibility.

For the eighty published probe IDs, tokenize canonical output with the pinned tokenizer, freeze the position after floor(L/2) tokens and save B0 float32 probability vectors over 262144 tokens. Publish positions/vectors/hashes. Candidate total-variation distance from B0 is a diagnostic only. No DQ normalization or BQ-latency measurement is needed. Optional BQ uses the supplied uniform INT4/group128/max-absolute recipe inside Work if the researcher wants that ablation.

Before scored activation, verify source/admission hashes, reconstruction correctness, original S1/S2/vision behavior, complete B0 evaluation, delivered-byte accounting and the full one-hour Judge envelope. Optional BQ need not be constructed.

## Unmeasured compute envelope

The 576×160-token maximum output envelope alone is 92,160 tokens; prefill, images, diagnostics and memory checks add cost. Work has two hours, Judge one hour and outer overhead fifteen minutes, for a 3.25-hour planning cycle. These are unmeasured estimates. If fixed B0 workload/runtime cannot fit, revise and version the contract before scored research; do not silently omit cases or relax gates. B0 reference evaluation belongs to one-time author preparation; optional controls belong to charged Work trials.
