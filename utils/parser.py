import os
import xml.etree.ElementTree as ET
import pandas as pd

def parse_bilingual_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.xlf', '.xliff']:
        return parse_xliff(file_path)
    elif ext in ['.xlsx', '.xls']:
        return parse_xlsx(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload .xliff or .xlsx.")

def parse_xliff(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'ns': root.tag.split('}')[0].strip('{')}

    segments = []
    declared_target_lang = root.attrib.get('target-language', 'und')  # 'und' = undefined

    for trans_unit in root.findall('.//ns:trans-unit', namespace):
        seg_id = trans_unit.attrib.get('id', '')
        source = trans_unit.findtext('ns:source', default='', namespaces=namespace).strip()
        target = trans_unit.findtext('ns:target', default='', namespaces=namespace).strip()
        segments.append({'id': seg_id, 'source': source, 'target': target})

    return segments, declared_target_lang

def parse_xlsx(file_path):
    df = pd.read_excel(file_path)
    required_cols = ['ID', 'Source', 'Target']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("XLSX file must contain columns: ID, Source, Target")

    segments = df[required_cols].fillna('').to_dict(orient='records')
    
    # Try to guess declared target language from a separate 'Target Lang' column or default to 'und'
    if 'Target Lang' in df.columns:
        declared_target_lang = str(df['Target Lang'].dropna().iloc[0])
    else:
        declared_target_lang = 'und'

    return segments, declared_target_lang
