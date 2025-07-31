from langdetect import detect, DetectorFactory, detect_langs

# For consistent results
DetectorFactory.seed = 42

def run_language_mismatch_check(segments, declared_lang_code):
    issues = []

    # Normalize declared language (e.g., 'fr-CA' → 'fr')
    declared_lang = declared_lang_code.split('-')[0].lower()

    for seg in segments:
        seg_id = seg.get('id', '')
        target = seg.get('target', '').strip()

        if not target or len(target) < 10:  # Skip very short targets
            continue

        try:
            # Detect top languages with confidence
            detected_langs = detect_langs(target)
            detected = detected_langs[0].lang if detected_langs else None
            confidence = detected_langs[0].prob if detected_langs else None

            if detected and detected != declared_lang:
                issues.append({
                    "id": seg_id,
                    "source": seg.get("source", ""),
                    "target": target,
                    "issue_type": "Language Mismatch",
                    "detected": detected,
                    "confidence": f"{confidence:.2f}" if confidence else "N/A",
                    "comment": f"Declared: {declared_lang}, Detected: {detected} (Confidence: {confidence:.2f})"
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": seg.get("source", ""),
                "target": target,
                "issue_type": "Language Mismatch",
                "detected": "N/A",
                "confidence": "N/A",
                "comment": f"Language detection failed: {str(e)}"
            })

    return issues
