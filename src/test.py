import os
import pandas as pd
import config
import load

def test_load_kaggle_data():
    df = load.get_kaggle_data(config.KAGGLE_DATASET_SLUG)
    assert not df.empty, "Failed to load Kaggle dataset"
    print("Kaggle data loaded successfully, head:\n", df.head())


def test_load_titles_from_csv():
    test_file = "test_titles.csv"
    df = pd.DataFrame({"Title": ["Product A", "Product B", "Product C"]})
    df.to_csv(test_file, index=False)

    titles = load.load_titles_from_csv(test_file)
    assert len(titles) > 0, "Failed to load titles from CSV"
    print(f"Loaded {len(titles)} titles successfully:\n", titles)
    os.remove(test_file)


if __name__ == "__main__":
    test_load_kaggle_data()
    test_load_titles_from_csv()