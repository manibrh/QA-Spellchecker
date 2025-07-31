import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_literalness_check(segments):
    issues = []

    for seg in segments:
        seg_id = seg.get("id", "")
        source = seg.get("source", "")
        target = seg.get("target", "")

        if not target.strip():
            continue

        prompt = (
            "You are a translation QA linguist. Check if the translation is too literal or unnatural.\n\n"
            "Instructions:\n"
            "- Compare the SOURCE and TARGET.\n"
            "- Determine if the TARGET is excessively literal or word-for-word, resulting in awkward phrasing.\n"
            "- If the TARGET sounds natural and appropriate, respond with exactly: No issues.\n"
            "- If the translation is too literal, describe the problem and suggest a more natural alternative in this format:\n"
            "  Issue: <description>\n"
            "  Suggestion: <improved version>\n\n"
            f"SOURCE: {source}\n"
            f"TARGET: {target}"
        )

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = res.choices[0].message.content.strip()

            if output.lower() != "no issues":
                issue = ""
                suggestion = ""
                for line in output.splitlines():
                    if line.lower().startswith("issue:"):
                        issue = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("suggestion:"):
                        suggestion = line.split(":", 1)[1].strip()
                if not issue:
                    issue = output

                issues.append({
                    "id": seg_id,
                    "source": source,
                    "target": target,
                    "issue_type": "Literalness",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Literalness",
                "issue": f"API Error: {str(e)}",
                "suggestion": ""
            })

    return issues
