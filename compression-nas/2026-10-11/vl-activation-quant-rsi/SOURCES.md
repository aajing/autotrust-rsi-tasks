# Source evidence and immutable revisions

Checked 2026-10-10 using public HTTPS APIs, raw source and selected image downloads. Source inspection does not assert measured H100 execution.

| Asset | Immutable pin | Access / license | Checked support |
| --- | --- | --- | --- |
| LLM Compressor | `229758564a9a9607b858daccb65edb0c633315ec` | Public; Apache-2.0 | Qwen2.5-VL FP8 and multimodal examples; mixed FP8 configuration; static FP8 test configs; calibration source |
| vLLM | `bf16c9c13949a10fc8e77189776f95538a598709` | Public; Apache-2.0 | Native qwen2_5_vl.py, compressed-tensors dispatch, actual W8A8 FP8 scheme implementation and H100 documentation |
| Qwen2.5-VL-7B-Instruct | HF `cc594898137f460bfe9f0759e9844b3ce807cfb5` | Apache-2.0; API `gated=false` | Existing released original BF16 model, processor/tokenizer snapshot |
| ChartQA | Git `044eabfc306abfe9340c5741f0093aefc5973d06` | Public; repository GPL-3.0 | Both original1250-row test JSONs; selected images and source Git blob SHA1; LICENSE |
| ScreenSpot-v2 | HF `5efbb1f1b5463a575f2eb7bc30fe29e49c15f93c` | Public ungated; dataset card Apache-2.0 | Parsed334/501/437-row annotation JSONs; image ZIP digest/size from LFS metadata |

Primary source links:

- https://github.com/vllm-project/llm-compressor/tree/229758564a9a9607b858daccb65edb0c633315ec
- https://github.com/vllm-project/llm-compressor/blob/229758564a9a9607b858daccb65edb0c633315ec/examples/quantization_w8a8_fp8/qwen_2_5_vl_example.py
- https://github.com/vllm-project/llm-compressor/blob/229758564a9a9607b858daccb65edb0c633315ec/examples/multimodal_vision/qwen_2_5_vl_example.py
- https://github.com/vllm-project/llm-compressor/blob/229758564a9a9607b858daccb65edb0c633315ec/tests/e2e/configs/fp8_static_per_tensor.yaml
- https://github.com/vllm-project/vllm/blob/bf16c9c13949a10fc8e77189776f95538a598709/vllm/model_executor/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_fp8.py
- https://github.com/vllm-project/vllm/blob/bf16c9c13949a10fc8e77189776f95538a598709/docs/features/quantization/llm_compressor/fp8.md
- https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/tree/cc594898137f460bfe9f0759e9844b3ce807cfb5
- https://github.com/vis-nlp/ChartQA/tree/044eabfc306abfe9340c5741f0093aefc5973d06
- https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2/tree/5efbb1f1b5463a575f2eb7bc30fe29e49c15f93c

## Static scales are a real execution parameter

Pinned vLLM `compressed_tensors_w8a8_fp8.py` constructs the static activation quantization key when `is_static_input_scheme` is true; it registers `input_scale`, loads/processes it, and supplies the selected FP8 linear kernel. For dynamic schemes it sets `input_scale=None`. The supported native-CUDA minimum is capability89, which includes H100 capability90. The file also collapses a fused group's static input scales to their maximum. This task accordingly requires one activation mode/scale for fused qkv and gate/up groups and evaluates the loaded effective scale, not unused export metadata.

The official Qwen example defaults to FP8_DYNAMIC and excludes the vision module; it is evidence for model support/export, **not** a claim that those default dynamic activations consume calibrated static scales. Static and nonuniform calibration are separate source-supported facilities. The task's explicit config groups combine those facilities; their integrated Qwen export/load still requires execution validation.

## What is and is not ready

The original BF16 reference exists publicly and is the sole mandatory B0. No new compressed checkpoint or pretraining run is a construction prerequisite. Do not substitute a ModelOpt-format NVIDIA checkpoint; its loader/hardware claims are different.

All selected annotations and ChartQA images are bundled and verified. The1.331GB ScreenSpot image ZIP is not downloaded here; exact public delivery, digest and a verification/extraction utility are provided. Model weight shards were not downloaded. No GPU build, static Qwen calibration, FP8 dispatch trace, full evaluation or throughput measurement was performed. The 1.5x/quality/memory targets are scientific contract thresholds, not observed results or a promise of attainability.

Contributor identity/expertise evidence is recorded in EXPERTISE.md using actual AutoTrust membership and release credit. No authorship of the external quantization repositories, independent datasets or runtime kernels is inferred.
