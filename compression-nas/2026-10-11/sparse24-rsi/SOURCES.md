# Verified sources and attribution

Checked on 2026-10-10. Primary code was resolved once and all retained source reads use that immutable revision. These are repository facts and read-only metadata/CPU data checks, not reproduced GPU results.

## Selected primary project

- Repository: https://github.com/NVIDIA/Model-Optimizer
- Immutable commit: `4c1f813828cb9dd07b0d842d60ba35e3946237dc`
- License: Apache-2.0; actual source license is included as `evidence/upstream/LICENSE`.
- The pinned hf_pts.py uses AutoModelForCausalLM; weight_sparsity/module.py registers generic nn.Linear, and config.py excludes lm_head by default. Mistral native source contains only supported linear shapes in the declared set. This is source-grounded adaptation evidence, not a claim that NVIDIA tested this exact Mistral lane. The README verifies 1×A100/H100 80GB PTS for Llama2-7B (~44GB memory), whereas its full SAT example uses eight GPUs. This task selects PTS and bounded single-block recovery; it does not adopt or imply the eight-GPU SAT run.

## Actual public reference model

`mistralai/Mistral-7B-v0.1`, revision `27d67f1b5f57dc0953326b2601d68371d40ea8da`. Public API returned private=false and gated=false and Apache-2.0 metadata: https://huggingface.co/api/models/mistralai/Mistral-7B-v0.1/revision/27d67f1b5f57dc0953326b2601d68371d40ea8da. Model tree: https://huggingface.co/mistralai/Mistral-7B-v0.1/tree/27d67f1b5f57dc0953326b2601d68371d40ea8da. The release has 7,241,732,096 BF16 parameters and native Mistral configuration: 32 layers, hidden 4096, intermediate 14336, 32 attention heads, 8 KV heads, vocabulary 32000. Config/tokenizer were actually downloaded; weight shards were not. The baseline is this existing dense artifact, never a promised newly compressed checkpoint.

## Fixed native runtime evidence

- PyTorch 2.8.0 at `ba56102387ef21a3b04b357e5b183d48f0afefc7`: https://github.com/pytorch/pytorch/tree/ba56102387ef21a3b04b357e5b183d48f0afefc7; its source license is in `evidence/licenses/pytorch.LICENSE`.
- Transformers 5.7.0 at `6ffbb07f93d9e44457450d1150136309b0dc966b`: https://github.com/huggingface/transformers/tree/6ffbb07f93d9e44457450d1150136309b0dc966b; native Mistral model source and Apache license are retained. Trust-remote-code is disabled.
- PyTorch torch/sparse/semi_structured.py exposes SparseSemiStructuredTensorCUSPARSELT.from_dense; its BF16 weight dimensions must be positive multiples of 16, and its _mm calls torch._cslt_sparse_mm. _semi_structured_ops.py wires nn.functional.linear to that sparse path. The 4096×4096, 1024×4096, 14336×4096 and 4096×14336 Mistral projections satisfy those shape constraints. This establishes an existing accelerated operator interface, not measured whole-model speed. The current Model Optimizer pyproject requires torch>=2.8 and Transformers>=5.5,<5.19, so the chosen versions satisfy declared constraints. NVIDIA Model Optimizer masking alone still performs dense operations; task-owned packing into the PyTorch cuSPARSELt subclass is mandatory. No vLLM/LLM-Compressor 2:4 feature is assumed.

## Public datasets

- https://huggingface.co/datasets/Salesforce/wikitext/tree/b08601e04326c79dfdd32d625aee71d232d685c3/wikitext-2-raw-v1 — CC-BY-SA-3.0/GFDL; all three small parquet splits downloaded.
- https://huggingface.co/datasets/openai/gsm8k/tree/740312add88f781978c0658806c59bc2815b9866/main — MIT; train/test parquet splits downloaded.
- Exact selection/cardinality and distribution obligations are in DATA.md. All published targets may be used in bounded research; the benchmark makes no secret-test claim.

## Contributor evidence and attribution boundary

Jing Qiu supplied the professional name, work email ajing@autotrust.ai and GitHub account aajing. AutoTrust’s official organization page lists ajing linking to Hugging Face uremia; the existing September 30, 2026 JEV release article credits ajing/uremia. The organization describes compression and efficient inference research. This establishes related project context, not authorship of SVD-LLM, NVIDIA Model Optimizer, Mistral or the evaluation datasets. The full-name/account association is contributor-provided.

Existing public links: https://huggingface.co/autotrust ; https://huggingface.co/uremia ; https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned ; https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca . These support related model-development and organizational context. Do not invent external-project coauthorship or the contributor’s personal familiarity with every source file. Before official submission, the contributor’s selected domain-expertise route/codebase-familiarity attestation must be confirmed explicitly if it has not already been confirmed; this local scientific draft does not manufacture that metadata.

## Recent research context, non-blocking

The rolling window is 2026-04-10 through 2026-10-10. Debias-SparseGPT: Bias-Aware Pruning for Large Language Models (Irina Proskurina, Guillaume Metzler, Antoine Gourru, Julien Velcin), submitted 2026-09-02, studies calibration choices and structured 2:4 quality tradeoffs: https://arxiv.org/abs/2609.02496 . The paper does not by itself establish this task’s kernel speed or Mistral quality. Fixed native operator evidence is supplied separately above. Search was not exhaustive; X activity was not independently verified. Those limits are not scientific-contract or resource blockers.
