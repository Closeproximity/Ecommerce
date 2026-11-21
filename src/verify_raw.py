"""
verify_raw.py - M2 Data Quality Analyst
=======================================
Proves the raw Olist files in data/raw/ are exactly the files the team audited.

It recalculates the SHA-256 fingerprint and size of every file listed in
docs/raw_file_checksums.csv and compares them with the saved values.
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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # project root (one level above src/)
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "docs" / "raw_file_checksums.csv"


def sha256_of(path):
    """Return the SHA-256 hex digest of a file, reading it in 1 MB chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:                      # "rb" = raw bytes, so line endings are never changed
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_files():
    """Compare every file in the manifest with the file on disk.

    Returns a list of (relative_path, status) where status is
    OK, MISSING, SIZE MISMATCH or HASH MISMATCH.
    """
    results = []
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = ROOT / row["file"]                # works on any OS: Path joins "data/raw/x.csv" correctly
            if not path.exists():
                status = "MISSING"
            elif path.stat().st_size != int(row["size_bytes"]):
                status = "SIZE MISMATCH"
            elif sha256_of(path) != row["sha256"].lower():
                status = "HASH MISMATCH"
            else:
                status = "OK"
            results.append((row["file"], status))
    return results


def update_manifest():
    """Rewrite the manifest from the files currently in data/raw/."""
    files = sorted(RAW.glob("*.csv"))
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "size_bytes", "sha256"])
        for path in files:
            writer.writerow([path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256_of(path)])
    print(f"Manifest rewritten with {len(files)} files: {MANIFEST.relative_to(ROOT).as_posix()}")


def main():
    parser = argparse.ArgumentParser(description="Verify raw data files against saved SHA-256 fingerprints.")
    parser.add_argument("--update", action="store_true",
                        help="rewrite the manifest from data/raw (only after an agreed new download)")
    args = parser.parse_args()

    if args.update:
        update_manifest()
        return 0

    results = verify_files()
    for file, status in results:
        print(f"{status:14} {file}")
    ok = all(status == "OK" for _, status in results)
    print("\nAll raw files match the audited versions." if ok
          else "\nWARNING: raw data differs from the audited version. Re-download from Kaggle before analysing.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())