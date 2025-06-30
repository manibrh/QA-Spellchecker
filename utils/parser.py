import pandas as pd
import xml.etree.ElementTree as ET
import os

def parse_bilingual_file(filepath):
    segments = []
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.xlsx':
        df = pd.read_excel(filepath)
        for idx, row in df.iterrows():
            segments.append({"id": str(idx+1), "source": row[0], "target": row[1]})
    elif ext in ('.xliff', '.xlf'):
        tree = ET.parse(filepath)
        root = tree.getroot()
        for unit in root.findall('.//trans-unit'):
            sid = unit.attrib.get('id', 'unknown')
            source = unit.find('source').text if unit.find('source') is not None else ''
            target = unit.find('target').text if unit.find('target') is not None else ''
            segments.append({"id": sid, "source": source, "target": target})
    return segments
