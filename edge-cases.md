# Tested edge cases
- empty text (never grouped)
- short text (< 3 words uses one shingle)
- repeated IDs (rejected)
- duplicate content across splits (linked, same group)
- empty-text isolation
- nonoverlapping split groups (no family crosses the new split)
- fewer than two groups (rejected: no non-empty holdout possible)
