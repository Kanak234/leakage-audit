1. I began with a CSV of labeled train and test examples.
2. In audit.py I shingled text and retrieved candidates with MinHash.
3. I checked the exact Jaccard score and exported shared phrases so a reviewer could verify the match.
4. I assigned whole connected components to splits and tested this in test_audit.py.
5. I compared detected pairs and residual leakage using bench.py.

**Main limitation.** Word-shingle overlap can miss paraphrases and connect chains of weakly related texts.
