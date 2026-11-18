
from pathlib import Path
import pandas as pd

# Locate project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "docs"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Find all CSV files
csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

summary_rows = []
column_rows = []

print("\n" + "=" * 75)
print("          OLIST DATASET - INITIAL INSPECTION")
print("=" * 75)

for file_path in csv_files:

    print(f"\nInspecting: {file_path.name}")

    # Load CSV
    df = pd.read_csv(file_path, low_memory=False)

    rows, columns = df.shape

    # Count duplicate full rows
    duplicate_rows = df.duplicated().sum()

    # Store table summary
    summary_rows.append({
        "file_name": file_path.name,
        "row_count": rows,
        "column_count": columns,
        "duplicate_full_rows": int(duplicate_rows),
        "file_size_mb": round(
            file_path.stat().st_size / (1024 * 1024), 2
        )
    })

    print(f"Rows: {rows:,}")
    print(f"Columns: {columns}")
    print(f"Duplicate full rows: {duplicate_rows:,}")

    print("\nColumn details:")

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        missing_percentage = (
            missing_count / rows * 100 if rows else 0
        )

        column_rows.append({
            "file_name": file_path.name,
            "column_name": column,
            "data_type": str(df[column].dtype),
            "missing_count": missing_count,
            "missing_percentage": round(missing_percentage, 2),
            "unique_values": int(df[column].nunique(dropna=True))
        })

        print(
            f"  {column:<45} "
            f"{str(df[column].dtype):<12} "
            f"Missing: {missing_percentage:>6.2f}%"
        )

# Convert results into DataFrames
summary_df = pd.DataFrame(summary_rows)
columns_df = pd.DataFrame(column_rows)

# Save inspection reports
summary_path = REPORT_DIR / "dataset_inspection_summary.csv"
columns_path = REPORT_DIR / "column_profile.csv"

summary_df.to_csv(summary_path, index=False)
columns_df.to_csv(columns_path, index=False)

print("\n" + "=" * 75)
print("INSPECTION COMPLETED")
print("=" * 75)

print(f"\nFiles inspected: {len(csv_files)}")
print(f"Summary saved: {summary_path}")
print(f"Column profile saved: {columns_path}")

print("\nFINAL DATASET SUMMARY:")
print(summary_df.to_string(index=False))
