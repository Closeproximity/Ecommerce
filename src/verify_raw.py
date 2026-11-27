"""
verify_raw.py - M2 Data Quality Analyst
=======================================
Proves the raw Olist files in data/raw/ are exactly the files the team audited.

Two checks:
1. The manifest docs/raw_file_checksums.csv lists each of the 9 expected
   Olist CSV files exactly once (nothing missing, duplicated or extra).
2. For every listed file, the size and SHA-256 fingerprint on disk match
   the saved values.

Paths in the manifest are relative to the project root and use "/", so the
check works the same on Windows, macOS and Linux.

How to run (from the project root, with .venv active):
    python src/verify_raw.py            # verify; exit code 0 = all OK, 1 = problem
    python src/verify_raw.py --update   # rewrite the manifest (ONLY after an agreed new download)
"""

import argparse
import csv
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # project root (one level above src/)
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "docs" / "raw_file_checksums.csv"

# The 9 files of the Olist dataset. The manifest must list each one exactly once.
EXPECTED_FILES = [
    "data/raw/olist_customers_dataset.csv",
    "data/raw/olist_geolocation_dataset.csv",
    "data/raw/olist_order_items_dataset.csv",
    "data/raw/olist_order_payments_dataset.csv",
    "data/raw/olist_order_reviews_dataset.csv",
    "data/raw/olist_orders_dataset.csv",
    "data/raw/olist_products_dataset.csv",
    "data/raw/olist_sellers_dataset.csv",
    "data/raw/product_category_name_translation.csv",
]


def sha256_of(path):
    """Return the SHA-256 hex digest of a file, reading it in 1 MB chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:                      # "rb" = raw bytes, so line endings are never changed
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_manifest(rows):
    """Check that the manifest lists every expected file exactly once and nothing else."""
    problems = []
    counts = Counter(row["file"] for row in rows)
    for file in EXPECTED_FILES:
        if counts[file] == 0:
            problems.append((file, "NOT IN MANIFEST"))
        elif counts[file] > 1:
            problems.append((file, f"LISTED {counts[file]} TIMES"))
    for file in sorted(set(counts) - set(EXPECTED_FILES)):
        problems.append((file, "UNEXPECTED IN MANIFEST"))
    return problems


def verify_files():
    """Run both checks. Returns a list of (relative_path, status); status "OK" means the file passed."""
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = check_manifest(rows)
    for row in rows:
        if row["file"] not in EXPECTED_FILES:
            continue                                 # already reported as unexpected
        path = ROOT / row["file"]                    # works on any OS: Path joins "data/raw/x.csv" correctly
        if not path.exists():
            status = "MISSING ON DISK"
        elif path.stat().st_size != int(row["size_bytes"]):
            status = "SIZE MISMATCH"
        elif sha256_of(path) != row["sha256"].lower():
            status = "HASH MISMATCH"
        else:
            status = "OK"
        results.append((row["file"], status))
    return results


def all_ok(results):
    """True only if every result is OK and all 9 expected files were checked."""
    checked_ok = {file for file, status in results if status == "OK"}
    return all(status == "OK" for _, status in results) and checked_ok == set(EXPECTED_FILES)


def update_manifest():
    """Rewrite the manifest from the 9 expected files currently in data/raw/."""
    missing = [f for f in EXPECTED_FILES if not (ROOT / f).exists()]
    if missing:
        print("Cannot update: these expected files are missing:", ", ".join(missing))
        return 1
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "size_bytes", "sha256"])
        for file in EXPECTED_FILES:
            path = ROOT / file
            writer.writerow([file, path.stat().st_size, sha256_of(path)])
    print(f"Manifest rewritten with {len(EXPECTED_FILES)} files: {MANIFEST.relative_to(ROOT).as_posix()}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Verify raw data files against saved SHA-256 fingerprints.")
    parser.add_argument("--update", action="store_true",
                        help="rewrite the manifest from data/raw (only after an agreed new download)")
    args = parser.parse_args()

    if args.update:
        return update_manifest()

    results = verify_files()
    for file, status in results:
        print(f"{status:22} {file}")
    ok = all_ok(results)
    print(f"\nAll {len(EXPECTED_FILES)} raw files match the audited versions." if ok
          else "\nFAILED: raw data or manifest differs from the audited version. "
               "Re-download from Kaggle before analysing.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())