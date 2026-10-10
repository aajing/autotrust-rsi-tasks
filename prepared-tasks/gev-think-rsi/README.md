# gev-think-rsi

Prepared proposal package. No official submission or model/GPU run is claimed. The main model, autotrust/GEV-26B-Decide, stays frozen. The research agent may fit a small **external compute-allocation router**; this is not weight self-improvement of GEV. Host RAM availability is contributor-confirmed.

## Fully public benchmark protocol

All 500 training, 100 development and 200 evaluation inputs, answers, executable oracles, construction seeds and group assignments are published without encryption under `data/public/`. The evaluation files are `evaluation.jsonl` and `evaluation_gold.jsonl`; seeds and groups are `seeds.json` and `groups.jsonl`. Work exports include all of them. There is no secret test set and no secret-test generalization claim.

By the declared research protocol, fit only on training data, select on development, and freeze the chosen router before evaluation. Do not fit prompts/router weights, choose policies, or build lookups from evaluation inputs, answers or traces. Public availability makes this a conduct rule, not an enforceable secrecy guarantee. Inspection for dataset auditing is permitted; disclose evaluation-informed changes and treat their scores as benchmark-conditioned exploratory results. A scored runtime passes only the current ordinary task to GEV and only admitted features to the router, even though researchers can inspect every answer.

## Data and implemented components

Five equally represented free-response families: Python traces, SQL, invoice arithmetic, schedules and stateful workflows. Each family contributes 100/20/40 records. Every semantic group has one direct and one compositional variant and belongs to one split; all 400 group fingerprints are distinct. These are related variants, not 800 independent scenarios.

Python varies update expressions, branch comparisons and nested-loop compositions. SQL varies grouping, aggregates, row filters and HAVING thresholds over two tables and three public checking databases. Invoices vary invoice-level versus per-line discount rounding before tax. Schedules vary precedence graphs, including up to two predecessors, and shuffle job presentation. Workflows may require a second item to wait until the first is archived. These increase structural variety; difficulty, adaptive-compute benefit and model headroom have not been measured.

`task.py` provides deterministic generation, bounded AST interpretation, read-only SQLite evaluation, schedule validation, state transitions and exact scoring. `policy.py` admits threshold policies and a two-hidden-layer ReLU JSON MLP of at most 65,536 parameters, over a fixed 72-feature order and five actions. The router never supplies answer text or tool arguments. `configs/` contains materializable B0 and controls, source pins and budgets. Original code is Apache-2.0; generated records are CC0-1.0.

## Reproduce and verify on CPU

Run from this package directory:

```sh
python3 scripts/prepare.py
python3 scripts/check_package.py
python3 scripts/materialize_baseline.py --output /tmp/gev-think-b0
python3 scripts/export_work.py --output /tmp/gev-think-public-work
python3 scripts/score.py --split evaluation --predictions /absolute/path/predictions.jsonl
```

`prepare.py` uses fixed, published version-2 seeds and rewrites reproducible data. `data/manifest.json` hashes every public record, answer, seed and group file plus the generator. Export destinations must not already exist. Prediction records are `{"id":"opaque-id","answer":{...}}`; arithmetic, SQL, schedules and workflow outputs follow the schema in each request. All requested IDs must occur exactly once. Missing/duplicate/extra IDs are unscored; ordinary malformed or wrong answers score zero for that item.

The diagnostic score is 100 × correct / 200. Full marks require every evaluation item correct; the proposed official run additionally requires all scope/resource checks. CPU oracle fixtures reach 100 and all-wrong fixtures reach zero. These fixtures test scoring and do not count as model performance. Tests also cover reproduction, grouped separation, destructive SQL, unsafe Python, invalid schedules, unfinished workflows, admission and budget denial.

## Execution boundary and remaining integration

`runtime_adapter.py` fails with `MODEL_RUNTIME_UNAVAILABLE`. Real GEV inference, its frozen 64-dimensional feature projection, authentic token receipts, controller/tool broker, runtime dependency/container locks and official Harness integration are pending. B0 is a ready JSON configuration, not an already measured model baseline. Standard safetensors loading and broader policy languages are outside the implemented contract; current artifacts use finite JSON arrays.

Planned ceilings: one H100 80 GB, 16 CPU cores, 128 GB host RAM, 180 GB disk; 2-hour Work and 1-hour Judge. Exact hardware performance is unknown. At most 12 attempted scored Judge calls and 24 hours total research; an optional separately recorded 48-hour extension changes neither call nor per-run limits. No GPU tests are required to inspect this proposal, and no runnable GPU result is implied.

Trusted scoring code must remain outside candidate modification and validate a frozen public manifest and admitted artifact. The supported shared Work snapshot plus Judge-only tests does not defeat arbitrary privileged-runtime tampering. Public answers deliberately provide no secrecy defense; the protocol must report that limitation.

Task publication target: `https://github.com/aajing/autotrust-rsi-tasks`, directory `prepared-tasks/gev-think-rsi/`; publishing records the actual commit. Contributor Jing Qiu (`aajing`), ajing@autotrust.ai; contributor-selected evidence: `https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca`. Model source and license terms are pinned in `configs/sources.json`.
