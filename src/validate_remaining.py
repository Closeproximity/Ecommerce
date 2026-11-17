
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# 1. Validate product category translation key
categories = pd.read_csv(
    RAW / "product_category_name_translation.csv"
)

print("\nCATEGORY TRANSLATION")
print("Rows:", len(categories))
print(
    "Duplicate category names:",
    categories.duplicated(
        subset=["product_category_name"],
        keep=False
    ).sum()
)
print(
    "Unique category names:",
    categories["product_category_name"].nunique()
)

# 2. Inspect geolocation ZIP-prefix groups
geo = pd.read_csv(
    RAW / "olist_geolocation_dataset.csv"
)

print("\nGEOLOCATION")
print("Rows:", len(geo))
print(
    "Unique ZIP prefixes:",
    geo["geolocation_zip_code_prefix"].nunique()
)

coordinates_per_zip = (
    geo.groupby("geolocation_zip_code_prefix")
    [["geolocation_lat", "geolocation_lng"]]
    .nunique()
)

multiple_coordinates = coordinates_per_zip[
    (coordinates_per_zip["geolocation_lat"] > 1)
    | (coordinates_per_zip["geolocation_lng"] > 1)
]

print(
    "ZIP prefixes with multiple latitude/longitude values:",
    len(multiple_coordinates)
)

print("\nExample ZIP prefixes with multiple coordinates:")
print(multiple_coordinates.head(10))
