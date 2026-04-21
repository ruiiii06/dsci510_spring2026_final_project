import config
import pandas as pd
from pytrends.request import TrendReq
import re
import time, random
from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import quote_plus


BRAND_MIN_COUNT = 3

# 1. Data cleaning
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all cleaning steps to the raw product DataFrame:
      1. Filter to monitor-only titles and deduplication
      2. Normalize Screen_size
      3. Normalize Resolution 
    Returns cleaned DataFrame
    """

    # Filter to monitor-only titles, and drop duplicates based on Title
    df = df.copy()  
    df = df[df["Title"].str.contains("monitor", case=False, na=False)].reset_index(drop=True)
    df = df.drop_duplicates(subset=["Title"], keep="first")

    # Normalize Screen Size
    def normalize_screen_size(raw) -> float:
        match = re.search(r"(\d+\.?\d*)", str(raw))        
        if match:
            size = float(match.group(1))
            for std in config.STANDARD_SIZE:
                if abs(size - std) <= config.SCREEN_SIZE_MARGIN:
                    return float(std)
            return size
        else:
            return None
    
    df["Screen Size"] = df["Screen Size"].apply(normalize_screen_size)
    
    # Normalize Resolution 
    def normalize_resolution(raw) -> str:
        for pattern, label in config.RESOLUTION_MAP:
            if re.search(pattern, str(raw), flags=re.IGNORECASE):
                return label
        return raw
    
    df['Resolution'] = df["Resolution"].apply(normalize_resolution)
    
    print(f"Data cleaned: {len(df)} monitor products identified.")
    return df


# 2. Google Trends fetching
def fetch_batch(pytrends, batch) -> pd.Series:
    pytrends.build_payload(batch, timeframe=config.TIMEFRAME, geo=config.GEO)
    trends = pytrends.interest_over_time()
    if not trends.empty:
        return trends.drop(columns=['isPartial'], errors='ignore').mean()
    else:
        print(f"No trends data found for batch: {batch}")
        return pd.Series(dtype=float)


def fetch_brand_trends(df: pd.DataFrame) -> pd.Series:
    # extract unique brands appearing more than BRAND_MIN_COUNT times
    # use generative AI to address the issue of excessive comparisons (the number of items exceeds 5)
    counts = df["Brand"].value_counts()
    brands = counts[counts >= BRAND_MIN_COUNT].index.tolist()
    keywords = [f"{b} monitor" for b in brands if isinstance(b, str) and b.strip()]

    
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    step = config.BATCH_SIZE - config.OVER_LAP
    batches, i = [], 0
    while i < len(keywords):
        batches.append(keywords[i:i+config.BATCH_SIZE])
        i += step
    
    batch_srs = []

    for i, batch in enumerate(batches):
        print(f"Fetching trends for batch {i+1}/{len(batches)}: {batch}")
        try:
            srs = fetch_batch(pytrends, batch)
            if not srs.empty:
                batch_srs.append(srs)
            else:
                print(f"No trends data returned for batch {batch}.")
        except Exception as e:
            print(f"Error fetching trends for batch {batch}: {e}")
        time.sleep(config.SLEEP_SEC)    # Avoid rate limits

    if not batch_srs:
        raise RuntimeError("Failed to fetch trends for all batches. No data collected.")


    # Chain normalized batch trends together
    normalized_srs = [batch_srs[0]]

    for i in range(1, len(batch_srs)):
        prev = normalized_srs[-1]
        curr = batch_srs[i]
        overlap_kws = [kw for kw in curr.index if kw in prev.index]

        if not overlap_kws:
            print(f"No overlap between batch {i} and batch {i+1}.")
            normalized_srs.append(curr)
            continue

        ratios = []
        for kw in overlap_kws:
            if pd.notna(prev[kw]) and pd.notna(curr[kw]) and curr[kw] != 0:
                ratios.append(prev[kw] / curr[kw])
        
        if not ratios:
            print(f"No valid ratios for normalization between batch {i} and batch {i+1}.")
            normalized_srs.append(curr)
            continue

        scale = pd.Series(ratios).median()

        curr_scaled = curr.copy()
        new_kws = [kw for kw in curr.index if kw not in prev.index]
        curr_scaled[new_kws] = curr_scaled[new_kws] * scale
        normalized_srs.append(curr_scaled)


    # Combine all normalized batches into one series
    result = normalized_srs[0]
    for srs in normalized_srs[1:]:
        new_kws = [kw for kw in srs.index if kw not in result.index]
        result = pd.concat([result, srs[new_kws]])

    result.name = "avg_trend"
    return result


def fetch_resolution_trends() -> pd.DataFrame:
    # use generative AI to solve the synonym merging problem
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    records  = []
 
    for tier, synonyms in config.RESOLUTION_KEYWORDS_GROUPS.items():
        batch = [config.TRENDS_ANCHOR_KEYWORD] + synonyms
        try:
            srs = fetch_batch(pytrends, batch)
            if srs.empty:
                print(f"[Resolution] No data retrieved for {tier}.")
                time.sleep(config.SLEEP_SEC)
                continue
 
            anchor = srs[config.TRENDS_ANCHOR_KEYWORD] or float("nan")
            # Normalize each synonym by anchor, then sum them to get composite score
            composite = sum(srs[kw] / anchor for kw in synonyms if kw in srs.index)
            records.append({"resolution_tier": tier, "avg_trend": composite})
 
        except Exception as e:
            print(f"{tier} failed: {e}")
        
        time.sleep(config.SLEEP_SEC)

    if not records:
        raise RuntimeError("[Resolution] No data retrieved.")
    return pd.DataFrame(records)


def fetch_screen_size_trends() -> pd.DataFrame:
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
 
    srs = fetch_batch(pytrends, config.SCREEN_SIZE_KEYWORDS)
    if srs.empty:
        raise RuntimeError("[Screen Size] No data retrieved.")
 
    result = srs.reset_index()
    result.columns = ["keyword", "avg_trend"]
    result["screen_size_inch"] = result["keyword"].str.extract(r"(\d+)").astype(float)
    return result[["keyword", "screen_size_inch", "avg_trend"]]



def fetch_all_trends(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    returns (df_brand, df_resolution, df_screen_size)
    """
    # Fetch brand trends
    brand_trend = fetch_brand_trends(df)
    df_brand = brand_trend.reset_index()
    df_brand.columns = ["keyword", "avg_trend"]
    df_brand["brand"] = df_brand["keyword"].str.replace(" monitor", "", case=False)


    # Fetch resolution trends
    df_resolution = fetch_resolution_trends()

    # Fetch screen size trends
    df_screen_size = fetch_screen_size_trends()

    return df_brand, df_resolution, df_screen_size



