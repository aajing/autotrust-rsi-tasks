# gev-quant-rsi

Public, inspectable benchmark package. The user authorized publication of all task material without encryption, including evaluation inputs, labels, executable gold, images, source seeds and scoring code. Nothing is described as a secret test.

Publication target: `https://github.com/aajing/autotrust-rsi-tasks/tree/main/prepared-tasks/gev-quant-rsi`. The publishing operator records the actual commit after upload; this package does not claim a completed upload or official acceptance.

The implementation includes deterministic six-family data, PNG inputs, objective CPU oracles, strict complete-coverage scoring, budget checks, tensor/admission reference utilities and materializer guards. Five families use free System 2 outputs; System 1 confidence is the sixth. Exact counts are in `task.json` and `data/manifest.json`. All split labels and canonical gold outputs are published.

Fit only on practice records. Development is for selection. Evaluation is available for inspection and independent verification, but fitting on its records, answer lookup, cached answers, arbitrary replacement of model outputs and evaluator tampering are prohibited by the published protocol. Scores measure performance on this public benchmark; they are not unbiased estimates of generalization to unseen tasks.

`python3 -m taskkit.cli audit` verifies data. `python3 -m unittest discover -s tests -v` runs CPU contracts. `scripts/stage_work.py` includes the evaluation assets and seed in Work. See [RUNBOOK.md](RUNBOOK.md) for reproduction and [INTEGRATION.md](INTEGRATION.md) for the remaining H100 adapter and measurement steps.

No model weights were downloaded and no model/GPU run occurred during this preparation. `public-authoring/reference_cache.json` contains null measurements, and assessment fails closed until real operator measurements exist. Those completed measurements will also be published. CPU oracle fixtures are not model scores.

The pinned starting release is [AutoTrust GEV-26B-Decide](https://huggingface.co/autotrust/GEV-26B-Decide/tree/7c89590ead085bf77630b4bf68264ea30b6ddc78). Contributor and source-license context are in [CONTRIBUTOR.md](CONTRIBUTOR.md) and [LICENSES.md](LICENSES.md).
The quantization protocol fixes CPU dequantization with the supplied arithmetic followed by ordinary BF16 backbone inference on H100. BQ and all candidates use this same path. The target is compressed artifact storage plus functional preservation, not native four-bit execution, lower GPU resident memory or speedup. Ephemeral reconstructed BF16 tensors are not extra delivered weights; all delivered model dependencies are counted once, and actual reconstruction time and memory remain charged. The ordinary model loader and runtime still need integration and measurement.
