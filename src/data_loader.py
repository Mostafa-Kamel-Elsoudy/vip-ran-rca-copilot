from pathlib import Path
import pandas as pd

def load_sample_data(base_path: str | Path = "."):
    base_path = Path(base_path)
    complaints = pd.read_csv(base_path / "data" / "sample_complaints.csv")
    kpis = pd.read_csv(base_path / "data" / "sample_kpis.csv")
    alarms = pd.read_csv(base_path / "data" / "sample_alarms.csv")
    return complaints, kpis, alarms

def merge_complaints_with_kpis(complaints: pd.DataFrame, kpis: pd.DataFrame, alarms: pd.DataFrame) -> pd.DataFrame:
    merged = complaints.merge(
        kpis,
        left_on="serving_cell",
        right_on="cell_name",
        how="left",
        suffixes=("", "_kpi")
    )

    active_alarms = (
        alarms[alarms["status"].str.lower() == "active"]
        .groupby("cell_name")
        .agg(
            active_alarm_count=("alarm_name", "count"),
            active_alarms=("alarm_name", lambda x: ", ".join(sorted(set(x))))
        )
        .reset_index()
    )

    merged = merged.merge(
        active_alarms,
        left_on="serving_cell",
        right_on="cell_name",
        how="left",
        suffixes=("", "_alarm")
    )

    merged["active_alarm_count"] = merged["active_alarm_count"].fillna(0).astype(int)
    merged["active_alarms"] = merged["active_alarms"].fillna("None")
    return merged