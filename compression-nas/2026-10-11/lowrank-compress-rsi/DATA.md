# Data and public benchmark contract

All files under `data/` are materialized locally, public in the intended package, and unencrypted. The exact manifest SHA256 is `e1d4c6a289600f9597e71c6dfd9d75c1b366518bd50487397abe4d2322bddd11`. No answer is withheld. Fitting on the disclosed evaluation examples is allowed within the fixed artifact, time and exposure budgets; results describe benchmark-conditioned compression, not unseen-task generalization.

## Immutable sources and actual eligibility

- WikiText-2 raw-v1: `Salesforce/wikitext` at `b08601e04326c79dfdd32d625aee71d232d685c3`; source parquet rows: 36,718 train / 3,760 validation / 4,358 test. Text is joined in source row order with two newlines and tokenized using the pinned Mistral tokenizer with special-token injection disabled. Actual token counts: 2,811,494 / 292,994 / 334,660. Nonoverlapping complete 512-token blocks are exact-hash deduplicated with test, validation, train priority. Eligible distinct blocks: 5,491 practice / 572 development / 653 evaluation. Thus the selected 256 / 64 / 128 exist without replacement.
- GSM8K main: `openai/gsm8k` at `740312add88f781978c0658806c59bc2815b9866`; 7,473 train / 1,319 test rows. Two shortest complete train question+rationale examples (token-length then canonical-question-hash ordering) form a fixed two-shot prompt and are excluded. Normalize question whitespace for exact deduplication, process test before train, and reject prompts over 2,048 tokens. Actual eligible counts are 7,471 train and 1,319 test; select 512 practice plus 64 development from train, and 256 evaluation from test.

Every selection is ordered by SHA256 of canonical JSON `[seed, split_role, record_id]`, with the exact implementation in `prepare_data.py` and seed `compression-nas-2026-10-10-v1`. The source revisions are fixed; no live dataset viewer or moving branch is used for selection. There are no few-shot/evaluation duplicates after the stated exact-key exclusions. This is exact duplicate control, not an assertion that all semantic paraphrases were detected.

## Scoring inputs and answers

WikiText records contain `[BOS=1]` followed by 512 corpus tokens. Predict the 512 subsequent tokens; aggregate total negative log-likelihood divided by exactly 65,536 evaluation targets, then optionally report perplexity as exp(mean NLL). Input tokens themselves contain all public targets. GSM8K records contain complete prompts, source questions, original worked solutions and normalized final numeric answers. Greedy generation allows 256 new tokens, stops at EOS, and parses the last `#### <number>` marker using decimal normalization; malformed/missing/truncated answers are wrong. No evaluator retries an answer.

Six timing buckets use batch 1/4 and sequence length 512/1024/2048. Each holds two batches of public token sequences assembled from fixed evaluation blocks, with no padding. One complete timing pass handles 35,840 input tokens. Two warmup passes plus five measured passes use 250,880 tokens per full timing sweep; these fixed Judge passes are included in the Judge wall limit. Every forward computes full vocabulary logits with no KV cache, speculative decoding, CUDA graphs or compilation.

## Reproduction and licensing

`prepare_data.py` uses pyarrow 25.0.1 and tokenizers 0.22.2, performs only CPU tokenization/data preparation, and reads the saved public parquet/tokenizer evidence. It imports no model or torch. `evidence/download-receipts.json` records actual downloaded bytes/hashes; `evidence/cardinality.json` records actual eligibility. All selected data is already included. WikiText retains its source CC-BY-SA-3.0/GFDL attribution and share-alike terms; GSM8K is MIT. See SOURCES.md and LICENSES.md. No GPU measurements or model weights were downloaded.
