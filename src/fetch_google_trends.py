"""
Google Trends Data Fetching Script (Multi-Dimension Keywords)
Reads brand list from brand_model_list.csv, combines with preset product spec keywords,
and fetches trend data in separate groups by dimension.

Keyword structure:
  - Brand keywords      : "Dell monitor" / "ASUS monitor" ...
      → Measures brand popularity; cross-batch values normalized via overlapping keywords
  - Resolution keywords : "4K monitor" / "QHD monitor" / "FHD monitor"
      → Measures demand by display resolution spec
  - Screen Size keywords: "24inch monitor" / "27inch monitor" ...
      → Measures demand by screen size spec

Dependencies:
    pip install pytrends pandas

Input : results/brand_model_list.csv
Output: results/trends_brand.csv
        results/trends_resolution.csv
        results/trends_screen_size.csv
"""

import time
from pathlib import Path
import pandas as pd
from pytrends.request import TrendReq

# Configuration
ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV           = ROOT / "results" / "brand_model_list.csv"
OUTPUT_BRAND        = ROOT / "results" / "trends_brand.csv"        # Brand keywords output
OUTPUT_RESOLUTION   = ROOT / "results" / "trends_resolution.csv"   # Resolution keywords output
OUTPUT_SCREEN_SIZE  = ROOT / "results" / "trends_screen_size.csv"  # Screen size keywords output

(ROOT / "results").mkdir(parents=True, exist_ok=True)

TIMEFRAME  = "today 12-m"   # Last 12 months
GEO        = "US"
BATCH_SIZE = 5              # Google Trends allows max 5 keywords per request
OVERLAP    = 2              # Number of keywords shared between consecutive brand batches
SLEEP_SEC  = 2              # Delay between batches (seconds) to avoid rate limiting

# Product Keywords by Spec Dimension
RESOLUTION_KEYWORDS = [
    "4K monitor",
    "QHD monitor",
    "FHD monitor",
]

SCREEN_SIZE_KEYWORDS = [
    "24 monitor",
    "27 monitor",
    "32 monitor",
    "34 monitor",
]

# Keyword → spec dimension mapping (for merging with Amazon dataset spec columns)
SPEC_MAP = {
    "4K monitor":     "Resolution",
    "QHD monitor":    "Resolution",
    "FHD monitor":    "Resolution",
    "24 monitor":     "Screen Size",
    "27 monitor":     "Screen Size",
    "32 monitor":     "Screen Size",
    "34 monitor":     "Screen Size",
}



# 1. Keyword Construction

def build_brand_keywords(df: pd.DataFrame, min_count: int = 3) -> list[str]:
    """
    Extracts brands appearing >= min_count times from brand_model_list,
    formatted as "<Brand> monitor".
    Tip: sort brands by approximate popularity so adjacent batches are comparable,
    which improves the stability of overlap-based scale factors.
    """
    brand_counts = df["Brand_normalized"].value_counts()
    brands = brand_counts[brand_counts >= min_count].index.tolist()
    keywords = [f"{b} monitor" for b in brands]
    print(f" Brand keywords ({len(keywords)} total): {keywords}")
    return keywords


# 2. Batch Construction

def build_overlapping_batches(keywords: list[str],
                               batch_size: int = BATCH_SIZE,
                               overlap: int = OVERLAP) -> list[list[str]]:
    """
    Splits keyword list into overlapping batches.

    Example (batch_size=5, overlap=2):
      Batch 1: [A, B, C, D, E]
      Batch 2: [D, E, F, G, H]   <- D, E are the bridge
      Batch 3: [G, H, I, J, K]   <- G, H are the bridge
    """
    step = batch_size - overlap
    batches = []
    i = 0
    while i < len(keywords):
        batches.append(keywords[i: i + batch_size])
        i += step
    return batches


# 3. Trends Fetching

