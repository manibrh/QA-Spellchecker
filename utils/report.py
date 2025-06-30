# utils/report.py

import pandas as pd
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def sanitize_sheet_name(name):
    name = re.sub(r'[\\/*?:\[\]]', '', name)
    return name[:31]

def generate_report(segments, all_issues):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"QA_Report_{timestamp}.xlsx"
    output_path = os.path.join("static", "qa_reports")
    os.makedirs(output_path, exist_ok=True)
    report_path = os.path.join(output_path, filename)

    logger.info(f"Generating report at: {report_path}")
    sheets_written = 0

    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        # If issues are grouped by type (dict)
        if isinstance(all_issues, dict):
            for issue_type, issues in all_issues.items():
                df = pd.DataFrame(issues)
                if not df.empty:
                    df = df.astype(str)
                    sheet_name = sanitize_sheet_name(issue_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheets_written += 1

        # If it's a flat list of issues
        elif isinstance(all_issues, list):
            df = pd.DataFrame(all_issues)
            if not df.empty:
                df = df.astype(str)
                df.to_excel(writer, sheet_name="Issues", index=False)
                sheets_written += 1

        # If no issues found, still write a summary
        if sheets_written == 0:
            pd.DataFrame([{"Info": "✅ No issues found."}]).to_excel(writer, sheet_name="Summary", index=False)

    return report_path
