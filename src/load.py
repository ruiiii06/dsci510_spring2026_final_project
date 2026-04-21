import os
import kagglehub
import pandas as pd
import config
import sys

API_KEY = os.getenv("RAINFOREST_API_KEY", "")

# download the monitor dataset from Kaggle
def get_kaggle_data(dataset_slug) -> pd.DataFrame:
    try:
        kagglehub.dataset_download(dataset_slug, output_dir=config.DATA_DIR)
        file_path = os.path.join(config.DATA_DIR, config.KAGGLE_FILENAME)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{config.KAGGLE_FILENAME} not found in downloaded dataset at {file_path}.\n")
        
        df = pd.read_csv(file_path)
        print(f"Successfully loaded dataset from {file_path}.")
        return df
    
    except Exception as e:
        print(f"Error occurred while downloading dataset: {e}")
        return pd.DataFrame()


def load_titles_from_csv(file_path) -> list:
    try:
        df = pd.read_csv(file_path)
        TITLE_COLUMN = "Title"
        if TITLE_COLUMN not in df.columns:
            raise ValueError(f"'{TITLE_COLUMN}' column not found in CSV at {file_path}. Available columns: {df.columns.tolist()}")
        
        titles = df[TITLE_COLUMN].dropna().tolist()
        print(f"Successfully loaded {len(titles)} titles from {file_path}.")
        return titles
    
    except Exception as e:
        print(f"Error occurred while loading titles from CSV: {e}")
        return []


def load_all_data() -> pd.DataFrame:
    # load and merge all data
    def load_from_path(filepath) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath, quotechar='"', engine='python', on_bad_lines='skip')
            return df
        except FileNotFoundError:
            print(f"data file not found: {filepath}")
            sys.exit(1)
    
    scraped = load_from_path(config.AMAZON_DATA_CSV)
    products = load_from_path(config.CLEANED_CSV)
    res_trend = load_from_path(config.TRENDS_RES_CSV)
    size_trend = load_from_path(config.TRENDS_SIZE_CSV)
    brand_trend = load_from_path(config.TRENDS_BRAND_CSV)

    products = products[["Title", "Brand", "Screen Size", "Resolution", "Price"]]
    scraped = scraped[scraped["status"] == "success"]
    scraped["ratings_total"] = pd.to_numeric(scraped["ratings_total"], errors="coerce")
    scraped = scraped[scraped["ratings_total"] <= 50000]


    df = products.merge(scraped[["input_title", "rating", "ratings_total"]].rename(columns={"input_title": "Title", "rating": "Rating", "ratings_total": "Reviews"}), on="Title", how="inner")
    df = df.merge(brand_trend[["brand", "avg_trend"]].rename(columns={"brand": "Brand", "avg_trend": "Brand_Trend"}), on="Brand", how="left")
    df = df.merge(res_trend[["resolution_tier", "avg_trend"]].rename(columns={"resolution_tier": "Resolution", "avg_trend": "Resolution_Trend"}), on="Resolution", how="left")
    df = df.merge(size_trend[["screen_size_inch", "avg_trend"]].rename(columns={"screen_size_inch": "Screen Size", "avg_trend": "Size_Trend"}), on="Screen Size", how="left")

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    df = df.dropna(subset=["Reviews", "Price", "Brand_Trend", "Resolution_Trend"])

    return df