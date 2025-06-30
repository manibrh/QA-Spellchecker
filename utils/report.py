import pandas as pd
import os
from datetime import datetime

def generate_report(segments, issues, return_preview=False):
    df_segments = pd.DataFrame(segments)
    df_issues = pd.DataFrame(issues)

    if not df_issues.empty:
        merged = pd.merge(df_segments, df_issues, on="id", how="left")
    else:
        merged = df_segments.copy()
        merged["issue_type"] = ""
        merged["comment"] = ""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"QA_Report_{timestamp}.xlsx"
    path = os.path.join("static", filename)
    os.makedirs("static", exist_ok=True)
   merged.to_excel(path, index=False, engine="openpyxl")

    if return_preview:
        # Create preview (first 20 rows only)
        preview_data = merged.head(20).to_dict(orient="records")
        return path, preview_data

    return path
