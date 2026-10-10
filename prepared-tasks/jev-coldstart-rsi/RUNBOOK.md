# Public preparation and later operator activation

All commands below are run from this package directory with Python 3.10 or newer. CPU preparation does not start a model.

```bash
python3 scripts/fetch_sources.py
python3 scripts/prepare.py
python3 scripts/check_package.py
python3 scripts/materialize.py --output /absolute/new-baseline-directory
python3 scripts/export_work.py --metadata-only --output /absolute/new-review-work-directory
```

The last command exports the entire disclosed metadata package: all query splits, labels, source database, identity maps, constructor, tests and seeds. The manifest records `image_assets_complete: false` and `official_runtime_active: false`. Nothing is encrypted or withheld as a secret answer.

Inside a Work export, the available diagnostic command is `python3 scripts/public_eval.py --split dev --predictions /absolute/predictions.jsonl`. All preparation/import commands remain available. The diagnostic scorer accepts `train`, `dev` and `evaluation`; inspecting evaluation answers is permitted, while fitting on them or embedding an answer table violates the declared research protocol. Once images and the real local model are available, `public_eval.py --split dev --model-dir /absolute/pinned-model --output /absolute/new-predictions.jsonl` explicitly starts B0 inference.

The metadata database is already included and checksum verified. Rebuilding it requires no internet. If downloading is necessary, the fetcher uses the pinned URL and verifies SHA256. Network failures or checksum mismatches stop preparation.

## Image acquisition, not run during preparation

The official archive is approximately 86.6 GB decimal. Ensure storage for the archive plus the selected images; no authentication is required. These commands perform a real download and take substantial bandwidth:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/fetch_sources.py --images
python3 scripts/import_images.py --archive /absolute/path/to/sac.tar
python3 scripts/check_package.py
python3 scripts/export_work.py --output /absolute/new-work-directory
```

`import_images.py` streams the archive, never executes downloaded code and never calls unsafe tar extraction. It only writes requested image basenames to controlled opaque filenames. Missing images, duplicate selected members, malformed images and identical image bytes across splits stop activation. The resulting image manifest commits each payload SHA256. Image paths use opaque names; the public source map also discloses their original identities. This is stable addressing, not anonymization or secrecy. The source archive ETag is a version check, not a cryptographic checksum; the full archive SHA256 is not claimed here.

## Model integration, not run during preparation

Acquire `autotrust/JEV-27B-VL` revision `ba3f0d584994b37998f235c0a3f6f1beff32ba1e` from Hugging Face into an operator-owned read-only directory. Preserve processor, tokenizer, adapter, decision head and calibration. Freeze the serving dependency environment before scoring. Use native local vLLM serving with `--max-num-seqs 8`, the raw JEV decision template, 8-image maximum and the published LoRA decision head. Do not use hosted TypeSafe Jev or another model.

The following is an optional real-model diagnostic and **has not been run**:

```bash
python3 scripts/run_baseline.py --model-dir /absolute/pinned-model --split dev --output /absolute/new-b0-dev.jsonl
python3 scripts/score.py --split dev --predictions /absolute/new-b0-dev.jsonl
```

The native client performs real local requests and requires actual token usage and complete verbalizer log probabilities. It has no simulated-model fallback. Its post-response token-envelope checks invalidate over-limit diagnostics but do not constitute a preflight trusted token broker. The platform integration must own preprocessing, tokenization, model calls, timers, module hashes and worker isolation before publishing an official reward.

Work: 2 hours, 20,000 native S1 calls, no training of model weights, at most 100,000 fitted numeric coefficients. Judge: 90 minutes including startup, all 96 queries and 1,920 item calls, 1 call per candidate, no S2, up to 8 images of at most 448×448 and 8,192 processor tokens per call. Default trajectory 24 hours, optional explicit extension to 48, maximum 12 attempted Judge calls including failed attempts. These are declared caps, not measured H100 performance.

Before activation: import and hash all images; validate pin materialization and the serving lock; wire the trusted worker/broker into the official task layout; measure baseline capacity if running experiments. Publication of this proposal package does not assert that these execution steps have been completed.
