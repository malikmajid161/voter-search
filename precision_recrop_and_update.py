import fitz
import json
import re
import os

print("Starting Precision Row Cropping and Database Update...")

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

# Specific corrections for names verified from PDF scans
verified_name_updates = {
    '38201-5057660-7': {'NameUrdu': 'محمد مجتبیٰ علی', 'FatherNameUrdu': 'احمد علی خان'},
    '38201-1116216-6': {'NameUrdu': 'شہناز اختر', 'FatherNameUrdu': 'زوجہ محمد سعید'},
    '38201-9004840-4': {'NameUrdu': 'عظمیٰ علی', 'FatherNameUrdu': 'دختر محمد سعید'},
    '38201-6205416-4': {'NameUrdu': 'عروج علی', 'FatherNameUrdu': 'دختر محمد سعید'},
    '38403-4407767-4': {'NameUrdu': 'ملکانی منصب', 'FatherNameUrdu': 'زوجہ حافظ ملک کامران اکبر'}
}

# Regex replacements for common OCR misreads across the database
ocr_replacements = [
    (r'\bمحمد چنگی علی\b', 'محمد مجتبیٰ علی'),
    (r'\bعقلی علی\b', 'عظمیٰ علی'),
    (r'\bمروج علی\b', 'عروج علی'),
    (r'\bشکائل منصب\b', 'ملکانی منصب'),
    (r'\bعقلی\b', 'عظمیٰ'),
    (r'\bمروج\b', 'عروج'),
    (r'\bچنگی\b', 'مجتبیٰ'),
    (r'\bشکائل\b', 'ملکانی')
]

def clean_ocr(text):
    if not text:
        return text
    res = text
    for pat, rep in ocr_replacements:
        res = re.sub(pat, rep, res)
    return res

# Update JSON files
def update_json_db(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    for v in data:
        cnic = v.get('CNIC')
        if cnic in verified_name_updates:
            v['NameUrdu'] = verified_name_updates[cnic]['NameUrdu']
            v['FatherNameUrdu'] = verified_name_updates[cnic]['FatherNameUrdu']
            updated += 1
        else:
            if v.get('NameUrdu'):
                v['NameUrdu'] = clean_ocr(v['NameUrdu'])
            if v.get('FatherNameUrdu'):
                v['FatherNameUrdu'] = clean_ocr(v['FatherNameUrdu'])
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated JSON database {file_path}")

update_json_db('ALL_VOTERS_COMBINED_FINAL.json')
update_json_db('voter-app/public/voter_data_final.json')

# Perform precision single-row cropping for all voters across all 299 pages
print("Cropping clean single-row image snippets for all 299 pages...")
crops_count = 0

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        
        # Tight single-row bounding box:
        # x from 325 (Father Name start) to 490 (Silsila/Gharana boundary)
        # y from y0-1 to y1+1 (prevents row overlap above/below)
        tight_box = fitz.Rect(325, max(0, y0 - 1), 490, min(page.rect.height, y1 + 1))
        
        pix = page.get_pixmap(clip=tight_box, dpi=250)
        img_path = os.path.join(output_names_dir, f"{cnic}.jpg")
        pix.save(img_path)
        crops_count += 1

print(f"Successfully generated {crops_count} tight single-row calligraphy crops in {output_names_dir}!")
