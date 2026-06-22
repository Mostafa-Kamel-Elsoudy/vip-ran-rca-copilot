from pathlib import Path
from datetime import datetime
import pandas as pd
from jinja2 import Template

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>VIP RAN RCA Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 32px; color: #222; }
        h1 { color: #7b1b1b; }
        .summary { background: #f5f5f5; padding: 16px; border-radius: 8px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 13px; }
        th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
        th { background: #eee; }
        .high { color: #9b0000; font-weight: bold; }
    </style>
</head>
<body>
    <h1>VIP RAN Complaint RCA Report</h1>
    <p>Generated at: {{ generated_at }}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p>Total complaints analyzed: <b>{{ total }}</b></p>
        <p>Top root cause: <b>{{ top_root_cause }}</b></p>
        <p>Most affected area: <b>{{ top_area }}</b></p>
    </div>

    <h2>Root Cause Distribution</h2>
    {{ distribution_table }}

    <h2>Detailed RCA Results</h2>
    {{ details_table }}
</body>
</html>
"""

def generate_html_report(df: pd.DataFrame, output_path: str | Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    distribution = (
        df["predicted_root_cause"]
        .value_counts()
        .reset_index()
    )
    distribution.columns = ["Root Cause", "Complaint Count"]

    top_root_cause = distribution.iloc[0]["Root Cause"] if len(distribution) else "N/A"
    top_area = df["area"].value_counts().index[0] if "area" in df.columns and len(df) else "N/A"

    details_cols = [
        "complaint_id", "customer_segment", "area", "serving_cell",
        "complaint_type", "priority", "predicted_root_cause",
        "rule_confidence", "rca_reasons", "recommended_action"
    ]
    details = df[details_cols].copy()
    details["rule_confidence"] = (details["rule_confidence"] * 100).round(1).astype(str) + "%"

    html = Template(HTML_TEMPLATE).render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total=len(df),
        top_root_cause=top_root_cause,
        top_area=top_area,
        distribution_table=distribution.to_html(index=False, escape=False),
        details_table=details.to_html(index=False, escape=False)
    )

    output_path.write_text(html, encoding="utf-8")
    return output_path