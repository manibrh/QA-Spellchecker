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
            continue

        prompt = (
            "You are a professional translation QA linguist.\n\n"
            "Task:\n"
            "1. Review the TARGET text for spelling, grammar, and punctuation issues.\n"
            "2. Also compare the SOURCE and TARGET to verify if the translated words reflect the correct meaning.\n"
            "3. If a word appears to be a mistranslation or an incorrect term (even if it’s not a typo), flag it.\n"
            "4. Provide your feedback in this format:\n"
            "   Issue: <Describe the problem>\n"
            "   Suggestion: <Corrected version of TARGET>\n"
            "5. If there are no issues, respond with exactly: No issues\n\n"
            f"SOURCE: {source}\n"
            f"TARGET: {target}"
        )

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
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
                    "issue_type": "Spelling/Meaning",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Spelling/Meaning",
                "issue": f"AI Error: {str(e)}",
                "suggestion": ""
            })

    return issues
