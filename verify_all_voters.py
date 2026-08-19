import fitz
import json
import re

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)
cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')

verified_db = {}

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y_center = (cw[1] + cw[3]) / 2.0
        row_words = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 12]
        
        silsila_words = [w[4] for w in row_words if w[0] > 490 and w[4].isdigit()]
        gharana_words = [w[4] for w in row_words if 465 <= w[0] <= 495 and w[4].isdigit()]
        
        if silsila_words and gharana_words:
            verified_db[cnic] = {
                'SilsilaNo': silsila_words[0],
                'GharanaNo': gharana_words[0],
                'Page': p_idx + 1
            }

with open('ALL_VOTERS_COMBINED_FINAL.json', encoding='utf-8') as f:
    json_voters = json.load(f)

mismatches = []
updated_count = 0

for v in json_voters:
    cnic = v.get('CNIC')
    if cnic in verified_db:
        pdf_v = verified_db[cnic]
        cur_sil = str(v.get('SilsilaNo', '')).strip()
        cur_gha = str(v.get('GharanaNo', '')).strip()
        new_sil = pdf_v['SilsilaNo']
        new_gha = pdf_v['GharanaNo']
        
        if cur_sil != new_sil or cur_gha != new_gha:
            mismatches.append((cnic, cur_sil, cur_gha, new_sil, new_gha, pdf_v['Page']))
            v['SilsilaNo'] = new_sil
            v['GharanaNo'] = new_gha
            v['Page'] = pdf_v['Page']
            if v.get('BlockCode'):
                v['FamilyId'] = f"{v['BlockCode']}_{new_gha}"
            updated_count += 1

print(f'Total voters checked: {len(json_voters)}')
print(f'Total Silsila/Gharana corrections made: {updated_count}')
print('Sample of corrections:')
for m in mismatches[:15]:
    print(f"CNIC {m[0]} (Page {m[5]}): Old (Silsila #{m[1]}, Gharana #{m[2]}) -> Corrected (Silsila #{m[3]}, Gharana #{m[4]})")

with open('ALL_VOTERS_COMBINED_FINAL.json', 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)

with open('voter-app/public/voter_data_final.json', 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)

print('Updated JSON files successfully saved!')
