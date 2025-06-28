# utils/qa_spell_ai.py
import openai
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []
    for seg in segments:
        prompt = f"""You are a translation QA checker. Check for spelling or unnatural usage in any language.
Source: {seg['source']}
Target: {seg['target']}
Return a JSON or bullet point list of spelling issues."""
        try:
            def run_spellcheck_ai(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}],
    )
    return response.choices[0].message.content
                content = res.choices[0].message['content']
            issues.append({"id": seg['id'], "issue_type": "Spelling (AI)", "detail": content})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Spelling (AI)", "detail": f"Error: {str(e)}"})
    return issues
