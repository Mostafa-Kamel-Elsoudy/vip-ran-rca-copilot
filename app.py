from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_sample_data, merge_complaints_with_kpis
from src.rca_rules import apply_rca
from src.ml_model import train_rca_model, add_ml_predictions
from src.report_generator import generate_html_report
from src.llm_summary import generate_management_summary

BASE_PATH = Path(__file__).resolve().parent

st.set_page_config(page_title="VIP RAN RCA Copilot", layout="wide")

st.title("VIP RAN Complaint RCA Copilot")
st.caption("Python + RAN Optimization + Automation + ML + Reporting")

st.sidebar.header("Data Source")
use_sample = st.sidebar.checkbox("Use sample synthetic data", value=True)

if use_sample:
    complaints, kpis, alarms = load_sample_data(BASE_PATH)
else:
    complaints_file = st.sidebar.file_uploader("Upload complaints CSV", type=["csv"])
    kpis_file = st.sidebar.file_uploader("Upload KPIs CSV", type=["csv"])
    alarms_file = st.sidebar.file_uploader("Upload alarms CSV", type=["csv"])

    if not complaints_file or not kpis_file or not alarms_file:
        st.info("Upload the three CSV files or use the sample synthetic data.")
        st.stop()

    complaints = pd.read_csv(complaints_file)
    kpis = pd.read_csv(kpis_file)
    alarms = pd.read_csv(alarms_file)

merged = merge_complaints_with_kpis(complaints, kpis, alarms)
results = apply_rca(merged)

model, importance, model_report = train_rca_model(results)
results = add_ml_predictions(results, model)
results["management_summary"] = results.apply(generate_management_summary, axis=1)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "RCA Results", "ML Insights", "Charts", "Report"
])

with tab1:
    st.subheader("Input Data Preview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Complaints", len(complaints))
    c2.metric("Cells", kpis["cell_name"].nunique())
    c3.metric("Active Alarms", len(alarms[alarms["status"].str.lower() == "active"]))
    c4.metric("Detected RCA Classes", results["predicted_root_cause"].nunique())

    st.write("Complaints sample")
    st.dataframe(complaints.head(10), use_container_width=True)

    st.write("KPI sample")
    st.dataframe(kpis.head(10), use_container_width=True)

with tab2:
    st.subheader("Automated RCA Results")
    selected_cols = [
        "complaint_id", "customer_segment", "area", "serving_cell",
        "complaint_type", "priority", "predicted_root_cause",
        "rule_confidence", "rca_reasons", "recommended_action",
        "ml_predicted_root_cause", "ml_confidence"
    ]
    st.dataframe(results[selected_cols], use_container_width=True)

    st.download_button(
        "Download RCA Results CSV",
        results[selected_cols].to_csv(index=False).encode("utf-8"),
        file_name="vip_rca_results.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("Machine Learning Insights")
    if importance is not None:
        st.write("Feature Importance")
        st.dataframe(importance, use_container_width=True)

        fig, ax = plt.subplots()
        ax.barh(importance["feature"], importance["importance"])
        ax.invert_yaxis()
        ax.set_xlabel("Importance")
        ax.set_title("RCA Model Feature Importance")
        st.pyplot(fig)

        with st.expander("Classification Report"):
            st.text(model_report)
    else:
        st.warning(model_report)

with tab4:
    st.subheader("Operational Charts")

    dist = results["predicted_root_cause"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.bar(dist.index, dist.values)
    ax1.set_ylabel("Complaint Count")
    ax1.set_title("Root Cause Distribution")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    worst_cells = (
        results.groupby("serving_cell")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )
    fig2, ax2 = plt.subplots()
    ax2.bar(worst_cells.index, worst_cells.values)
    ax2.set_ylabel("Complaint Count")
    ax2.set_title("Top Complaint Cells")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

with tab5:
    st.subheader("Generate HTML Report")
    report_path = BASE_PATH / "reports" / "vip_ran_rca_report.html"
    if st.button("Generate Report"):
        generate_html_report(results, report_path)
        st.success(f"Report generated: {report_path}")

    if report_path.exists():
        st.download_button(
            "Download HTML Report",
            report_path.read_bytes(),
            file_name="vip_ran_rca_report.html",
            mime="text/html"
        )

    st.write("Sample management summaries")
    st.dataframe(
        results[["complaint_id", "management_summary"]].head(10),
        use_container_width=True
    )