def fetch_batch(pytrends: TrendReq, batch: list[str],
                timeframe: str, geo: str) -> pd.DataFrame:
    """Fetches trend data for a single batch (up to 5 keywords)."""
    pytrends.build_payload(batch, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame()
    return df.drop(columns=["isPartial"], errors="ignore")


def fetch_all_simple(keywords: list[str], timeframe: str,
                     geo: str, label: str) -> pd.DataFrame:
    """
    Fetches keywords in non-overlapping batches and concatenates results.
    Used for Resolution and Screen Size groups where all keywords fit in 1-2 batches
    and cross-batch normalization is not needed.
    """
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    all_dfs = []
    total = (len(keywords) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(keywords), BATCH_SIZE):
        batch = keywords[i: i + BATCH_SIZE]
        batch_no = i // BATCH_SIZE + 1
        print(f" [{label}] Batch {batch_no}/{total}: {batch}")
        try:
            df = fetch_batch(pytrends, batch, timeframe, geo)
            if not df.empty:
                all_dfs.append(df)
            else:
                print(f" Batch {batch_no} returned empty data, skipping.")
        except Exception as e:
            print(f" Batch {batch_no} failed: {e}")
        time.sleep(SLEEP_SEC)

    if not all_dfs:
        raise RuntimeError(f"[{label}] No data retrieved. Check keywords or network connection.")

    merged = pd.concat(all_dfs, axis=1)
    merged = merged.loc[:, ~merged.columns.duplicated()]
    merged.index.name = "date"
    return merged.reset_index()


def fetch_all_with_overlap(keywords: list[str], timeframe: str,
                            geo: str, label: str) -> pd.DataFrame:
    """
    Fetches brand keywords using overlapping batches, then applies chain normalization
    so that all brand values are on a comparable scale.
    """
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    batches = build_overlapping_batches(keywords, BATCH_SIZE, OVERLAP)
    batch_dfs = []

    for i, batch in enumerate(batches):
        print(f" [{label}] Batch {i+1}/{len(batches)}: {batch}")
        try:
            df = fetch_batch(pytrends, batch, timeframe, geo)
            if not df.empty:
                batch_dfs.append(df)
            else:
                print(f" Batch {i+1} returned empty data, skipping.")
        except Exception as e:
            print(f" Batch {i+1} failed: {e}")
        time.sleep(SLEEP_SEC)

    if not batch_dfs:
        raise RuntimeError(f"[{label}] No data retrieved.")
    

    # Ensure 'date' is a column (not index) in every batch before normalization.
    batch_dfs = [
        df.reset_index() if "date" not in df.columns else df
        for df in batch_dfs
    ]

    # Chain normalization via overlapping keywords
    # Batch 1 is the reference; each subsequent batch is rescaled to match it.
    normalized = [batch_dfs[0]]

    for i in range(1, len(batch_dfs)):
        prev = normalized[i - 1]
        curr = batch_dfs[i]
        overlap_kws = [c for c in curr.columns if c in prev.columns and c != "date"]

        if not overlap_kws:
            print(f" No overlap found between batch {i} and {i+1}, appending unscaled.")
            normalized.append(curr)
            continue

        # Scale factor = median ratio of overlapping keyword means across the two batches.
        # Median is more robust than mean when one overlap keyword has an outlier spike.
        ratios = []
        for kw in overlap_kws:
            mean_prev = prev[kw].replace(0, float("nan")).mean()
            mean_curr = curr[kw].replace(0, float("nan")).mean()
            if mean_prev and mean_curr:
                ratios.append(mean_prev / mean_curr)

        if not ratios:
            print(f" Could not compute scale for batch {i+1}, appending unscaled.")
            normalized.append(curr)
            continue

        scale = pd.Series(ratios).median()
        print(f" Scale factor batch {i+1} -> batch {i}: {scale:.4f} "
              f"(overlap keywords: {overlap_kws})")

        # Only scale the new (non-overlap) columns; overlap columns already exist in prev.
        curr_scaled = curr.copy()
        new_cols = [c for c in curr.columns if c not in overlap_kws + ["date"]]
        curr_scaled[new_cols] = curr_scaled[new_cols] * scale
        normalized.append(curr_scaled)

    # Merge all batches, keeping only one copy of each overlap column
    merged = normalized[0]
    for df in normalized[1:]:
        new_cols = ["date"] + [c for c in df.columns if c not in merged.columns]
        merged = merged.merge(df[new_cols], on="date", how="outer")

    return merged.reset_index(drop=True)


# 4. Wide → Long Format

def wide_to_long(df_wide: pd.DataFrame, keyword_type: str) -> pd.DataFrame:
    """
    Converts wide-format table to long format, tagging each row with keyword_type.
    Output columns: date | keyword | search_interest | keyword_type
    """
    df_long = df_wide.melt(
        id_vars="date",
        var_name="keyword",
        value_name="search_interest"
    )
    df_long["keyword_type"] = keyword_type
    return df_long




def main():
    print(" Google Trends Fetcher ")
    print("=" * 60)

    # Load brand/model list
    df_products = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df_products)} product records across "
          f"{df_products['Brand_normalized'].nunique()} brands.\n")

    # Brand Keywords (overlapping batch normalization)
    print(" Group 1: Brand Keywords")
    brand_kws = build_brand_keywords(df_products, min_count=3)
    df_brand_wide = fetch_all_with_overlap(brand_kws, TIMEFRAME, GEO, label="Brand")
    df_brand = wide_to_long(df_brand_wide, keyword_type="brand")
    # Add a clean brand column (strip " monitor" suffix) for merging with product data
    df_brand["brand"] = df_brand["keyword"].str.replace(
        " monitor", "", case=False).str.strip()
    df_brand.to_csv(OUTPUT_BRAND, index=False, encoding="utf-8-sig")
    print(f" Brand trends saved to {OUTPUT_BRAND} ({len(df_brand)} rows)\n")

    # Resolution Keywords
    # no cross-batch normalization needed.
    print(" Group 2: Resolution Keywords")
    print(f" Resolution keywords ({len(RESOLUTION_KEYWORDS)} total): {RESOLUTION_KEYWORDS}")
    df_res_wide = fetch_all_simple(RESOLUTION_KEYWORDS, TIMEFRAME, GEO, label="Resolution")
    df_resolution = wide_to_long(df_res_wide, keyword_type="resolution")
    df_resolution["spec_tag"] = df_resolution["keyword"].map(SPEC_MAP)
    df_resolution.to_csv(OUTPUT_RESOLUTION, index=False, encoding="utf-8-sig")
    print(f" Resolution trends saved to {OUTPUT_RESOLUTION} ({len(df_resolution)} rows)\n")

    # Screen Size Keywords
    # no cross-batch normalization needed.
    print(" Group 3: Screen Size Keywords")
    print(f" Screen size keywords ({len(SCREEN_SIZE_KEYWORDS)} total): {SCREEN_SIZE_KEYWORDS}")
    df_size_wide = fetch_all_simple(SCREEN_SIZE_KEYWORDS, TIMEFRAME, GEO, label="Screen Size")
    df_screen_size = wide_to_long(df_size_wide, keyword_type="screen_size")
    df_screen_size["spec_tag"] = df_screen_size["keyword"].map(SPEC_MAP)
    df_screen_size.to_csv(OUTPUT_SCREEN_SIZE, index=False, encoding="utf-8-sig")
    print(f" Screen size trends saved to {OUTPUT_SCREEN_SIZE} ({len(df_screen_size)} rows)\n")

    # Summary Preview
    print("=" * 60)
    print("Preview — Brand trends (first 5 rows):")
    print(df_brand[["date", "keyword", "brand", "search_interest"]].head().to_string(index=False))

    print("\nPreview — Resolution trends (first 5 rows):")
    print(df_resolution[["date", "keyword", "spec_tag", "search_interest"]].head().to_string(index=False))

    print("\nPreview — Screen size trends (first 5 rows):")
    print(df_screen_size[["date", "keyword", "spec_tag", "search_interest"]].head().to_string(index=False))


if __name__ == "__main__":
    main()