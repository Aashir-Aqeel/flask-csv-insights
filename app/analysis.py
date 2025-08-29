# app/analysis.py
import io, json, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-GUI backend for servers
import matplotlib.pyplot as plt
import seaborn as sns

def _png_bytes_from_current_fig():
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=140)
    plt.close()
    return buf.getvalue()

def run_basic_eda(df: pd.DataFrame):
    # Coerce obvious date columns
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass

    summary = {
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "missing": df.isna().sum().to_dict(),
        "numeric_summary": df.select_dtypes(include="number").describe().to_dict(),
    }

    charts = []

    # 1) Correlation heatmap for numeric columns
    num = df.select_dtypes(include="number")
    if not num.empty and num.shape[1] > 1:
        plt.figure()
        sns.heatmap(num.corr(numeric_only=True), annot=False)
        plt.title("Correlation Heatmap")
        charts.append(("Correlation Heatmap", _png_bytes_from_current_fig()))

    # 2) Bar chart for first categorical column
    cat = df.select_dtypes(include=["object", "category"])
    if not cat.empty:
        c0 = cat.columns[0]
        plt.figure()
        df[c0].value_counts().head(10).plot(kind="bar")
        plt.title(f"Top {c0} values")
        charts.append((f"Top {c0} values", _png_bytes_from_current_fig()))

    # 3) Simple daily counts if a datetime column exists
    date_cols = [c for c in df.columns if np.issubdtype(df[c].dtype, np.datetime64)]
    if date_cols:
        d0 = date_cols[0]
        plt.figure()
        df.groupby(pd.Grouper(key=d0, freq="D")).size().plot()
        plt.title(f"Rows per day ({d0})")
        charts.append((f"Rows per day ({d0})", _png_bytes_from_current_fig()))

    return summary, charts
