# Sources and licensing

Task author: Jing Qiu, AutoTrust. This is a local preparation bundle; no submission is implied.

Vendored `sources/JEV-9B/` files come unmodified from [autotrust/JEV-9B revision b63f651ce8ed64481d3f5e73ecdb05f740042f01](https://huggingface.co/autotrust/JEV-9B/tree/b63f651ce8ed64481d3f5e73ecdb05f740042f01). The model card declares Apache-2.0. `configs/source_manifest.json` records exact upstream URLs, SHA-256 values and byte counts. The original servo demonstration inspired B0; the new task controller/environment are separately authored and do not reproduce the source's claimed model score.

[Qwen/Qwen3.5-9B revision c202236235762e1c871ad0ccb60c8ee5ba337b9a](https://huggingface.co/Qwen/Qwen3.5-9B/tree/c202236235762e1c871ad0ccb60c8ee5ba337b9a) declares Apache-2.0. No Qwen weight file is bundled. Model download metadata is not a model license substitution; preserve downloaded upstream notices when constructing the runtime.

MuJoCo upstream reference: `https://github.com/google-deepmind/mujoco` commit `3a4f422053673ff731f7fef593fd014d8984cfce`, Apache-2.0. MuJoCo source/binaries are not bundled or executed. The optional XML adapter is newly authored; its output does not change the certified CPU lane.

Pillow is a separately installed dependency under its upstream HPND license. No third-party image corpus is used. Scene records, generated images, reference controllers and evaluator code are authored for this task. They follow the package's first-party license; upstream files retain their stated licenses and attribution. All evaluation records, reference solutions and reconstruction seeds are public and inspectable. The submitted controller is separately bound by the observation-only method contract; publication is not a guarantee against memorization or per-instance answer encoding.
