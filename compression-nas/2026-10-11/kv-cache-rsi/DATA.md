# Fixed public data contract

This is a disclosed-benchmark optimization task. Every selected input, answer, row ID, seed and scoring rule is public and unencrypted. Work may fit or select its allowed cache policy using all these records. Results do not establish unseen-data generalization.

## Sources and verified counts

Dataset: `zai-org/LongBench` (the former `THUDM/LongBench` URL redirects here), HF revision `5e628be450b7e67fb7ae6e201bd6d8f7056f7672`.

Archive: https://huggingface.co/datasets/zai-org/LongBench/resolve/5e628be450b7e67fb7ae6e201bd6d8f7056f7672/data.zip

The 113,932,529-byte archive was downloaded and its SHA256 verified as `cb45b11a4133c6bc1d6a44b0f8e701335ff1e543195db1103472e575857f7f64`. The public delivery package contains the manifest and `materialize_data.py`, and excludes the raw archive and six selected JSONL files. Existing local copies remain in `data/`. Run `python materialize_data.py` during setup to reconstruct the identical plaintext inputs and gold directly from the pinned public source; `--archive /path/to/data.zip` supports an existing download, and `--cache /path/to/cache` selects the download cache. All six selected-file hashes are checked before writing.

| Family | Source rows counted from exact archive | Selected | Metric |
| --- | ---: | ---: | --- |
| qasper | 200 | 32 | Pinned KIVI `qa_f1_score`, best gold |
| hotpotqa | 200 | 32 | Pinned KIVI `qa_f1_score`, best gold |
| musique | 200 | 32 | Pinned KIVI `qa_f1_score`, best gold |
| gov_report | 200 | 32 | Pinned KIVI `rouge_score`, best gold |
| passage_count | 200 | 32 | Pinned KIVI `count_score`, best gold |
| passage_retrieval_en | 200 | 32 | Pinned KIVI `retrieval_score`, best gold |
| Total | 1,200 | 192 | Equal mean of six family scores |

For each family independently, compute `SHA256(UTF8(family + "\0" + original_record["_id"]))`, sort ascending, and take the first 32. Original source IDs were unique within each family. No length, answer, duplicate-text or performance exclusion applies. `data-manifest.json` lists every selected ID, the raw source-entry SHA256 and the selected-file SHA256. No fallback cohort or replacement sample is permitted. A failed source checksum or malformed source prevents setup; it does not shrink evaluation.

## Prompt and context boundary

Use the exact family prompt from pinned KIVI `config/dataset2prompt.json`, fill original `input` and `context`, apply one pinned Mistral user chat template, and tokenize. Preserve the resulting integer IDs, not a decode-and-reencode roundtrip. If needed, retain the first floor(L/2) and last ceil(L/2) IDs, where `L=32768-max_new_tokens`. This explicit task adapter fixes upstream behavior that could add chat-template tokens after truncation.

Generation caps: qasper/hotpotqa/musique 128; gov_report 512; passage_count/passage_retrieval_en 32. Greedy, one beam, seed 42, no sampling, source EOS only. Identical IDs and caps for B0 and every candidate. Thus input plus generation can never exceed Mistral's 32,768 positions. Do not pad quality records into synthetic long contexts.

The six performance cells are separate, fully specified synthetic traces: lengths 8,192 / 16,384 / 32,256 crossed with batches 1 / 4, then exactly 128 forced continuation tokens. The context of the first selected gov_report row is tokenized without a chat wrapper and cycled to the required length. Batch member j starts at offset 257*j modulo that source token stream. Continue the same stream for the forced 128 tokens. No random generator or remote data is needed. Maximum trace length is 32,384 including decode.

## Labels, fitting and runtime separation

Gold data may be inspected and used during offline policy fitting. The deployed cache callback receives tensors and positions only. It cannot access raw text, source IDs, hashes, paths, gold files or previous requests. No answer table or ID-specific cache policy is allowed. Parameters conditioned on the fixed public benchmark are allowed within the cache/tensor form. This boundary limits the runtime artifact, not the researcher's knowledge of the benchmark.

## Access and rights

The dataset archive is public and ungated. Its HF card does not declare a single dataset-wide license; the KIVI MIT code license is not asserted to license LongBench text. The selected records retain their source dataset fields, and users should retain the original LongBench/source-dataset attribution and applicable underlying terms. This package makes no blanket permissive-license claim for aggregated text. SOURCE-NOTICES.md records verified CC BY 4.0 / CC BY-SA 4.0 upstream declarations and unresolved per-article provenance for synthetic Wikipedia passages. Public packaging uses source fetching instead of republishing raw text. This changes delivery only; all inputs and answers remain public, unencrypted and usable by the same fixed task.

## Mandatory quality-request cache audit

All192real quality requests are included in the primary cache objective, not just synthetic performance traces. For each exact manifest family/ID, record task-owned prompt token count P and generated token count G (including EOS), with1<=G<=thefamilycap. Standard autoregressive generation has a prefill and max(G-1,0) subsequent decoder forwards; record G cache samples after those operations. At decode update j=0..G-1, dense reference KV payload bytes are131072*(P+j), using32layers,8KVheads,128dimensions,2(K/V) and2FP16bytes. Count all candidate persistent storage/metadata/shadows in the numerator. Report the maximum ratio for eachrequest; R takes the maximum over these192ratios and the sixperformance-cell ratios. The scorer requires every exact selectedID, family counts, P+G<=32768, decode_updates=G-1 and sample_count=G. Raw samples are public and task-owned instrumentation computes summaries. Emptydecodedtext still has at least one generatedtoken (for example EOS); a missing generation process is incomplete/unscored. This removes the loophole of retaining full caches on real questions while compressing only recognizable synthetic timing inputs.
