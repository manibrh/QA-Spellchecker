import pandas as pd
import os
import datetime

def generate_report(segments, issues, return_preview=False):
    df_segments = pd.DataFrame(segments)
    df_issues = pd.DataFrame(issues)

    if not df_issues.empty and 'id' in df_issues.columns and 'id' in df_segments.columns:
        merged = pd.merge(df_segments, df_issues, on='id', how='left')
    else:
        merged = df_segments.copy()

    merged.fillna('', inplace=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"QA_Report_{timestamp}.xlsx"
    path = os.path.join("uploads", filename)
    merged.to_excel(path, index=False, engine="openpyxl")

    preview = ""
    if return_preview:
        if df_issues.empty:
            preview = "✅ No issues found."
        else:
            grouped = df_issues.groupby('id')
            lines = []
            for seg_id, items in grouped:
                for _, row in items.iterrows():
                    issue = row.get('issue', 'Unknown issue')
                    suggestion = row.get('suggestion', '')
                    lines.append(f"Segment {seg_id}: {issue}" + (f" → {suggestion}" if suggestion else ""))
            preview = "\n".join(lines)

    return path, preview
