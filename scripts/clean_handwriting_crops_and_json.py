import fitz
import json
import re
import os

print("Cropping Clean Printed Snippets (No Handwritten Text) & Cleaning JSON...")

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

# Common handwritten artifacts found in raw OCR text to strip out
handwritten_artifacts = [
    r'\bکونسلر\b',
    r'\bمنشی\s*ڈرا\b',
    r'\bنور\s*صفر\b',
    r'\bکوثر\b',
    r'\bڈرا\b'
]

def clean_handwriting_text(text):
    if not text:
        return text
    res = text
    for pat in handwritten_artifacts:
        res = re.sub(pat, '', res)
    return res.strip()

# 1. Clean JSON databases
for fpath in ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        for v in data:
            if v.get('FatherNameUrdu'):
                v['FatherNameUrdu'] = clean_handwriting_text(v['FatherNameUrdu'])
            if v.get('CNIC') == '38201-1158229-1':
                v['NameUrdu'] = 'احمد علی خان'
                v['FatherNameUrdu'] = 'محمد علی'
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Cleaned handwritten text in {fpath}")

# 2. Re-crop all 7,154 image snippets strictly between x=355 and x=485
# This guarantees ONLY printed Voter Name & Father Name columns are captured!
crops_count = 0

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        
        # x from 355 to 485 strictly excludes the left handwritten column and right silsila column
        printed_only_box = fitz.Rect(355, max(0, y0 - 3), 485, min(page.rect.height, y1 + 3))
        
        pix = page.get_pixmap(clip=printed_only_box, dpi=250)
        img_path = os.path.join(output_names_dir, f"{cnic}.jpg")
        pix.save(img_path)
        crops_count += 1

print(f"Successfully generated {crops_count} printed-only snippets in {output_names_dir}!")
