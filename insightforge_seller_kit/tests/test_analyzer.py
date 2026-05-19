import numpy as np
import pandas as pd

from insightforge.analyzer import analyze_dataframe, normalize_dataframe, top_correlations
from insightforge.report import render_html_report


def test_analyze_dataframe_basic():
    df = pd.DataFrame({
        "speed": [10, 11, 12, 13, 1000, 14, 15, 16, 17, 18, 19, 20],
        "temp": [20, 21, 20, 22, 80, 21, 20, 23, 22, 21, 20, 22],
        "label": ["a"] * 12,
    })
    result = analyze_dataframe(df)
    assert result["shape"]["rows"] == 12
    assert "speed" in result["types"]["numeric"]
    assert "numeric_summary" in result
    assert "recommendations" in result


def test_normalize_removes_empty_rows_and_columns():
    df = pd.DataFrame({"a": [1, 2, np.nan], "empty": [np.nan, np.nan, np.nan]})
    out = normalize_dataframe(df)
    assert "empty" not in out.columns
    assert len(out) == 2


def test_top_correlations_output_columns():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [2, 4, 6], "c": [3, 1, 2]})
    corr = top_correlations(df)
    assert {"feature_a", "feature_b", "correlation", "abs_correlation"}.issubset(corr.columns)
    assert not corr.empty


def test_html_report_renders():
    df = pd.DataFrame({"a": range(20), "b": range(20, 40)})
    result = analyze_dataframe(df)
    html = render_html_report(result)
    assert "InsightForge" in html
    assert "Executive interpretation" in html
