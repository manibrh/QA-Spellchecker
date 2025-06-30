import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_language_check(segments, expected_lang_code):
    issues = []
    for seg in segments:
        target = seg.get("target", "").strip()
        if not target:
            continue

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Identify the language of the following text and compare it with the expected language code. "
                            "If it doesn't match, respond with a message indicating mismatch and the detected language. "
                            "If it matches, reply 'Match'."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Text: {target}\nExpected language code: {expected_lang_code}"
                    }
                ],
                temperature=0
            )
            reply = response.choices[0].message.content.strip()
            if reply.lower() != "match":
                issues.append({
                    "id": seg['id'],
                    "issue_type": "Language Mismatch",
                    "detail": reply
                })

        except Exception as e:
            issues.append({
                "id": seg['id'],
                "issue_type": "Language Mismatch",
                "detail": f"Error: {str(e)}"
            })

    return issues
