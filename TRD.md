# Technical design
Build three-word shingles, retrieve MinHash LSH candidates, verify exact Jaccard similarity, then union matching components before assigning groups to train or test.

Grouping can chain weakly related endpoints. Test fraction is by group, so large groups may skew row counts. Next evaluate labeled paraphrases.
