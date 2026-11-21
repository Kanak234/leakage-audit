"""Find cross-split near duplicates in id,text,split CSV files."""

import argparse
import csv
import itertools
import re
from pathlib import Path
from datasketch import MinHash, MinHashLSH


def shingles(text):
    words = re.findall(r"\w+", text.casefold())
    # Short records still have one shingle. Empty records cannot establish duplicate identity.
    width = min(3, len(words))
    return (
        {" ".join(words[i : i + width]) for i in range(len(words) - width + 1)}
        if width
        else set()
    )


def audit(rows, threshold=0.65):
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between zero and one")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate record ID")
    index = MinHashLSH(threshold=threshold, num_perm=128)
    tokens, edges, parent = [], [], list(range(len(rows)))

    def root(i):
        while i != parent[i]:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, row in enumerate(rows):
        current = shingles(row["text"])
        tokens.append(current)
        if not current:
            continue
        signature = MinHash(num_perm=128, seed=42)
        signature.update_batch([s.encode() for s in sorted(current)])
        for j in sorted(index.query(signature)):
            shared = current & tokens[j]
            score = len(shared) / len(current | tokens[j])
            # Verify candidate similarity exactly before joining its connected component.
            if score >= threshold:
                parent[root(i)] = root(j)
                edges.append((j, i, score, sorted(shared)[:4]))
        index.insert(i, signature)
    return edges, [root(i) for i in range(len(rows))]


def export(source, destination):
    import random

    with source.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    edges, groups = audit(rows)
    clusters = sorted(set(groups))
    random.Random(42).shuffle(clusters)
    # Keep whole components together. Report a single component as an unsplittable corpus.
    if len(clusters) < 2:
        raise ValueError("Need two independent groups for a nonempty holdout")
    holdout = set(clusters[: max(1, round(0.2 * len(clusters)))])
    destination.mkdir(exist_ok=False)
    with (destination / "overlap.csv").open("w", newline="", encoding="utf8") as s:
        out = csv.writer(s)
        out.writerow(["left", "right", "jaccard", "shared_shingles"])
        for j, i, score, examples in edges:
            if rows[j]["split"] != rows[i]["split"]:
                out.writerow(
                    [rows[j]["id"], rows[i]["id"], score, " | ".join(examples)]
                )
    with (destination / "split.csv").open("w", newline="", encoding="utf8") as s:
        out = csv.DictWriter(s, fieldnames=["id", "text", "split", "group"])
        out.writeheader()
        for row, group in zip(rows, groups):
            out.writerow(
                dict(
                    id=row["id"],
                    text=row["text"],
                    group=group,
                    split="test" if group in holdout else "train",
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    export(args.source, args.destination)
