import pandas as pd
import os
import re
from datetime import datetime

def sanitize_sheet_name(name):
    """
    Removes characters not allowed in Excel sheet names and trims to 31 characters.
    """
    # Remove invalid characters: \ / * ? : [ ]
    name = re.sub(r'[\\/*?:\[\]]', '', name)
    return name[:31]  # Excel sheet name limit

def generate_report(segments, all_issues):
    """
    Generates an Excel report with each issue type on a separate sheet.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"QA_Report_{timestamp}.xlsx"
    output_path = os.path.join("static", "reports")
    os.makedirs(output_path, exist_ok=True)
    full_path = os.path.join(output_path, filename)

    with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
        for issue_type, issues in all_issues.items():
            df = pd.DataFrame(issues)
            if df.empty:
                continue
            sheet_name = sanitize_sheet_name(issue_type)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return full_path
