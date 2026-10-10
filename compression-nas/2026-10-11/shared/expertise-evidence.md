# Contributor expertise evidence audit

Updated 2026-10-10 after the contributor directed us to their membership on AutoTrust's official organization page. This report distinguishes contributor-provided identity association from public project evidence. No public identity profile or upstream authorship record was edited to create evidence.

## Current conclusion

There is now a concrete, usable evidence chain for the revised proposals:

1. **Contributor-provided association:** the contributor supplied the professional name Jing Qiu, work email ajing@autotrust.ai and GitHub account `aajing`; they subsequently said their membership is visible on the AutoTrust organization homepage. That direction associates the contributor with the `ajing` member found there. This is contributor-supplied identity context, not an independent public full-name lookup.
2. **Public organizational membership:** https://huggingface.co/autotrust lists team member `ajing`, linked to https://huggingface.co/uremia. The organization member panel was checked in the browser. The public profile/API also associates `uremia`, display name `ajing`, with `autotrust`.
3. **Publicly credited relevant work:** https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned credits `ajing` / `uremia` / `autotrust` among the September 30, 2026 JEV-27B-VL release article's authors. Its technical subject covers calibrated multimodal decisions, response judging and personalized image recommendation.
4. **Additional pre-existing project contribution:** GitHub attributes AutoTrust's language-model research release and visual-representation research release to `aajing`, at the exact commits below.

Use the organization page, member profile and existing JEV article together. Organization membership alone does not establish authorship of every organization project, but the separate existing JEV release credit supports relevant shared project experience. The public profiles do **not** spell out Jing Qiu, and this report does not claim otherwise. Nor does article coauthorship establish that the contributor personally wrote every JEV component.

The revisions can now make this evidence chain explicit instead of repeating the previously insufficient generic training link. This is stronger evidence addressing the reviewers' concern; the official reviewer still decides eligibility. No acceptance is claimed.

## Superseded initial finding

The initial audit found no independently published full-name/GitHub/HF cross-link and correctly did not assume that similarly named accounts were the same person. It therefore treated the JEV article credit as unattributable and requested account disambiguation. That **request to re-establish the association is superseded by the contributor's subsequent direction to their organization membership and the verified member/article chain above**. The narrower observation that the profile does not publicly display the full professional name remains true. Do not present the initial evidence gap as an unchanged blocker, or require newly manufactured author declarations in the task repository.

## Applicable official rule

Read `.agents/skills/proposal-agent/references/onboarding.md` and `repository-research.md` in the official-template checkout at OpenRSI revision `dcfbc43b117b92d276837aa0d48f291d544fcf7a`.

The **coauthored route** requires a genuine contributor-confirmed project relationship and public authorship evidence. The rule expressly does not require investigation of the coauthor's exact module contribution. The **domain-expertise route** uses contributor confirmation of codebase familiarity and public evidence aligned with the research area. Neither route requires a separate prior paper on the exact Brier-calibration objective or personal authorship of the robot-arm module. Describe the actual relationship; do not change article credit into a claim of sole model or code authorship.

## Verified primary sources and limits

