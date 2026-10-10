# Task-Agent integration handoff

This is a complete scientific proposal package with public data manifests and a CPU reward oracle. It does not claim a built H100 evaluator, trained quantized model or measured baseline.

## Runtime and reference

Use the exact LLM Compressor and vLLM commits from task.json. Resolve a compatible dependency lock/container digest during Task-Agent packaging, using separate local Python environments for compression and inference if required. All execution stays on one H100 node. Build actual CUDA90-compatible FP8 kernels; do not require host Docker sockets or remote workers.

Base downloads the exact ungated original Qwen2.5-VL model/processor/tokenizer and existing ScreenSpot ZIP using prepare_images.py. Verify hashes then disable Work/Judge network. Preserve original full images and fixed pixel policy, native vision/projector, embedding/lm_head, BF16 KV and architecture. Allowed equivalent language normalization/linear reparameterizations must explicitly show their paired inverse and preserve the unquantized function; no unrelated tensor changes.

Solution materializes the released B0 identity without calibration, training or evaluation. A separate trusted reference capture runs the full fixed protocol once and records public, integrity-protected reference.json. Normal Judge runs only the candidate against that stored same-H100 record. No newly compressed control is needed to construct or score the task.

## Candidate calibration and static scales

Candidate is a standard compressed-tensors checkpoint/config, loaded using the native Qwen2.5-VL class with trust_remote_code=False. No custom inference Python, adapters, alternate architecture or additional model. Editable Work code performs calibration/quantization and saves all scales/weights before Judge; Judge never trains.

Eligible language q/k/v/o and gate/up/down weights use FP8 E4M3FN per-output-channel, except at most5% protected BF16 original weight scalars. At least80% of the same denominator uses calibrated static per-tensor FP8 activations; the remaining nonprotected groups may use dynamic per-token FP8. No block/FP4/MX format or arbitrary weight-bit search. Use explicit QuantizationModifier configuration groups rather than an unchanged FP8_DYNAMIC-only recipe.

The pinned vLLM W8A8 FP8 scheme registers and consumes positive finite input_scale for static mode and sets input_scale=None for dynamic mode. Fused qkv share mode/scale; fused gate/up share mode/scale. The runtime's maximum-collapse for a fused group's scale is authoritative; do not count unused or collapsed per-subprojection scales as separate calibrated behavior. This is source-supported semantics, not claimed already validated end-to-end on the Qwen model.

Research may change calibration sample weights and modality mixture, static scale/clipping objectives, quantization rounding, weight clipping, equivalent diagonal rescaling and bounded dynamic/protected group assignment. Ordinary SFT/LoRA/distillation, pruning, image-policy changes and runtime answer dispatch remain prohibited. B0 identity is allowed as the explicit score0 starting artifact.

## Task-owned entrypoints

```text
python task_adapter.py materialize-reference --task task.json --out baseline/identity.json
python task_adapter.py capture-reference --task task.json --out reference.json
python task_adapter.py evaluate --task task.json --candidate candidate/ --reference reference.json --out candidate-metrics.json
python scoring.py candidate-metrics.json reference.json
```

`task_adapter.py` is an implementation handoff API, not an existing executable in this draft. The fixed runner implements DATA.md quality prompts/metrics and candidate-independent forced-continuation timing through the same native model layers and actual FP8 kernels. Comparing Transformers fake-quant timing against vLLM B0 timing is invalid.

Use TP1, max_model_len4096, max_num_seqs8, disabled prefix caching, fixed2GiB KV reservation via kv_cache_memory_bytes=2147483648, and identical runtime optimizations/attention backend. Explicit KV bytes override utilization-based sizing; gpu_memory_utilization cannot create apparent memory gains. Performance batches1/8 process the same40 requests with64 forced decode tokens. Include processor/vision/prefill/decode and synchronize CUDA. Loading/compilation is excluded only from repeated timing, and still charged in cycle overhead. Peak memory includes allocated/reserved/process memory using one consistent measurement path.

## Audit and CPU metrics

Judge checks actual compressed format, all original/allowed transformed tensor provenance, static coverage, protection cap, fused-group mode/scale consistency, fixed processor/image settings and actual FP8 GEMM dispatch. BF16 fake-quant arithmetic is invalid even if it produces accurate outputs.

The reward oracle requires task-owned status, artifact_valid, format_valid, actual_fp8_dispatch, static_parameter_coverage, protected_bf16_parameter_fraction, five exact quality scores, quality_counts64perfamily and quality_total320. Candidate/reference data_manifest_sha256 and runtime_fingerprint must be identical64-character lowercase SHA256 digests. Fingerprint the task.json protocol, model/source/runtime revision and lock, processor/tokenizer, GPU SKU/clock/power, engine settings and evaluator version. artifact_sha256 identifies the complete actual snapshot. Judge creates these bindings; candidate-authored metrics are not trusted.

Cells batch1/batch8 each provide five elapsed_seconds for entire40-request passes and gpu_peak_bytes. Raw measurements/predictions are public. A verified B0 identity may omit compressed-format requirements only when its complete artifact digest equals B0; all quality counts and timing cells remain mandatory before0 can be assigned. Missing, invalid, crashed, OOM, NaN, timeout or incomplete outcomes are unscored. Completed valid scientific-gate failures score0. Empty or invalid-format completed answers are incorrect, never omitted.

## Budget and remaining work

Work60min + full Judge45min +15min overhead is an unmeasured120min cycle estimate. Judge includes320 quality requests and560 performance/warmup request executions. Timeout90min. All edits, export/compile, Work, Judge and retry wall time is charged; at most one same-artifact infrastructure retry, never counted as another adaptive loop. A120min one-time reference/setup reserve leaves22 full cycles plus120min margin in48h, or10 full cycles plus120min margin in24h.

Remaining implementation: complete native artifact/provenance auditor; standard static-FP8 Qwen export/load integration; quality and forced-continuation runner; memory/dispatch measurements; dependency lock and H100 validation. Download the already identified public ScreenSpot ZIP and model weights. No GPU result, achieved score, actual throughput, measured variability or target attainability is asserted by local CPU tests.

## No cross-request multimodal cache shortcuts

Set mm_processor_cache_gb=0 and limit_mm_per_prompt={"image":1}. Prefix-cache disabling alone does not disable image caches. For everyquality/performance request, including allwarmup and timed repeats, the task-owned runner assigns a globally unique multi_modal_uuids image identifier (phase/cell/repeat/request sequence); this affects cache identity only, neverpixels or modelinputs. No encoder output may be reused acrossrequests in manager orworker caches. Reusing the image embedding within the same request acrossits decode steps is permitted. Instrument raw image-item processing and vision-encoder consumption: require320processed/encoded images acrossquality, and280processed/encoded images in eachperformancecell (40requests*(2warmups+5timedpasses)); count imageitems, not batched Python invocations. Missing counters or bypassed processor/vision work makes the measurement invalid and unscored. This applies equally to B0 andcandidate.
