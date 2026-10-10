# jev-judge-rsi

Prepared proposal package. No official submission, model inference, training or GPU validation is claimed. This task judges whether another agent completed a task; it does not optimize an acting agent to execute it. JEV-27B-VL stays frozen; permitted research adjusts judge prompts, optional review/recheck use and a small external probability calibrator. Host RAM availability is contributor-confirmed.

## Fully public benchmark protocol

All 480 training, 144 development and 240 evaluation observations, gold worlds, answers, tests, seeds and group mappings are unencrypted in `data/public/`. The package includes 432 original 768×768 PNGs in `data/public/media/`. Work exports include evaluation inputs and answers. No hidden answers or secret-test generalization claim remain.

The research protocol permits training-label fitting and development selection, then requires freezing the selected policy before evaluation. Do not fit prompts/calibrators, select policies or construct lookups from evaluation inputs, labels or verdicts. Auditing these public assets is allowed; disclose evaluation-informed changes and describe resulting scores as benchmark-conditioned exploratory evidence. This is a declared conduct rule, not technically assured secrecy. The model's ordinary inference input contains request, context, transcript, artifacts and images; gold fields are not automatically inserted into that interface, although researchers can inspect them.

## Independent worlds and exact gold

Six equally represented families: browser transactions, account settings, Python repair, SQL analysis, document extraction and document-to-inventory workflows. Per family there are 80/24/40 train/dev/evaluation cases. Each balanced construction batch has **eight independently sampled worlds**: four successful outcomes and four failures, one each for omission, wrong value, uncommitted change and misleading completion claim. The 864 semantic worlds are distinct and split-disjoint; successful cases no longer repeat one world four times. Gold grouping records have one ID each.

Wrong values use legitimate domains: ordinary invoice IDs/recipients, allowed settings, order states and SQL thresholds. SYSTEM, MONTHLY and UTC-1 are valid settings in positive cases; DRAFT/SUBMITTED and UNPAID/PAID can all be requested correct final states. Tests verify those positive examples and domain membership. Claims are sampled independently of outcomes. Omission is an actual missing required field/operation. This removes identified marker shortcuts, but does not establish absence of every correlation or natural-world difficulty.

Gold is computed by actual postconditions, restricted Python AST interpretation, read-only SQL on three public databases, exact document arithmetic and persisted-state checks. Mutation tags are provenance, not the oracle. The corpus is controlled synthetic data, not sampled real agent behavior. Original code is Apache-2.0; generated records and PNGs are CC0-1.0.

## CPU commands and output schema

Run from this package directory:

```sh
python3 scripts/prepare.py
python3 scripts/check_package.py
python3 scripts/materialize_baseline.py --baseline b0 --output /tmp/jev-judge-b0
python3 scripts/export_work.py --output /tmp/jev-judge-public-work
python3 scripts/score.py --split evaluation --predictions /absolute/path/predictions.jsonl
```

Fixed published version-2 seeds reproduce the corpus; the manifest hashes every public asset and generator. Prediction JSONL: `{"id":"opaque-id","p_complete":0.7,"evidence":[],"diagnosis":"..."}`. Evidence allows up to four references: `{"kind":"transcript","start":1,"end":2}`, `{"kind":"artifact","name":"answer.py","start":1,"end":2}`, or `{"kind":"image","image":0,"box":[0.1,0.1,0.3,0.2]}`. Lines are one-based, referenced text at most 160 characters; boxes are normalized x/y/width/height. Diagnosis is at most 120 words and is not LLM-graded.

Item loss is (p−y)². Malformed probabilities/references receive loss one. Missing/duplicate/extra IDs make a run unscored. Score is 100 × max(0, 1 − mean loss / 0.25); full marks mean every valid probability exactly equals its gold 0/1 label, complete coverage, and, for the proposed official run, valid scope/resource checks. Perfect oracle fixtures score 100, constant 0.5 scores zero and reversed gold has Brier loss one. These are scorer tests, not model results.

## Implemented versus pending

CPU tests validate quotas, all 864 gold labels, reproducibility, independent worlds, PNG dimensions, observation schema, former marker positive coverage, scoring, forbidden Python, policy admission and budget reservation. `policy.py` admits affine calibration or a two-hidden-layer JSON MLP with at most 16,384 parameters and clipped outputs; fixed features are initial/review probability, text length normalized by 3000, and image count normalized by two. `fit_calibrator.py` fits only from supplied training predictions; no real fitted B2 exists.

B0/B1 are ready configuration artifacts, not measured baselines. `runtime_adapter.py` raises `MODEL_RUNTIME_UNAVAILABLE`. Real JEV inference, tokenizer/image accounting, model-generated evidence, trusted call broker, H100 profiling, runtime locks and official Harness integration remain pending. Character admission limits do not substitute for tokenizer enforcement. The planned allowance is one H100 80 GB, 2-hour Work, 1-hour Judge, maximum 24-hour research and 12 attempted scored Judge calls; 48 hours is only an optional separately recorded extension. RAM availability is confirmed; runtime performance is unknown.

Trusted evaluator code and frozen manifests remain outside candidate modification. The existing Work-snapshot/Judge-only-tests lifecycle does not guarantee resistance to arbitrary privileged tampering. All answers are intentionally public; protocol compliance must be reported honestly.

Publication target: `https://github.com/aajing/autotrust-rsi-tasks`, directory `prepared-tasks/jev-judge-rsi/`; the actual publication commit will be recorded. Contributor Jing Qiu (`aajing`), ajing@autotrust.ai; evidence: `https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca`. The pinned model and upstream author-reported AgentRewardBench precedent are documented in `configs/sources.json` and `proposal.md`.
