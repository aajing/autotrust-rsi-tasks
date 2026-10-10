# kv-cache-rsi

Complete English proposal draft for review, not submitted or accepted. Sole contributor: Jing Qiu (ajing@autotrust.ai). No GPU experiment or model inference has been run.

Start with proposal.md (the official28-field structure). task.json fixes the scientific contract; DATA.md/data-manifest.json fix public inputs and gold; SOURCES.md records source pins/licenses/access; INTEGRATION.md is the Task-Agent implementation handoff.

Public delivery includes `materialize_data.py`, exact selection/hash manifests and SOURCE-NOTICES.md. The six raw LongBench JSONL files and source ZIP are excluded from public packaging; setup retrieves the existing pinned public source and reconstructs the identical plaintext inputs and answers. Local preparation copies remain intact.

Setup and CPU verification:

```sh
python materialize_data.py
# Or: python materialize_data.py --archive /path/to/data.zip
python verify_data.py
python -m unittest test_scoring.py test_materialize_data.py -v
```

scoring.py is a CPU oracle for task-owned measurements, not a GPU evaluator. CHECKS.json records completed local checks and remaining execution work. All included data and answers are plaintext.
