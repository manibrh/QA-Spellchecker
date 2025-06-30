# utils/qa_spell_ai.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []
    
    for segment in segments:
        seg_id = segment.get("id", "")
        source = segment.get("source", "").strip()
        target = segment.get("target", "").strip()

        if not target:
            continue  # skip empty targets

        prompt = (
            f"You are a professional Tamil language proofreader.\n"
            f"Your job is to check the **target text only** for spelling or grammar issues.\n"
            f"Use the source text for context, but do NOT assume it is a correct translation.\n\n"
            f"Source (for context): {source}\n"
            f"Target (to be reviewed): {target}\n\n"
            f"If you find any spelling or grammar errors in the target, reply in the following format:\n"
            f"Issue: <explanation of the problem>\n"
            f"Suggestion: <corrected version>\n\n"
            f"Reply only with 'No issues' if the target is perfectly correct."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            output = response.choices[0].message.content.strip()

            if "no issues" not in output.lower():
                issue_data = {"id": seg_id, "issue_type": "Spelling/Grammar", "issue": "", "suggestion": ""}
                
                if "Issue:" in output and "Suggestion:" in output:
                    # Split using keywords
                    parts = output.split("Suggestion:")
                    issue_data["issue"] = parts[0].replace("Issue:", "").strip()
                    issue_data["suggestion"] = parts[1].strip()
                else:
                    issue_data["issue"] = output

                issues.append(issue_data)

        except Exception as e:
            issues.append({
                "id": seg_id,
                "issue_type": "Spelling/Grammar",
                "issue": f"Error from AI: {str(e)}",
                "suggestion": ""
            })

    return issues
