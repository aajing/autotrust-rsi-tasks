# Submission and provenance notes

These six packages are newly prepared proposal drafts. The contributor selected all six directions for development. No Discussion has been created, no official reviewer result is claimed, and no GPU experiment has run for this batch.

## Contributor

The submitting contact is Jing Qiu, ajing@autotrust.ai, GitHub aajing, representing AutoTrust. The contributor confirmed authorization to use AutoTrust's organizational achievements. Existing evidence links the contributor-provided identity to AutoTrust member ajing/uremia and credited JEV release work. The official AutoTrust organization page describes work on Blocks of Experts, quantization and model pruning. These are relevant public context, not a claim of personal authorship of every component or of unrelated upstream repositories.

The contributor explicitly confirmed Jing Qiu as the sole listed author for this batch. A single submission contact does not establish or limit the eventual paper's authorship; the organizers control their final attribution policy.

On October 11, 2026, the contributor explicitly confirmed familiarity with the codebases of KIVI, LLM Compressor, SVD-LLM, NVIDIA Model Optimizer and HW-GPT-Bench. These five proposals use the domain-expertise route. This factual declaration is separate from organizational authorization and does not claim authorship of the external projects.

## Source and model revisions

Each proposal's Exact commit/tag must resolve in the repository named by that proposal. A Hugging Face Git repository may be the primary source if it contains the actual implementation; its revision must not be presented as a commit in an unrelated GitHub repository. Model and dataset revisions are separately labeled.

An existing released model is the reference. A newly compressed, trained or calibrated control is produced in Work unless it is itself already publicly released. The absence of a measured reference score is not the absence of the reference artifact. Solution materializes existing reference files without fitting or evaluation; subsequent author validation establishes matched reference measurements.

## Disclosure and research claims

Inputs, answers, evaluator definitions, construction seeds and feedback are public and unencrypted. Each task explicitly defines permitted benchmark-informed fitting. Scores describe optimization on a disclosed fixed workload; they are not evidence of unseen-data generalization. Submission artifacts remain bounded model structures, parameters or runtime policies, and cannot include an answer lookup table or fabricated measurement file.

Use the current shared Base/Work/Judge snapshot. Judge's task tests are injected there; do not promise an independent clean-Base verifier or perfect isolation against an adversarial administrator.

## Compute and readiness

One H100 with 80 GB VRAM, one physical node and available host RAM are the planning lane. Exact CPU, RAM, Work time, Judge time, attempts and overhead appear in each proposal. Estimates are not measurements. Count full Work plus Judge cycles; proxy diagnostics or parallel trials do not count as additional adaptive loops. No paid compute is provisioned by this package.

Local format and CPU scoring checks establish only their specific contracts. They do not establish model accuracy, attainable full marks, accelerator compatibility, end-to-end speedup, official acceptance or final benchmark inclusion. Concrete acquisition and integration paths are supplied for subsequent task construction and validation.

## Official handoff

Use one original native session and dedicated official checkout for each proposal. Render the final scientific contract for contributor review, then follow the official proposal-agent lifecycle. Keep the new batch separate from the six already passing Discussions #210–#215. A later update to an existing Discussion must reuse its original session; do not post duplicate Discussions or a /task command merely to hurry the runner.

Support-material publication does not create an official Discussion. These proposals remain unsubmitted until the contributor confirms each final proposal in its dedicated native session.
