# utils/qa_lang_mismatch.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_language_mismatch_check(segments, expected_lang_code):
    issues = []
    for seg in segments:
        try:
            prompt = f"""You are a language detector. Identify if the text is in the expected language code: {expected_lang_code}.
Just respond 'Match' if it's the same language, otherwise say which language it is.

Target: {seg['target']}"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            reply = response.choices[0].message.content.strip()

            if 'match' not in reply.lower():
                issues.append({
                    "id": seg['id'],
                    "issue_type": "Language Mismatch",
                    "detail": f"Expected: {expected_lang_code}, Detected: {reply}"
                })

        except Exception as e:
            issues.append({
                "id": seg['id'],
                "issue_type": "Language Mismatch",
                "detail": str(e)
            })

    return issues
