import fitz
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Performing full system-wide row alignment audit across all 299 PDF pages...")

doc = fitz.open('Voting List Full 2023.pdf')
cnic_pat = re.compile(r'\b\d{5}-\d{7}-\d\b')

mismatches = []
total_checked = 0

with open('voter-app/public/voter_data_final.json', encoding='utf-8') as f:
    voter_db = json.load(f)

voter_by_cnic = {v['CNIC']: v for v in voter_db}

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnics = [w for w in words if cnic_pat.match(w[4])]
    cnics.sort(key=lambda w: w[1]) # Top-to-bottom
    
    for i, cw in enumerate(cnics):
        cnic = cw[4]
        total_checked += 1
        y_center = (cw[1] + cw[3]) / 2.0
        row_w = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 14]
        
        sil_words = [w[4] for w in row_w if (w[0]+w[2])/2.0 > 510]
        sil_num = [re.sub(r'\D', '', w) for w in sil_words if re.sub(r'\D', '', w)]
        
        gh_words = [w[4] for w in row_w if 470 <= (w[0]+w[2])/2.0 <= 510]
        gh_num = [re.sub(r'\D', '', w) for w in gh_words if re.sub(r'\D', '', w)]
        
        v = voter_by_cnic.get(cnic)
        if v:
            expected_sil = sil_num[0] if sil_num else None
            expected_gh = gh_num[0] if gh_num else None
            
            if expected_sil and v.get('SilsilaNo') != expected_sil:
                mismatches.append((cnic, 'SilsilaNo', v.get('SilsilaNo'), expected_sil, p_idx+1))
            if expected_gh and v.get('GharanaNo') != expected_gh:
                mismatches.append((cnic, 'GharanaNo', v.get('GharanaNo'), expected_gh, p_idx+1))

print(f"Audited {total_checked} voter rows across PDF.")
print(f"Total Silsila/Gharana mismatches found: {len(mismatches)}")

if mismatches:
    print("First 10 mismatches:")
    for m in mismatches[:10]:
        print(f"  CNIC {m[0]} (Page {m[4]}): {m[1]} in JSON is '{m[2]}', physical PDF shows '{m[3]}'")
