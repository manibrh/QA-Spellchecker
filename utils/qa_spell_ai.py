import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(target_texts, segments):
    issues = []

    for i, text in enumerate(target_texts):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a localization QA specialist. "
                            "Identify spelling and grammar mistakes in the **target** text only. "
                            "Only list clear issues (like typos, grammar errors, or punctuation problems). "
                            "If no issues found, say 'No issues'."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Target text:\n{text}"
                    }
                ],
                temperature=0.2
            )

            reply = response.choices[0].message.content.strip()

            if "no issue" not in reply.lower():
                issues.append({
                    "id": segments[i].get("id", str(i)),
                    "issue_type": "Spelling/Grammar",
                    "detail": reply
                })

        except Exception as e:
            issues.append({
                "id": segments[i].get("id", str(i)),
                "issue_type": "Spelling/Grammar",
                "detail": f"API Error: {str(e)}"
            })

    return issues
