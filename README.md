# dsci510_spring2026_final_project
This is a DSCI510 Spring 2026 final project.

**Environment Setup**
pip install -r requirements.txt


**Workflow**
Step 1: Extract Brand and Model

Run:
python extract_brand_model.py

Input:
extracted_product_info_amazon.csv
Output:
brand_model_list.csv

This step cleans product data and extracts brand information for later use.

Step 2: Fetch Google Trends Data

Run:
python fetch_google_trends.py
Output:
trends_brand.csv
trends_resolution.csv
trends_screen_size.csv

This script collects search interest data using Google Trends.
Keywords used：
Brand
Resolution (4K monitor/QHD monitor/FHD monitor)
Screen Size (24 monitor/27 monitor/32 monitor/34 monitor)


**Test**

Run:
python test.py

This verifies that:
scripts run without errors, data files are generated correctly, and Google Trends API works as expected


**Current Progress**
Dataset selected and processed
Brand/model extraction implemented
Google Trends API integrated
Keywords separated by resolution and screen size


Author

Hanrui Zhong
DSCI 510 – Spring 2026
University of Southern California
