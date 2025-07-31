import pandas as pd

def load_dnt_terms(filepath):
    if not filepath:
        return set()
    if filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
    return set(df.iloc[:, 0].dropna().astype(str).str.strip())

def run_dnt_check(segments, dnt_path):
    issues = []
    dnt_terms = load_dnt_terms(dnt_path)

    for seg in segments:
        seg_id = seg.get('id', '')
        source = seg.get('source', '') or ''
        target = seg.get('target', '') or ''

        if not source or not target:
            continue

        source_lc = source.lower()
        target_lc = target.lower()

        for term in dnt_terms:
            term_lc = term.lower()
            if term_lc in source_lc and term_lc not in target_lc:
                issues.append({
                    "id": seg_id,
                    "source": source,
                    "target": target,
                    "issue_type": "DNT",
                    "term": term,
                    "comment": f"DNT term '{term}' is present in source but missing or altered in target."
                })

    return issues
