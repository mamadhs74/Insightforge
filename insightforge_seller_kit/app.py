from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from insightforge.analyzer import AnalysisSettings, analyze_dataframe, safe_read_table
from insightforge.report import render_html_report

st.set_page_config(page_title="InsightForge Engineering Edition", page_icon="📊", layout="wide")

st.title("InsightForge Engineering Edition")
st.caption("Turn raw CSV/XLSX engineering, research, telemetry, and lab data into structured technical reports.")

with st.sidebar:
    st.header("Analysis settings")
    contamination = st.slider("Expected anomaly rate", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
    max_corr = st.slider("Max correlation pairs", min_value=5, max_value=30, value=12, step=1)
    st.markdown("---")
    st.markdown("**Best for:** test-bench exports, sensor logs, experiment tables, telemetry CSVs, simulation result tables.")

uploaded = st.file_uploader("Upload CSV, XLS, or XLSX", type=["csv", "xls", "xlsx"])

if uploaded is None:
    st.info("Upload a dataset to generate a technical report. A sample dataset is included in /sample_data.")
    sample_path = Path("sample_data/sample_telemetry.csv")
    if sample_path.exists():
        st.download_button("Download sample telemetry CSV", sample_path.read_bytes(), "sample_telemetry.csv", "text/csv")
    st.stop()

try:
    raw_df = safe_read_table(uploaded)
    analysis = analyze_dataframe(raw_df, AnalysisSettings(anomaly_contamination=contamination, max_correlation_pairs=max_corr))
    df = analysis["dataframe"]
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not analyze file: {exc}")
    st.stop()

rows, cols = analysis["shape"]["rows"], analysis["shape"]["columns"]
num_cols = analysis["types"]["numeric"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows", rows)
m2.metric("Columns", cols)
m3.metric("Numeric columns", len(num_cols))
m4.metric("Anomaly candidates", analysis["anomaly_count"])

st.subheader("Executive interpretation")
for rec in analysis["recommendations"]:
    st.write(f"- {rec}")

tabs = st.tabs(["Overview", "Quality", "Correlations", "Anomalies", "Charts", "Export"])

with tabs[0]:
    st.subheader("Dataset preview")
    st.dataframe(df.head(100), use_container_width=True)
    st.subheader("Numeric summary")
    if analysis["numeric_summary"].empty:
        st.warning("No numeric columns found.")
    else:
        st.dataframe(analysis["numeric_summary"], use_container_width=True)

with tabs[1]:
    st.subheader("Data quality checks")
    if analysis["quality_checks"]:
        st.dataframe(pd.DataFrame(analysis["quality_checks"]), use_container_width=True)
    else:
        st.success("No major structural data-quality issue detected.")

with tabs[2]:
    st.subheader("Top numeric correlations")
    if analysis["correlations"].empty:
        st.warning("Not enough numeric columns for correlation analysis.")
    else:
        st.dataframe(analysis["correlations"], use_container_width=True)
        fig = px.bar(
            analysis["correlations"],
            x="abs_correlation",
            y=analysis["correlations"].apply(lambda r: f"{r['feature_a']} × {r['feature_b']}", axis=1),
            orientation="h",
            title="Strongest numeric relationships",
            labels={"y": "Feature pair", "abs_correlation": "Absolute correlation"},
        )
        st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("Anomaly candidates")
    if analysis["anomalies"].empty:
        st.info("No anomaly candidates detected or dataset too small.")
    else:
        st.dataframe(analysis["anomalies"], use_container_width=True)
        annotated_csv = analysis["annotated_dataframe"].to_csv(index=False).encode("utf-8")
        st.download_button("Download dataset with anomaly flags", annotated_csv, "insightforge_anomaly_flags.csv", "text/csv")

with tabs[4]:
    st.subheader("Quick charts")
    if len(num_cols) == 0:
        st.warning("No numeric columns available for plotting.")
    elif len(num_cols) == 1:
        selected = st.selectbox("Column", num_cols)
        st.plotly_chart(px.histogram(df, x=selected, title=f"Distribution of {selected}"), use_container_width=True)
    else:
        c1, c2 = st.columns(2)
        x_col = c1.selectbox("X axis", num_cols, index=0)
        y_col = c2.selectbox("Y axis", num_cols, index=1)
        st.plotly_chart(px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}"), use_container_width=True)
        hist_col = st.selectbox("Distribution column", num_cols)
        st.plotly_chart(px.histogram(df, x=hist_col, title=f"Distribution of {hist_col}"), use_container_width=True)

with tabs[5]:
    st.subheader("Export report")
    report_title = st.text_input("Report title", "InsightForge Technical Data Report")
    html = render_html_report(analysis, title=report_title)
    st.download_button("Download HTML report", html.encode("utf-8"), "insightforge_report.html", "text/html")
    st.caption("Tip: open the HTML report in a browser and print/save as PDF for client delivery.")
