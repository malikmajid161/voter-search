import json
import fitz
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Applying verified corrections to JSON and re-generating clean image crops...")

# List of specific corrections verified from original PDF
corrections = {
    '38201-4203147-6': {'NameUrdu': 'الشبہ نسیم', 'FatherNameUrdu': 'دختر محمد نسیم'},
    '38201-9495135-4': {'NameUrdu': 'نصیرہ جمال', 'FatherNameUrdu': 'زوجہ محمد فیصل'},
    '38201-1158229-1': {'NameUrdu': 'احمد علی خان', 'FatherNameUrdu': 'محمد علی'},
    '38201-15683-8': {'NameUrdu': 'سمیہ علی', 'FatherNameUrdu': 'زوجہ ایاز احمد خان'},
}

json_files = ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']

for fpath in json_files:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        
        for v in data:
            cnic = v.get('CNIC', '')
            for target_cnic, updates in corrections.items():
                if target_cnic in cnic:
                    v.update(updates)
                    print(f"Updated {cnic} in {fpath}: {updates}")
                    
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# Re-crop all image snippets across all pages with clean boundaries (x: 360 -> 475)
pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

crops_count = 0

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        
        # Crop strictly inside the two name columns (Father Name & Voter Name)
        clean_box = fitz.Rect(360, max(0, y0 - 5), 475, min(page.rect.height, y1 + 5))
        
        pix = page.get_pixmap(clip=clean_box, dpi=250)
        img_path = os.path.join(output_names_dir, f"{cnic}.jpg")
        pix.save(img_path)
        crops_count += 1

print(f"Successfully re-cropped {crops_count} voter name snippets with ultra-clean boundaries!")
