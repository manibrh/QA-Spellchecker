import os
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_glossary(filepath):
    """
    Loads a glossary from an Excel (.xlsx) or tab-separated text file (.txt).

    Args:
        filepath (str): The path to the glossary file.

    Returns:
        list: A list of lists, where each inner list represents a glossary pair [source, target].
              Returns an empty list if the filepath is empty or if the file cannot be read.
    """
    if not filepath:
        return []

    df = None
    if filepath.endswith(".xlsx"):
        # Handle Excel files
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            print(f"Error reading Excel file {filepath}: {e}")
            return []
    else:
        # Handle all other delimited text files, including .txt and .csv
        # Use sep='\t' for tab-separated files as per your example.
        encodings_to_try = ['utf-8', 'utf-16', 'latin1', 'iso-8859-1']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(filepath, sep='\t', encoding=encoding)
                print(f"Successfully read file with encoding: {encoding}")
                break  # Exit loop if successful
            except UnicodeDecodeError:
                print(f"Failed to read file with encoding: {encoding}. Trying next...")
                continue
            except Exception as e:
                print(f"Error reading text file {filepath} with encoding {encoding}: {e}")
                return []
        
        if df is None:
            print(f"Could not read text file {filepath} with any of the attempted encodings.")
            return []

    # Ensure the DataFrame has at least two columns and clean up data
    if df is not None and df.shape[1] >= 2:
        return df.iloc[:, :2].dropna().values.tolist()
    else:
        print(f"Glossary file {filepath} does not contain enough columns or is empty after loading.")
        return []

def run_glossary_style_check(segments, glossary_path=None, style_guide=None):
    """
    Reviews translation segments for glossary and style guide compliance using an LLM.

    Args:
        segments (list): A list of dictionaries, where each dictionary represents a segment
                         with 'id', 'source', and 'target' keys.
        glossary_path (str, optional): Path to the glossary file. Defaults to None.
        style_guide (str, optional): Text content of the style guide. Defaults to None.

    Returns:
        list: A list of dictionaries, where each dictionary represents an identified issue.
    """
    glossary = load_glossary(glossary_path)
    issues = []

    # Limit to first 50 glossary entries to avoid excessive token usage with the LLM
    glossary_pairs = glossary[:50]
    glossary_text = "\n".join([f"{src} -> {tgt}" for src, tgt in glossary_pairs]) if glossary_pairs else "None"
    style_text = style_guide if style_guide else "None"

    for seg in segments:
        seg_id = seg.get("id", "")
        source = seg.get("source", "")
        target = seg.get("target", "")

        if not target.strip():
            continue

        prompt = (
            "You are a translation QA reviewer. Please review the following segment for both glossary and style guide compliance.\n\n"
            f"Glossary Terms:\n{glossary_text}\n\n"
            f"Style Guide:\n{style_text}\n\n"
            "Instructions:\n"
            "- Verify the TARGET uses glossary terms appropriately.\n"
            "- Check if the TARGET adheres to style guidelines (e.g., tone, punctuation, structure).\n"
            "- If there are no issues, reply exactly: No issues\n"
            "- Otherwise, respond with:\n"
            "  Issue: <description>\n"
            "  Suggestion: <corrected or improved version>\n\n"
            f"SOURCE: {source}\n"
            f"TARGET: {target}"
        )

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            result = res.choices[0].message.content.strip()

            if result.lower() != "no issues":
                issue = ""
                suggestion = ""

                for line in result.splitlines():
                    if line.lower().startswith("issue:"):
                        issue = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("suggestion:"):
                        suggestion = line.split(":", 1)[1].strip()

                if not issue:
                    issue = result

                issues.append({
                    "id": seg_id,
                    "source": source,
                    "target": target,
                    "issue_type": "Glossary/Style",
                    "issue": issue,
                    "suggestion": suggestion
                })

        except Exception as e:
            issues.append({
                "id": seg_id,
                "source": source,
                "target": target,
                "issue_type": "Glossary/Style",
                "issue": f"API Error: {str(e)}",
                "suggestion": ""
            })

    return issues
