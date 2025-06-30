import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_mistranslation_check(segments):
    issues = []
    for seg in segments:
        prompt = f"""You are a QA expert. Analyze if the translation (target) is a correct interpretation of the source. 
Only highlight real mistranslations and explain briefly why.
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
                issues.append({"id": seg['id'], "issue_type": "Mistranslation", "detail": result})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Mistranslation", "detail": str(e)})
    return issues
