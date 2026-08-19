import fitz
import json
import re
import os

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)
cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')

# 1. First build a high-precision spatial index from all PDF pages
pdf_spatial_data = {}

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y_center = (cw[1] + cw[3]) / 2.0
        row_words = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 12]
        
        # Sort words left-to-right
        row_words.sort(key=lambda w: w[0])
        
        silsila_words = [w[4] for w in row_words if w[0] > 490 and w[4].isdigit()]
        gharana_words = [w[4] for w in row_words if 465 <= w[0] <= 495 and w[4].isdigit()]
        age_words = [re.sub(r'\D', '', w[4]) for w in row_words if 200 <= w[0] <= 240 and re.sub(r'\D', '', w[4]).isdigit()]
        
        silsila = silsila_words[0] if silsila_words else None
        gharana = gharana_words[0] if gharana_words else None
        age = age_words[0] if age_words else None
        
        pdf_spatial_data[cnic] = {
            'SilsilaNo': silsila,
            'GharanaNo': gharana,
            'Age': age,
            'Page': p_idx + 1,
            'y0': cw[1],
            'y1': cw[3]
        }

# 2. Specific manual corrections verified directly from PDF scans
manual_corrections = {
    '38201-9004840-4': {'NameUrdu': 'عظمیٰ علی', 'FatherNameUrdu': 'دختر محمد سعید', 'Age': '28'},
    '38201-6205416-4': {'NameUrdu': 'عروج علی', 'FatherNameUrdu': 'دختر محمد سعید', 'Age': '25'},
    '38201-5057660-7': {'NameUrdu': 'محمد مجتبیٰ علی', 'FatherNameUrdu': 'احمد علی خان', 'Age': '18'},
    '38403-4407767-4': {'NameUrdu': 'ملکانی منصب', 'FatherNameUrdu': 'زوجہ حافظ ملک کامران اکبر', 'SilsilaNo': '164', 'GharanaNo': '256'},
    '38201-1158228-1': {'NameUrdu': 'محمد سعید', 'FatherNameUrdu': 'محمد اسماعیل مرحوم', 'Age': '63'},
    '38201-0202235-5': {'NameUrdu': 'محمد ماجد علی', 'FatherNameUrdu': 'محمد سعید', 'Age': '20'},
    '38201-1116216-6': {'NameUrdu': 'شہزاد اختر', 'FatherNameUrdu': 'زوجہ محمد سعید', 'Age': '52'}
}

# Common OCR typo replacement rules
typo_replacements = [
    (r'\bعقلی\b', 'عظمیٰ'),
    (r'\bمروج\b', 'عروج'),
    (r'\bچنگی\b', 'مجتبیٰ'),
    (r'\bشکائل\b', 'ملکانی')
]

def clean_ocr_typos(text):
    if not text:
        return text
    res = text
    for pat, rep in typo_replacements:
        res = re.sub(pat, rep, res)
    return res

def process_file(json_file):
    if not os.path.exists(json_file):
        return
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    updated_records = 0
    for v in data:
        cnic = v.get('CNIC')
        
        # Apply spatial corrections for Silsila/Gharana/Age/Page
        if cnic in pdf_spatial_data:
            sp = pdf_spatial_data[cnic]
            if sp['SilsilaNo']: v['SilsilaNo'] = sp['SilsilaNo']
            if sp['GharanaNo']: v['GharanaNo'] = sp['GharanaNo']
            if sp['Age'] and not v.get('Age'): v['Age'] = sp['Age']
            v['Page'] = sp['Page']
            if v.get('BlockCode') and sp['GharanaNo']:
                v['FamilyId'] = f"{v['BlockCode']}_{sp['GharanaNo']}"
        
        # Apply clean OCR replacements
        if v.get('NameUrdu'):
            v['NameUrdu'] = clean_ocr_typos(v['NameUrdu'])
        if v.get('FatherNameUrdu'):
            v['FatherNameUrdu'] = clean_ocr_typos(v['FatherNameUrdu'])
        
        # Apply manual specific overrides
        if cnic in manual_corrections:
            for k, val in manual_corrections[cnic].items():
                v[k] = val
            if v.get('BlockCode') and v.get('GharanaNo'):
                v['FamilyId'] = f"{v['BlockCode']}_{v['GharanaNo']}"
            updated_records += 1

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Audited & Saved {json_file}")

process_file('ALL_VOTERS_COMBINED_FINAL.json')
process_file('voter-app/public/voter_data_final.json')

# 3. Re-crop precision name screenshots for updated records into public/names/
names_dir = 'voter-app/public/names'
os.makedirs(names_dir, exist_ok=True)

for cnic in manual_corrections.keys():
    if cnic in pdf_spatial_data:
        p_num = pdf_spatial_data[cnic]['Page']
        page = doc[p_num - 1]
        rects = page.search_for(cnic)
        if rects:
            r = rects[0]
            name_crop_box = fitz.Rect(280, max(0, r.y0 - 15), 520, min(page.rect.height, r.y1 + 15))
            pix = page.get_pixmap(clip=name_crop_box, dpi=200)
            pix.save(os.path.join(names_dir, f'{cnic}.jpg'))
            print(f"Generated fresh calligraphy crop for {cnic}")

print("Audit complete successfully!")
