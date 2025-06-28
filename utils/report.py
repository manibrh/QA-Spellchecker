import os
import pandas as pd
import datetime
import re
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_sheet_name(name):
    """Remove invalid Excel sheet characters and truncate to 31 characters."""
    name = re.sub(r'[\\/*?:\[\]]', '', name)
    return name[:31]

def generate_report(segments, all_issues):
    output_dir = "static/qa_reports"
    os.makedirs(output_dir, exist_ok=True)

    report_name = f"QA_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    report_path = os.path.join(output_dir, report_name)

    logger.info(f"Generating report at: {report_path}")

    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        used_sheet_names = set()

        # Write each issue type to its own sheet
        for issue_type, issues in all_issues.items():
            if issues:
                df = pd.DataFrame(issues)
                base_name = sanitize_sheet_name(issue_type)
                sheet_name = base_name

                # Ensure sheet name is unique
                suffix = 1
                while sheet_name in used_sheet_names:
                    sheet_name = f"{base_name[:28]}_{suffix}"
                    suffix += 1

                used_sheet_names.add(sheet_name)

                try:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    logger.info(f"Wrote sheet: {sheet_name} with {len(df)} issues")
                except Exception as e:
                    logger.error(f"Failed to write sheet '{sheet_name}': {e}")

        # Write segment summary
        try:
            segments_df = pd.DataFrame(segments)
            segments_df.to_excel(writer, sheet_name="Segments", index=False)
            logger.info("Wrote segment summary")
        except Exception as e:
            logger.error(f"Failed to write segment sheet: {e}")

    logger.info("Report generation completed.")
    return report_path
