# AutoTrust RSI proposal index

Prepared for Jing Qiu, ajing@autotrust.ai, GitHub `aajing`. Each document uses the official English 28-field proposal table. These six proposals are **not submitted to official review**; their public packages are available for handoff.

| Proposal | Focus |
| --- | --- |
| [gev-think-rsi](gev-think-rsi.md) | Trainable external reasoning/compute router around a frozen GEV backbone |
| [jev-judge-rsi](jev-judge-rsi.md) | Calibrated mixed-task evaluation from native JEV evidence review |
| [jev-coldstart-rsi](jev-coldstart-rsi.md) | Human-rated personalized ranking of generated images |
| [jev-visual-control-rsi](jev-visual-control-rsi.md) | Visual manipulation through prompt and controller optimization |
| [gev-quant-rsi](gev-quant-rsi.md) | Quality-constrained quantization of generation and decision components |
| [moe-prune-rsi](moe-prune-rsi.md) | Quality-constrained expert pruning and recovery |

All prepared evaluation answers and seeds are public and unencrypted. This is an explicitly disclosed fixed-benchmark protocol with auditable method restrictions, not a secret-test design. Training/fitting may only use each task's declared learning split; general methods must not hard-code per-item answers. Public inspection and adaptive reuse remain limitations.

See `../../../prepared-tasks/README.md` for package counts, source access and download scope, and `../../../prepared-tasks/STATUS.md` for outstanding execution work. Model experiments and GPU timing have not been run. The source provenance and official field schema are under `evidence/`.
