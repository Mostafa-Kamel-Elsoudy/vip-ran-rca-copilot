# VIP RAN Complaint RCA Copilot

Python tool that turns three CSV feeds (VIP complaints, cell KPIs, alarms) into a root cause, a recommended action, and an on-call style RCA report for each complaint. Built around RAN operations work, with the same shape as an SRE triage loop: ingest telemetry, correlate it to the affected component, apply ordered rules, hand off evidence.

All bundled data is synthetic. No operator data is included.

## What it does

1. Ingest: loads complaints, per-cell KPIs and alarms (`src/data_loader.py`).
2. Correlate: joins each complaint to its serving cell's KPIs, and counts and names the cell's active alarms (alarm rows with `status` equal to `active`, case-insensitive).
3. Isolate the fault: evaluates deterministic rules in a fixed priority order and stops at the first match (`src/rca_rules.py`).
4. Explain: each result carries a rule confidence, the evidence string that triggered it, and a recommended action.
5. Report: HTML report with an executive summary, root cause distribution and a per-complaint RCA table (`src/report_generator.py`), plus CSV export from the Streamlit app.
6. ML demo: trains a RandomForest on the rule outputs used as pseudo-labels and shows feature importance (`src/ml_model.py`). It illustrates the approach and is not validated against real RCA labels.

## Rule order

Rules are plain Python in `diagnose_row`. The first match wins.

| Order | Condition | Root cause | Confidence |
| --- | --- | --- | --- |
| 1 | one or more active alarms on the serving cell | Site / Alarm Issue | 0.92 |
| 2 | `rsrp_dbm` < -105 | Coverage Issue | 0.88 |
| 3 | `sinr_db` < 5 and `rsrp_dbm` >= -105 | Interference Issue | 0.86 |
| 4 | `prb_utilization_pct` > 85 and `dl_throughput_mbps` < 5 | Congestion Issue | 0.90 |
| 5 | `handover_success_rate_pct` < 90 | Handover / Mobility Issue | 0.84 |
| 6 | `drop_rate_pct` > 5 | Quality / Drop Issue | 0.80 |
| 7 | none of the above | No Clear RCA / Needs Trace Analysis | 0.65 |

Each root cause maps to a specific recommended action, for example alarm clearance and site health checks for rule 1, or neighbor definitions and handover parameters for rule 5.

On the bundled sample (60 complaints, 60 cells, 15 alarms) the rules classify 10 as Site / Alarm, 9 as Coverage, 9 as Handover / Mobility, 8 as Interference, 1 as Quality / Drop, 1 as Congestion, and leave 22 as No Clear RCA.

## Data format

`data/sample_complaints.csv`

```text
complaint_id, customer_segment, area, serving_cell, complaint_type, priority
```

`data/sample_kpis.csv`

```text
cell_name, area, vendor, rsrp_dbm, rsrq_db, sinr_db, dl_throughput_mbps,
ul_throughput_mbps, prb_utilization_pct, drop_rate_pct,
handover_success_rate_pct, complaints_count
```

`data/sample_alarms.csv`

```text
cell_name, alarm_name, severity, status
```

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app has five tabs: Overview, RCA Results, ML Insights, Charts and Report. The Report tab writes `reports/vip_ran_rca_report.html`. A pre-generated example is in `reports/sample_vip_rca_report.html`.

To run the rule engine and report without Streamlit:

```python
from src.data_loader import load_sample_data, merge_complaints_with_kpis
from src.rca_rules import apply_rca
from src.report_generator import generate_html_report

complaints, kpis, alarms = load_sample_data(".")
results = apply_rca(merge_complaints_with_kpis(complaints, kpis, alarms))
generate_html_report(results, "reports/rca_report.html")
```

## Project structure

```text
app.py                   Streamlit UI
requirements.txt
data/                    synthetic complaints, KPIs, alarms
reports/                 sample HTML report
src/
  data_loader.py         CSV loading, complaint/KPI/alarm join
  rca_rules.py           ordered rule evaluation
  ml_model.py            RandomForest on pseudo-labels, feature importance
  report_generator.py    Jinja2 HTML report
  llm_summary.py         templated management summary (no LLM call)
```

## Limits

- The rule thresholds are starting values and need review by radio engineers before operational use.
- `src/llm_summary.py` builds a text summary from a template. It does not call a language model.
- The ML step learns from the rule output, so it reproduces the rules. With validated historical RCA labels it could be trained on those instead.
