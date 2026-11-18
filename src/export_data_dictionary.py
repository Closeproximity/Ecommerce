
from pathlib import Path
import re

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DOC_PATH = ROOT / "docs" / "data_dictionary.md"
OUTPUT_PATH = ROOT / "docs" / "data_dictionary.xlsx"

FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def extract_descriptions(markdown):
    descriptions = {}
    current_table = None

    for line in markdown.splitlines():
        heading = re.match(r"### 2\.\d+ (\w+)", line)

        if heading:
            current_table = heading.group(1)
            descriptions[current_table] = {}
            continue

        if current_table and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]

            if len(cells) == 2:
                column, description = cells

                if column.lower() != "column" and not set(column) <= {"-", ":"}:
                    descriptions[current_table][column] = description

    return descriptions


def get_data_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "Integer"
    if pd.api.types.is_float_dtype(series):
        return "Float"
    if pd.api.types.is_bool_dtype(series):
        return "Boolean"

    return "String / Text"


def main():
    markdown = DOC_PATH.read_text(encoding="utf-8")
    descriptions = extract_descriptions(markdown)

    records = []

    for table, filename in FILES.items():
        path = RAW_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}")

        df = pd.read_csv(path)

        print(f"Processing {table}: {len(df):,} rows")

        for column in df.columns:
            series = df[column]
            non_null = series.dropna()

            example = (
                str(non_null.iloc[0])
                if not non_null.empty
                else "No non-null example"
            )

            records.append({
                "Table": table,
                "Column": column,
                "Data type": get_data_type(series),
                "Meaning": descriptions.get(table, {}).get(
                    column, "Description pending review"
                ),
                "Example value": example,
                "% Missing": round(series.isna().mean() * 100, 2),
                "Notes": "",
            })

    result = pd.DataFrame(records)

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        result.to_excel(
            writer,
            sheet_name="Data Dictionary",
            index=False
        )

        worksheet = writer.sheets["Data Dictionary"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        header_fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )

        for cell in worksheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        widths = [22, 36, 18, 65, 35, 15, 40]

        for index, width in enumerate(widths, start=1):
            worksheet.column_dimensions[
                get_column_letter(index)
            ].width = width

        for row in worksheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True
                )

    print("\nData dictionary exported successfully.")
    print(f"Total documented columns: {len(result)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
