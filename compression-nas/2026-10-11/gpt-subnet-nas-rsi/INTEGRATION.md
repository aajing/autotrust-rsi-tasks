# Integration handoff and actual readiness

This package defines the complete scientific contract and supplies CPU scoring checks plus inspected primary-source evidence. It has not executed or downloaded the1.48GB GPT-S checkpoint, run a GPU experiment, verified current Whittle compatibility or submitted an official Discussion.

## Native checkpoint path

Use `pl_gpt/pl_module/lm_evaluator_configurable.py` and `hwgpt/model/gpt/model.py` at the exact repository SHA. The evaluator loads checkpoint['state_dict'], removes the documented `model.` prefix and calls strict load_state_dict. Its native set_sample_config accepts embedding width, per-layer intermediate sizes, per-layer heads, depth, bias flag and retained original layer indices. Native datamodule adds GPT2 pad and rounds vocab size to a multiple of 128 (50304). The YAML still contains 50254 defaults; they are overwritten by this datamodule and must not be copied literally.

Preserve source-native RoPE fraction0.5 from the GPT-S evaluation config,64-dimensional attention heads, normalization, shared embedding behavior, residual ordering and padded logits. Hardware-only profiling configs and the older Whittle large-model example are not authoritative drop-in loaders for this checkpoint. `hwgpt/model/gpt_base/model.py` supplies a fixed-shape starting implementation, but extraction equivalence to the configurable model still has to be established. Any mismatch is an integration issue to resolve before B0 is frozen; do not silently call a changed model the baseline.

## Task-owned entrypoints to implement

- `task_runtime/materialize.py --reference B0 --out baseline/B0`: fetch existing checkpoint, build its maximum native subnet, export independent tensors/config; no training/evaluation.
- `task_runtime/export.py --supernet assets/gpt_s.ckpt --architecture candidate/architecture.json --out candidate/model.safetensors`: slice only legal native tensors or serialize allowed Work-trained replacements, retaining all actual model buffers. No parent-supernet link is accepted in final artifacts.
- `task_runtime/validate.py --candidate candidate`: allowlist structure/precision, source layer indices, tensor shapes/storage accounting, no executable inference and no extraneous tensor cache. Every declared graph is fixed across both domains and all workloads.
- `task_runtime/evaluate.py --candidate candidate --protocol task.json --out report.json`: load candidate via the task-owned fixed native-equivalent model, evaluate six NLL cells and all 3 H100 forward workloads, capture actual peak memory and pass trusted metrics to scoring.py.

These paths are specified new overlay interfaces, not existing upstream commands. Candidate Work search/recovery code can change; evaluator/export-validation/runtime code cannot.

## Reference and export parity

Before opening research, validate maximum-network output against the native configurable supernet on fixed public token batches at lengths 128,512,1024. In FP32 construction validation require maximum absolute logit error<=1e-4 and mean NLL difference<=1e-5; then lock the common BF16 runtime and publish precision-specific parity diagnostics. If it fails, correct the conversion rather than weaken thresholds or update benchmark data. Check selected intermediate subnet exports too. Freeze the B0 report once under the exact task protocol; normal Judge calls evaluate candidates only. Solution itself simply materializes the traceable B0 artifact.

Checkpoint tensor shapes and source-derived tying determine canonical stored bytes. All actual unique tensors, including embeddings, LM head and numeric buffers, count. BF16 is fixed except FP32 values required by the common native runtime. Weight aliases may count once only when both B0 and candidate loader truly share one stored tensor and the runtime uses that alias. Compression containers and artifact metadata do not determine the scientific byte score.

## Execution environment and remaining ordinary work

One physical node,16 CPU cores,256GiB RAM, one H100 80GB. No remote execution, sidecar or Docker-in-Docker requirement. The Task Agent must pin native source dependencies to a compatible PyTorch/H100 environment and pre-download declared public files. Work and Judge are serial, so end-to-end peak remains one GPU.

The actual remaining implementation/validation work is: download and hash the full released checkpoint; prove native loading/extraction parity; materialize exact token streams and count scored tokens; implement the trusted graph validator and reports; freeze actual B0 NLL, canonical bytes, H100 timing and memory; measure a complete Work+Judge+overhead cycle. These steps require no new scientific-policy decision, but can expose incompatibility or unrealistic target thresholds. No unavailable trained control is needed.

The proposed full-score quality tolerance+40% latency reduction may be difficult: moving fromwidth 768 to384/192 saves substantial parameters, but smaller width may lose more than0.08 nats/token; reducing only heads/MLPs may not yield40% real H100 acceleration at all workloads. Local recovery training and heterogeneous allocation are plausible mechanisms, not proof of attainability. Keep this limitation visible rather than reporting hypothetical scores as measured.

Estimate: Work 20-60min, full Judge 10-30min, mandatory overhead15min; complete upper cycle 105min.24h with 2h setup permits 12 complete loops;48h with 4h margin permits 25. Proxy trials and parallel candidates do not multiply this adaptive-loop estimate. Real full-loop H100 timing remains unverified.

## Frozen report binding

Every trusted complete report carries data_manifest_sha256 and runtime_fingerprint, each a 64-character lowercase SHA256. Data binding covers the exact materialized evaluation inputs, targets, selection and tokenization manifest; runtime binding covers the fixed source, tokenizer, evaluator/operator configuration, precision and H100 environment. Candidate and frozen B0 bindings must match exactly. Missing/malformed/different bindings make the result unscored. valid_artifact and structural integrity flags must be literal JSON true, never truthy strings. These fields are produced by the trusted runtime, not accepted from candidate claims.
