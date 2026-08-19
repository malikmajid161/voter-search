import fitz
import json
import re
import os
import sys

print("Initializing 299-Frame Full PDF Auditor...")

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)
total_pages = len(doc)
print(f"Loaded PDF: {total_pages} total page frames.")

cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')
block_pattern = re.compile(r'\b\d{9}\b')

# Directory for verified visual calligraphy crops
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

# Load existing JSON database
json_path = 'ALL_VOTERS_COMBINED_FINAL.json'
with open(json_path, encoding='utf-8') as f:
    voters_db = json.load(f)

voter_dict = {v['CNIC']: v for v in voters_db if v.get('CNIC')}

total_extracted_rows = 0
updated_silsila_gharana = 0
crops_generated = 0

print("Starting page-by-page frame verification across all 299 pages...")

for p_idx in range(total_pages):
    page = doc[p_idx]
    page_num = p_idx + 1
    words = page.get_text('words')
    
    # Extract page BlockCode from header if present
    page_blocks = [w[4] for w in words if block_pattern.match(w[4])]
    current_block = page_blocks[0] if page_blocks else None
    
    # Find all voter CNICs on this page frame
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        total_extracted_rows += 1
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        y_center = (y0 + y1) / 2.0
        
        # Gather all text tokens on this specific row (vertical tolerance +/- 12pt)
        row_words = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 12]
        row_words.sort(key=lambda w: w[0]) # Left to right
        
        # Spatial extraction based on fixed column coordinates:
        # Silsila No: Far right (x > 490)
        silsila_tokens = [w[4] for w in row_words if w[0] > 490 and w[4].isdigit()]
        # Gharana No: Middle right (465 <= x <= 495)
        gharana_tokens = [w[4] for w in row_words if 465 <= w[0] <= 495 and w[4].isdigit()]
        # Age: Left of CNIC (200 <= x <= 245)
        age_tokens = [re.sub(r'\D', '', w[4]) for w in row_words if 200 <= w[0] <= 245 and re.sub(r'\D', '', w[4]).isdigit()]
        
        silsila = silsila_tokens[0] if silsila_tokens else None
        gharana = gharana_tokens[0] if gharana_tokens else None
        age = age_tokens[0] if age_tokens else None
        
        # Update or create record in voter_dict
        if cnic in voter_dict:
            rec = voter_dict[cnic]
        else:
            rec = {'CNIC': cnic}
            voter_dict[cnic] = rec
        
        rec['Page'] = page_num
        if current_block and not rec.get('BlockCode'):
            rec['BlockCode'] = current_block
            
        if silsila:
            if rec.get('SilsilaNo') != silsila:
                rec['SilsilaNo'] = silsila
                updated_silsila_gharana += 1
        if gharana:
            if rec.get('GharanaNo') != gharana:
                rec['GharanaNo'] = gharana
                updated_silsila_gharana += 1
                
        if rec.get('BlockCode') and rec.get('GharanaNo'):
            rec['FamilyId'] = f"{rec['BlockCode']}_{rec['GharanaNo']}"
            
        if age and (not rec.get('Age') or rec.get('Age') == ''):
            rec['Age'] = age
            
        # Crop precise Urdu Name calligraphy snippet directly from PDF page frame
        crop_box = fitz.Rect(280, max(0, y0 - 15), 520, min(page.rect.height, y1 + 15))
        pix = page.get_pixmap(clip=crop_box, dpi=180)
        img_file = os.path.join(output_names_dir, f"{cnic}.jpg")
        pix.save(img_file)
        crops_generated += 1

print("\n--- 299-PAGE FRAME AUDIT COMPLETE ---")
print(f"Total Pages Processed: {total_pages}")
print(f"Total Voter Rows Verified: {total_extracted_rows}")
print(f"Total Silsila/Gharana Values Updated: {updated_silsila_gharana}")
print(f"Total High-Res Calligraphy Crops Saved: {crops_generated}")

# Re-apply verified manual name text fixes
manual_name_fixes = {
    '38201-9004840-4': ('عظمیٰ علی', 'دختر محمد سعید'),
    '38201-6205416-4': ('عروج علی', 'دختر محمد سعید'),
    '38201-5057660-7': ('محمد مجتبیٰ علی', 'احمد علی خان'),
    '38403-4407767-4': ('ملکانی منصب', 'زوجہ حافظ ملک کامران اکبر')
}
for cnic, (name, fname) in manual_name_fixes.items():
    if cnic in voter_dict:
        voter_dict[cnic]['NameUrdu'] = name
        voter_dict[cnic]['FatherNameUrdu'] = fname

# Save final updated voter array
final_voter_list = list(voter_dict.values())

with open('ALL_VOTERS_COMBINED_FINAL.json', 'w', encoding='utf-8') as f:
    json.dump(final_voter_list, f, ensure_ascii=False, indent=2)

with open('voter-app/public/voter_data_final.json', 'w', encoding='utf-8') as f:
    json.dump(final_voter_list, f, ensure_ascii=False, indent=2)

print("Saved verified database to ALL_VOTERS_COMBINED_FINAL.json and voter_data_final.json!")
