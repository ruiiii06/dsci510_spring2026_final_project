"""
Brand & Model Extraction Script
Extracts brand and model information from the Amazon monitor dataset CSV,
deduplicates entries, and outputs brand_model_list.csv.

Dependencies:
    pip install pandas

Input : extracted_product_info_amazon.csv
Output: brand_model_list.csv
"""

import re
import pandas as pd

INPUT_CSV  = "extracted_product_info_amazon.csv"
OUTPUT_CSV = "brand_model_list.csv"



def extract_model(title: str, brand: str) -> str:
    """
    Extracts model name from product title.
    Strategy: strip brand name → take content before first delimiter (| , () → truncate to 60 chars.
    """
    # remove brand name from title
    cleaned = re.sub(re.escape(brand), "", title, flags=re.IGNORECASE).strip()
    model = re.split(r"[|,\(]", cleaned)[0].strip()
    return model[:60].strip()


def normalize_brand(brand: str) -> str:
    """Normalizes brand name: title-case, strip extra whitespace."""
    return str(brand).strip().title()


def main():
    print("=" * 50)
    print("  Brand & Model Extraction")
    print("=" * 50)

    # 1. Load raw data
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} records across {df['Brand'].nunique()} brands.")

    # 2. Normalize brand names
    df["Brand_normalized"] = df["Brand"].apply(normalize_brand)

    # 3. Extract model names
    df["Model"] = df.apply(
        lambda r: extract_model(str(r["Title"]), str(r["Brand"])), axis=1
    )

    # 4. Deduplicate by Brand_normalized + Model
    result = (
        df[["Brand_normalized", "Model", "Title"]]
        .drop_duplicates(subset=["Brand_normalized", "Model"])
        .reset_index(drop=True)
    )
    print(f"After deduplication: {len(result)} unique Brand + Model combinations.")

    # 5. Save
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved to {OUTPUT_CSV}")

    # 6. Preview
    print("\nBrand distribution (Top 10):")
    print(result["Brand_normalized"].value_counts().head(10).to_string())
    print("\nData preview (first 5 rows):")
    print(result[["Brand_normalized", "Model"]].head().to_string(index=False))


if __name__ == "__main__":
    main()
