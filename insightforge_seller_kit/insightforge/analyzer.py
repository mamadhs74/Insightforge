from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


@dataclass
class AnalysisSettings:
    anomaly_contamination: float = 0.05
    max_correlation_pairs: int = 12
    max_example_rows: int = 10


def safe_read_table(uploaded_file_or_path: Any) -> pd.DataFrame:
    """Read CSV/XLS/XLSX with practical fallbacks for messy user files."""
    name = getattr(uploaded_file_or_path, "name", str(uploaded_file_or_path)).lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file_or_path)

    encodings = ["utf-8", "utf-8-sig", "latin1"]
    separators = [None, ",", ";", "\t", "|"]
    last_error: Exception | None = None
    for enc in encodings:
        for sep in separators:
            try:
                if hasattr(uploaded_file_or_path, "seek"):
                    uploaded_file_or_path.seek(0)
                return pd.read_csv(uploaded_file_or_path, sep=sep, engine="python", encoding=enc)
            except Exception as exc:  # noqa: BLE001 - fallback reader intentionally broad
                last_error = exc
    raise ValueError(f"Could not read file. Last parser error: {last_error}")


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names, remove fully empty rows/columns, preserve original values."""
    if df.empty:
        raise ValueError("The uploaded file contains no rows.")

    out = df.copy()
    out.columns = [str(c).strip() if str(c).strip() else f"unnamed_{i}" for i, c in enumerate(out.columns)]
    out = out.dropna(axis=0, how="all").dropna(axis=1, how="all")

    if out.empty or out.shape[1] == 0:
        raise ValueError("The uploaded file has no usable rows or columns after removing empty data.")
    return out


def infer_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    datetime_cols: list[str] = []
    categorical_cols: list[str] = []

    for col in df.columns:
        if col in numeric_cols:
            continue
        sample = df[col].dropna().astype(str).head(50)
        # Avoid noisy date parsing on arbitrary text labels. Only try when values look date-like.
        looks_date_like = sample.str.contains(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", regex=True).mean() > 0.5 if len(sample) else False
        if len(sample) >= 3 and looks_date_like:
            parsed = pd.to_datetime(sample, errors="coerce", utc=False)
            if parsed.notna().mean() > 0.7:
                datetime_cols.append(col)
                continue
        categorical_cols.append(col)

    return {
        "numeric": numeric_cols,
        "datetime": datetime_cols,
        "categorical": categorical_cols,
    }


def data_quality_checks(df: pd.DataFrame) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    total_rows = len(df)

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        checks.append({
            "severity": "warning",
            "issue": "Duplicate rows",
            "detail": f"{duplicate_count} duplicate rows detected ({duplicate_count / max(total_rows, 1):.1%}).",
        })

    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing:
            severity = "critical" if missing / max(total_rows, 1) > 0.3 else "warning"
            checks.append({
                "severity": severity,
                "issue": "Missing values",
                "detail": f"Column '{col}' has {missing} missing values ({missing / max(total_rows, 1):.1%}).",
            })
        if df[col].nunique(dropna=True) <= 1:
            checks.append({
                "severity": "warning",
                "issue": "Constant column",
                "detail": f"Column '{col}' has one or zero unique non-empty values.",
            })

    return checks


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    nums = df.select_dtypes(include=[np.number])
    if nums.empty:
        return pd.DataFrame()
    summary = nums.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    summary["missing"] = nums.isna().sum()
    summary["missing_%"] = nums.isna().mean() * 100
    summary["unique"] = nums.nunique(dropna=True)
    return summary.reset_index().rename(columns={"index": "column"})


def top_correlations(df: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    nums = df.select_dtypes(include=[np.number])
    if nums.shape[1] < 2:
        return pd.DataFrame(columns=["feature_a", "feature_b", "correlation", "abs_correlation"])

    corr = nums.corr(numeric_only=True).replace([np.inf, -np.inf], np.nan)
    rows: list[dict[str, Any]] = []
    cols = corr.columns.tolist()
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            val = corr.loc[a, b]
            if pd.notna(val):
                rows.append({"feature_a": a, "feature_b": b, "correlation": float(val), "abs_correlation": abs(float(val))})
    return pd.DataFrame(rows).sort_values("abs_correlation", ascending=False).head(limit).reset_index(drop=True)


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> tuple[pd.DataFrame, pd.DataFrame]:
    nums = df.select_dtypes(include=[np.number]).copy()
    if nums.shape[1] == 0 or len(nums) < 10:
        out = df.copy()
        out["insightforge_anomaly"] = False
        out["insightforge_anomaly_score"] = np.nan
        return out, pd.DataFrame()

    contamination = min(max(float(contamination), 0.001), 0.25)
    filled = nums.replace([np.inf, -np.inf], np.nan)
    filled = filled.fillna(filled.median(numeric_only=True)).fillna(0)
    scaled = StandardScaler().fit_transform(filled)

    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    labels = model.fit_predict(scaled)
    scores = -model.score_samples(scaled)

    out = df.copy()
    out["insightforge_anomaly"] = labels == -1
    out["insightforge_anomaly_score"] = scores

    anomalous = out[out["insightforge_anomaly"]].sort_values("insightforge_anomaly_score", ascending=False)
    return out, anomalous


def generate_recommendations(df: pd.DataFrame, checks: list[dict[str, str]], correlations: pd.DataFrame, anomaly_count: int) -> list[str]:
    recs: list[str] = []
    if checks:
        critical = sum(1 for c in checks if c["severity"] == "critical")
        if critical:
            recs.append("Resolve critical data-quality issues before using this dataset for final engineering or business decisions.")
        else:
            recs.append("Review warnings before presenting the dataset; most issues appear manageable for exploratory analysis.")
    else:
        recs.append("No major structural data-quality issues were detected in the uploaded table.")

    if anomaly_count > 0:
        recs.append(f"Inspect the {anomaly_count} anomaly candidate rows; they may indicate measurement spikes, process events, or data-entry errors.")

    if not correlations.empty and correlations.iloc[0]["abs_correlation"] >= 0.8:
        top = correlations.iloc[0]
        recs.append(f"Strong relationship detected between '{top['feature_a']}' and '{top['feature_b']}'. Consider including it in the technical interpretation.")

    if df.select_dtypes(include=[np.number]).shape[1] < 2:
        recs.append("Add more numeric measurements if you need correlation, anomaly, or trend analysis.")
    return recs


def analyze_dataframe(df: pd.DataFrame, settings: AnalysisSettings | None = None) -> dict[str, Any]:
    settings = settings or AnalysisSettings()
    clean = normalize_dataframe(df)
    types = infer_column_types(clean)
    checks = data_quality_checks(clean)
    summary = numeric_summary(clean)
    correlations = top_correlations(clean, settings.max_correlation_pairs)
    annotated, anomalies = detect_anomalies(clean, settings.anomaly_contamination)

    result = {
        "dataframe": clean,
        "annotated_dataframe": annotated,
        "shape": {"rows": int(clean.shape[0]), "columns": int(clean.shape[1])},
        "types": types,
        "quality_checks": checks,
        "numeric_summary": summary,
        "correlations": correlations,
        "anomalies": anomalies.head(settings.max_example_rows),
        "anomaly_count": int(annotated["insightforge_anomaly"].sum()),
        "recommendations": generate_recommendations(clean, checks, correlations, int(annotated["insightforge_anomaly"].sum())),
    }
    return result
