# dsci510_spring2026_final_project
This is a DSCI510 Spring 2026 final project.

# Analyzing Factors Influencing the Popularity of Computer Monitors in Online Markets

This project analyzes factors influencing the popularity of computer monitors in online markets.  
Popularity is approximated using review count and is analyzed together with product specifications and Google Trends data.

---

## Data sources

| Name / short description | Source URL | Type | List of field | Format | Python access | Estimated data size |
|:------------------------|:-----------|:----:|:--------------|:------:|:-------------:|--------------------:|
| Amazon Monitor Dataset | https://www.kaggle.com/datasets/durjoychandrapaul/amazon-products-sales-monitor-dataset | file | brand, resolution, screen size, price | csv | yes | ~900 (~300 unique products) |
| Google Trends data (search interest for monitor-related keywords) | https://trends.google.com | API | keyword, search_interest | json | yes | ~300 data points |
| Amazon (web scraping) | https://www.amazon.com/ | Web page | rating, review count | html | yes | ~300 data points |
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

- Install dependencies: 
`pip install -r requirements.txt`
`# Download Chromium for Playwright (one-time setup)`
`playwright install chromium`

---

## Running analysis

From `src/` directory run:

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`