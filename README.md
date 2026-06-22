# VIP RAN Complaint RCA Copilot

A proof-of-work prototype for automating first-level analysis of VIP radio network complaints.

This project demonstrates how Python automation can support RAN optimization workflows by correlating:
- VIP complaints
- Cell-level radio KPIs
- Active alarms

The tool then performs:
- Rule-based Root Cause Analysis (RCA)
- Recommended action generation
- ML feature-importance demo
- HTML report generation

> The included data is synthetic and does not contain any confidential operator information.

---

## Why this project exists

VIP complaint handling often requires manual checks across complaints, KPIs, alarms, traces, and reports.  
This prototype shows how a Python-based automation layer can reduce repetitive work, standardize first-level RCA, and produce a clear technical report.

---

## Main workflow

```text
Complaints CSV
      ↓
Serving Cell Mapping
      ↓
KPI + Alarm Correlation
      ↓
Rule-Based RCA
      ↓
ML Feature Importance Demo
      ↓
Recommended Action
      ↓
HTML Report
```

---

## RCA logic examples

```text
Active alarm exists                         → Site / Alarm Issue
RSRP < -105 dBm                             → Coverage Issue
SINR < 5 dB with acceptable RSRP             → Interference Issue
PRB utilization > 85% and low throughput     → Congestion Issue
Handover success rate < 90%                  → Handover / Mobility Issue
```

---

## Project structure

```text
vip_ran_rca_copilot/
├── app.py
├── requirements.txt
├── data/
│   ├── sample_complaints.csv
│   ├── sample_kpis.csv
│   └── sample_alarms.csv
├── reports/
│   └── sample_vip_rca_report.html
└── src/
    ├── data_loader.py
    ├── rca_rules.py
    ├── ml_model.py
    ├── report_generator.py
    └── llm_summary.py
```

---

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On PowerShell, if activation is blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

Or run Streamlit without activation:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

---

## Expected input files

### `sample_complaints.csv`

```text
complaint_id, customer_segment, area, serving_cell, complaint_type, priority
```

### `sample_kpis.csv`

```text
cell_name, rsrp_dbm, rsrq_db, sinr_db, dl_throughput_mbps,
ul_throughput_mbps, prb_utilization_pct, drop_rate_pct,
handover_success_rate_pct
```

### `sample_alarms.csv`

```text
cell_name, alarm_name, severity, status
```

---

## Notes

This is not production-ready software. It is a technical proof-of-work designed to demonstrate:
- Python development skills
- Telecom/RAN KPI understanding
- Automation thinking
- RCA workflow awareness
- Ability to turn technical data into a useful report

In a production environment, the rule base should be validated by radio engineers and the ML model should be trained on historical validated RCA labels.
