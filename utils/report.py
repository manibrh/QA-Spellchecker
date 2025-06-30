import pandas as pd
import os
import datetime

def generate_report(segments, issues, return_preview=False):
    df_segments = pd.DataFrame(segments)
    df_issues = pd.DataFrame(issues)

    # Merge segments with issues if possible
    if not df_issues.empty and 'id' in df_issues.columns and 'id' in df_segments.columns:
        merged = pd.merge(df_segments, df_issues, on='id', how='left')
    else:
        merged = df_segments.copy()

    merged.fillna('', inplace=True)

    # Ensure uploads/ directory exists
    os.makedirs("uploads", exist_ok=True)

    # Filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"QA_Report_{timestamp}.xlsx"
    path = os.path.join("uploads", filename)

    # Save Excel using context manager (ensures closing file)
    with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
        merged.to_excel(writer, index=False)

    # Build preview
    preview = "✅ No issues found."
    if return_preview and not df_issues.empty:
        grouped = df_issues.groupby('id')
        lines = []
        for seg_id, items in grouped:
            for _, row in items.iterrows():
                issue = row.get('issue', 'Unknown issue')
                suggestion = row.get('suggestion', '')
                line = f"Segment {seg_id}: {issue}"
                if suggestion:
                    line += f" → {suggestion}"
                lines.append(line)
        preview = "\n".join(lines)

    return path, preview
