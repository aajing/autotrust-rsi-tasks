# AutoTrust RSI tasks

Six research proposals for OpenRSI / RSI-Anything, prepared by **Jing Qiu** (`aajing`, `ajing@autotrust.ai`). Every prepared evaluation input, answer, seed, reference solution and scoring implementation is public. No files are encrypted or password protected.

| Task | Research question | Proposal |
| --- | --- | --- |
| gev-think-rsi | Can a trainable external router allocate reasoning and tools more effectively around frozen GEV? | [English proposal](draft-proposals/2026-10-10/gev-think-rsi.md) |
| jev-judge-rsi | Can native JEV review improve calibrated judgments across mixed task families? | [English proposal](draft-proposals/2026-10-10/jev-judge-rsi.md) |
| jev-coldstart-rsi | Can evidence and prompt optimization improve personalized image ranking? | [English proposal](draft-proposals/2026-10-10/jev-coldstart-rsi.md) |
| jev-visual-control-rsi | Can iterative prompt and controller optimization improve visual manipulation? | [English proposal](draft-proposals/2026-10-10/jev-visual-control-rsi.md) |
| gev-quant-rsi | Can data-dependent precision allocation reduce quantization distortion under a storage constraint? | [English proposal](draft-proposals/2026-10-10/gev-quant-rsi.md) |
| moe-prune-rsi | Can expert selection and bounded recovery preserve quality after substantial pruning? | [English proposal](draft-proposals/2026-10-10/moe-prune-rsi.md) |

## Download

Repository: `https://github.com/aajing/autotrust-rsi-tasks`

Release and individual packages: `https://github.com/aajing/autotrust-rsi-tasks/releases/tag/public-proposals-2026-10-10`

Complete unencrypted ZIP: `https://github.com/aajing/autotrust-rsi-tasks/releases/download/public-proposals-2026-10-10/autotrust-six-task-proposals-public.zip`

The release includes six individual task ZIPs, the combined ZIP, `SHA256SUMS` and `archives.json`. On macOS use `shasum -a 256 -c SHA256SUMS` after downloading the listed ZIPs; on Linux use `sha256sum -c SHA256SUMS`.

## Scope and status

These are **public proposal packages, not submitted to official review**. Publication is not official acceptance. Each proposal uses the 28 official fields and supplies concrete data, baseline, modification bounds, budgets and full-score rules. See [package index](prepared-tasks/README.md), [execution status](prepared-tasks/STATUS.md) and [delivery record](delivery.json).

The disclosed evaluation sets support reproducible, auditable fixed-benchmark research. Researchers can inspect the answers; submitted methods must obey train-only fitting and input-interface rules and cannot hard-code per-item answers. No unseen-test or memorization-proof guarantee is made.

All locally prepared task files are included. Public model weights are downloaded from pinned Hugging Face sources. The coldstart package includes the complete CC0 SQLite metadata and a precise selected-image manifest; the approximately 86.6 GB upstream image archive is publicly downloadable but not mirrored here. Package runbooks give the source interfaces and import steps.

CPU contracts and deterministic data checks have run. **No GPU/model experiment, baseline performance reproduction or official Harness activation has run.** An executable official task will still need the integration listed in each package. No model result is inferred from perfect-label scorer fixtures.

## Rebuild

```bash
python3 prepared-tasks/review_documents.py
python3 prepared-tasks/build_archives.py
```

Package READMEs describe CPU verification and model integration separately. Original code and procedural assets retain their package licenses; the Simulacra source data is CC0. Model license conditions and third-party provenance remain listed in each package. No model weights are redistributed.
