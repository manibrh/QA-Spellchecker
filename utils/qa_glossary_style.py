# utils/qa_glossary_style.py
import openai
import os
import pandas as pd
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_glossary(filepath):
    if not filepath:
        return []
    df = pd.read_excel(filepath) if filepath.endswith(".xlsx") else pd.read_csv(filepath)
    return df.iloc[:, :2].dropna().values.tolist()

def run_glossary_style_check(segments, glossary_path=None, style_guide=None):
    glossary = load_glossary(glossary_path)
    issues = []
    glossary_text = "\n".join([f"{src} -> {tgt}" for src, tgt in glossary])
    for seg in segments:
        prompt = f"""You are a QA checker. Evaluate the target for glossary and style guide compliance.
Glossary:
{glossary_text if glossary_text else 'None'}
Style Guide:
{style_guide if style_guide else 'None'}

Source: {seg['source']}
Target: {seg['target']}"""
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = res.choices[0].message['content']
            if 'no issues' not in result.lower():
                issues.append({"id": seg['id'], "issue_type": "Glossary/Style", "detail": result})
        except Exception as e:
            issues.append({"id": seg['id'], "issue_type": "Glossary/Style", "detail": str(e)})
    return issues
