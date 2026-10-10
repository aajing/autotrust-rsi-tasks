# AutoTrust RSI research proposals

Six English task proposals and complete public preparation materials for **Jing Qiu**, **ajing@autotrust.ai**, GitHub `aajing`. Prepared 10 October 2026. Public release is authorized; these six proposals are **not submitted to official review**. This repository is a proposal handoff, not a claim that official tasks or GPU experiments have already run.

| Task | Learning / development / evaluation | Research target |
| --- | --- | --- |
| [gev-think-rsi](gev-think-rsi/proposal.md) | 500 / 100 / 200 | Train an external adaptive compute router around frozen GEV; optimize reasoning and tool allocation |
| [jev-judge-rsi](jev-judge-rsi/proposal.md) | 480 / 144 / 240 | Improve native JEV evidence review and calibrated success probabilities across mixed task families |
| [jev-coldstart-rsi](jev-coldstart-rsi/proposal.md) | 342 / 96 / 96 | Improve personalized image ranking with fixed JEV and genuine open human ratings |
| [jev-visual-control-rsi](jev-visual-control-rsi/proposal.md) | 128 / 48 / 48 | Improve prompts and controller logic for visual manipulation in a deterministic CPU simulator |
| [gev-quant-rsi](gev-quant-rsi/proposal.md) | 1,152 / 288 / 576 | Allocate quantization precision while preserving generative and decision behavior |
| [moe-prune-rsi](moe-prune-rsi/proposal.md) | 1,536 / 384 / 576 | Prune experts and recover mixed-task quality under fixed compute and quality gates |

Every evaluation input, answer, seed, generated scene, reference certificate and scoring function prepared for these tasks is public. There is **no encrypted archive, password, secret answer pack or withheld evaluation seed**. Work exports expose the complete public assets. Fitting remains limited to the specified learning split; development supports method selection. Submitted methods must follow their input interfaces and may not embed answer tables or read labels at inference. Those are audit rules, not guarantees that public data cannot be memorized. Results are optimization findings on disclosed fixed benchmarks, not secret-test generalization evidence.

Each package includes the official 28-field proposal, source pins, baseline materializer, modification bounds, score/full-mark rules, budget, data construction, scoring code, CPU contract checks and execution instructions. Native decision models motivate the methods; evaluation includes general Python, SQL, numerical reasoning, workflows, visual tasks and recommendation, rather than only decision-model benchmarks.

## What is included and what is downloaded separately

Five task suites are generated from original open procedural code and include their generated input/answer assets. The recommendation package includes the actual 44,748,800-byte CC0 Simulacra SQLite database, all derived metadata and ratings, and the exact 3,560-image import list. All 57 / 16 / 16 eligible survey-user groups are used; six paired views per group give the listed counts. The evaluation split has 16 independent groups and is explicitly a pilot.

Model weights are available through the pinned public Hugging Face repositories. The Simulacra image archive is available without credentials at its public upstream URL; its 86,569,533,440 bytes are **not mirrored here**. Its importer and access metadata are included. No image pixels or model outputs have been fabricated. All locally prepared task material is published, while these large upstream dependencies retain their documented download interfaces.

## Download and verification

The release contains six individual `*-public.zip` packages and `autotrust-six-task-proposals-public.zip`, plus `SHA256SUMS` and `archives.json`. All ZIP files are ordinary unencrypted ZIPs. Source and package links are indexed in the repository root.

To inspect locally, open a package's `proposal.md` and its `README.md` or `RUNBOOK.md`. To verify the proposal copies and regenerate downloadable archives:

```bash
python3 prepared-tasks/review_documents.py
python3 prepared-tasks/build_archives.py
```

These commands do not start a model or provision a GPU. CPU oracle fixtures check scoring arithmetic and are never reported as model scores. All six specify one H100 80 GB on one physical node; sufficient host RAM was confirmed. No GPU experiment has run. See [STATUS.md](STATUS.md) for remaining execution integration and [the proposal index](../draft-proposals/2026-10-10/README.md).
