# Source and access ledger

Checked 2026-10-10; source code was inspected as text, not remotely executed.

| Asset | Immutable revision or existing delivery | Verified evidence | License/provenance |
| --- | --- | --- | --- |
| Official HW-GPT-Bench source | https://github.com/automl/HW-GPT-Bench/tree/1f43ee8322e6295d56c1e2004319123509fd53b8 | GitHub commit API resolved main once; all saved source reads use thatSHA | Apache-2.0; LICENSE copied into evidence/ |
| Existing GPT-S checkpoint | README-linked https://drive.google.com/drive/folders/1uUxO05Hx-T_KOiTkA3zT_iuaeK6HdxM0?usp=sharing ; file https://drive.google.com/file/d/1N7CMOktSBulsfCmVpLMYlbFNeOYn_JLU/view | Anonymous directory HTML actually lists gpt_s.ckpt and1,484,460,504 bytes | Published by source project with its release; separate checkpoint license document was not inspected, so do not invent one |
| Native model loader | pl_gpt/pl_module/lm_evaluator_configurable.py and hwgpt/model/gpt/model.py at source SHA | Both read and archived | Native checkpoint['state_dict'] strict-load path, source subnet sampler |
| Native data/tokenizer semantics | pl_gpt/data/lm_datamodule_nas.py at source SHA | Read and archived; GPT2+added pad, vocabulary ceil(/128)*128 | Preserve50304 padded logits; not stale YAML50254 |
| Native source configs | configs/config_eval/owt_s_eval.yaml; configs/config_train/owt_s.yaml | Both read at same SHA | Width192/384/768, depth10/11/12, head4/8/12, MLP2/3/4; source RoPE0.5 |
| GPT2 tokenizer only | https://huggingface.co/openai-community/gpt2/tree/607a30d783dfa663caf39e06633721c8d4cfcd7e | Public ungated model API and file listing; use tokenizer.json/vocab.json/merges.txt/tokenizer_config.json | Card MIT; do not import GPT2 model weights |
| WikiText | https://huggingface.co/datasets/Salesforce/wikitext/tree/b08601e04326c79dfdd32d625aee71d232d685c3 | Pinned card read; raw-v1 test 4,358 physical rows, validation 3,760, train 36,718 | Metadata lists CC-BY-SA3.0 andGFDL; preserve notices/attribution. Card narrative also linksCC-BY-SA4.0; record this upstream inconsistency rather than relabel files |
| TinyStories | https://huggingface.co/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64 | Pinned card and whole TinyStories-valid.txt read; actual 21,990 nonempty stories | CDLA-Sharing1.0; preserve source notice and provenance |
| Whittle context only | https://github.com/whittle-org/whittle | Public library documents NAS and actual subnet checkpoint export | Apache-2.0; not a required runtime, and current checkpoint compatibility not claimed |

## Checkpoint verification limit

The Drive file is an existing delivery interface from the official README, not a promise of a future uploaded baseline. Full1.48GB checkpoint bytes were not downloaded. Consequently task.json deliberately has `sha256:null` and `full_payload_verified:false`; these are transparent artifact-verification fields, not missing research/reward decisions. During setup, Task Agent downloads that exact file, records its SHA256, verifies native load and freezes it before research. If it is unavailable or loading/parity fails, stop construction; do not replace it with a newly trained baseline or a surrogate.

No table lookup or pretrained proxy is a final evaluator. The source API exposes surrogate metrics, but this task requires actual neural forward passes and materialized tensors.

## Expertise and current relevance

EXPERTISE.md links contributor-associated AutoTrust model-development evidence and describes its limits; no claim of authorship of HW-GPT-Bench is made. The upstream HW-GPT-Bench paper/release is 2024, not evidence of a new paper in the rolling 2026-04-10 through2026-10-10 window. Current source/Whittle availability supports implementability; a comprehensive recent-paper frontier review was not completed and is non-blocking. The proposal is useful independently of a novelty claim about NAS itself.
