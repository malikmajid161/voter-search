import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

def clean_urdu_name(text_str):
    if not text_str:
        return ""
    # Remove leading OCR sequence numbers like '18 ', '69 18 '
    text_str = re.sub(r'^\d+[\s\d]*', '', text_str)
    # Remove quote marks
    text_str = text_str.replace('"', '').replace("'", '').strip()
    return text_str

sections = text.split('صفحہ نمبر')
extracted_database = {}

last_seen_father = ""

for s_idx, sec in enumerate(sections):
    lines = [l.strip() for l in sec.splitlines() if l.strip()]
    if not lines:
        continue

    for idx, l in enumerate(lines):
        m = cnic_re.search(l)
        if m:
            cnic = m.group(1)
            # Find voter name & father name above this line
            candidates = []
            for b in range(idx-1, max(-1, idx-6), -1):
                pl = lines[b]
                if cnic_re.search(pl):
                    break
                if 'صفحہ' in pl or 'کتاب' in pl or 'پر نٹنگ' in pl or 'حتمی' in pl or 'شماریاتی' in pl:
                    break
                if re.match(r'^\d+\s*سال', pl) or 'سال' in pl or 'تحصیل' in pl or 'ضلع' in pl:
                    continue
                if re.match(r'^\d+$', pl):
                    continue
                c_clean = clean_urdu_name(pl)
                if c_clean:
                    candidates.append(c_clean)
            
            # Usually candidate[0] is father or caste, candidate[1] is voter name
            if len(candidates) >= 2:
                name_cand = candidates[1]
                father_cand = candidates[0]
                if father_cand == "" or father_cand == '"':
                    father_cand = last_seen_father
                else:
                    last_seen_father = father_cand
                    
                extracted_database[cnic] = {
                    'NameUrdu': name_cand,
                    'FatherNameUrdu': father_cand,
                    'CNIC': cnic
                }
            elif len(candidates) == 1:
                name_cand = candidates[0]
                extracted_database[cnic] = {
                    'NameUrdu': name_cand,
                    'FatherNameUrdu': last_seen_father,
                    'CNIC': cnic
                }

print(f"Extracted {len(extracted_database)} voters from TXT.")

# Audit against JSON
conflicts = []
for cnic, txt_v in extracted_database.items():
    if cnic not in json_map:
        continue
    j_v = json_map[cnic]
    j_name = j_v.get('NameUrdu', '').strip()
    j_father = j_v.get('FatherNameUrdu', '').strip()
    
    t_name = txt_v['NameUrdu'].strip()
    t_father = txt_v['FatherNameUrdu'].strip()
    
    # Clean comparison
    if j_name != t_name or (t_father and t_father not in j_father):
        conflicts.append({
            'CNIC': cnic,
            'JSON_Name': j_name,
            'JSON_Father': j_father,
            'TXT_Name': t_name,
            'TXT_Father': t_father,
            'SilsilaNo': j_v.get('SilsilaNo'),
            'BlockCode': j_v.get('BlockCode'),
            'PageNo': j_v.get('PageNo')
        })

print(f"Total conflicts found: {len(conflicts)}")
print("\nFirst 30 Conflicts Detail:")
for c in conflicts[:30]:
    print(f"CNIC: {c['CNIC']} (Silsila {c['SilsilaNo']}, Block {c['BlockCode']})")
    print(f"  JSON Name:   '{c['JSON_Name']}' | Father: '{c['JSON_Father']}'")
    print(f"  TXT Name:    '{c['TXT_Name']}' | Father: '{c['TXT_Father']}'")
    print("-" * 60)
