import pandas as pd
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def sanitize_sheet_name(name):
    """Sanitize sheet name to meet Excel constraints."""
    name = re.sub(r'[\\/*?:\[\]]', '', name)
    return name[:31]

def generate_report(segments, all_issues):
    """
    Generate an Excel report where each issue_type is placed in a separate sheet.
    If there are no issues, creates a summary sheet saying "No issues found".
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"QA_Report_{timestamp}.xlsx"
    output_path = os.path.join("static", "qa_reports")
    os.makedirs(output_path, exist_ok=True)
    report_path = os.path.join(output_path, filename)

    logger.info(f"Generating report at: {report_path}")
    sheets_written = 0

    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        if isinstance(all_issues, list):
            # Group issues by 'issue_type' key
            issues_by_type = {}
            for issue in all_issues:
                issue_type = issue.get("issue_type", "Unknown")
                issues_by_type.setdefault(issue_type, []).append(issue)

            for issue_type, issues in issues_by_type.items():
                df = pd.DataFrame(issues)
                if not df.empty:
                    df = df.astype(str)
                    sheet_name = sanitize_sheet_name(issue_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheets_written += 1

        elif isinstance(all_issues, dict):
            # Already grouped
            for issue_type, issues in all_issues.items():
                df = pd.DataFrame(issues)
                if not df.empty:
                    df = df.astype(str)
                    sheet_name = sanitize_sheet_name(issue_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheets_written += 1

        if sheets_written == 0:
            pd.DataFrame([{"Info": "✅ No issues found."}]).to_excel(writer, sheet_name="Summary", index=False)

    return report_path
