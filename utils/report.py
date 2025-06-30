import pandas as pd
import os
import datetime

def generate_report(segments, issues, return_preview=False):
    df_segments = pd.DataFrame(segments)
    df_issues = pd.DataFrame(issues)

    # Merge on segment ID if possible
    if not df_issues.empty and 'id' in df_issues.columns and 'id' in df_segments.columns:
        merged = pd.merge(df_segments, df_issues, on='id', how='left')
    else:
        merged = df_segments.copy()

    # Fill NaNs
    merged.fillna('', inplace=True)

    # Create uploads folder if missing
    output_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(output_dir, exist_ok=True)

    # Timestamped report filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"QA_Report_{timestamp}.xlsx"
    path = os.path.join(output_dir, filename)

    try:
        # Use openpyxl explicitly
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            merged.to_excel(writer, index=False)
    except Exception as e:
        print("⚠️ Excel writing error:", e)
        raise

    # Preview (for web UI)
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
