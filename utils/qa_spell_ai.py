# utils/qa_spell_ai.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_spellcheck_ai(segments):
    issues = []
    for segment in segments:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a localization QA specialist. Identify spelling and grammar issues in the provided text. Only report real issues, and skip segments that are fine. Also in the target text typo or spelling in the target languages to be strictly checked."},
                    {"role": "user", "content": f"Check this text: {segment}"}
                ],
                temperature=0.1
            )
            reply = response.choices[0].message.content.strip()
            if "no issue" not in reply.lower():
                issues.append({"Segment": segment, "Issue Type": "Spelling/Grammar", "Details": reply})
        except Exception as e:
            issues.append({"Segment": segment, "Issue Type": "API Error", "Details": str(e)})
    return issues
