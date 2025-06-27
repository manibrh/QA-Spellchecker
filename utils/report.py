# utils/report.py
import pandas as pd
import os

def generate_report(segments, all_issues):
    grouped = {}
    for issue in all_issues:
        issue_type = issue['issue_type']
        if issue_type not in grouped:
            grouped[issue_type] = []
        seg = next((s for s in segments if s['id'] == issue['id']), {})
        grouped[issue_type].append({
            "Segment ID": issue['id'],
            "Source": seg.get('source'),
            "Target": seg.get('target'),
            "Issue Type": issue_type,
            "Detail": issue['detail']
        })

    with pd.ExcelWriter(os.path.join("uploads", "QA_Report.xlsx"), engine='openpyxl') as writer:
        for issue_type, rows in grouped.items():
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=issue_type[:31], index=False)  # Excel sheet name limit

    return os.path.join("uploads", "QA_Report.xlsx")