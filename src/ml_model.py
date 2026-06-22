import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

FEATURES = [
    "rsrp_dbm",
    "rsrq_db",
    "sinr_db",
    "dl_throughput_mbps",
    "ul_throughput_mbps",
    "prb_utilization_pct",
    "drop_rate_pct",
    "handover_success_rate_pct",
    "active_alarm_count",
    "complaints_count",
]

def train_rca_model(df: pd.DataFrame):
    # In this prototype, we use rule-based labels as pseudo-labels.
    # With real historical data, replace predicted_root_cause with the final validated RCA label.
    X = df[FEATURES].fillna(0)
    y = df["predicted_root_cause"]

    if y.nunique() < 2:
        return None, None, "Not enough label diversity to train a model."

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, zero_division=0)

    importance = (
        pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    return model, importance, report

def add_ml_predictions(df: pd.DataFrame, model):
    if model is None:
        df["ml_predicted_root_cause"] = df["predicted_root_cause"]
        df["ml_confidence"] = df["rule_confidence"]
        return df

    X = df[FEATURES].fillna(0)
    proba = model.predict_proba(X)
    preds = model.predict(X)

    df = df.copy()
    df["ml_predicted_root_cause"] = preds
    df["ml_confidence"] = proba.max(axis=1)
    return df