# 3. Scrape the number of reviews from Amazon URLs
SELECTORS = {
    "results_container": '[data-component-type="s-search-result"]',
    "rating":            '[data-component-type="s-search-result"] .a-icon-alt',
    "ratings_total":     '[data-component-type="s-search-result"] .s-underline-text',
    "title":             'h2 a span',
}

def clean_search_term(title: str) -> str:
    for sep in ("|", ":"):
        if sep in title:
            title = title.split(sep)[0]
    title = re.sub(r'\s+', ' ', title).strip()

    if len(title) > 100:
        title = title[:100].rsplit(' ', 1)[0]
    
    return title.strip()

# use generative AI to simulate real browser behavior via Playwright
def setup_browser(playwright):
    browser = playwright.chromium.launch(
        headless=config.HEADLESS,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/New_York",
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return browser, context

def fail_record(title: str, status: str = "fail") -> dict:
    return {
        "input_title"  : title,
        "matched_title": None,
        "asin"         : None,
        "rating"       : None,
        "ratings_total": None,
        "status"       : status,
    }

def scrape_product(page, title: str) -> dict:
    search_term = clean_search_term(title)
    url = f"https://www.{config.AMAZON_DOMAIN}/s?k={quote_plus(search_term)}"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        page.wait_for_selector(SELECTORS["results_container"], timeout=10_000)
    except TimeoutError:
        print(f"[Timeout] Page failed to load: {title}")
        return fail_record(title)

    # check for CAPTCHA
    if "Enter the characters you see below" in page.content() or \
       "Sorry, we just need to make sure" in page.content():
        print(f"  [CAPTCHA]: {title}")
        return fail_record(title, status="CAPTCHA")

    cards = page.query_selector_all(SELECTORS["results_container"])
    if not cards:
        print(f"Product card not found: {title}")
        return fail_record(title)

    for card in cards:
        asin = card.get_attribute("data-asin")
        if not asin:
            continue
        
        is_sponsored = card.query_selector(
            '.s-sponsored-label-text, '
            '[data-component-type="sp-sponsored-result"], '
            '.puis-sponsored-label-text'
        )
        if is_sponsored:
            continue

        title_el = card.query_selector(SELECTORS["title"])
        matched_title = title_el.inner_text().strip() if title_el else None

        rating_el = card.query_selector(".a-icon-alt")
        if rating_el:
            rating_raw = rating_el.inner_text().strip()
            match = re.search(r'(\d+\.?\d*)\s+out of', rating_raw)
            rating = float(match.group(1)) if match else None
        else:
            rating = None

        rt_el = card.query_selector(".s-underline-text")
        if rt_el:
            rt_raw = rt_el.inner_text().strip()
            digits = re.sub(r'[^\d]', '', rt_raw)
            ratings_total = int(digits) if digits and len(digits) <= 7 else None
        else:
            ratings_total = None

        return {
            "input_title"  : title,
            "matched_title": matched_title,
            "asin"         : asin,
            "rating"       : rating,
            "ratings_total": ratings_total,
            "status"       : "success",
        }

    return fail_record(title)


def get_ratings_from_titles(titles: list[str]) -> pd.DataFrame:
    records = []

    with sync_playwright() as pw:
        browser, context = setup_browser(pw)
        page = context.new_page()

        # visit Amazon homepage first to get cookies
        print("Accessing Amazon homepage to get cookies.")
        page.goto(f"https://www.{config.AMAZON_DOMAIN}", wait_until="domcontentloaded", timeout=20_000)
        time.sleep(2)

        for i, title in enumerate(titles, 1):
            record = scrape_product(page, title)
            records.append(record)
            time.sleep(config.REQUEST_DELAY + random.uniform(0.5, 1.0))

            if i % 10 == 0:
                print(f"Processed {i}/{len(titles)} items")
                print(record)

        browser.close()

    return pd.DataFrame(records, columns=["input_title", "matched_title", "asin", "rating", "ratings_total", "status"])