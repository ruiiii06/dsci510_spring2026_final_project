"""
Brand & Model 提取脚本
从 Amazon 显示器数据集 CSV 中提取品牌和型号，去重后生成 brand_model_list.csv。

依赖安装:
    pip install pandas

输入: extracted_product_info_amazon.csv
输出: brand_model_list.csv
"""

import re
import pandas as pd

# ── 配置 ──────────────────────────────────────────────────────────────────────
INPUT_CSV  = "extracted_product_info_amazon.csv"
OUTPUT_CSV = "brand_model_list.csv"
# ─────────────────────────────────────────────────────────────────────────────


def extract_model(title: str, brand: str) -> str:
    """
    从产品标题中提取型号。
    策略：去掉品牌名 → 取第一个分隔符（| , (）之前的内容 → 截断到60字符。
    """
    # 去掉品牌名（大小写不敏感）
    cleaned = re.sub(re.escape(brand), "", title, flags=re.IGNORECASE).strip()
    # 取第一个分隔符之前的内容
    model = re.split(r"[|,\(]", cleaned)[0].strip()
    return model[:60].strip()


def normalize_brand(brand: str) -> str:
    """品牌名标准化：首字母大写，去除多余空格。"""
    return str(brand).strip().title()


def main():
    print("=" * 50)
    print("  Brand & Model 提取")
    print("=" * 50)

    # 1. 读取原始数据
    df = pd.read_csv(INPUT_CSV)
    print(f"读取完成：{len(df)} 条记录，{df['Brand'].nunique()} 个品牌。")

    # 2. 标准化品牌名
    df["Brand_normalized"] = df["Brand"].apply(normalize_brand)

    # 3. 提取型号
    df["Model"] = df.apply(
        lambda r: extract_model(str(r["Title"]), str(r["Brand"])), axis=1
    )

    # 4. 去重（按 Brand_normalized + Model）
    result = (
        df[["Brand_normalized", "Model", "Title"]]
        .drop_duplicates(subset=["Brand_normalized", "Model"])
        .reset_index(drop=True)
    )
    print(f"去重后：{len(result)} 条唯一 Brand + Model 组合。")

    # 5. 保存
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"已保存至 {OUTPUT_CSV}")

    # 6. 预览
    print("\n品牌分布（Top 10）：")
    print(result["Brand_normalized"].value_counts().head(10).to_string())
    print("\n数据预览（前5行）：")
    print(result[["Brand_normalized", "Model"]].head().to_string(index=False))


if __name__ == "__main__":
    main()
