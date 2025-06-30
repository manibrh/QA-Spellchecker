import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []
    for seg in segments:
        target = seg.get("target", "")
        if not target.strip():
            continue

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a localization QA bot. Analyze the following target text "
                            "only for spelling or grammar mistakes. Only report actual issues "
                            "if they exist. Reply with 'No issues' if it's clean."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Target: {target}"
                    }
                ],
                temperature=0.2,
            )
            reply = response.choices[0].message.content.strip()
            if "no issue" not in reply.lower():
                issues.append({
                    "id": seg['id'],
                    "issue_type": "Spelling/Grammar",
                    "detail": reply
                })

        except Exception as e:
            issues.append({
                "id": seg['id'],
                "issue_type": "Spelling/Grammar",
                "detail": f"Error: {str(e)}"
            })
    return issues
