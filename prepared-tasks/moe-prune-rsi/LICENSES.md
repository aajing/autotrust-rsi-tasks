# Source licensing and attribution

The new task code, procedural data, PNG renderer outputs, seeds, gold answers and evaluation specification are intended for the public `aajing/autotrust-rsi-tasks` repository under the license selected for that repository. This package does not silently relicense third-party weights or code.

The pinned [GEV model card](https://huggingface.co/autotrust/GEV-26B-Decide/blob/7c89590ead085bf77630b4bf68264ea30b6ddc78/README.md) declares Apache-2.0 metadata. It incorporates the Gemma-4 backbone; the operator must acquire and retain the actual applicable backbone/model/adapter license files when obtaining weights. This statement records the source declaration rather than guaranteeing that one card label resolves all inherited terms.

The pinned [GLM Flash GGUF card](https://huggingface.co/autotrust/GLM-5.3-Flash-GGUF-DGX-Spark/blob/989cc0291ce3d3182e23e995c11fbbae6f473c9a/README.md) identifies an MIT base-model lineage. Its measurements and method description are cited as precedent; GLM weights and code are not bundled or required.

Only the GEV config and model-index JSON were downloaded. Their exact URLs, revision and hashes are in `source/metadata-receipts.json`. Full model weights, third-party training data and GPU runtime distributions are not included. NumPy remains subject to its upstream license. Future runtime packaging must preserve licenses/notices for every acquired dependency.

All benchmark answers and seeds are intentionally public, inspectable and unencrypted. Public availability does not authorize using evaluation labels for fitting or substituting answer lookup for model inference under the benchmark protocol.

