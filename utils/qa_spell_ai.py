# utils/qa_spell_ai.py
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_spellcheck_ai(segments):
    issues = []
    for seg in segments:
        prompt = f"""You are a translation QA checker. Check for spelling or unnatural usage in any language.
Source: {seg['source']}
Target: {seg['target']}
Return a JSON or bullet point list of spelling issues."""
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            content = res.choices[0].message['content']
            issues.append({"id": seg['id'], "issue_type": "Spelling (AI)", "detail": content})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Spelling (AI)", "detail": f"Error: {str(e)}"})
    return issues
