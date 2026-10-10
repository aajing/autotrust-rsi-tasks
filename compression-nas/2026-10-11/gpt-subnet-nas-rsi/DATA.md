# Public text and actual-workload contract

All text is public, including every next-token target and timing input. Work may fit on evaluated data. The claim is optimization of a fixed disclosed benchmark; no unseen-generalization claim is made.

## Fixed assets and cardinality evidence

| Asset | Immutable source | Actual cardinality evidence | Judge selection |
| --- | --- | --- | --- |
| WikiText-2-raw-v1 | Salesforce/wikitext at b08601e04326c79dfdd32d625aee71d232d685c3 | Pinned dataset card lists train 36,718 / validation 3,760 / test 4,358 physical rows | All4,358 test rows, physical order, including empty strings |
| TinyStories-valid.txt | roneneldan/TinyStories at f54c09fd23315a6f9c86f9dc80f725de7d8f9c64 | Complete19,447,282-byte text file was read and counted:21,990 nonempty documents | First2,048 nonempty `<|endoftext|>`-delimited documents in physical order |
| GPT2 tokenizer | openai-community/gpt2 at 607a30d783dfa663caf39e06633721c8d4cfcd7e | Native upstream datamodule adds `<pad>` and rounds vocabulary to a multiple of 128 | Same tokenizer for every candidate |

TinyStories complete file SHA256 is `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`; evidence/tiny-cardinality.json records this actual inspection. The WikiText cardinality is authoritative pinned metadata, not a locally repeated Parquet count; setup verifies all 4,358 rows rather than silently accepting a mismatch. No selected data-file names or counts depend on candidate performance.

Work data access is exactly the three WikiText-2-raw-v1 splits and the complete TinyStories-valid.txt file. No WikiText-103, TinyStories train/V2/all-data archives, external text, external pretrained teacher or task-specific answers beyond these sources are required or permitted. All counts refer to source items, not invented token counts. The exact token count is deterministic after setup tokenization and is included in the public data manifest; it is not a contributor-owned unresolved choice.

## Deterministic conversion

1. WikiText: preserve every raw text value in physical order, including blank strings. TinyStories: split on the literal `<|endoftext|>`, trim surrounding whitespace, discard only empty resulting segments, and take the first 2,048. Do not otherwise normalize case, whitespace or punctuation.
2. Encode each item without automatic special tokens, then append EOS 50256. Append an EOS also after an empty WikiText item. Concatenate separately by domain.
3. Native GPT2 adds pad token 50257; padded output vocabulary is 50304 as the source datamodule derives. Preserve all native logits, including padded vocabulary rows in softmax normalization; padding positions in a final short batch are masked, not scored. No undocumented vocabulary cropping.
4. For each L in256,512,1024, partition each domain stream into consecutive nonoverlapping windows of at mostL tokens. Predict positions1..length-1 from positions0..length-2. Include the last window if it has at least2 tokens; ignore a terminal singleton. These boundary omissions are deterministic and disclosed. Six domain/context NLL cells result; each averages all scored token losses, not document means. Use FP32 log-softmax and FP64 aggregation. No training occurs in Judge.
5. Timing workloads are batch/sequence pairs(1,128),(4,512),(8,1024). Construct input IDs by cycling through the concatenated evaluation streams in WikiText then TinyStories order, taking distinct consecutive windows. Fix seed20261010 for setup only. Inputs and target streams are saved openly. Compute the complete vocabulary logits, do not measure a stub or cached-output call.

## Exact quality and performance rules

Every one of the six mean-NLL values must be no more than B0+0.08 natural-log nats/token. Each measured timing ratio must be<=1.05; maximum allocated GPU memory, across quality and timing, must be<=1.05B0. Quality cells are domain-family gates; good TinyStories results cannot compensate for lost WikiText quality, and short-context gains cannot compensate for 1024-token loss.

Each timing workload receives five predetermined rounds of25 warmup and100 timed forwards. Synchronize GPU before and after a timed full forward; keep no output cache. Take each round's median wall time and then the median of five medians; form the geometric mean of the three candidate/B0 ratios. Memory includes weights, runtime workspace and materialized logits. Operator backend, precision, compilation mode, clocks and power policy remain the same as frozen B0. Discretionary repeats or best-of measurements are prohibited.

Full score requires geometric-mean latency <=60%B0 and canonical tensor storage <=70%B0, with all gates. This is an aspirational task target and has not been validated on H100. The structural space includes much smaller models, but that does not establish retention of language quality; this is the research question.

## Work budget and outcomes

At most 10,000,000 non-padding training-input token exposures and60 Work wall minutes per candidate, whichever is first. Every repeated token/teacher pass counts. Weights may be inherited with zero recovery training, but all exported tensors must come from the allowed source and bounded updates. Full Judge cap30min, mandatory overhead15min. Default trajectory24h, extension48h. A fixed artifact gets at most one infrastructure retry, counting all wall time, with no candidate-failure retry or data resampling. Invalid, crashed, timed-out, non-finite or incomplete executions are unscored. Only a valid fully evaluated candidate can receive numeric zero for scientific gate failure.

## Frozen report binding

Every trusted complete report carries data_manifest_sha256 and runtime_fingerprint, each a 64-character lowercase SHA256. Data binding covers the exact materialized evaluation inputs, targets, selection and tokenization manifest; runtime binding covers the fixed source, tokenizer, evaluator/operator configuration, precision and H100 environment. Candidate and frozen B0 bindings must match exactly. Missing/malformed/different bindings make the result unscored. valid_artifact and structural integrity flags must be literal JSON true, never truthy strings. These fields are produced by the trusted runtime, not accepted from candidate claims.
