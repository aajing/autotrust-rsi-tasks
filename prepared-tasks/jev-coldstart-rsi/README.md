# jev-coldstart-rsi

Public proposal package, not submitted to official review. Prepared 10 October 2026 for Jing Qiu, ajing@autotrust.ai, GitHub `aajing`.

Improve personalized ranking of new generated images using frozen `autotrust/JEV-27B-VL`. Optimize evidence selection, image composition, prompts and bounded numerical calibration. Return one real-valued score for each of 20 candidate images.

AutoTrust's JEV recommendation demonstration motivates the use of native S1 decision probabilities for ranking. This task uses **Simulacra Aesthetic Captions v1.0 (CC0)** and genuine recorded human ratings. It measures offline aesthetic preference, not next-watch prediction, click uplift or chronological upload novelty. Source-demo numbers are not this task's baseline.

The complete SQLite metadata and all derived inputs, answers, source maps and seeds are public. There are **342 / 96 / 96** learning / development / evaluation queries from **57 / 16 / 16** disjoint synthetic survey-user groups. Each group contributes six cells: text/image/both crossed with 3/20 history items. The evaluation split has only 16 independent groups and is a pilot benchmark.

This is a disclosed fixed benchmark: researchers may inspect all material. Fit learned numerical parameters on learning data only; select methods on development data. A submitted policy must rank from its supplied history and candidate evidence, not retrieve per-item answers or contain an answer table. Those are auditable method rules, not a secrecy guarantee. Scores do not establish unseen-test generalization.

| Path | Contents |
| --- | --- |
| `proposal.md` | English proposal in the 28 official fields |
| `configs/` | Task bounds, schemas and pinned source revisions |
| `data/source/` | Complete 44,748,800-byte CC0 SQLite snapshot |
| `data/public/` | Every split, every label, source map and exact 3,560-image request list |
| `baseline/` | Materializable B0 policy; one native JEV S1 request per candidate |
| `src/` | Deterministic construction, tie-aware NDCG and real local JEV client |
| `scripts/` | Acquisition, safe image import, public export and diagnostics |
| `tests/`, `evidence/` | CPU contracts, provenance and truthful acquisition status |

Full score is 100 when every query reaches ideal DCG@10 and all runtime/integrity gates pass. A perfect-label CPU fixture verifies this arithmetic; it is not a measured model result.

One H100 80 GB, 16 CPU cores, 96 GB RAM and 200 GB free storage are specified. Host RAM availability was confirmed. GPU inference, baseline quality and latency have not been measured. The official runtime entry point fails closed until integration is completed.

The public upstream image archive is 86,569,533,440 bytes and is not mirrored in this package. The exact selected-image list, public download URL and safe extractor are included. Image import/hash validation, model materialization and trusted runtime integration are execution requirements; they are not represented as completed. No placeholder images, secret answer archive or encryption is used. See `RUNBOOK.md` and `DATA_CARD.md`.
