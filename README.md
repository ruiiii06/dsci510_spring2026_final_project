# dsci510_spring2026_final_project
This is a DSCI510 Spring 2026 final project.

# Analyzing Factors Influencing the Popularity of Computer Monitors in Online Markets

This project analyzes factors influencing the popularity of computer monitors in online markets.  
Popularity is approximated using review count, which serves as a proxy for sales volume. It is analyzed together with product specifications (resolution, screen size), price and market demand signals from Google Trends. The goal is to identify which factors have the strongest impact on popularity and pricing.

Generative AI used: Claude (Anthropic) and ChatGPT (OpenAI) were used to assist with code generation. All AI-generated code sections are labeled.

---

## Data sources

| Name / short description | Source URL | Type | List of field | Format | Python access | Estimated data size |
|:------------------------|:-----------|:----:|:--------------|:------:|:-------------:|--------------------:|
| Amazon Monitor Dataset | https://www.kaggle.com/datasets/durjoychandrapaul/amazon-products-sales-monitor-dataset | file | brand, resolution, screen size, price | csv | yes | ~900 (~300 unique products) |
| Google Trends data (search interest for monitor-related keywords) | https://trends.google.com | API | keyword, search_interest | json | yes | 34 keywords |
| Amazon (web scraping) | https://www.amazon.com/ | Web page | rating, review count | html | yes | ~300 data points |
---

## Results

Review count is highly right-skewed, which means that a small number of products dominate in popularity.

Correlation analysis shows weak relationships between all variables and review count (max r = 0.16), while the strongest relationships are associated with price.

Ordinary least squares (OLS) models are built, Model 1a/1b examines how price and Google Trends market demand signals affect product popularity, while Model 2 examines how market demand signals drive product pricing.
Model 1a: R² = 0.034. Price and Resolution_Trend do not significantly predict review count, and Brand_Trend is statistically significant with a modest positive effect.
Model 1b: R² = 0.000. Size_Trend shows no significant independent effect on review count.
Model 2: R² = 0.233. Price is partially explained by resolution trend and brand trend.

Findings suggest review count may be driven by factors not captured in this dataset (e.g., time listed and panel technology type), and market demand signals are more useful for explaining price than popularity.

---

## Installation

- No API keys are required.

- Install dependencies: 
`pip install -r requirements.txt`
`# Download Chromium for Playwright (one-time setup)`
`playwright install chromium`

---

## Running analysis

- Run full pipeline (without visualization):

`python main.py `

Results will appear in `results/` folder. All obtained will be stored in `data/`

- Run notebook
Open `results.ipynb` in Jupyter or VS Code and run all cells.
**Note**: In step 3, the scraping step uses Playwright Sync API, which conflicts with Jupyter's asyncio loop. It is recommended to run this step from the terminal `python main.py --scrape` rather than from the notebook.