# Source and access ledger

Checked 2026-10-10. No credentials were stored and no source model code was executed. Repository text snapshots under evidence/ are documentary evidence, not executables run during this preparation.

| Asset | Exact source/pin | Access evidence | License/provenance |
| --- | --- | --- | --- |
| Official JEV code and release | https://huggingface.co/autotrust/JEV-9B/tree/d7bf1c0051f78e3a7bd5bbb90add79bfd769079b | Anonymous HF API: public, ungated; pinned README, configs and vl serving Python fetched | Repository card declares Apache-2.0; model card explicitly covers released weights and acknowledges Qwen |
| Native System1 adapter | same revision, adapter/adapter_model.safetensors | Safetensors header read only:400 tensors,40,108,032 scalar values, all F32 | Existing released trained artifact, no new control training |
| Native24-slot head | same revision, head.safetensors | Safetensors header read: 2 F32 tensors, 98,328 scalars; recorded in evidence/baseline-shapes.json | Existing head; card gives [24,4096] weight+[24] bias |
| Source corpus | https://huggingface.co/datasets/SargeDev/jev-distill-corpus-v3/tree/75111a13a8455032f0435050bfc7e0c9026ecfe8 | Public ungated API; complete test_set_30k bytes streamed, SHA/counts in evidence/data-cardinality.json | Apache-2.0; credit SargeDev; openjev_v2 source additionally CC0 |
| Decision graph loader basis | Pinned README native Transformers+PEFT example; judge_config.json; adapter config; vl/serve_decide.py | Contents actually read and archived locally | New bounded graph/task evaluator remain overlay implementation, clearly separated from source code |
| Related official task | https://index.openrsi.foundation/tasks/kev-decision-architecture | Public current task description inspected | Different goal: better0.5B decisions from original base, not reduced released9B capability-block storage |
| Related official task family | https://index.openrsi.foundation/tasks | Lists Allocate Decoder Width Across Depth | Backbone capacity redistribution differs from detachable branch topology/sharing |

Baseline model pin and corpus pin are different repositories and never substituted into the proposal's source-commit field. The primary source is HF Git, not an invented GitHub mirror. Exact Git source SHA was obtained from HF API and pinned raw-file reads. Local git-ls-remote encountered TLS transport errors; anonymous HF raw/resolve API delivery still exists and was exercised. This is documented, not hidden by presenting a checkout as successful.

The local code/data metadata SHA256 inventory is evidence-manifest.json. Full backbone/adapter tensor-payload checksums and GPU loading have not been verified; task construction must verify them before freezing B0. No unrelated training baseline or unavailable control is a prerequisite.

## Public author expertise and attribution limits

See EXPERTISE.md. AutoTrust membership and the existing JEV release article support shared relevant model-development experience; they do not prove sole authorship of every adapter/vision module. The submitting identity and work email are contributor-provided. No new public identity claims or upstream credits were manufactured.

## Current relevance and evidence limit

The October 2026 JEV-9B model card provides a current concrete detachable-block target. Existing LoRA/adapter and NAS mechanisms supply research context, but this package does not claim a completed six-month survey of distinct papers or a novel NAS algorithm. Official frontier review remains separate and non-blocking. All performance figures attributed to the source are labeled upstream and unreplicated for this task.

The two inspected headers contain 40,206,360 scalar tensor values. Including the three published temperatures yields 40,206,363 counted FP32 scalars, or 160,825,452 canonical bytes for B0. This is metadata arithmetic, not a model-quality or runtime measurement. Fixed task-defined op/shape constants (for example the original alpha/r scaling rule) are not learned artifact values; any candidate-specific gain, gate, normalization value or additional inference constant must be materialized and counted.
