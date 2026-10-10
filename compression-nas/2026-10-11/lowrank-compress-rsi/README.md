# lowrank-compress-rsi

Can an autonomous researcher allocate different matrix ranks, choose activation-whitening data and perform bounded sequential recovery to remove 40% of a public 7B model’s weight payload while preserving language modeling and free-response mathematics?

Local English draft only; not published, officially submitted, accepted or GPU-tested. The data and answers are fully present and unencrypted. Public-benchmark fitting is explicitly allowed under fixed budgets; no unseen-task claim is made.

- [proposal.md](proposal.md): exact 28-field official format.
- [task.json](task.json): machine-readable scientific contract, budgets and full-score rule.
- [DATA.md](DATA.md): actual source cardinality, deterministic selection, answers and licenses.
- [SOURCES.md](SOURCES.md): immutable primary code/model/runtime/data pins and contributor attribution limits.
- [INTEGRATION.md](INTEGRATION.md): actual source entrypoints, fixed native inference path and remaining ordinary packaging.
- [data/manifest.json](data/manifest.json): materialized data hashes, counts and seed.

Full score: C/C0 <= 0.60 and every quality/resource gate; C is actual BF16 weight/factor tensor payload bytes, including every frozen inference weight once.

CPU verification: `python3 -m unittest test_scoring -v`; deterministic data rebuild: `python3 prepare_data.py` with requirements-cpu.txt. Rebuild reads already downloaded public evidence and never imports torch or downloads weights. Model performance and runtime must be measured during normal post-acceptance activation, not fabricated in this proposal.

Before external submission, resolve the official contributor route/codebase-familiarity attestation rather than claiming authorship of the selected external repository. No external action is authorized by this local draft alone.
