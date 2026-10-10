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

## Structural-pruning contract

Keep 30 layers, BF16 weights/activations and top-eight routing. Retain 64–128 unique original experts per layer. Slice fused experts and `router.proj.weight` / `router.per_expert_scale` along the same static original-ID mapping; preserve surviving scale values, global router scale and normalization. Only surviving router projection rows and declared rank≤16 expert recovery are mutable. A task-owned wrapper supports heterogeneous counts; changing only global `num_experts` is insufficient. CPU constructors/admission functions specify values/shapes, not a tested GPU wrapper.

The sole reference is intact B0. The existing score remains `100*clip((3840-E)/1440,0,1)` under unchanged gates. The identity map retaining all 3840 experts is valid and gets zero because of no removal/storage gate failure. Full score needs E≤2400 and every gate. The declared optional B96 recipe profiles 384 fixed practice IDs, retains the 96 most-selected experts per layer, breaks ties by original ID and applies no recovery. Its profile/routing counts and pruned weights are produced only if the agent chooses that Work ablation. They are not needed for setup or reward computation.

Before activation, verify complete B0 evaluation and a no-pruning wrapper reconstruction against it. Validate the heterogeneous loader with safe structural fixtures before scoring candidate outputs. Missing optional B96 is not an activation failure. Quality preservation at the full-score endpoint is not asserted.

## Unmeasured compute envelope

The 576×160-token maximum output envelope alone is 92,160 tokens; prefill, images, diagnostics and memory checks add cost. Work has two hours, Judge one hour and outer overhead fifteen minutes, for a 3.25-hour planning cycle. These are unmeasured estimates. If fixed B0 workload/runtime cannot fit, revise and version the contract before scored research; do not silently omit cases or relax gates. B0 reference evaluation belongs to one-time author preparation; optional controls belong to charged Work trials.
