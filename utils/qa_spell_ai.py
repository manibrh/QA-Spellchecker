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
            f"You are a professional linguist reviewing translations in multiple languages.\n"
            f"Your task is to check the following TARGET text for spelling and grammar mistakes ONLY.\n"
            f"Use the SOURCE as context, but do not translate or compare meaning.\n\n"
            f"Instructions:\n"
            f"- Only comment on spelling and grammar issues in the TARGET.\n"
            f"- If there are errors, explain the issue and suggest a corrected version.\n"
            f"- If there are no issues, respond with exactly: No issues.\n\n"
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
                # Attempt to extract issue and suggestion
                if "Suggestion:" in output:
                    parts = output.split("Suggestion:")
                    issue = parts[0].strip()
                    suggestion = parts[1].strip()
                elif "→" in output:
                    parts = output.split("→")
                    issue = parts[0].strip()
                    suggestion = parts[1].strip()
                else:
                    issue = output
                    suggestion = ""

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
