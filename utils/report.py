import pandas as pd
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def sanitize_sheet_name(name):
    name = re.sub(r'[\\/*?:\[\]]', '', name)
    return name[:31]

def generate_report(segments, all_issues, return_preview=False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"QA_Report_{timestamp}.xlsx"
    output_dir = os.path.join("static", "qa_reports")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, filename)

    preview_lines = []
    sheets_written = 0

    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        if isinstance(all_issues, dict):
            for issue_type, issues in all_issues.items():
                df = pd.DataFrame(issues)
                if not df.empty:
                    sheet_name = sanitize_sheet_name(issue_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheets_written += 1

                    # Preview content
                    for row in issues:
                        preview_lines.append(f"{issue_type} - Segment {row.get('id', '')}: {row.get('issue', '')}")
        
        elif isinstance(all_issues, list):
            df = pd.DataFrame(all_issues)
            if not df.empty:
                df.to_excel(writer, sheet_name="Issues", index=False)
                sheets_written += 1
                for row in all_issues:
                    preview_lines.append(f"Segment {row.get('id', '')}: {row.get('issue', '')}")

        else:
            logger.error("Unsupported format for all_issues. Must be dict or list.")

        if sheets_written == 0:
            pd.DataFrame([{"Info": "✅ No issues found."}]).to_excel(writer, sheet_name="Summary", index=False)
            preview_lines.append("✅ No issues found.")

    if return_preview:
        return report_path, "\n".join(preview_lines)
    return report_path
