"""
Pipeline Runner
  Step 1: extract_brand_model.py  →  results/brand_model_list.csv
  Step 2: fetch_google_trends.py  →  results/trends_brand.csv
                                     results/trends_resolution.csv
                                     results/trends_screen_size.csv
 
File structure:
  sample_project/
  ├── data/
  │   └── extracted_product_info_amazon.csv   ← download from Kaggle (see README)
  ├── results/                                 ← auto-created on first run
  ├── src/
  │   ├── test.py
  │   ├── extract_brand_model.py
  │   └── fetch_google_trends.py
  ├── .gitignore
  ├── README.md
  └── requirements.txt
 
Run with (from project root):
    python src/test.py
"""

import os
import sys
import traceback
from pathlib import Path

SRC_DIR  = Path(__file__).resolve().parent          # .../src/
ROOT_DIR = SRC_DIR.parent                           # project root

sys.path.insert(0, str(SRC_DIR))  # Ensure src/ is in the import path

import extract_brand_model
import fetch_google_trends
# import fetch_keepa_prices


def run_step(step_no: int, name: str, func):
    """Runs a step function with error handling and prints status."""
    print(f"\n{'═' * 60}")
    print(f"  Step {step_no} / 2 — {name}")
    try:
        func()
        print(f" Step {step_no} finished successfully.")
        return True
    except Exception:
        print(f" Step {step_no} failed:")
        traceback.print_exc()
        return False


def print_summary():
    """Prints the generation status of all output files."""
    print(f"\n{'═' * 60}")
    print("  Run completed — Output file summary")
    files = {
        ROOT_DIR / "results" / "brand_model_list.csv":    "Brand & Model List",
        ROOT_DIR / "results" / "trends_brand.csv":        "Google Trends — Brand Popularity",
        ROOT_DIR / "results" / "trends_resolution.csv":   "Google Trends — Resolution",
        ROOT_DIR / "results" / "trends_screen_size.csv":  "Google Trends — Screen Size",
        # "keepa_price_history.csv": "Keepa — Price History",
    }
    for path, desc in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  {desc:30s}  {path}  ({size:,} bytes)")
        else:
            print(f"  {desc:30s}  {path}  (not found)")
    print()


def main():
    # Step 1
    flag = run_step(1, "Brand & Model Extraction", extract_brand_model.main)
    if not flag:
        print("\nStep 1 failed, terminating execution.")
        sys.exit(1)

    # Step 2
    run_step(2, "Google Trends Data Fetching", fetch_google_trends.main)

    # # Step 3
    # run_step(3, "Keepa Price History Fetching", fetch_keepa_prices.main)

    print_summary()


if __name__ == "__main__":
    main()
