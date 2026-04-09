# dsci510_spring2026_final_project
This is a DSCI510 Spring 2026 final project.

# Analyzing Factors Influencing the Popularity of Computer Monitors in Online Markets

This project analyzes factors influencing the popularity of computer monitors in online markets.  
Popularity is approximated using review count and is analyzed together with product specifications and Google Trends data.

---

## Data sources

| Name / short description | Source URL | Type | List of field | Format | Python access | Estimated data size |
|:------------------------|:-----------|:----:|:--------------|:------:|:-------------:|--------------------:|
| Amazon Monitor Dataset (product specifications and ratings) | https://www.kaggle.com/datasets/durjoychandrapaul/amazon-products-sales-monitor-dataset | file | brand, resolution, screen size, price, rating | csv | yes | ~900 (≈300 unique products) |
| Google Trends data (search interest for monitor-related keywords) | https://trends.google.com | API | keyword, date, search_interest | json | yes | ~300+ data points |
| Rainforest API (product-level price, deal, and review data) | https://www.rainforestapi.com/ | API | product_id, price, deal info, review count | json | in progress | ~300+ planned |
---

## Results

At the current stage, the project focuses on data preparation and integration.

- Brand and model information has been extracted and standardized from the raw dataset.  
- Google Trends data has been successfully collected.  
- Preliminary datasets are ready for merging and further analysis.  

No final analytical results have been produced yet, as the project is still in the data collection and preprocessing phase.

---

## Installation

- No API keys are required for Google Trends (pytrends).  
- If using Rainforest API, users need to provide their API key in a `.env` file.
- Install dependencies: pip install -r requirements.txt

---

## Running analysis

### Step 1

Before running this step, download the dataset from Kaggle:

https://www.kaggle.com/datasets/durjoychandrapaul/amazon-products-sales-monitor-dataset

Download the file: extracted_product_info_amazon.csv

### Step 2

Run:
python src/test.py

Results will appear in the results/ folder.
Raw/intermediate data should be stored in the data/ folder.