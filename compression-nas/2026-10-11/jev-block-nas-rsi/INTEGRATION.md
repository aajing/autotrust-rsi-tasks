# Integration handoff and actual readiness

The scientific contract, public selection manifest and CPU scoring contract are supplied. This is a proposal package, not a claim that the complete GPU task runtime already exists. No GPU run, measured candidate quality, full checkpoint download or official review occurred here.

## Existing mechanism

The official HF Git repository is the primary code/artifact source. README.md includes a complete native Transformers+PEFT System1 inference example. `vl/serve_decide.py` provides fixed decision rendering and state truncation behavior; `judge_config.json` defines slots and original projection modules. `adapter/adapter_model.safetensors` and `head.safetensors` are already trained and publicly delivered. The model implementation is the Transformers Qwen3.5 text class declared by config.json; no external hosted service or additional model is needed.

Task Agent must implement these new task-owned entrypoints, which are design specifications rather than existing source commands:

- `task_runtime/materialize.py --reference B0 --out baseline/B0`: download exact pins, construct the equivalent allowed graph and tensor file, preserving FP32 branch tensors/temperature scalars; no training or evaluation.
- `task_runtime/validate_graph.py --candidate candidate`: enforce dimensions, op allowlist, acyclic composition, bounds, actual tensor use, parameter aliases, canonical bytes and protected-source hashes.
- `task_runtime/train.py --candidate candidate --ledger candidate/training-ledger.json`: optional Work helper for fixed inputs, teacher/target losses and exposure accounting. The research agent may replace Work training code inside its declared workspace; submitted inference remains declarative.
- `task_runtime/evaluate.py --candidate candidate --protocol task.json --out report.json`: inference-only native model execution, family/primitive metrics, two timing batch workloads, memory and integrity checks. It passes a trusted metrics report to the local scoring formula.

## Graph schema and System2 preservation

A graph names source projection locations and decoder-block output locations. Each projection LoRA is a matrix-delta branch at one of the original target modules, with declared A/B tensors, rank, scalar gain and optional equal-shape shared IDs. Added residual nodes have hidden input/output4096, low-rank linear or SiLU bottleneck structure, optional scalar sigmoid gate, and explicit serial/parallel-sum composition at a block boundary. At most two added residual nodes per block. There are no model-input-dependent control-flow operators. Shared IDs refer only to equal-shape tensors/modules and count once in canonical storage. The head is a linear4096→24 map or a one-hidden-layer SiLU map with an allowed width. Biases, normalization parameters, gates, gains and all auxiliary numeric buffers count. Use standard fixed task-owned PyTorch modules; no custom candidate kernels or dynamic code.

For B0 import, reproduce the original 400 LoRA parameter tensors, original 24-slot head and original three temperatures. The layer module names and shapes are read from pinned config and safetensors headers. Original branch values are not rounded or retrained. Candidate branch tensors must use FP32; runtime matmuls follow the same BF16 autocast policy for B0 and all candidates. The canonical size definition is 4 bytes per unique learned/auxiliary scalar, independent of file metadata/zip compression. Fixed task-defined op/shape constants are excluded; candidate-specific gains or inference constants are materialized and counted. B0 header inspection gives 40,108,032 LoRA + 98,328 head + 3 temperature scalars = 160,825,452 canonical bytes. Full score at25% of B0 is only branch compression; backbone and original lm_head are excluded because they are unchanged shared assets. Deployment speed gains are not assumed.

Never merge a candidate into the protected backbone. Task-owned System2 dispatch disables every branch node/head and uses the exact original backbone/lm_head. Hash equality is the primary invariant; sixteen public fixed prompt probes compare disabled-branch logits to baseline within 1e-5 maximum absolute difference under the same deterministic implementation. Probes: the first 16 selected manifest rows rendered as plain state+question text; no new evaluation data. If the graph runtime cannot guarantee disable semantics, reject the artifact before scoring.

## Fixed timing order

Take the first 32 rows per primitive in manifest order. Interleave them as noul[0], choice[0], score[0], noul[1], choice[1], score[1], and so on, yielding a 96-row ring. For each batch size, start the cursor at zero and consume consecutive rows modulo 96 through all five rounds; each round consumes 10 warmup batches followed by 30 measured batches. Advance the cursor for both warmup and measured batches, and do not reset it between rounds. B0 and candidates use the identical sequence.

## Environment and validation work remaining

Use one native container/process environment on one H100 80GB node; no host Docker socket, privileged inner container or sidecar. The source card records torch2.13+cu130, Transformers5.16 and PEFT0.21 plus flash-linear-attention0.5.2. These are source-reported versions, not locally tested dependencies; Task Agent should pin a compatible H100 build and preserve the source numerics. BF16 backbone storage plus gradients through the frozen backbone and branch optimizer/activations must fit80GB; gradient checkpointing and small microbatches are allowed Work choices.

Execution validation must: obtain/checksum the complete released weights; verify source-native and graph-imported B0 probability parity on public rows; freeze the6,144-row same-protocol B0 metrics/timing/memory report; test candidate graph export/reload, shared tensor accounting and System2 disable; measure a complete Work+Judge+overhead loop on H100. These are ordinary implementation/measurement tasks, not missing contributor-owned scientific decisions. They may reveal performance or feasibility problems; no claim of acceptance or achieved full score is made.

Work 60-100min + full Judge 20-45min +15min overhead yields a 160min upper planned cycle. At48h, reserving 4h leaves 16 complete cycles; at 24h with 2h setup about 8 worst-case cycles. Tiny proxy runs do not increase that count. The48h extension is the proposed normal path if measured cycles resemble this upper estimate. If a complete candidate times out, it is unscored rather than silently evaluated on fewer rows.

## Source access note

HF API and pinned raw files were accessible without credentials. Two local `git ls-remote` attempts encountered a TLS transport error; this is recorded as an access-method limitation, not proof the source is unavailable. The existing anonymous pinned HF resolve/raw interface provides the complete file-tree/artifact delivery route. No credentials, encryption, fabricated checksum or future private mirror is required.

## Frozen report binding

Every trusted complete report carries data_manifest_sha256 and runtime_fingerprint, each a 64-character lowercase SHA256. Data binding covers the exact materialized evaluation inputs, targets, selection and tokenization manifest; runtime binding covers the fixed source, tokenizer, evaluator/operator configuration, precision and H100 environment. Candidate and frozen B0 bindings must match exactly. Missing/malformed/different bindings make the result unscored. valid_artifact and structural integrity flags must be literal JSON true, never truthy strings. These fields are produced by the trusted runtime, not accepted from candidate claims.
