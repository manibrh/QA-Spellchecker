import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_mistranslation_check(segments):
    issues = []
    for seg in segments:
        prompt = f"""Check this translation for mistranslation:
Source: {seg['source']}
Target: {seg['target']}"""
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = res.choices[0].message.content
            if 'no issues' not in output.lower():
                issues.append({"id": seg['id'], "issue_type": "Mistranslation", "detail": output})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Mistranslation", "detail": str(e)})
    return issues
