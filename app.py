# app.py
import os
from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv
from utils.parser import parse_bilingual_file
from utils.qa_dnt import run_dnt_check
from utils.qa_spell_ai import run_spellcheck_ai
from utils.qa_mistranslation import run_mistranslation_check
from utils.qa_literalness import run_literalness_check
from utils.qa_glossary_style import run_glossary_style_check
from utils.report import generate_report

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bilingual_files = request.files.getlist('bilingual_file')
        dnt_file = request.files.get('dnt_file')
        glossary_file = request.files.get('glossary_file')
        style_guide = request.form.get('style_guide')

        if not bilingual_files or len(bilingual_files) == 0:
            return jsonify({"success": False, "message": "No bilingual files uploaded"}), 400

        segments = []
        for file in bilingual_files:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            segments.extend(parse_bilingual_file(path))

        dnt_path = None
        glossary_path = None

        if dnt_file and dnt_file.filename:
            dnt_path = os.path.join(UPLOAD_FOLDER, dnt_file.filename)
            dnt_file.save(dnt_path)

        if glossary_file and glossary_file.filename:
            glossary_path = os.path.join(UPLOAD_FOLDER, glossary_file.filename)
            glossary_file.save(glossary_path)

        # Run QA checks
        all_issues = []
        all_issues.extend(run_dnt_check(segments, dnt_path))
        all_issues.extend(run_spellcheck_ai(segments))
        all_issues.extend(run_mistranslation_check(segments))
        all_issues.extend(run_literalness_check(segments))
        all_issues.extend(run_glossary_style_check(segments, glossary_path, style_guide))

        report_path = generate_report(segments, all_issues)
        filename = os.path.basename(report_path)

        return jsonify({
            "success": True,
            "filename": filename,
            "message": "QA report ready"
        })

    return render_template('index.html')


@app.route('/download/<filename>')
def download_report(filename):
    path = os.path.join("static", "qa_reports", filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
