# Source evidence and immutable revisions

Checked 2026-10-10 using public HTTPS metadata and raw files. These are proposal-stage source checks, not GPU execution results. No upstream code was executed. Primary sources below are authoritative; local evidence copies support review.

| Asset | Immutable revision / digest | License and access | Evidence checked |
| --- | --- | --- | --- |
| KIVI | `876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6` | MIT; public GitHub | README, LICENSE, docs/long_bench.md, pred_long_bench.py, eval_long_bench.py, metrics.py, models/mistral_kivi.py, quant/new_pack.py, quant/matmul.py, quant/setup.py, config/dataset2prompt.json, config/dataset2maxlen.json |
| Mistral-7B-Instruct-v0.2 | HF `63a8b081895390a26e140280378bc85ec8bce07a` | Apache-2.0; HF API `gated=false` | Public model API metadata, config.json; 32 layers,8KV heads,128head dimension,32768positions,BF16 source dtype |
| LongBench | HF `5e628be450b7e67fb7ae6e201bd6d8f7056f7672` | Public ungated archive; no single license declared by dataset card | Original API/tree metadata, complete archive SHA256, parsed source cardinality and deterministic selected-file hashes; source materializer supplied |
| LongBench code/context | Git `2e00731f8d0bff23dc4325161044d0ed8af94c1e` | Public GitHub; evaluator used by this task is pinned KIVI copy | Repository metadata and public dataset-card task descriptions |
| Contributor evidence | Existing AutoTrust sources linked below | Public attribution; account/full-name association contributor supplied | Prior 2026-10-10 evidence audit in existing approved task repository, plus public source URLs |

Direct source links:

- https://github.com/jy-yuan/KIVI/tree/876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6
- https://github.com/jy-yuan/KIVI/blob/876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6/pred_long_bench.py
- https://github.com/jy-yuan/KIVI/blob/876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6/docs/long_bench.md
- https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/tree/63a8b081895390a26e140280378bc85ec8bce07a
- https://huggingface.co/datasets/zai-org/LongBench/tree/5e628be450b7e67fb7ae6e201bd6d8f7056f7672
- https://huggingface.co/autotrust
- https://huggingface.co/uremia
- https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned

## What the source does establish

KIVI supplies real packed-cache CUDA/Triton code and a Mistral branch. Its LongBench documentation names Mistral-7B-Instruct-v0.2. `pred_long_bench.py` explicitly sets FP16 and chooses a native full-cache branch when k_bits=v_bits=16. This task therefore uses a matched FP16 runtime cast of the already released BF16 source artifact. No BF16 support for the custom KIVI kernels is assumed.

The source is research starting material. This proposal specifies stronger cache retention/action boundaries and a fixed six-family evaluation overlay. It does not say an unchanged KIVI command already implements that overlay or achieves full marks.

## Limits and rights provenance

No H100 build, model load, baseline score, latency, memory, variance or end-to-end loop time was measured. GPU acceptance remains Task-Agent execution validation, not a requirement claimed already met by this proposal package.

LongBench combines underlying text datasets and its current HF card lacks a single dataset-wide license declaration. Public downloadability is verified; a blanket MIT/Apache license for its text is not. Preserve the source `dataset` metadata and original attribution/underlying terms when distributing examples. KIVI's MIT license applies to code. SOURCE-NOTICES.md supplies underlying-source license declarations and the public manifest-plus-fetch delivery policy. This is an explicit rights-provenance limitation, not a hidden access dependency.

The source-review record does not establish Jing Qiu as an author of KIVI or LongBench. EXPERTISE.md provides the actual AutoTrust organization/member/release evidence chain instead.

## Files intentionally not materialized

Model weight shards were not downloaded. The exact public model snapshot is the existing delivery interface. The full 113,932,529-byte data archive was previously verified; local selected full text/gold files are retained. The public package excludes the archive and those raw records, and supplies `materialize_data.py` plus exact IDs and source/output hashes to reconstruct all 192 records from the existing upstream delivery. `python materialize_data.py --verify-only` validates the full reconstruction; the default command writes the plaintext cohort. No credential, encrypted asset, hidden gold set or private download service is required.
