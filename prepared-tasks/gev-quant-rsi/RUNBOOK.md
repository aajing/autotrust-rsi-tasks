# Reproduction and public evaluation

All data, answers, seeds and evaluator code are public. No model weights were downloaded and no GPU experiment was run in this preparation.

## CPU package checks

Use Python 3.10+ and the NumPy version in `requirements-cpu.lock.txt`.

```sh
python3 -m taskkit.cli audit --root .
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

Checks cover exact split counts, gold oracles, scenario separation, arithmetic/admission, revised scoring and baseline hash/copy behavior. Synthetic tiny model/cache fixtures are only file-contract tests, never GEV artifacts or scores. Rebuilding via `python3 -m taskkit.cli build --root .` preserves the released seed and exact manifest. Any changed data invalidates measured cache bindings.

`python3 scripts/stage_work.py /absolute/new/work-directory` includes evaluation gold/PNGs/seeds. Public captured-output diagnostics use `python3 -m taskkit.cli public-assess --split development --predictions results.jsonl`; practice/evaluation are also accepted for inspection. This is not trusted model execution or an official reward.

## Existing B0 materialization

During author setup on the execution machine, install the normal Hugging Face CLI and download the existing pinned release. This command is documented here and was not executed during proposal repair:

```sh
hf download autotrust/GEV-26B-Decide --revision 7c89590ead085bf77630b4bf68264ea30b6ddc78
```

The command prints the standard cache `snapshots/7c89590ead085bf77630b4bf68264ea30b6ddc78` directory. Keep that cache and its blob symlinks. Do not use `--local-dir`, because this materializer deliberately checks the standard cache content-addressed blobs.

```sh
python3 solution/materialize_baseline.py --source-snapshot /absolute/cache/models--autotrust--GEV-26B-Decide/snapshots/7c89590ead085bf77630b4bf68264ea30b6ddc78 --output /absolute/new/b0-artifact
```

Solution verifies SHA256/Git blob hashes, pinned metadata and complete safetensors/index payload coverage, then copies B0 and writes `prepared-artifact.json`. It does not need that wrapper in advance and performs no download, model loading, profiling, pruning, quantization, fitting or evaluation. Missing or corrupted real source files fail closed. Ordinary file copying uses zero GPUs. Required weights already exist upstream; task-specific score measurements are separate post-acceptance work. For additional exact remote per-file membership binding, author setup can run `python3 scripts/fetch_source_inventory.py --output source/upstream-inventory.json` (metadata only) and pass `--inventory source/upstream-inventory.json` to Solution. This API could not be reached during repair; current checks establish cache integrity plus pinned config/index binding, not a claim that every remote weight hash has already been retrieved.

## Evaluation and controls

After implementing trusted H100 inference and measuring B0, call `python3 -m taskkit.cli assess --predictions PREDICTIONS.jsonl --resources RESOURCES.json --references public-authoring/reference_cache.json` with `--probe-dir DIR`. Only a task-owned runtime may create official outputs/resource receipts; candidate-created JSON is not trusted evidence. Null B0 measurements deliberately yield unscored. `scripts/gpu_entrypoint.py` still stops until ordinary GPU integration is completed.

`100 * clip((1 - delivered_bytes / B0_bytes) / 0.60, 0, 1)`. Full score requires at most 40% of B0 delivered inference weight bytes and every quality/resource gate. The unchanged B0 has zero score. The 40% ratio is now the full-score target rather than an eligibility gate; intermediate reductions receive graded credit. B0 distribution distortion is reported, not BQ-normalized.

BQ is an optional Work-produced ablation. Its absent checkpoint or measurements never block baseline materialization, activation or the primary score. All optional-control profiling, fitting/export, repeated/discarded invocations and evaluation consume the same Work budgets; submitting it consumes a Judge attempt. Preserve provenance and report optional control results only if actually generated.

All complete gate failures get zero; invalid, crashed, timed-out or incomplete attempts are unscored. Real outputs/reference measurements will remain public. B0 calibration/quality/bytes/latency are frozen against data/source/runtime hashes. No frozen cache may be changed by a candidate.

## Budgets and limits

One node, one H100 80 GB, 24 CPU cores, 256 GB host RAM and 300 GB free SSD; Work and Judge are sequential. Two-hour Work, one-hour Judge and fifteen-minute overhead imply 3.25 hours/cycle: at most seven worst-case cycles in 24 hours or fourteen in 48 hours before the twelve-attempt cap. Actual model feasibility remains unmeasured. Pruning recovery has separate exposure/update caps; every repeated exposure and invocation counts. See `task.json` and INTEGRATION.md.

Published scenario groups separate practice/development/evaluation, but do not establish answer secrecy. Only practice is for fitting and development for selection; public benchmark overfitting remains a stated limitation. No encrypted assets or withheld answer bank exists.
