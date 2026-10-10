# Data card and provenance

Source: `https://github.com/JD-P/simulacra-aesthetic-captions`

Frozen source revision: `5b78f9eee45698ba8629fbaa461952952433553d`.

The original authors state that prompts, generated images and ratings were released under CC0 1.0. The license declaration, source URL and downloaded README hash are recorded in `evidence/upstream/simulacra-source-evidence.json`. The dataset is separately authored by John David Pressman, Katherine Crowson and Simulacra Captions Contributors. It is not AutoTrust data. The source declaration is not a guarantee about every depicted third-party subject or right.

Public data is acquired without credentials. The 44,748,800-byte SQLite snapshot is included with SHA256 `da6fe7ca508982daf27b92d316d8dfa1e6b27e934f1b19495c6175d418f579d3`. It contains 176,939 recorded rating rows. It does not contain image pixels. The image archive URL and observed ETag/size are in `configs/source-pins.json`. Image payloads and image-level checksums remain pending import.

The `sid` field is a synthetic identity inferred from a user's aesthetic survey, not a verified real-person identifier. Exclude survey groups unless they contain exactly question IDs 0–19 with valid 1–10 ratings. Use recorded ratings regardless of the source's `verified` flag; no automated model score or synthetic user preference is substituted. Exclude empty prompts, malformed paths and invalid ratings. Select one image per normalized generation prompt per user. Remove prompts occurring under multiple user groups before split selection. Require at least 40 distinct remaining prompts per user.

The frozen SHA256 user partition uses salt `sac-coldstart-v1`, residues 0–5 for learning, 6–7 for development and 8–9 for evaluation. There are 57/16/16 eligible users after filtering. Use every eligible group: 57/16/16, without consulting a model. Each user supplies 20 history items and 20 different candidates, from distinct prompt groups. No candidate rating is visible in inputs. History ratings are visible evidence. The first 3 history items form the short-history cell; all 20 form the long-history cell. Text-only, image-only and combined cells share candidates, providing a paired modality comparison within each user. Candidate and history order is a fixed hash permutation, not a real timeline.

The resulting 342/96/96 query rows correspond to only 57/16/16 independent survey-user groups. Keep all six cells of a user together in bootstrap resampling. Do not treat modality duplicates as independent evidence or claim broad population gains from this small user sample.

Coldstart denotes the 3/20-history condition presented to the inference model. All published labels, including scoring labels, may inform fitting and adaptive selection, so the task does not claim unseen-item or heldout-user generalization. Candidate/history IDs and normalized prompts are disjoint across partitions as a construction property, not a data-access restriction. Image-byte duplicates are reported and retained at import, including cross-partition matches. There is no pixel-dependent filtering, denominator change, partial-workload fallback or claim that all selected pixels are unique. Missing/corrupt images are unscored infrastructure failures until acquired correctly. Semantic near-duplicates and public-source pretraining exposure remain possible.

The score is macro NDCG@10 over six cells with linear human-rating gain and expected discount for tied model scores. Full score is 100 when every query attains ideal DCG@10 and all runtime/integrity rules pass. This requires the best available ratings at the discounted positions, in nonincreasing rating order; order below rank 10 is immaterial. Items with identical human ratings may tie. Tying unequal ratings across a positive discount loses utility.

Citation:

```bibtex
@techreport{pressmancrowson2022,
  author={John David Pressman and Katherine Crowson and Simulacra Captions Contributors},
  title={Simulacra Aesthetic Captions}, year={2022},
  institution={Stability AI}, number={Version 1.0},
  url={https://github.com/JD-P/simulacra-aesthetic-captions}
}
```

All input files, answers, salts, source maps and reference scoring code are public and unencrypted. There is no secret evaluation set. Results characterize optimization on this disclosed benchmark; label inspection, possible memorization and the small user count limit any generalization claim.
