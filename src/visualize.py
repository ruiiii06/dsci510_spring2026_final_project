import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import config

sns.set_theme(style="whitegrid", palette="colorblind")
COLORS = sns.color_palette("colorblind")


def save(fig, filename: str):
    path = os.path.join(config.RESULTS_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[output] saved -> {path}")



def load_data():
    products = pd.read_csv(config.CLEANED_CSV, engine="python", on_bad_lines="skip")
    scraped = pd.read_csv(config.AMAZON_DATA_CSV, engine="python", on_bad_lines="skip")
    t_brand = pd.read_csv(config.TRENDS_BRAND_CSV)
    t_res = pd.read_csv(config.TRENDS_RES_CSV)
    t_size = pd.read_csv(config.TRENDS_SIZE_CSV)

    products = products[["Title", "Brand", "Screen Size", "Resolution", "Price"]]
    scraped["ratings_total"] = pd.to_numeric(scraped["ratings_total"], errors="coerce")
    # scraped = scraped[scraped["ratings_total"] <= 50000]
    scraped = scraped[(scraped["ratings_total"] >= 5) & (scraped["ratings_total"] <= 50000)]
    products["Price"] = pd.to_numeric(products["Price"], errors="coerce")

    df = products.merge(scraped[["input_title", "rating", "ratings_total"]].rename(columns={"input_title": "Title", "rating": "Rating", "ratings_total": "Reviews"}), on="Title", how="inner")


    return df, t_brand, t_res, t_size


def plot_review_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["Reviews"].dropna(), bins=30, edgecolor="white")
    ax.set_xlabel("Reviews Count")
    ax.set_ylabel("Number of Products")
    ax.set_title("Distribution of Product Review Count")
    save(fig, "review_distribution.png")



def plot_trends_combined(t_brand, t_res, t_size):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    brand_df = t_brand.copy()
    brand_df = brand_df.sort_values("avg_trend", ascending=True).tail(10)
    axes[0].barh(brand_df["brand"], brand_df["avg_trend"], color=COLORS[0])
    axes[0].set_title("Brand Trend")
    axes[0].set_xlabel("Avg Search Interest")

 
    axes[1].bar(t_res[t_res.columns[0]], t_res["avg_trend"], color=COLORS[1])
    axes[1].set_title("Resolution Trend")
    axes[1].set_ylabel("Avg Search Interest")
    axes[1].tick_params(axis="x", rotation=20)

    
    axes[2].bar(t_size[t_size.columns[0]], t_size["avg_trend"], color=COLORS[2])
    axes[2].set_title("Screen Size Trend")
    axes[2].set_ylabel("Avg Search Interest")
    axes[2].tick_params(axis="x", rotation=20)

    fig.suptitle("Google Trends Summary", fontsize=14)
    plt.tight_layout()
    save(fig, "trends_combined.png")



def main():
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    df, t_brand, t_res, t_size = load_data()
    print(f"{len(df)} products loaded")

    plot_review_distribution(df)
    plot_trends_combined(t_brand, t_res, t_size)

    print("charts saved to results/")


if __name__ == "__main__":
    main()
