# AutoTrust RSI tasks

Six research proposals for OpenRSI / RSI-Anything, prepared by **Jing Qiu** (`aajing`, `ajing@autotrust.ai`). Every prepared evaluation input, answer, seed, reference solution and scoring implementation is public. No files are encrypted or password protected.

| Task | Research question | Proposal |
| --- | --- | --- |
| gev-think-rsi | Can a trainable external router improve compute allocation around frozen GEV on a fully disclosed benchmark? | [English revision](draft-proposals/2026-10-10/gev-think-rsi.md) |
| jev-judge-rsi | Can native JEV review improve calibrated judgments across mixed task families? | [English proposal](draft-proposals/2026-10-10/jev-judge-rsi.md) |
| jev-coldstart-rsi | Can bounded evidence-selection policies and prompts improve native JEV personalized image ranking? | [English revision](draft-proposals/2026-10-10/jev-coldstart-rsi.md) |
| jev-visual-control-rsi | Can iterative prompt and controller optimization improve visual manipulation? | [English proposal](draft-proposals/2026-10-10/jev-visual-control-rsi.md) |
| gev-quant-rsi | Can data-dependent precision allocation reduce storage while preserving the released BF16 model's quality? | [English revision](draft-proposals/2026-10-10/gev-quant-rsi.md) |
| moe-prune-rsi | Can expert selection and bounded recovery preserve quality after substantial pruning? | [English revision](draft-proposals/2026-10-10/moe-prune-rsi.md) |

## Download

Repository: `https://github.com/aajing/autotrust-rsi-tasks`

Immutable revision release and individual packages (packaged as drafts before contributor confirmation): `https://github.com/aajing/autotrust-rsi-tasks/releases/tag/review-revision-1-2026-10-10`

Original submitted packages remain archived at `https://github.com/aajing/autotrust-rsi-tasks/releases/tag/public-proposals-2026-10-10`

Complete unencrypted ZIP: `https://github.com/aajing/autotrust-rsi-tasks/releases/download/review-revision-1-2026-10-10/autotrust-six-task-proposals-public.zip`

The release includes six individual task ZIPs, the combined ZIP, `SHA256SUMS` and `archives.json`. On macOS use `shasum -a 256 -c SHA256SUMS` after downloading the listed ZIPs; on Linux use `sha256sum -c SHA256SUMS`.

## Scope and status

All six revised proposals received **Pass in official proposal review on 10 October 2026**. The [official discussions and status](official-submissions/README.md) records the verified results and exact posted English bodies. Task generation, execution validation and final benchmark inclusion are later stages. The original submissions received Reject; the contributor confirmed the revisions, which were posted to the same Discussions. The immutable revision release preserves the drafts as packaged before confirmation. See [confirmed revision changes](review-revisions/README.md), [package index](prepared-tasks/README.md), [execution status](prepared-tasks/STATUS.md) and [delivery record](delivery.json).

The disclosed evaluation sets support reproducible, auditable fixed-benchmark research. Researchers can inspect the answers. The confirmed think and coldstart revisions explicitly allow evaluation-informed fitting and selection; they measure optimization on the disclosed benchmark. Each task defines its allowed artifact and inference interface separately. No unseen-test or memorization-proof guarantee is made.

All locally prepared task files are included. Public model weights are downloaded from pinned Hugging Face sources. The coldstart package includes the complete CC0 SQLite metadata and a precise selected-image manifest; the approximately 86.6 GB upstream image archive is publicly downloadable but not mirrored here. Package runbooks give the source interfaces and import steps.

CPU contracts and deterministic data checks have run. **No GPU/model experiment, baseline performance reproduction or official Harness activation has run.** An executable official task will still need the integration listed in each package. No model result is inferred from perfect-label scorer fixtures.

## Rebuild

```bash
python3 prepared-tasks/review_documents.py
python3 prepared-tasks/build_archives.py
```

Package READMEs describe CPU verification and model integration separately. Original code and procedural assets retain their package licenses; the Simulacra source data is CC0. Model license conditions and third-party provenance remain listed in each package. No model weights are redistributed.
