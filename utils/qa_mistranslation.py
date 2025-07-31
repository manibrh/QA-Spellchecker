import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_mistranslation_check(segments):
    issues = []

    for seg in segments:
        seg_id = seg.get("id", "")
        source = seg.get("source", "")
        target = seg.get("target", "")

        if not target.strip():
            continue

        prompt = (
            "You are a professional linguist. Review the translation for mistranslation issues.\n\n"
            "Instructions:\n"
            "- Compare the SOURCE and TARGET to determine if meaning has been preserved.\n"
            "- If there is a mistranslation, describe the issue and suggest a correction.\n"
            "- If there is no issue, respond with exactly: No issues.\n\n"
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
                # Try to extract issue and suggestion if available
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
                    "issue_type": "Mistranslation",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Mistranslation",
                "issue": f"API Error: {str(e)}",
                "suggestion": ""
            })

    return issues
