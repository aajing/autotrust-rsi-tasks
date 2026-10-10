# vl-activation-quant-rsi

Complete English proposal draft for review, not submitted or accepted. Sole contributor: Jing Qiu (ajing@autotrust.ai). No GPU experiment or model inference has been run.

Start with proposal.md (the official28-field structure). task.json fixes the scientific contract; DATA.md/data-manifest.json fix public inputs and gold; SOURCES.md records source pins/licenses/access; INTEGRATION.md is the Task-Agent implementation handoff.

CPU verification:

```sh
python verify_data.py
python -m unittest test_scoring.py -v
```

scoring.py is a CPU oracle for task-owned measurements, not a GPU evaluator. CHECKS.json records completed local checks and remaining execution work. All included data and answers are plaintext.
