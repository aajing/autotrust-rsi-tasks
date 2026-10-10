# Fixed public multimodal data contract

All 320 selected questions, instructions, answers, bounding boxes, source row IDs and selection rules are public in `data/` and `data-manifest.json`. No split is claimed hidden or reserved from fitting. This is fixed public-benchmark optimization, with all disclosed records available for calibration and candidate selection.

| Family | Exact source count, parsed locally | Selected |
| --- | ---: | ---: |
| ChartQA human test | 1,250 | 64 |
| ChartQA augmented test | 1,250 | 64 |
| ScreenSpot-v2 desktop | 334 | 64 |
| ScreenSpot-v2 mobile | 501 | 64 |
| ScreenSpot-v2 web | 437 | 64 |
| Total | 3,772 | 320 |

## Immutable sources and selection

ChartQA source repository: https://github.com/vis-nlp/ChartQA/tree/044eabfc306abfe9340c5741f0093aefc5973d06 . Read `ChartQA Dataset/test/test_human.json` and `test_augmented.json`, each as its original JSON array. Original annotations are preserved in `evidence/chartqa-test-*.json`. Source images are `ChartQA Dataset/test/png/<imgname>` from the same commit.

ScreenSpot-v2 source dataset: https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2/tree/5efbb1f1b5463a575f2eb7bc30fe29e49c15f93c . Original annotations are `screenspot_desktop_v2.json`, `screenspot_mobile_v2.json`, `screenspot_web_v2.json`; checked copies are in `evidence/`.

For each of the five families independently, zero-index the original array. Compute `SHA256(UTF8(family + "\0" + str(source_index)))`, sort ascending and select the first 64. There are no length, question, image-duplicate, model-success or annotation-type exclusions. Repeated source images remain separate question instances and contribute separately. `data-manifest.json` stores the resulting exact IDs; no data are silently replaced on download failure.

`data/chartqa-selected.json` includes each question and gold, exact public image URL and source Git blob SHA1. All 124 unique ChartQA images for the 128 selected questions are already bundled in `data/chartqa-images/` (5,663,330 total bytes). Each was checked against the source Git blob object hash; SHA256 values are in `data/chartqa-image-hashes.json`.

`data/screenspot-selected.json` contains all 192 selected instructions and original-pixel `xywh` bounding boxes. The image archive is **not bundled**:

https://huggingface.co/datasets/OS-Copilot/ScreenSpot-v2/resolve/5efbb1f1b5463a575f2eb7bc30fe29e49c15f93c/screenspotv2_image.zip

Exact size: 1,331,012,233 bytes. SHA256: `750555b8b06e3898634c610cd904600feb7ec7ca530e625a00c1416a73d829ee`. These values were verified from the pinned HF tree/LFS metadata, not by downloading the archive. `prepare_images.py` downloads it with normal TLS validation, verifies the complete SHA256, and extracts only selected filenames. It rejects duplicate basenames or absent files. No access token, account, encryption or future upload is needed. Failure prevents setup; it does not drop examples.

## Fixed inputs and scoring

Use the Qwen processor/tokenizer from HF model revision `cc594898137f460bfe9f0759e9844b3ce807cfb5`. `min_pixels=200704`, `max_pixels=1003520` (256 to 1,280 visual tokens). The original full image is passed once; the same processor resize applies to B0 and candidates. Cropping, changed pixel budgets, image omission and alternate OCR preprocessing are forbidden. Preserve the original image width/height for point scoring.

Chart prompt: `Answer the question using the chart. Reply with only the answer.\nQuestion: {query}`. Correct if trimmed casefolded strings exactly match, or both parse as numbers and relative error is at most 5%; gold zero instead requires absolute error <=1e-6. Remove numeric grouping commas; a trailing percent divides by 100 on either side. No semantic or LLM judge. Native gold is a string; if an upstream record supplies multiple gold strings, take the maximum without selecting gold based on the candidate.

GUI prompt: `Locate the interface element for this instruction: {instruction}\nReturn only a JSON array [x, y] giving the center point in integer coordinates from 0 to 1000, relative to the original full image.` Parse exactly one two-integer JSON array, both values in [0,1000]. Divide predicted coordinates by 1,000, normalize the source xywh box by original width/height, and accept an inclusive point-in-box hit. Invalid or empty completed output scores 0. Coordinates are predictions; the model never receives gold boxes.

Quality: seed42, temperature0, greedy max64 new tokens, standard EOS, no retries or best-of sampling. The five family scores are percentages and equally weighted. All 64 rows per family must be present. Timeout/crash means unscored incomplete run, not a dropped row.

Performance: first eight selected rows per family, interleaved by within-family selection rank and family order from task.json. Forty requests per pass; batch1 and batch8; two warmups and five timed passes per batch. Force exactly64 continuation tokens formed by repeating the tokenizer encoding of `Measurement continuation.` and truncating to64 tokens. This task-owned path uses the same native model layers and actual quantized kernels; no candidate can select continuation or bypass work. Include image processing, vision encoding, text prefill and decode in wall time; exclude only one-time model loading/compilation, which is charged elsewhere in the budget.

## Access and licenses

ChartQA repository includes GPL-3.0 LICENSE (copied in evidence/chartqa/LICENSE); retain its source/attribution and applicable image-source rights. HF ChartQA mirror also declares GPL-3.0. ScreenSpot-v2 HF card declares Apache-2.0, publicly and without gating; preserve that card and source attribution. Neither model performance nor source cardinality is inferred from these licenses. This package claims only the checked downloads and counts described above.

## No cross-request multimodal cache shortcuts

Set mm_processor_cache_gb=0 and limit_mm_per_prompt={"image":1}. Prefix-cache disabling alone does not disable image caches. For everyquality/performance request, including allwarmup and timed repeats, the task-owned runner assigns a globally unique multi_modal_uuids image identifier (phase/cell/repeat/request sequence); this affects cache identity only, neverpixels or modelinputs. No encoder output may be reused acrossrequests in manager orworker caches. Reusing the image embedding within the same request acrossits decode steps is permitted. Instrument raw image-item processing and vision-encoder consumption: require320processed/encoded images acrossquality, and280processed/encoded images in eachperformancecell (40requests*(2warmups+5timedpasses)); count imageitems, not batched Python invocations. Missing counters or bypassed processor/vision work makes the measurement invalid and unscored. This applies equally to B0 andcandidate.
