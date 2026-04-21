import config
import load
import process
import os
import analysis



if __name__ == "__main__":
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    # Step 1: Load data, clean and standardize data, and save to results directory
    df = load.get_kaggle_data(config.KAGGLE_DATASET_SLUG)
    if df.empty:
        print("No data loaded. Exiting.")
        exit(1)
    else:
        print(f"Loaded dataset with {len(df)} records, head:\n{df.head()}")
    
    df = process.clean_data(df)
    print(f"Cleaned dataset with {len(df)} records, head:\n{df.head()}")
    df.to_csv(config.CLEANED_CSV, index=False)
    print(f"Cleaned data saved to {config.CLEANED_CSV}")

    # Step 2: fetch trends
    df_brand, df_resolution, df_screen_size = process.fetch_all_trends(df)
    df_brand.to_csv(config.TRENDS_BRAND_CSV, index=False)
    print(f"Brand trends saved to {config.TRENDS_BRAND_CSV}")

    df_resolution.to_csv(config.TRENDS_RES_CSV, index=False)
    print(f"Resolution trends saved to {config.TRENDS_RES_CSV}")

    df_screen_size.to_csv(config.TRENDS_SIZE_CSV, index=False)
    print(f"Screen size trends saved to {config.TRENDS_SIZE_CSV}")

    # Step 3: scrape the Amazon URLs
    titles = load.load_titles_from_csv(config.CLEANED_CSV)
    df = process.get_ratings_from_titles(titles)
    df.to_csv(config.AMAZON_DATA_CSV, index=False)
    print(f"The product data scraped saved to {config.AMAZON_DATA_CSV}")

    # Step 4: analyze
    df = load.load_all_data()
    analysis.correlation_analysis(df)
    m1a, m1b = analysis.model_popularity(df)