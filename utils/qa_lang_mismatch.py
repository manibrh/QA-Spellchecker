from langdetect import detect

def run_language_mismatch_check(segments, declared_lang_code):
    issues = []
    for seg in segments:
        target = seg.get('target', '').strip()
        if not target:
            continue
        try:
            detected = detect(target)
            if detected and not detected.startswith(declared_lang_code.split('-')[0]):
                issues.append({
                    "id": seg['id'],
                    "issue_type": "Language Mismatch",
                    "detail": f"Declared: {declared_lang_code}, Detected: {detected}"
                })
        except Exception as e:
            issues.append({
                "id": seg['id'],
                "issue_type": "Language Mismatch",
                "detail": f"Language detection failed: {str(e)}"
            })
    return issues
