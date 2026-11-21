# TRD — Leakage Audit

## Stack
| Part | Choice | Why |
|---|---|---|
| Candidate search | datasketch `MinHashLSH` (128 perms, seed 42) | Sub-quadratic; avoids comparing every pair |
| Verification | exact Jaccard on shingle sets | LSH is probabilistic; exact check removes false candidates |
| Grouping | union-find with path halving | Near-linear, and handles chains |
| Baselines (optional) | Deepchecks 0.19.1 `TrainTestSamplesMix`, cleanlab 2.7.1 Datalab near-duplicates on TF-IDF | Popular existing tools to compare against |

## Data flow
1. `shingles(text)`: casefold, `\w+` tokens, 3-word shingles. Texts shorter than three words use the full text as one shingle. An empty text gives an empty set and is never indexed.
2. `audit(rows, threshold=0.65)`:
   - For each row, build a MinHash.
   - Query the LSH for earlier rows and verify Jaccard ≥ threshold.
   - Union the two rows and record the edge `(j, i, score, first 4 shared shingles)`.
   - Insert the row into the LSH.
3. `export()`: shuffle the group roots (seed 42), take `round(0.2 × groups)` as test, and write `overlap.csv` (cross-split edges only) and `split.csv`.

## Key decisions
- **Split by group, not by row**, so no family can straddle the boundary. The trade-off is that the test row fraction can drift from 20% when groups are large.
- **Show the evidence**: shared shingles are exported so a human can confirm each link.
- **Two requirement files.** `requirements.txt` holds the tool. `baselines.txt` pins the comparison libraries, which only install on Python 3.11–3.12.

## Limits and roadmap
Word-shingle overlap misses paraphrases and can chain weakly related texts (A~B~C). Next: a labelled paraphrase set and an optional embedding-based candidate stage.
