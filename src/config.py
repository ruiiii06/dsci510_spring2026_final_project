from pathlib import Path
from dotenv import load_dotenv
# import os


ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

# project configuration
DATA_DIR = ROOT / 'data'
RESULTS_DIR = ROOT / 'results'

# data source configuration
KAGGLE_DATASET_SLUG = 'durjoychandrapaul/amazon-products-sales-monitor-dataset'
KAGGLE_FILENAME = 'extracted_product_info_amazon.csv'

CLEANED_CSV          = RESULTS_DIR / "cleaned_products.csv"
TRENDS_BRAND_CSV     = RESULTS_DIR / "trends_brand.csv"
TRENDS_RES_CSV       = RESULTS_DIR / "trends_resolution.csv"
TRENDS_SIZE_CSV      = RESULTS_DIR / "trends_screen_size.csv"
RAINFOREST_DATA_CSV  = RESULTS_DIR / "rainforest_data.csv"
AMAZON_DATA_CSV      = RESULTS_DIR / "amazon_data.csv"

STANDARD_SIZE = [24, 27, 32, 34]    # inches
SCREEN_SIZE_MARGIN = 1.0            # +/- margin for screen size matching (inches)

RESOLUTION_MAP = [
    (r"2160|4K|UHD",  "2160p"),
    (r"1440|QHD|2K",  "1440p"),
    (r"1080|FHD|1K|Full HD",  "1080p"),
]

# Google trends configuration
TIMEFRAME  = "today 12-m"
GEO        = "US"
BATCH_SIZE = 5
SLEEP_SEC  = 10
OVER_LAP   = 2

TRENDS_ANCHOR_KEYWORD = "computer monitor"
RESOLUTION_KEYWORDS_GROUPS = {
    "2160p": ["4K monitor", "UHD monitor", "2160p monitor"],
    "1440p": ["2K monitor", "QHD monitor", "1440p monitor"],
    "1080p": ["1K monitor", "FHD monitor", "1080p monitor"],
}
 
SCREEN_SIZE_KEYWORDS = [
    "24 monitor",
    "27 monitor",
    "32 monitor",
    "34 monitor",
]

# Rainforest API configuration
# RAIN_SLEEP_SEC = 0.1
# RAINFOREST_API_KEY = os.getenv("RAINFOREST_API_KEY", "")
# BASE_URL = "https://api.rainforestapi.com/request"

# Amazon scraping configuration
REQUEST_DELAY = 1.5
HEADLESS      = True
AMAZON_DOMAIN = "amazon.com"
