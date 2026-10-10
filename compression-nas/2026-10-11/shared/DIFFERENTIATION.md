# Distinct research objectives

The six new directions were selected for development together. They are not renamed copies of the previously passing GEV quantization and MoE pruning proposals.

| New task | Manipulated component | Distinction from existing work in this submission series |
| --- | --- | --- |
| kv-cache-rsi | Runtime attention-state encoding and retention | Compresses input-dependent inference state with frozen model weights; previous gev-quant-rsi compresses resident expert weights. |
| vl-activation-quant-rsi | Quantization calibration and activation treatment in a vision-language model | Studies cross-modal activation error and measured throughput under fixed image processing; does not reallocate the precision of GEV's experts. |
| lowrank-compress-rsi | Static low-rank factorization of dense projection matrices | Changes matrix representation and per-layer approximation capacity; neither integer quantization nor expert deletion is the optimized treatment. |
| sparse24-rsi | Hardware-supported fine-grained sparse weight masks | Studies sparse matrix execution at unchanged layer/expert topology, with actual full-model speed as the outcome. A high zero fraction alone is insufficient. |
| jev-block-nas-rsi | The topology, placement and sharing of a detachable capability branch | Compresses an already released JEV branch under a fixed backbone. It does not redesign the entire small decision model from scratch or claim whole-backbone compression. |
| gpt-subnet-nas-rsi | Inherited trained supernetwork architecture and exported subnet | Selects and materializes a smaller trained network under quality and measured execution constraints. It does not retrain a decoder from scratch under a fixed 200M pretraining budget. |

Official neighboring tasks include `kev-decision-architecture` and `depth-width-allocation`. Their public descriptions can be inspected at https://index.openrsi.foundation/tasks and https://github.com/OpenRSI-Foundation/OpenRSI-Index . This comparison establishes scope differences; it is not a guarantee that the organizers will judge the new proposals sufficiently novel.

Each research agent must be able to revise a hypothesis after seeing an actual candidate evaluation. Fixed score tables and latency predictors can be search aids where declared; they cannot replace execution of the submitted model. A list of preset multiple-choice solutions is not the research action space.
