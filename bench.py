"""Controlled family benchmark. Each index pair denotes one ground-truth edit."""

from audit import audit
import random
import hashlib
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer


def main():
    rng = random.Random(23)
    texts = []
    for i in range(60):
        words = [f"term{rng.randrange(1000)}" for _ in range(20)]
        texts.extend(
            [" ".join(words), " ".join(words if i % 2 else words[:-1] + ["edited"])]
        )
    rows = [dict(id=str(i), text=t) for i, t in enumerate(texts)]
    truth = {(i, i + 1) for i in range(0, len(rows), 2)}

    def score(name, pairs):
        # Evaluation places even rows in train and odd rows in test for every detector.
        pairs = {(i, j) for i, j in pairs if i % 2 != j % 2}
        print(
            name,
            dict(
                detected=len(pairs & truth),
                missed=len(truth - pairs),
                false_pairs=len(pairs - truth),
            ),
        )

    digests = [hashlib.sha256(text.encode()).digest() for text in texts]
    exact = {
        (i, j) for i, j in combinations(range(len(rows)), 2) if digests[i] == digests[j]
    }
    score("exact hash equality", exact)
    edges, groups = audit(rows)
    score("MinHash", {(i, j) for i, j, _, _ in edges})
    for name, labels in [
        ("random", list(range(len(rows)))),
        ("exact grouping", texts),
        ("MinHash groups", groups),
    ]:
        keys = sorted(set(labels))
        rng.shuffle(keys)
        test = set(keys[: max(1, len(keys) // 5)])
        print(
            name,
            "residual cross-split families",
            sum((labels[i] in test) != (labels[j] in test) for i, j in truth),
        )
    # Feed independent libraries the same text families and report unavailable adapters explicitly.
    try:
        import pandas as pd
        from deepchecks.tabular import Dataset
        from deepchecks.tabular.checks import TrainTestSamplesMix

        frames = [
            # A constant format version gives Deepchecks a tuple grouping key. It cannot change equality.
            Dataset(pd.DataFrame({"text": texts[k::2], "format_version": 1}), cat_features=["text"])
            for k in (0, 1)
        ]
        result = TrainTestSamplesMix().run(*frames)
        # Each test row has one labeled train partner, so the affected-row ratio is comparable here.
        print("Deepchecks test rows overlapping", round(result.value["ratio"] * len(truth)), "/", len(truth))
    except ImportError as err:
        print("Deepchecks unavailable:", err)
    try:
        from cleanlab import Datalab
        import numpy as np

        features = TfidfVectorizer().fit_transform(texts).toarray()
        lab = Datalab(data={"text": texts})
        lab.find_issues(features=features, issue_types={"near_duplicate": {}})
        issue = lab.get_issues("near_duplicate")
        pairs = {
            tuple(sorted((i, int(j))))
            for i, neighbors in enumerate(issue["near_duplicate_sets"])
            for j in neighbors
            if i != j
        }
        score("cleanlab TF-IDF", pairs)
    except ImportError as err:
        print("cleanlab unavailable:", err)


if __name__ == "__main__":
    main()

