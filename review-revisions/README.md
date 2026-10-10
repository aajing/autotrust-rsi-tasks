# First-review revisions

These are contributor-confirmed revisions responding to the six completed initial Reject decisions on 10 October 2026. The contributor approved the changed scientific contracts and requested official re-review. The current Discussion bodies and observed official review receipts are recorded in `../official-submissions/`; the original versions remain in Git history. Publishing files here does not resubmit a proposal and does not imply official acceptance.

Every prepared input, answer, construction seed, reference solution and evaluator remains public and unencrypted. No GPU experiment, model baseline measurement or paid compute job was run for this revision.

## Confirmed changes

| Task | Concrete revision | Confirmation / evidence status |
| --- | --- | --- |
| gev-think-rsi | Explicitly permit fitting and policy selection on all published splits. The objective is bounded compute allocation on this disclosed benchmark; it is not an unseen-test generalization estimate. Keep the restricted router artifact and evaluator-owned answer generation. | Confirmed by contributor. |
| jev-judge-rsi | Separate task Git revision from Hugging Face revisions so the review fetches the correct repository. Preserve the previously reviewed scientific contract. Add the public evidence audit rather than assert unverified authorship. | New organization-member and JEV release-author evidence supplied for re-review; no scientific-contract change. |
| jev-coldstart-rsi | Permit benchmark-conditioned optimization; replace executable ranking candidates with a bounded declarative prompt/evidence policy; native frozen JEV probabilities determine rankings. Cite the existing metadata-derived cohort evidence. Keep the selected cohort fixed and report image duplicates instead of silently changing counts after import. | Confirmed by contributor; organization-member and release-author evidence included. |
| jev-visual-control-rsi | Separate task and model refs. Preserve the previously reviewed controller, data and reward contract. Record evidence limits explicitly. | New contributor-directed organization membership and shared JEV multimodal release-author evidence included; no claim of robot-arm module authorship. |
| gev-quant-rsi | Use the existing pinned upstream BF16 B0 as the materializable reference. Treat INT4 BQ as an optional Work-produced control. Reward storage reduction relative to B0, subject to preserved quality/resource constraints, with full score at at most 40% of B0 bytes. Report distribution distortion as a diagnostic. | Confirmed by contributor. The previous reward was distortion reduction relative to an unavailable BQ artifact. |
| moe-prune-rsi | Use existing pinned B0 as the materializable reference. Treat B96 profiling/pruning as an optional Work-produced control. Preserve the expert-removal reward and quality gates. | Reference/lifecycle change confirmed by contributor. |

The quantization full-score endpoint accounts for the pinned architecture: frozen nonexpert tensors plus INT4/group128 expert tensors have an estimated storage floor near 35.7% of B0 before packaging overhead. A 25% endpoint would be structurally impossible under the allowed transformations. A 40% endpoint is not a claim that the model will meet the quality gates.

## Evidence and remaining boundaries

See [contributor evidence audit](expertise-evidence.md). Organization-hosted projects, model cards and release articles are relevant evidence. They must still support a truthful link to the named contributor. Existing public coauthor credit is enough to establish coauthorship; the workflow does not require proving authorship of each individual module. A new assertion in this proposal repository is not independent proof of prior expertise.

Source acquisition is distinct from authoring: the first coldstart review tried a model SHA against the task GitHub repository. Revised `Exact commit/tag` fields identify only the task Git commit; upstream model hashes appear in separately labeled evidence fields. The already published split report and selected manifest are cited directly.

The changes above are substantive scientific-contract revisions. The contributor has explicitly confirmed them. All six revisions have been posted to their original Discussions; no extra GPU reproduction is required for this proposal step.

The original discussion/session mapping is retained. With the changed scientific contracts confirmed, updates go to the same discussions, one native session per task. Do not create duplicate discussions or post `/task` to force a second review.

## Official update snapshot

All six confirmed revisions posted. At 2026-10-10T14:28:30.166300+00:00, the observed proposal-review results are 6 Pass, 0 Reject, 0 awaiting a completed review. See the [exact posted bodies and official receipt](../official-submissions/README.md). These are proposal-review outcomes; task generation, execution validation and benchmark inclusion are later stages. The revision release was published and all nine uploaded asset digests and sizes match the local files.
