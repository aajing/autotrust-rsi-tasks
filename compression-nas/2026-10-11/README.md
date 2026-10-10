# Compression, quantization and neural architecture search proposals

Six English proposal packages prepared for Jing Qiu, ajing@autotrust.ai, GitHub `aajing`.

This batch contains six English proposal drafts and their public supporting contracts, prepared by Jing Qiu on behalf of AutoTrust. It is separate from the six earlier proposals that passed official review. All six proposals have now been submitted to official Task Ideas Discussions. Their submitted English bodies have been checked against the confirmed files. See [official submission records](OFFICIAL-SUBMISSIONS.json) for the dated review status and direct links. No GPU experiment has been run. The v2 archives retain their original preparation snapshot and checksums.

| Task | Question | Proposal |
| --- | --- | --- |
| kv-cache-rsi | How much long-context attention state can a reusable encoding and retention policy remove while preserving answer quality and latency? | [Official Discussion #216](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/216) |
| vl-activation-quant-rsi | Can cross-modal calibration and activation treatment improve a real low-precision vision-language deployment under fixed image processing? | [Official Discussion #221](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/221) |
| lowrank-compress-rsi | Can nonuniform low-rank matrix representations compress a dense language model while retaining its general capabilities? | [Official Discussion #217](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/217) |
| sparse24-rsi | Can structured sparse masks deliver an actual whole-model execution improvement while meeting quality constraints? | [Official Discussion #218](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/218) |
| jev-block-nas-rsi | Can a smaller detachable neural capability branch preserve the released JEV branch's probabilities and calibration? | [Official Discussion #219](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/219) |
| gpt-subnet-nas-rsi | Can architecture search extract a trained standalone GPT subnet with a better measured quality/resource tradeoff? | [Official Discussion #220](https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/220) |

## Review downloads

- [All six proposal packages](https://github.com/aajing/autotrust-rsi-tasks/releases/download/compression-nas-2026-10-11-v2/compression-nas-six-proposals.zip)
- [Archive checksums](https://github.com/aajing/autotrust-rsi-tasks/releases/download/compression-nas-2026-10-11-v2/SHA256SUMS)
- [Local validation report](validation-report.json)
- [Publication scope and data delivery](PUBLICATION.json)

## Contents and scope

Each task folder contains the official 28-field `proposal.md`, a machine-readable `task.json`, pinned public-source evidence, a deterministic data specification, and an integration plan. Any local scoring code is a CPU contract implementation, not a replacement for the task's model evaluator. The main score, full-score endpoint, resource and quality gates, and invalid-run semantics belong to that task's contract.

The [distinction from neighboring tasks](shared/DIFFERENTIATION.md), [contributor evidence](shared/expertise-evidence.md) and [handoff notes](shared/SUBMISSION-NOTES.md) are shared across the batch. Names and project contributions are not invented. The contributor confirmed Jing Qiu as the sole listed author for this batch.

Published-source inputs and answers are disclosed; all locally included data, manifests and archives are unencrypted. Model weights and large upstream assets remain available through their specified source interfaces. A listed source interface does not mean the entire upstream artifact is mirrored inside this handoff. Each task's `DATA.md` and `SOURCES.md` distinguish included records, acquisition instructions and metadata-only verification.

## Local preparation checks

For a public checkout, first run `python3 kv-cache-rsi/materialize_data.py` to reconstruct the 192 plaintext LongBench records from their pinned public source. Work and Judge remain offline after setup. See the source notices for attribution.

From this directory, `python3 tools/preflight.py --output preflight-report.json` checks the table structure, source revision presence, required files and local JSON validity. It does not issue an OpenRSI approval. `python3 tools/validate_local.py` runs the six CPU scoring suites, checks included LongBench/ChartQA/WikiText/GSM8K payload hashes and parses task JSON/Python files. These checks exercise reward and admission boundaries; they do not execute model inference.

After checks, `python3 tools/package.py` builds six individual ZIPs and one combined ZIP in `dist/`, verifies archive integrity and confirms the encryption flag is off. `dist/SHA256SUMS` identifies the exact archive bytes. The per-file manifest records hashes of the local handoff files.


The contributor has explicitly confirmed familiarity with all five external source codebases and personal participation in the selected JEV-9B project. The current preparation checks comprise 65 CPU scoring tests, 6 materializer tests, and 146 local data hash/count checks. A fresh full LongBench download did not complete because of network failures; the 192 previously prepared records still match their pinned hashes. See [materialization check](kv-cache-rsi/materialization-check.json). No fresh full-archive success is claimed.

## Official review and execution

The user selected all six directions for development. The scientific contracts were confirmed for official handoff and submitted without changing their 28-field review tables. Runtime allocations are estimates, and full-score attainability has not been measured. Existing released artifacts are used as references; new compression and recovery work belongs to Work rather than becoming an unavailable baseline prerequisite.

Proposal review, task generation, execution validation and final benchmark inclusion are distinct stages. The official handoff must preserve one native proposal session per task. No GPU service has been started and no original session trajectory is bundled in these review archives.
