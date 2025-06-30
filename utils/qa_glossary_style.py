import os
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_glossary(filepath):
    if not filepath:
        return []
    df = pd.read_excel(filepath) if filepath.endswith(".xlsx") else pd.read_csv(filepath)
    return df.iloc[:, :2].dropna().values.tolist()

def run_glossary_style_check(segments, glossary_path=None, style_guide=None):
    glossary = load_glossary(glossary_path)
    glossary_text = "\n".join([f"{src} -> {tgt}" for src, tgt in glossary])
    issues = []

    for seg in segments:
        prompt = f"""Check if the target text complies with the glossary and style guide.
Glossary:
{glossary_text if glossary_text else 'None'}
Style Guide:
{style_guide if style_guide else 'None'}

Target: {seg['target']}"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            reply = response.choices[0].message["content"].strip()
            if "no issues" not in reply.lower():
                issues.append({"id": seg['id'], "issue_type": "Glossary/Style", "detail": reply})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Glossary/Style", "detail": str(e)})
    return issues
