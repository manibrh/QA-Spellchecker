import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []

    for seg in segments:
        seg_id = seg.get('id', '')
        source = seg.get('source', '')
        target = seg.get('target', '')

        if not target.strip():
            continue  # Skip empty targets

        prompt = (
            "You are a professional translation QA linguist. Your task is to check the TARGET text "
            "for spelling, grammar, punctuation, and casing issues.\n\n"
            "Please follow these instructions:\n"
            "1. Only evaluate the TARGET text, using the SOURCE as optional context.\n"
            "2. Do not check meaning or translation accuracy — only language mechanics.\n"
            "3. Return one of the following:\n"
            "   - If there are no issues: respond with exactly --> No issues\n"
            "   - If there are issues: respond with this format:\n"
            "     Issue: <description of the language problem>\n"
            "     Suggestion: <suggested corrected version of the TARGET>\n\n"
            f"SOURCE (context only): {source}\n"
            f"TARGET (to review): {target}"
        )

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            output = res.choices[0].message.content.strip()

            if output.lower().strip() != "no issues":
                issue = ""
                suggestion = ""

                # Robust parsing
                lines = output.splitlines()
                for line in lines:
                    if line.lower().startswith("issue:"):
                        issue = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("suggestion:"):
                        suggestion = line.split(":", 1)[1].strip()

                if not issue:
                    issue = output  # fallback

                issues.append({
                    "id": seg_id,
                    "source": source,
                    "target": target,
                    "issue_type": "Spelling/Grammar",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Spelling/Grammar",
                "issue": f"AI Error: {str(e)}",
                "suggestion": ""
            })

    return issues
