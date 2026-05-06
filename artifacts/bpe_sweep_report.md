# BPE Sweep Report

## Summary

| Model | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold |
| --- | ---: | ---: | ---: | ---: |
| custom | 6.6400 | 2.7438 | 1.0000 | 50/50 |
| bpe_200 | 11.5400 | 4.7686 | 0.5488 | 0/50 |
| bpe_500 | 8.3600 | 3.4545 | 0.6123 | 1/50 |
| bpe_1000 | 6.6400 | 2.7438 | 0.6277 | 1/50 |

## Category Summary

| Category | custom F1 | bpe_200 F1 | bpe_500 F1 | bpe_1000 F1 |
| --- | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5487 | 0.6582 | 0.6866 |
| informal | 1.0000 | 0.5833 | 0.7742 | 0.7200 |
| negative_word | 1.0000 | 0.5227 | 0.6154 | 0.7143 |
| proper_name | 1.0000 | 0.5588 | 0.5738 | 0.6139 |
| question | 1.0000 | 0.6098 | 0.7188 | 0.7541 |
| softening | 1.0000 | 0.5636 | 0.6000 | 0.6000 |
| suffix_chain | 1.0000 | 0.5138 | 0.5435 | 0.5176 |
| verb_future | 1.0000 | 0.3944 | 0.4828 | 0.5185 |
| verb_past | 1.0000 | 0.6923 | 0.6939 | 0.6222 |

## Notes

- Token count tek basina kalite degildir.
- Boundary F1, gold morfolojik sinirlarla karakter boundary uyumunu olcer.
- Toy BPE production baseline degildir; yalnizca karsilastirma altyapisi icin minimal baseline'dir.
