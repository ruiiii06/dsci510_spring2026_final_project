import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import numpy as np
import config
import statsmodels.formula.api as smf
import matplotlib.patches as mpatches


def correlation_analysis(df: pd.DataFrame):
    cols = ["Reviews", "Price", "Brand_Trend", "Resolution_Trend", "Size_Trend", "Rating"]
    corr = df[cols].dropna().corr()

    fig, ax = plt.subplots(figsize=(8,6))
    seaborn.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True, linewidths=0.5, ax=ax)
    ax.set_title("Correlation Matrix")
    plt.tight_layout()
    path = os.path.join(config.RESULTS_DIR, "correlation_matrix.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"output saved to {path}")

    pairs = (
        corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        .stack().abs().sort_values(ascending=False)
    )
    print("\nTop correlations:")
    print(pairs.head(5).round(3))


def plot_coefficients(model, title: str, filename: str):
    coef  = model.params.drop("Intercept")
    ci    = model.conf_int().drop("Intercept")
    pvals = model.pvalues.drop("Intercept")

    labels = [n.replace("C(Brand)[T.", "Brand: ").replace("]", "").replace("_", " ")
              for n in coef.index]
    colors = ["#4C72B0" if p < 0.05 else "#AABDD6" for p in pvals]

    fig, ax = plt.subplots(figsize=(8, max(5, len(coef) * 0.45)))
    y = range(len(coef))

    ax.barh(list(y), coef, color=colors, alpha=0.85)
    ax.errorbar(coef, list(y),
                xerr=[coef - ci[0], ci[1] - coef],
                fmt="none", color="black", capsize=3)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_title(title)

    legend = [mpatches.Patch(color="#4C72B0", label="p < 0.05"),
              mpatches.Patch(color="#AABDD6", label="p ≥ 0.05")]
    ax.legend(handles=legend, fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(config.RESULTS_DIR, filename), dpi=150)
    plt.close(fig)
    

def model_popularity(df: pd.DataFrame):
    df = df.copy()
    df["log_rt"] = np.log1p(df["Reviews"])

    model_1 = smf.ols("log_rt ~ Brand_Trend + Resolution_Trend + Price", data=df).fit()
    print(model_1.summary())
    print(f"Model 1: n={len(df)}, R²={model_1.rsquared:.3f}")

    plot_coefficients(
        model_1,
        title="Independent Effect of Each Factor on Log(Review Count)",
        filename="model_1_coefficients.png"
    )
    
    df_2 = df.dropna(subset=["Size_Trend"])

    model_2 = smf.ols("log_rt ~ Size_Trend + Price", data=df_2).fit()
    print(model_2.summary())
    print(f"Model 2: n={len(df_2)}, R²={model_2.rsquared:.3f}")

    plot_coefficients(
        model_2,
        title="Independent Effect of Screen Size Trend on Log(Review Count)",
        filename="model_2_coefficients.png"
    )

    return model_1, model_2


