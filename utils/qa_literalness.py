import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_literalness_check(segments):
    issues = []
    for seg in segments:
        prompt = f"""Check if the target translation is too literal (word-for-word) and not naturally adapted.
Only report literal translations that reduce readability or clarity.
Source: {seg['source']}
Target: {seg['target']}"""
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            result = res.choices[0].message["content"].strip()
            if "no issues" not in result.lower():
                issues.append({"id": seg['id'], "issue_type": "Literalness", "detail": result})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Literalness", "detail": str(e)})
    return issues
