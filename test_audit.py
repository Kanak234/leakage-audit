import pytest
from pathlib import Path
import csv
from audit import audit, shingles, export


def test_export_independent_groups(tmp_path):
    dest = tmp_path / "output"
    export(Path(__file__).with_name("example.csv"), dest)
    with (dest / "split.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["split"] == rows[1]["split"]
    assert {row["split"] for row in rows} == {"train", "test"}
    assert "1,2" in (dest / "overlap.csv").read_text()


def test_short_and_empty():
    assert shingles("") == set() and shingles("One") == {"one"}


def test_duplicate_id():
    with pytest.raises(ValueError):
        audit([{"id": "x"}, {"id": "x"}])


def test_groups():
    rows = [
        dict(id=str(i), text=t)
        for i, t in enumerate(["Alpha Beta", "alpha beta", "", ""])
    ]
    edges, groups = audit(rows)
    assert edges[0][2] == 1 and groups[0] == groups[1] and groups[2] != groups[3]
