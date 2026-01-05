# gtfs_zip.py

import csv
import zipfile
from typing import Dict, Iterator

def iter_rows(zip_path: str, filename: str) -> Iterator[Dict[str, str]]:
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(filename, "r") as f:
            text_iter = (line.decode("utf-8-sig") for line in f)
            reader = csv.DictReader(text_iter)
            for row in reader:
                yield row

def has_file(zip_path: str, filename: str) -> bool:
    with zipfile.ZipFile(zip_path, "r") as z:
        return filename in z.namelist()
    