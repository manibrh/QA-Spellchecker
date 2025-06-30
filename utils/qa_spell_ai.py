import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_spellcheck_ai(segments):
    issues = []
    for seg in segments:
        target = seg['target']
        if not target.strip():
            continue
        prompt = f"""You are a language QA checker. Review the following text for spelling and grammar issues. 
Only list real mistakes in the 'target'. Do NOT reference the source or suggest rephrasing unless it’s a clear grammatical/spelling error.
Target: {target}"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            reply = response.choices[0].message["content"].strip()
            if "no issues" not in reply.lower():
                issues.append({"id": seg['id'], "issue_type": "Spelling/Grammar", "detail": reply})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Spelling/Grammar", "detail": str(e)})
    return issues
