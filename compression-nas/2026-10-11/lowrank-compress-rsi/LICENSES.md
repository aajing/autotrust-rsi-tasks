# Source and data licenses

This local package retains upstream attribution. It does not relicense model weights or source datasets.

- Primary SVD-LLM or NVIDIA Model Optimizer source: Apache-2.0, included `evidence/upstream/LICENSE`.
- Transformers source: Apache-2.0, included `evidence/licenses/transformers.LICENSE`.
- PyTorch source: BSD-style license, included `evidence/licenses/pytorch.LICENSE`.
- Mistral-7B-v0.1: Apache-2.0 according to its pinned official model metadata/card. Only small config/tokenizer metadata is included here; model weights remain at their public upstream revision.
- WikiText: source declares CC-BY-SA-3.0 and GFDL. The selected/tokenized text is derived from Salesforce WikiText and retains those attribution/share-alike obligations. Source and exact revision are in SOURCES.md; source parquet files and deterministic changes are documented in DATA.md.
- GSM8K: MIT, from OpenAI’s pinned public main configuration, with worked answers retained. Source and exact revision are in SOURCES.md.

Task-specific draft prose, selection scripts and CPU score arithmetic are newly authored for Jing Qiu’s proposal. No external-source coauthorship or right to remove source notices is claimed.
