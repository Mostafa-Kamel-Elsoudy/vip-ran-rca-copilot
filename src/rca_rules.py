def diagnose_row(row):
    reasons = []
    recommendations = []

    rsrp = row.get("rsrp_dbm")
    sinr = row.get("sinr_db")
    prb = row.get("prb_utilization_pct")
    dl_tp = row.get("dl_throughput_mbps")
    drop = row.get("drop_rate_pct")
    ho_sr = row.get("handover_success_rate_pct")
    alarm_count = row.get("active_alarm_count", 0)

    # Priority order: active alarms first, then severe KPI symptoms.
    if alarm_count and alarm_count > 0:
        reasons.append(f"Active alarm detected: {row.get('active_alarms', 'Unknown')}")
        recommendations.append("Check site health, hardware, power, transmission, and alarm clearance.")
        return "Site / Alarm Issue", 0.92, reasons, recommendations

    if rsrp is not None and rsrp < -105:
        reasons.append(f"Weak RSRP = {rsrp:.1f} dBm, indicating poor coverage.")
        recommendations.append("Check coverage footprint, antenna tilt/azimuth, site distance, and indoor penetration.")
        return "Coverage Issue", 0.88, reasons, recommendations

    if sinr is not None and sinr < 5 and rsrp is not None and rsrp >= -105:
        reasons.append(f"Low SINR = {sinr:.1f} dB while RSRP is acceptable, indicating interference/noise.")
        recommendations.append("Check interference, PCI planning, overshooting cells, and neighboring relations.")
        return "Interference Issue", 0.86, reasons, recommendations

    if prb is not None and prb > 85 and dl_tp is not None and dl_tp < 5:
        reasons.append(f"High PRB utilization = {prb:.1f}% with low DL throughput = {dl_tp:.1f} Mbps.")
        recommendations.append("Check congestion trend, load balancing, capacity expansion, and carrier utilization.")
        return "Congestion Issue", 0.90, reasons, recommendations

    if ho_sr is not None and ho_sr < 90:
        reasons.append(f"Low handover success rate = {ho_sr:.1f}%.")
        recommendations.append("Check neighbor definitions, handover parameters, coverage overlap, and mobility traces.")
        return "Handover / Mobility Issue", 0.84, reasons, recommendations

    if drop is not None and drop > 5:
        reasons.append(f"High drop rate = {drop:.1f}%.")
        recommendations.append("Check radio link failures, coverage/interference, alarms, and trace logs.")
        return "Quality / Drop Issue", 0.80, reasons, recommendations

    reasons.append("No severe KPI degradation detected from the available data.")
    recommendations.append("Perform deeper E2E trace analysis and validate with recent KPIs/drive test if complaint persists.")
    return "No Clear RCA / Needs Trace Analysis", 0.65, reasons, recommendations


def apply_rca(df):
    results = df.apply(lambda row: diagnose_row(row), axis=1)
    df = df.copy()
    df["predicted_root_cause"] = [r[0] for r in results]
    df["rule_confidence"] = [r[1] for r in results]
    df["rca_reasons"] = [" | ".join(r[2]) for r in results]
    df["recommended_action"] = [" | ".join(r[3]) for r in results]
    return df