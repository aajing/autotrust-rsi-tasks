# Source notices and public data delivery

Checked 2026-10-11. This file records published source statements; it does not grant new rights or claim a single permissive license for all LongBench text.

The public proposal package distributes the fixed selection manifest, hashes, code and this notice. It does not republish the six raw LongBench JSONL files or the source ZIP. `materialize_data.py` downloads the existing public pinned archive directly from its source during setup and reconstructs all 192 records, including answers, as plaintext. The original local preparation files remain available locally. This is an upstream-delivery choice, not hidden evaluation, encryption, removal of answers or a changed cohort.

## Source declarations

| Selected family | Primary source and published terms | Attribution/provenance |
| --- | --- | --- |
| qasper | https://huggingface.co/datasets/allenai/qasper — CC BY 4.0 | Dasigi et al., *A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers* (2021). The card identifies S2ORC as its full-text source; do not claim separate ownership of the underlying papers. |
| hotpotqa | https://hotpotqa.github.io/ — CC BY-SA 4.0 | Yang, Qi, Zhang et al., *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering* (2018). The project also publishes its processed Wikipedia under CC BY-SA 4.0. |
| musique | https://github.com/StonyBrookNLP/musique — CC BY 4.0 | Trivedi et al., *MuSiQue: Multi-hop Questions via Single-hop Question Composition*, TACL (2022). Preserve its source and citation. |
| gov_report | https://gov-report-data.github.io/ — CC BY 4.0 | Huang et al., *Efficient Attentions for Long Document Summarization*, NAACL (2021). The project identifies Congressional Research Service and U.S. Government Accountability Office reports as sources. |
| passage_count; passage_retrieval_en | LongBench's pinned construction documentation identifies English Wikipedia as the passage source | These selected records have dataset labels and random LongBench IDs, but no original article URLs or revision mapping. Per-passage attribution provenance is not established by the selected JSONL files. Do not invent a mapping or claim the repository MIT license covers the text. |

Creative Commons terms: https://creativecommons.org/licenses/by/4.0/ and https://creativecommons.org/licenses/by-sa/4.0/ . Attribution, license notices and change identification remain applicable; ShareAlike applies where required by the source license. Wikimedia reuse terms: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content . This notice does not substitute for source-specific terms.

## LongBench and software

The exact benchmark source is `zai-org/LongBench` at HF revision `5e628be450b7e67fb7ae6e201bd6d8f7056f7672`. Its checked HF card does not state one dataset-wide license. The separate software repository has an MIT license; that software notice is not treated as a blanket grant for incorporated third-party text.

- Pinned construction and underlying-source descriptions: https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/LongBench/task.md
- Pinned citation and original-dataset acknowledgement: https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/LongBench/README.md
- Software license: https://github.com/THUDM/LongBench/blob/2e00731f8d0bff23dc4325161044d0ed8af94c1e/LICENSE
- LongBench citation: Bai et al., *LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding*, ACL (2024), https://aclanthology.org/2024.acl-long.172/ .

KIVI code separately retains the MIT license in `evidence/upstream/LICENSE`. Mistral model artifacts retain their Apache-2.0 terms. Neither licenses LongBench text. Preserve the original dataset labels and these attribution links after materialization; any later redistribution of raw text must address the applicable underlying terms and missing article-level provenance rather than relying on this package's software license.

## Exact reconstruction

Run `python materialize_data.py` during setup, or `python materialize_data.py --archive /path/to/data.zip` for a previously obtained source archive. `--cache /path/to/cache` selects the verified download cache; `--output /path/to/data` selects the plaintext destination; `--verify-only` checks all reconstructed bytes without writing selected records.

The script verifies archive size/SHA256, each named ZIP member hash, all six 200-row source cardinalities and unique IDs, the independent hash ordering of the first 32 records, and every selected-file SHA256. It reads only the six explicit ZIP members without extracting archive paths or executing source code. All six outputs are validated before atomic per-file writes. No failed or missing record is replaced or dropped. Source access is setup-only; subsequent Work/Judge runs stay offline.
