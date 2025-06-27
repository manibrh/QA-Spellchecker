import pandas as pd

def load_dnt_terms(filepath):
    if filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
    return set(df.iloc[:, 0].dropna().astype(str).str.strip())

def run_dnt_check(segments, dnt_path):
    if not dnt_path:
        return []
    dnt_terms = load_dnt_terms(dnt_path)
    issues = []
    for seg in segments:
        for term in dnt_terms:
            if term in seg['source'] and term not in seg['target']:
                issues.append({"id": seg['id'], "issue_type": "DNT", "term": term, "detail": f"DNT term '{term}' missing or changed in target"})
    return issues