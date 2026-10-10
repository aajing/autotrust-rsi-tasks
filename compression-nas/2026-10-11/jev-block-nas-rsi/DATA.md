# Public data and metrics contract

This is a fixed disclosed benchmark. Inputs, targets, family metadata, IDs, selection hashes and seeds may be examined and used in Work fitting. There are no hidden answers and no encryption. The scientific conclusion concerns this corpus, not unseen generalization.

## Source and actual counts

Dataset: https://huggingface.co/datasets/SargeDev/jev-distill-corpus-v3/tree/75111a13a8455032f0435050bfc7e0c9026ecfe8 . The public Apache-2.0 card reports 655,806 train, 14,111 validation, 13,766 calibration, 14,261 test, 13,058 ood and 29,955 test_set_30k rows. All six public files are allowed Work inputs. `ood` is a source filename, not a claim of hidden evaluation in this task.

The complete pinned `test_set_30k.jsonl` was streamed on 2026-10-10, parsed and counted without model execution. SHA256: `53b044fa5bbcb22164d9a28811e56fabcd82ae29224d994c693b069eeb5d23ed`.

| Source/kind | Actual available rows | Selected for Judge |
| --- | ---: | ---: |
| yuri_v3/noul | 8,537 | 2,048 |
| yuri_v3/choice | 8,312 | 2,048 |
| yuri_v3/score | 8,527 | 2,048 |
| openjev_v2/noul | 1,432 | 0 |
| openjev_v2/choice | 887 | 0 |
| yuri_v1/noul | 2,260 | 0 |

Evaluation intentionally uses teacher-distribution rows only; placeholder `yuri_v1` targets are not a meaningful fidelity test. Selection is fixed before any candidate: for each of noul, choice, score, sort source=yuri_v3 rows by SHA256 of the UTF-8 string `jev-block-nas-rsi:v1:` followed by the source `id`; break ties by physical zero-based source line ordinal; take the first 2,048. Preserve duplicate text if present; do not deduplicate or replace after selection. Materialize the selected original JSON objects including target distributions. `evaluation-manifest.json` already records all 6,144 IDs and ordinals; `materialize_selection.py` produces the full public JSONL after a task setup download. All original targets remain publicly accessible at the pinned source, and are not withheld by this package.

The actual selected thirteen families are agent660, biology405, business565, chemistry340, genomics446, knowledge579, medical532, physics363, science392, spatial392, structured403, technical651 and theology416. Every family is separately quality-gated. Options: 2-option rows 2,048; 3-option21; 4-option2,004; 5-option23; 6-option2,048. No source-count extrapolation is needed. This set does not represent the full 2-16 option capability, a declared limitation.

## Input and output

Use the pinned native bare-v1 template in the model README: kind, state, question, options and final `[decision]:`; choices have A-P labels. Slot ranges: noul[0,2), score[2,8), choice[8,24), restricted to the row's option count. IDs, family/source names and targets are excluded from model inputs. Rendering remains the same for B0 and every graph.

Use the native state-only truncation rule: when rendered length exceeds 1,024 tokens, remove only state tokens, retaining 60% from its beginning and 40% from its end (integer head=floor(0.6*retained_budget), remainder to tail). If the non-state fields themselves exceed 1,024 tokens, retain those fields and an empty state; the complete fixed row is still evaluated. No row is discarded. Right-padding uses the pinned tokenizer's approved runtime padding value with an attention mask; hidden state is read at the final non-padding token. Padding never contributes to Work token-exposure accounting.

## Metrics

All metrics are computed in FP64 from task-owned native graph outputs. Targets q are normalized once by their positive finite row sum; invalid upstream targets halt task construction instead of shrinking the corpus. Candidate p must be finite, nonnegative and sum to one within 1e-6. A small floating sum error within that tolerance is renormalized; otherwise outcome is invalid/unscored.

- KL per row: sum over q_i>0 of q_i*log(q_i/max(p_i,1e-12)), natural logs. Compute means independently for each primitive and separately for each of the thirteen families.
- soft-ECE10 per primitive: let j=argmax(p), with lower-index tie break; confidence c=p_j and soft correctness a=q_j. Bin c into ten equal-width intervals [0,.1),...,[.9,1]. Sum n_bin/N * abs(mean(c)-mean(a)); empty bins contribute0. This measures soft-target distribution consistency, not human-ground-truth calibration.
- choice agreement: mean(argmax(p)==argmax(q)), lower-index ties for both.
- noul Brier: mean((p_true-q_true)^2).
- score RPS: for six ordered levels, average the five squared differences between cumulative p and q through levels0,...,4; then mean over score rows.

Use absolute delta gates from task.json against the frozen same-protocol B0 report. These are not comparisons with upstream headline metrics. Full score combines every primitive/family/calibration/latency/memory gate with canonical branch size <=25%B0; the target is proposed, not experimentally established.

## Fixed timing order

Take the first 32 rows per primitive in manifest order. Interleave them as noul[0], choice[0], score[0], noul[1], choice[1], score[1], and so on, yielding a 96-row ring. For each batch size, start the cursor at zero and consume consecutive rows modulo 96 through all five rounds; each round consumes 10 warmup batches followed by 30 measured batches. Advance the cursor for both warmup and measured batches, and do not reset it between rounds. B0 and candidates use the identical sequence.

## Budgets and complete accounting

At most 8,000,000 non-padding input-token exposures and100 Work wall minutes per candidate, whichever is first; every repeat and local teacher pass counts. All training remains in Work. Timing uses fixed selected rows, not new data. A Judge run always evaluates6,144 quality rows plus both timing workloads and memory/integrity checks. Fixed timing repetitions are measurements, not new candidate trials. One infrastructure retry of the same snapshot is allowed; it consumes trajectory wall time and returns no score if incomplete. No row replacement, best-of selection or reset of the global24/48h budget.

## Frozen report binding

Every trusted complete report carries data_manifest_sha256 and runtime_fingerprint, each a 64-character lowercase SHA256. Data binding covers the exact materialized evaluation inputs, targets, selection and tokenization manifest; runtime binding covers the fixed source, tokenizer, evaluator/operator configuration, precision and H100 environment. Candidate and frozen B0 bindings must match exactly. Missing/malformed/different bindings make the result unscored. valid_artifact and structural integrity flags must be literal JSON true, never truthy strings. These fields are produced by the trusted runtime, not accepted from candidate claims.
