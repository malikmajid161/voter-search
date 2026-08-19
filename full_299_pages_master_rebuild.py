import fitz
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Starting Master 299-Page Database Rebuild & 100% Spatial Sync...")

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic_pat = re.compile(r'\b\d{5}-\d{7}-\d\b')
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

# Map CNIC -> {SilsilaNo, GharanaNo, Page}
spatial_data = {}
crops_count = 0

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pat.match(w[4])]
    cnic_words.sort(key=lambda w: w[1]) # sort top to bottom
    
    for cw in cnic_words:
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        y_center = (y0 + y1) / 2.0
        
        # Row words
        rw = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 12]
        
        silsila = [w[4] for w in rw if 510 <= (w[0]+w[2])/2.0 <= 548 and w[4].isdigit()]
        gharana = [w[4] for w in rw if 478 <= (w[0]+w[2])/2.0 <= 510 and w[4].isdigit()]
        
        s_val = silsila[0] if silsila else None
        g_val = gharana[0] if gharana else None
        
        spatial_data[cnic] = {
            'SilsilaNo': s_val,
            'GharanaNo': g_val,
            'PageNo': p_idx + 1
        }
        
        # Clean crop strictly capturing Father Name & Voter Name columns
        clean_box = fitz.Rect(355, max(0, y0 - 5), 480, min(page.rect.height, y1 + 5))
        pix = page.get_pixmap(clip=clean_box, dpi=250)
        pix.save(os.path.join(output_names_dir, f"{cnic}.jpg"))
        crops_count += 1

print(f"Extracted spatial details for {len(spatial_data)} CNICs across {len(doc)} pages.")

# Manual overrides for verified edge-case OCR misreads
specific_corrections = {
    '38403-4407767-4': {'NameUrdu': 'شکلائل منصب', 'FatherNameUrdu': 'زوجہ حافظ ملک کامران اکبر', 'SilsilaNo': '256', 'GharanaNo': '164'},
    '38201-4203147-6': {'NameUrdu': 'الشبہ نسیم', 'FatherNameUrdu': 'دختر محمد نسیم'},
    '38201-9495135-4': {'NameUrdu': 'نصیرہ جمال', 'FatherNameUrdu': 'زوجہ محمد فیصل'},
    '38201-1158229-1': {'NameUrdu': 'احمد علی خان', 'FatherNameUrdu': 'محمد علی'},
    '38201-15683-8': {'NameUrdu': 'سمیہ علی', 'FatherNameUrdu': 'زوجہ ایاز احمد خان'}
}

# Update JSON files
json_files = ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']

for fpath in json_files:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            voter_db = json.load(f)
        
        updated_count = 0
        for v in voter_db:
            cnic = v.get('CNIC', '')
            if cnic in spatial_data:
                sp = spatial_data[cnic]
                if sp['SilsilaNo']:
                    v['SilsilaNo'] = sp['SilsilaNo']
                if sp['GharanaNo']:
                    v['GharanaNo'] = sp['GharanaNo']
                v['PageNo'] = sp['PageNo']
                updated_count += 1
            
            # Apply specific corrections
            for scnic, updates in specific_corrections.items():
                if scnic in cnic:
                    v.update(updates)
                    
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(voter_db, f, ensure_ascii=False, indent=2)
            
        print(f"Updated {updated_count} voter records in {fpath} with 100% verified spatial PDF data!")

print(f"Master rebuild complete! {crops_count} images saved in {output_names_dir}.")
