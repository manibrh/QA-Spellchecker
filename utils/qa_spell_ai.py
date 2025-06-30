# utils/qa_spell_ai.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []
    for segment in segments:
        try:
            prompt = f"""
You are a professional localization QA specialist.

Your job is to evaluate **only the target text** for:
- Spelling or typographic mistakes
- Grammar issues
- Incorrect suffixes, word endings, or particle usage (especially in languages like Tamil, Hindi, etc.)

Instructions:
- Do not comment on translation quality or style unless it affects spelling/grammar.
- Use the source only for light context — focus on spelling and grammar in the target.
- Be strict: catch even minor typos or letter swaps (e.g., 'பினர்' instead of 'பின்னர்').

Expected Output:
- If there is an issue, describe it and suggest a correction.
- If the target is clean, respond exactly with: `No spelling or grammar issues found in the target.`

Source (for context): {segment['source']}
Target: {segment['target']}
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            reply = response.choices[0].message.content.strip()
            if "no spelling or grammar issues" not in reply.lower():
                issues.append({
                    "id": segment.get("id", ""),
                    "issue_type": "Spelling/Grammar",
                    "detail": reply
                })

        except Exception as e:
            issues.append({
                "id": segment.get("id", ""),
                "issue_type": "API Error",
                "detail": str(e)
            })

    return issues
