def generate_management_summary(row):
    # This is a safe placeholder for an LLM layer.
    # In a real version, you can send the structured RCA output to an LLM
    # and ask it to produce a management-friendly summary.
    return (
        f"Complaint {row['complaint_id']} on cell {row['serving_cell']} is most likely caused by "
        f"{row['predicted_root_cause']}. Evidence: {row['rca_reasons']} "
        f"Recommended action: {row['recommended_action']}"
    )