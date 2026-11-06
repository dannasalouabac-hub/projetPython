import gzip
import os
import os.path as pt


def ingest(path: str) -> list[str]:
    rows = []
    for file in sorted(os.listdir(path)):
        file_path = pt.join(path, file)
        if not pt.isfile(file_path):
            continue
        opener = gzip.open if file.endswith(".gz") else open
        with opener(file_path, mode="rt", encoding="utf-8") as f:
            rows.extend(f.readlines())
    return rows

