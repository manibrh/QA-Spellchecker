# utils/qa_literalness.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_literalness_check(segments):
    issues = []
    for seg in segments:
        prompt = f"""Check if the translation is too literal:\nSource: {seg['source']}\nTarget: {seg['target']}"""
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = res.choices[0].message.content.strip()
            if "no issues" not in output.lower():
                issues.append({"id": seg['id'], "issue_type": "Literalness", "detail": output})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Literalness", "detail": str(e)})
    return issues
