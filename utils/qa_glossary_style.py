import os
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_glossary(filepath):
    if not filepath:
        return []
    df = pd.read_excel(filepath) if filepath.endswith(".xlsx") else pd.read_csv(filepath)
    return df.iloc[:, :2].dropna().values.tolist()

def run_glossary_style_check(segments, glossary_path=None, style_guide=None):
    glossary = load_glossary(glossary_path)
    issues = []

    # Limit to first 50 glossary entries to avoid token explosion
    glossary_pairs = glossary[:50]
    glossary_text = "\n".join([f"{src} -> {tgt}" for src, tgt in glossary_pairs]) if glossary_pairs else "None"
    style_text = style_guide if style_guide else "None"

    for seg in segments:
        seg_id = seg.get("id", "")
        source = seg.get("source", "")
        target = seg.get("target", "")

        if not target.strip():
            continue

        prompt = (
            "You are a translation QA reviewer. Please review the following segment for both glossary and style guide compliance.\n\n"
            f"Glossary Terms:\n{glossary_text}\n\n"
            f"Style Guide:\n{style_text}\n\n"
            "Instructions:\n"
            "- Verify the TARGET uses glossary terms appropriately.\n"
            "- Check if the TARGET adheres to style guidelines (e.g., tone, punctuation, structure).\n"
            "- If there are no issues, reply exactly: No issues\n"
            "- Otherwise, respond with:\n"
            "  Issue: <description>\n"
            "  Suggestion: <corrected or improved version>\n\n"
            f"SOURCE: {source}\n"
            f"TARGET: {target}"
        )

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = res.choices[0].message.content.strip()

            if result.lower() != "no issues":
                issue = ""
                suggestion = ""

                for line in result.splitlines():
                    if line.lower().startswith("issue:"):
                        issue = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("suggestion:"):
                        suggestion = line.split(":", 1)[1].strip()

                if not issue:
                    issue = result  # fallback to raw response

                issues.append({
                    "id": seg_id,
                    "source": source,
                    "target": target,
                    "issue_type": "Glossary/Style",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Glossary/Style",
                "issue": f"API Error: {str(e)}",
                "suggestion": ""
            })

    return issues
