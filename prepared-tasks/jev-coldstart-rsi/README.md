# jev-coldstart-rsi

Revision addressing official discussion #212 for Jing Qiu, ajing@autotrust.ai, GitHub `aajing`. No model/GPU execution or measured model score is claimed.

Improve the ranking produced by frozen `autotrust/JEV-27B-VL` through compact evidence-selection policies and global prompts. This is **benchmark-conditioned optimization**: all inputs, human ratings, seeds, source maps and model feedback from **all three published partitions may guide fitting and selection**. There is no fit-excluded partition and no unseen-item, heldout-user or population-generalization claim. Coldstart describes the limited 3/20-history view supplied to the model at inference.

The final artifact is strict, code-free `policy.json`. `src/policy.py` owns its admission and execution. The policy selects up to seven histories using linear coefficients or a small two-hidden-layer MLP over six fixed evidence features, plus two global prompt strings. The selector has at most 4,096 finite numeric parameters; each hidden layer has at most 32 units. Prompt strings are at most 512 characters each and have no interpolation or conditional execution. Every candidate's score equals the unmodified probability from one fresh native JEV S1 call. No prediction maps, answer tables, file paths, callback hooks or candidate executable rankers are accepted. Public-label specialization within this admitted interface is allowed and does not demonstrate generalization.

This preserves several research hypotheses: content relevance versus rating diversity, linear versus nonlinear history selection, prompt framing and how these mechanisms behave across modalities/history lengths. The model weights, feature definitions, scorer and resource limits stay fixed. B0 uses the first five histories (all three for short cells), the original fixed question and the same one-call score extraction. `scripts/materialize.py` copies/admit-checks its existing JSON without inference or fitting.

Data is **Simulacra Aesthetic Captions v1.0 (CC0)**. The included checksum-verified 44,748,800-byte SQLite and deterministic constructor produce **342 / 96 / 96** query rows from **57 / 16 / 16** disjoint survey-user groups, six views per user. These are reported in `evidence/split-report.json`. Human ratings measure generated-image aesthetics, not clicks or online engagement. The independent scoring workload contains only 16 user groups.

The exact selection contains 3,560 item records. All metadata and answers are delivered. Pixels use a concrete public 86,569,533,440-byte archive plus the exact `data/public/image-requests.jsonl` selection. The importer verifies selected PNGs, writes SHA256 hashes and **reports but retains identical-byte groups**, including cross-partition matches. Pixel duplication never reduces the fixed cohort, changes the metric denominator or activates a fallback. Missing/corrupt assets are unscored infrastructure failures; no replacements or partial cohort scores are allowed.

Full score is 100 when all 96 queries reach ideal DCG@10 and all resource/integrity gates pass. Expected discount handles ties; all six cells have equal weight. CPU oracle fixtures verify arithmetic and are not model results. User-group bootstrap may describe workload sensitivity, not unseen-population confidence after adaptive public-label selection.

CPU-only checks:

```sh
python3 scripts/prepare.py
python3 scripts/check_package.py
python3 scripts/materialize.py --output /absolute/new-baseline-directory
python3 scripts/export_work.py --metadata-only --output /absolute/new-review-directory
```

One H100 80 GB, 16 CPU cores, 96 GB RAM and 200 GB disk are specified. Work: 2 hours/20,000 native calls. Judge: 90 minutes/1,920 calls across all 96 queries. The actual GPU/runtime envelope remains unmeasured. Native serving/token accounting and official Harness integration remain task-generation work; `official_judge.py` fails closed until then. Current shared Work/Judge snapshots do not guarantee privileged-root isolation. See `RUNBOOK.md`, `DATA_CARD.md` and `proposal.md` for the full contract.
