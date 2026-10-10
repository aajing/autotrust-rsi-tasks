# Reproduction and public evaluation

This is a public benchmark with fully released data, seeds, answers and evaluators. It is not a secret-test package. CPU preparation is implemented; real H100 execution, baseline measurement and official OpenRSI integration are not yet implemented or claimed.

1. Use Python 3.10+ and the NumPy version in `requirements-cpu.lock.txt`. These are CPU requirements; they do not specify a GPU serving environment.
2. Run `python3 -m taskkit.cli audit --root .`, then `python3 -m unittest discover -s tests -v`. Tests validate counts, semantic group separation, golden oracles, packed arithmetic, scope/admission rules and scoring formulas using explicitly synthetic fixtures.
3. `python3 -m taskkit.cli build --root .` reproduces all three splits from the published seed. It preserves the existing seed. Any dataset change requires a manifest/version change and invalidates measured reference bindings; never reuse a reference cache with a different data hash.
4. `python3 scripts/stage_work.py /absolute/new/work-directory` copies the public task, including evaluation gold, images, seed and reference declarations. No encrypted or excluded answer bank exists.
5. Public output diagnostics: `python3 -m taskkit.cli public-assess --split development --predictions results.jsonl`. The same command accepts practice and evaluation for public inspection. It assesses captured outputs, not a model execution or official research reward.
6. Baseline materialization: `python3 solution/materialize_baseline.py --prepared PATH --output NEW_PATH`. The source must already contain a real materialized checkpoint and complete per-file hashes. This command only verifies/copies. It refuses missing baselines; it never trains, infers or invents tensors.
7. Once actual operator references exist, use `python3 -m taskkit.cli assess --predictions PREDICTIONS.jsonl --resources RESOURCES.json --references public-authoring/reference_cache.json`, with `--probe-dir DIR` for quantization or `--expert-map MAP.json` for pruning. Current null references intentionally produce unscored. Files alone cannot mint an official reward: the operator must connect trusted inference, admission and accounting.
8. `scripts/gpu_entrypoint.py` explicitly stops because the adapter has not been activated. Follow INTEGRATION.md rather than mistaking CPU pack/dequant functions for a tested H100 engine.

## Published layout and protocol

All practice/development/evaluation inputs, gold and PNGs live under `data/public/`. `public-authoring/` holds the published evaluation seed, probe specification, any B96 profiling plan and reference-cache declaration. Completed baseline/output/measurement records will be added here as public reproducibility evidence. Only the operator may modify frozen references in a scored run; access to their contents is unrestricted.

The six families are exact arithmetic, restricted single-return Python, SQLite SELECT, tool-call JSON, visual numerical/spatial output and binary confidence. Gold includes every Python test, SQL database, answer and canonical output. A bounded AST interpreter evaluates Python without host execution; SQLite uses an authorizer and operation cap. Malformed completed answers are wrong. Missing, duplicated or additional prediction IDs invalidate the complete assessment.

Concrete canonical scenarios are grouped before split assignment. Practice/development/evaluation share grammar and difficulty support but do not share scenario groups. This separation supports reproducibility and a fit-only-practice protocol; with published evaluation labels it does not establish unseen-data generalization. Models and candidate artifacts must still produce answers by inference rather than looking up released gold.

Model scores and resource receipts remain absent. A future measured reference must bind the source revision, dataset hash, runtime/container fingerprint, tensor inventory, numerical settings, B0 quality/calibration/bytes/latency, and task-control measurements. Quantization requires eighty published reference vectors and fixed tokenizer probe positions; neither exists yet. The reference vectors have a planned total size of 80 MiB. No vector is synthesized from gold.

The fixed quantization execution path reconstructs every packed expert to BF16 on CPU using the supplied arithmetic, then loads the same ordinary BF16 backbone runtime for BQ and every candidate. There is no backend selection or packed-kernel dependency. Count all delivered model weights/scales/adapters and frozen dependencies once. Deterministically reconstructed runtime BF16 tensors are ephemeral derivatives, not additional submitted weights or independently fitted parameters; exclude them from delivered-storage bytes but charge reconstruction/loading to Judge wall time and measure actual memory. No native four-bit execution, GPU memory reduction or speedup is claimed.

Each resource receipt covers delivered-artifact bytes, actual peak GPU allocation, three warmed-inference timing passes and full Judge duration. The scorer checks formulas but cannot authenticate a candidate's self-reported GPU measurements. Only an operator-owned runtime may issue the official evidence.

## Pruning endpoint and unchanged quality gates

For pruning, the fixed control is B96: 96 experts per layer, 2,880 overall. Its maximum structural score is 66.6667, subject to every gate. The formula is `100*clip((3840-E)/1440,0,1)`; full marks require E≤2,400 (80 experts per layer on average, 37.5% removed), every layer retaining 64–128 experts and all quality/resource gates. This endpoint was chosen before any model run; attainability is unverified. Quantization retains its original distortion-reduction formula. Neither task's 1-percentage-point overall accuracy loss, 3-point family loss or Brier +0.01 limits were loosened.

## Budgets and evidence

One H100 80 GB and 256 GB host RAM are specified; the user confirmed RAM availability. Work is two hours and Judge sixty minutes. The trajectory is 24 hours, up to twelve attempted Judge calls including failures; a recorded 48-hour extension retains the call cap. All model invocation input/output tokens count, including profiling, teacher generation, development evaluation, repeats and discarded attempts. Pruning recovery exposures and optimizer updates have separate ceilings.

`cpu-validation.json` records CPU checks only. No reported perfect oracle fixture is a model baseline. No runtime feasibility, full-score attainability or official acceptance is implied. Public release does not resolve inherited model licenses, runtime compatibility or the official shared-snapshot trust boundary; see LICENSES.md and INTEGRATION.md.