| Source | Supported fact | Attribution limit |
| --- | --- | --- |
| https://huggingface.co/autotrust | Official AutoTrust AI Lab organization page links to its website and GitHub organization; its browser member panel lists `ajing` linking to `uremia`. The organization describes work on decision models and efficient training/inference. | Membership is organizational affiliation, not personal authorship of every release. The page does not spell out Jing Qiu. |
| https://huggingface.co/uremia and https://huggingface.co/api/users/uremia/overview | Public display name `ajing`; account `uremia`; membership in `autotrust`; profile lists the JEV articles. | The full-name/GitHub association is contributor-provided; profile details contain no independent full-name or GitHub cross-link. |
| https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned | Existing September 30, 2026 AutoTrust article credits `ajing` / `uremia`. Discusses multimodal calibrated inference, history-conditioned image ranking, response judging and uncertainty. | Attribute release-article coauthorship and shared relevant project experience, not a specific individual's implementation or all underlying model results. |
| https://github.com/aajing and https://api.github.com/users/aajing | GitHub account confirmed by the contributor. Public profile API returned no full name, bio or website. | Public profile itself does not resolve the professional name; do not claim it does. |
| https://github.com/AutoTrustAI/autoresearch-sota-strategy/commit/e00c83e1017916f094a2b604c01d816ec6dfa9ca | GitHub attributes the September 1, 2026 project release to `aajing`, with training code, data preparation, results and attribution files. | Related model-development evidence. Public author field is the handle and its GitHub noreply address. |
| https://github.com/AutoTrustAI/nanopath-sota-strategy/commit/f7c0cc7f32ecf81bfbaf02a9d30637ec74928b8e | GitHub attributes a September 3, 2026 visual-representation research release, including model/training/data source and experiment matrix, to `aajing`. | Publication attribution is not proof of personal implementation of autonomously generated methods. |
| https://github.com/AutoTrustAI/nanopath-sota-strategy/blob/daf4c6bc7a2e238ae18fdb5809fb5b3515c0b593/README.md | Documents visual-backbone/readout optimization and maintainer validation, separating autonomous research, human operation and maintainer reproduction. | Supplementary visual-model evidence; no claim of an individual's medical or robotic specialization. |
| https://github.com/yuhai-china/JEV-27B-DEMO/tree/403b9662a76ef621ecbf3224d6b2b4e1a205701c | Official article links this codebase, which provides judging and recommendation demonstrations. | Retrieved commits are attributed to `yuhai-china`, not `aajing`; use it as project-mechanism evidence, not Jing Qiu's personal commit history. |
| https://huggingface.co/autotrust/JEV-9B/tree/b63f651ce8ed64481d3f5e73ecdb05f740042f01 and https://huggingface.co/autotrust/JEV-9B/blob/b63f651ce8ed64481d3f5e73ecdb05f740042f01/vl/demos/robot_arm.py | The shared JEV source project includes a public visual-control precedent; the release commit is displayed under `cloudyu`, and the model citation credits AutoTrust AI. | Do not attribute this specific commit or module to Jing Qiu. Relevant shared multimodal-decision project experience can support the proposed extension without that unsupported claim. |

These sources existed before the report update. Search did not establish any unrelated same-name researcher as this contributor; none of those papers are attributed to them. Some HF API calls failed with TLS errors; those failures were not treated as evidence of absence.

## Task relevance

| Task | Evidence-based fit |
| --- | --- |
| jev-judge-rsi | The credited JEV release concerns calibrated multimodal decisions, response judging and confidence. The proposal extends this shared model-development mechanism to completion assessment. It need not claim a separate specialty publication on the exact calibration loss. |
| jev-coldstart-rsi | The credited release describes ranking candidate images from a user's preceding image history. This directly grounds the source mechanism; the proposal uses another open evaluation dataset, without claiming the contributor authored that dataset. |
| jev-visual-control-rsi | The credited JEV project establishes related multimodal decision expertise. The task studies visual evidence, decision queries and feedback around that family of models, using the public JEV-9B demo as project precedent. Describe this shared model-development relationship; do not demand or assert personal authorship of `robot_arm.py` or physical-robot experience. |
| gev-think-rsi, gev-quant-rsi, moe-prune-rsi | Existing AutoTrust model-development publication history and documented organizational research provide additional relevant context. Keep the individual evidence, organization releases and proposed task-owned mechanisms distinct. |

Initial official reviews: https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/210, https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/212, https://github.com/OpenRSI-Foundation/OpenRSI-Index/discussions/213. They framed the failure as insufficient public evidence, not a finding that the contributor lacked expertise.

## Recommended truthful proposal wording

> Jing Qiu (ajing@autotrust.ai; GitHub aajing) supplied the submitting identity and directed us to their membership on AutoTrust's official organization page. That page publicly lists ajing, linked to Hugging Face account uremia. The existing September 30, 2026 JEV-27B-VL release article publicly credits ajing/uremia as an AutoTrust coauthor and documents calibrated multimodal decisions, judging and image recommendation. These public sources support the contributor's relationship to AutoTrust's shared decision-model work. The professional-name/account association is contributor-provided; the public profile displays ajing rather than Jing Qiu. No authorship of every model component or of the independent evaluation dataset is inferred.

Append the task-specific mechanism from the preceding table. Link the actual organization/profile/article, rather than presenting this report or a new task-repository declaration as independent authorship evidence. No private identity documents, GPU experiments or module-level attribution request is needed to document the supplied relationship accurately.

## Current contributor declaration for this batch

On October 11, 2026, Jing Qiu confirmed representing AutoTrust, authorization to use its organizational achievements, and familiarity with the codebases of KIVI, LLM Compressor, SVD-LLM, NVIDIA Model Optimizer and HW-GPT-Bench. The five external-source proposals use the domain-expertise route; no external-project authorship is asserted.
