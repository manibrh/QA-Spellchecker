import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from utils.parser import parse_bilingual_file, detect_target_language_from_xliff
from utils.qa_dnt import run_dnt_check
from utils.qa_spell_ai import run_spellcheck_ai
from utils.qa_mistranslation import run_mistranslation_check
from utils.qa_literalness import run_literalness_check
from utils.qa_glossary_style import run_glossary_style_check
from utils.qa_lang_mismatch import run_language_mismatch_check
from utils.report import generate_report

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def run_qa():
    bilingual_file = request.files.get('bilingual_file')
    dnt_file = request.files.get('dnt_file')
    glossary_file = request.files.get('glossary_file')
    style_guide = request.form.get('style_guide')
    selected_checks = request.form.getlist('qa_checks')

    if not bilingual_file:
        return "No bilingual file uploaded", 400

    bilingual_path = os.path.join(UPLOAD_FOLDER, bilingual_file.filename)
    bilingual_file.save(bilingual_path)

    dnt_path = glossary_path = None
    if dnt_file and dnt_file.filename:
        dnt_path = os.path.join(UPLOAD_FOLDER, dnt_file.filename)
        dnt_file.save(dnt_path)
    if glossary_file and glossary_file.filename:
        glossary_path = os.path.join(UPLOAD_FOLDER, glossary_file.filename)
        glossary_file.save(glossary_path)

    # Detect declared language from XLIFF (if present)
    xliff_lang_code = detect_target_language_from_xliff(bilingual_path)
    
    # Parse bilingual segments
    segments = parse_bilingual_file(bilingual_path)

    # Run selected QA checks
    all_issues = []

    if 'dnt' in selected_checks:
        all_issues.extend(run_dnt_check(segments, dnt_path))
    if 'spell' in selected_checks:
        all_issues.extend(run_spellcheck_ai(segments))
    if 'mistranslation' in selected_checks:
        all_issues.extend(run_mistranslation_check(segments))
    if 'literal' in selected_checks:
        all_issues.extend(run_literalness_check(segments))
    if 'glossary' in selected_checks:
        all_issues.extend(run_glossary_style_check(segments, glossary_path, style_guide))
    if 'langcheck' in selected_checks:
        all_issues.extend(run_language_mismatch_check(segments, xliff_lang_code))

    # Generate Excel report
    report_path = generate_report(segments, all_issues)

    # Inline summary for preview
    short_summary = [
        f"[{issue['issue_type']}] ID {issue['id']}: {issue['detail']}"
        for issue in all_issues
    ]

    return jsonify({
        "preview": short_summary[:50],  # first 50 issues
        "download_link": f"/download_report?file={os.path.basename(report_path)}"
    })

@app.route('/download_report')
def download_report():
    filename = request.args.get('file')
    filepath = os.path.join("static", "qa_reports", filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
