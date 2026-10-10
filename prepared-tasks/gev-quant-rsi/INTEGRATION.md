# Concrete H100 integration specification

Status: no model weights, GPU adapter, serving container or real inference results have been prepared. This is the integration recipe and acceptance boundary, not a claim that it runs. No GPU is started by any command in this document.

## Common preparation

1. Acquire `autotrust/GEV-26B-Decide` at `7c89590ead085bf77630b4bf68264ea30b6ddc78`, its complete index/shards, processor/tokenizer, original S1 adapters/head/calibration and applicable license files. Record SHA256 of every file. The bundled config and index metadata already have receipt hashes; they are not weight receipts.
2. Freeze a specific Gemma4-capable Transformers/PyTorch/CUDA container and its source hashes. First load the intact BF16 model on one H100 80 GB. Preserve the original S1 readout, original vision preprocessing and System 2 generation path. No alternate model, quantized upstream checkpoint or reduced precision is a silent fallback.
3. Render each public request with the frozen family template. Native System 2 performs five free-output families with S1 adapter disabled; only confidence uses the unchanged S1 interface. Use greedy generation, thinking disabled, context/output/image bounds from the proposal. Hash templates and decoder settings.
4. Record complete model-inference outputs, source inventory, runtime fingerprint, wall time, image-expanded/input/output token counts and peak allocated/reserved GPU memory. Publish the measured records and reference summaries before using them as fixed controls.
5. Connect the official shared-snapshot lifecycle and operator-owned Judge. Published gold is readable, but the candidate artifact must not inject cached answers, alter the evaluator or replace the runtime evidence. The current CPU assessment interface is deliberately not an official Judge.

## Quantization adapter

The source has 60 fused expert tensors, named `model.language_model.layers.L.experts.gate_up_proj` and `...down_proj` for L=0..29. Their leading expert dimension is 128. The exact name allowlist comes from the pinned model index.

The CPU reference format uses signed symmetric INT4 values −7..7 packed low-nibble first in two's complement; −8 is forbidden. INT8 is −127..127; −128 is forbidden. Groups of 32/64/128 run along the last matrix dimension, with declared zero-padding trimmed during reconstruction. Scales are positive float32; round-to-nearest uses ties-to-even. BF16 passthrough uses exact uint16 payloads. The default BQ recipe is INT4/group128/max-absolute scale, and overrides are restricted to declared original expert slices.

The fixed execution contract is CPU reconstruction to BF16, followed by ordinary BF16 inference with the pinned source architecture on H100. For every BQ and candidate, trusted task-owned code validates the artifact, uses the supplied `taskkit.tensors.dequantize` arithmetic for each expert slice, assembles BF16 tensors, and loads those tensors into the same frozen backbone runtime. BF16 passthrough remains bit-preserving. No native packed-weight H100 kernel is required or allowed in this protocol. The research objective is compressed delivered storage and preservation of model behavior, not native four-bit execution, reduced resident GPU memory or speedup. CPU packing is not NVIDIA NVFP4. A future packed backend would be a different protocol revision with fresh references, outside this task.

Artifact bytes count every required delivered model weight, scale and adapter once, including frozen/shared model dependencies. Source originals of compressed experts are validation-only and cannot be extra inference dependencies. Reconstructed BF16 tensors are deterministic, ephemeral runtime derivatives, not additional submitted weights; they contain no independently fitted values and are excluded from delivered-artifact storage bytes. Their actual CPU/GPU memory use, reconstruction/loading duration and any temporary-file cost still count in runtime accounting. BQ and every candidate use identical reconstruction and BF16 inference code. The unchanged 64-GiB actual GPU peak, latency and one-hour Judge gates still apply; reconstruction is included in Judge wall time, while the fixed warmed-inference timing passes retain their declared scope.

Required checks before activation: tensor-shape/hash/allowed-scope admission, CPU reconstruction/BF16 loaded-tensor equality, S1/S2 and image smoke checks, intact-vs-reconstructed B0 behavior, a complete BQ evaluation, all model-byte accounting, three timing passes and the complete one-hour Judge envelope. None is claimed complete here.

Tokenize the public canonical probe outputs with the pinned tokenizer and freeze positions after floor(L/2) tokens. For the 80 declared probe IDs, save B0 float32 probability vectors and measured BQ total-variation distances. Publish these files and hashes. The scorer rejects null or incompatible references.

## Structural-pruning adapter

Keep the native 30 layers and top-eight routing. The static mapping retains 64–128 original experts per layer. The source uses fused expert tensors plus `router.proj.weight`, `router.per_expert_scale` and `router.scale`. Slice the first two router/expert axes by the same original-ID list. Preserve each surviving per-expert scale, global router scale and the source normalization computation. Only surviving projection rows and declared rank≤16 expert recovery are mutable.

A custom task-owned model wrapper must support each layer's retained count; changing only the checkpoint's global `num_experts` is insufficient for heterogeneous counts. Preserve the original source forward semantics and dynamically sized top-eight selection within each static retained set. CPU `construct_pruned_layer`, `iter_pruned_checkpoint` and `admit_pruned_layer` provide shape/value references; they are not CUDA kernels or a loaded Transformers architecture.

Measure intact B0 first. B96 profiles the fixed 384 practice records listed in `public-authoring/b96_profile_plan.json`, keeps the 96 most selected experts per layer, breaks ties by original ID, and performs no recovery. Publish routing counts, retained IDs and complete B96 output/resource records. B96 is an intentionally non-full-score control. A full-score candidate removes at least 1,440 experts while satisfying unchanged gates; no achievable result is asserted.

## Reference integrity and time

Do not accept candidate-created resource JSON as official evidence. Frozen references remain operator-owned and integrity-checked even though their contents are public. A reference cache is bound to the exact data manifest and source/runtime hashes. The shared snapshot does not imply a clean base or immunity to privileged tampering.

Loading, preprocessing, inference, all repeats and export count against the declared per-run clocks. The 576×160-token upper output envelope alone is 92,160 tokens; prefill, image processing, probes and memory checks add cost. The two-hour Work and one-hour Judge budgets remain unmeasured requirements. If infeasible, revise and version the contract before scored research; do not silently omit cases or relax gates afterward.
