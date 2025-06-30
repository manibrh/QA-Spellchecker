# app.py
import os
from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
from utils.parser import parse_bilingual_file
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bilingual_file = request.files.get('bilingual_file')
        dnt_file = request.files.get('dnt_file')
        glossary_file = request.files.get('glossary_file')
        style_guide = request.form.get('style_guide', '')
        selected_checks = request.form.getlist('issue_types')
        expected_lang = request.form.get('expected_lang', '').strip()

        if not bilingual_file:
            return "No bilingual file uploaded", 400

        bilingual_path = os.path.join(UPLOAD_FOLDER, bilingual_file.filename)
        bilingual_file.save(bilingual_path)

        dnt_path = None
        glossary_path = None

        if dnt_file and dnt_file.filename:
            dnt_path = os.path.join(UPLOAD_FOLDER, dnt_file.filename)
            dnt_file.save(dnt_path)

        if glossary_file and glossary_file.filename:
            glossary_path = os.path.join(UPLOAD_FOLDER, glossary_file.filename)
            glossary_file.save(glossary_path)

        # Parse segments
        segments = parse_bilingual_file(bilingual_path)

        # Run checks
        all_issues = []

        if 'dnt' in selected_checks:
            all_issues.extend(run_dnt_check(segments, dnt_path))

        if 'spell' in selected_checks:
            all_issues.extend(run_spellcheck_ai(segments))

        if 'mistranslation' in selected_checks:
            all_issues.extend(run_mistranslation_check(segments))

        if 'literal' in selected_checks:
            all_issues.extend(run_literalness_check(segments))

        if 'glossary_style' in selected_checks:
            all_issues.extend(run_glossary_style_check(segments, glossary_path, style_guide))

        if 'lang_mismatch' in selected_checks and expected_lang:
            all_issues.extend(run_language_mismatch_check(segments, expected_lang))

        # Generate report
        report_path = generate_report(segments, all_issues)

        return send_file(report_path, as_attachment=True)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
