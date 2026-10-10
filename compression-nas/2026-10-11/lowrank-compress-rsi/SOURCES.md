# Verified sources and attribution

Checked on 2026-10-10. Primary code was resolved once and all retained source reads use that immutable revision. These are repository facts and read-only metadata/CPU data checks, not reproduced GPU results.

## Selected primary project

- Repository: https://github.com/AIoT-MLSys-Lab/SVD-LLM
- Immutable commit: `7538cca98880ff312a79a16252aab5a7b480fbe9`
- License: Apache-2.0; actual source license is included as `evidence/upstream/LICENSE`.
- SVDLLM.py explicitly selects Mistral attention/MLP factor modules; utils/model_utils.py explicitly handles mistral. profle_svdllm_low_resource and whitening_local_update supply the one-layer-at-a-time numerical mechanism. The CLI inverts its ratio, while this task declares explicit ranks. Source serialization uses pickle; the fixed Judge instead accepts only safetensors and its own factor wrapper.

## Actual public reference model

`mistralai/Mistral-7B-v0.1`, revision `27d67f1b5f57dc0953326b2601d68371d40ea8da`. Public API returned private=false and gated=false and Apache-2.0 metadata: https://huggingface.co/api/models/mistralai/Mistral-7B-v0.1/revision/27d67f1b5f57dc0953326b2601d68371d40ea8da. Model tree: https://huggingface.co/mistralai/Mistral-7B-v0.1/tree/27d67f1b5f57dc0953326b2601d68371d40ea8da. The release has 7,241,732,096 BF16 parameters and native Mistral configuration: 32 layers, hidden 4096, intermediate 14336, 32 attention heads, 8 KV heads, vocabulary 32000. Config/tokenizer were actually downloaded; weight shards were not. The baseline is this existing dense artifact, never a promised newly compressed checkpoint.

## Fixed native runtime evidence

- PyTorch 2.8.0 at `ba56102387ef21a3b04b357e5b183d48f0afefc7`: https://github.com/pytorch/pytorch/tree/ba56102387ef21a3b04b357e5b183d48f0afefc7; its source license is in `evidence/licenses/pytorch.LICENSE`.
- Transformers 5.7.0 at `6ffbb07f93d9e44457450d1150136309b0dc966b`: https://github.com/huggingface/transformers/tree/6ffbb07f93d9e44457450d1150136309b0dc966b; native Mistral model source and Apache license are retained. Trust-remote-code is disabled.
- Source numerical SVD/whitening routines are adapted to this fixed native graph; an exact source CLI run under its older Transformers pin is not falsely claimed. Rank-specific two-linear wrappers preserve all native Mistral attention/GQA/RoPE semantics.

## Public datasets

- https://huggingface.co/datasets/Salesforce/wikitext/tree/b08601e04326c79dfdd32d625aee71d232d685c3/wikitext-2-raw-v1 — CC-BY-SA-3.0/GFDL; all three small parquet splits downloaded.
- https://huggingface.co/datasets/openai/gsm8k/tree/740312add88f781978c0658806c59bc2815b9866/main — MIT; train/test parquet splits downloaded.
- Exact selection/cardinality and distribution obligations are in DATA.md. All published targets may be used in bounded research; the benchmark makes no secret-test claim.

## Contributor evidence and attribution boundary

Jing Qiu supplied the professional name, work email ajing@autotrust.ai and GitHub account aajing. AutoTrust’s official organization page lists ajing linking to Hugging Face uremia; the existing September 30, 2026 JEV release article credits ajing/uremia. The organization describes compression and efficient inference research. This establishes related project context, not authorship of SVD-LLM, NVIDIA Model Optimizer, Mistral or the evaluation datasets. The full-name/account association is contributor-provided.

Existing public links: https://huggingface.co/autotrust ; https://huggingface.co/uremia ; https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned ; https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca . These support related model-development and organizational context. Do not invent external-project coauthorship or the contributor’s personal familiarity with every source file. Before official submission, the contributor’s selected domain-expertise route/codebase-familiarity attestation must be confirmed explicitly if it has not already been confirmed; this local scientific draft does not manufacture that metadata.

## Recent research context, non-blocking

The rolling window is 2026-04-10 through 2026-10-10. UniRank: Unified Rank Allocation for Low-Rank LLM Compression (Chao Han, Yongjie Du, Junjie Tan, Zihao Xuan), submitted 2026-06-20, directly studies global rank allocation and bounded recovery: https://arxiv.org/abs/2606.21847 . LASER (Haiyu Wang et al.), submitted 2026-05-30, studies loss-aware decomposition/rank allocation in vision-language models: https://arxiv.org/abs/2606.00573 . The latter is adjacent VLM evidence, not a claim that this text-model task tests vision. Search was not exhaustive; X activity was not independently verified. Those limits are not scientific-contract or resource blockers.
