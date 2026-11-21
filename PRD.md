# PRD — Leakage Audit

## Problem
When the same or almost the same text ends up in both the training and the test split, test scores are inflated and a model looks better than it is. Plain random splitting allows this. Exact-hash deduplication only catches identical strings, so a one-word edit slips through.

## Users
- **Primary:** a student or ML engineer preparing a text-classification dataset as an `id,text,split` CSV.
- **Secondary:** a reviewer who needs to see *why* two rows were linked.

## Goals
1. Find cross-split near-duplicates and show the evidence (Jaccard score plus shared phrases).
2. Produce a new split in which every near-duplicate family sits entirely in train or entirely in test.
3. Run offline on a laptop with no GPU.

## Non-goals
- Semantic or paraphrase detection (no embeddings yet).
- Deduplicating within a single split.
- Balancing labels or classes.

## Features
| Feature | Behaviour |
|---|---|
| Input | CSV with `id,text,split`; IDs must be unique |
| Detection | 3-word shingles → MinHash LSH candidates (128 permutations) → exact Jaccard ≥ 0.65 |
| Grouping | union-find over verified pairs |
| Output | `overlap.csv` (cross-split pairs plus up to 4 shared shingles), `split.csv` (new split plus group id) |
| Holdout | ~20% of groups (not rows), seeded shuffle (seed 42) |

## Acceptance criteria
- `python -m pytest -q` passes.
- `bench.py`: MinHash detects 60/60 pairs, 0 false pairs, 0 residual crossing families.
- Duplicate IDs, a threshold outside (0, 1), or fewer than two groups stop the run with a clear error.
- Empty texts never join a group.
