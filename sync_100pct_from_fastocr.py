import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=========================================================================")
print("  DIRECT 100% SYNCHRONIZATION FROM Voting List Full 2023-ocr-fastocr.txt")
print("=========================================================================\n")

def normalize_urdu(s):
    if not s:
        return ""
    s = s.replace('ه', 'ہ').replace('ى', 'ی').replace('ك', 'ک')
    s = re.sub(r'^\d+[\s\d]*', '', s) # remove leading OCR numbers like '18 ', '69 18 '
    s = s.replace('"', '').replace("'", '').strip()
    return s

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

noise_words = [
    'صفحہ', 'کتاب', 'پر نٹنگ', 'دستخط', 'انتخابی', 'شماریاتی', 'سلسلہ', 'گھرانہ',
    'قومی شناختی', 'پتہ', 'عمر', 'موقع', 'تحصیل', 'ضلع', 'مردوال', 'محلہ', 'پٹوار',
    'حتمی', 'فہرست', 'مرد', 'خواتین', 'میزان', 'تاریخ', 'آفیسر', 'لوکل گورنمنٹ',
    'رائے دہندگان', 'ڈاک', 'خانہ'
]

caste_words = ['کڑوگ', 'قصائی', 'نوچی', 'انصاری', 'توپی', 'ڈٹا', 'کلچه', 'رجیال', 'ہما سے را', 'قاضی', 'مشتری', 'شیر دا', 'سلی']

def is_noise_line(line):
    if any(k in line for k in noise_words):
        return True
    if 'سال' in line or re.search(r'\d+\s*سال', line):
        return True
    return False

lines = [l.strip() for l in text.splitlines() if l.strip()]

# Extract exact entries for every CNIC line in FastOCR txt
fastocr_entries = {}

for idx, line in enumerate(lines):
    m = cnic_re.search(line)
    if not m:
        continue
    cnic = m.group(1)
    
    # Look backwards up to 6 lines to find Name and Father Name
    candidates = []
    for b in range(idx-1, max(-1, idx-6), -1):
        pl = lines[b]
        if cnic_re.search(pl):
            break
        if is_noise_line(pl):
            continue
        if re.match(r'^\d+$', pl):
            continue
        c_clean = normalize_urdu(pl)
        if c_clean and c_clean not in caste_words:
            candidates.append(c_clean)
        if len(candidates) >= 2:
            break
            
    if len(candidates) >= 2:
        fastocr_entries[cnic] = {
            'NameUrdu': candidates[1],
            'FatherNameUrdu': candidates[0]
        }
    elif len(candidates) == 1:
        fastocr_entries[cnic] = {
            'NameUrdu': candidates[0],
            'FatherNameUrdu': ''
        }

print(f"Extracted {len(fastocr_entries)} CNIC voter entries from FastOCR text file.")

# Apply 100% of FastOCR text extracted updates to JSON voters
total_updated = 0
names_updated = 0
fathers_updated = 0

# Manual verified overrides for specific entries like Silsila 32 Sumayya Ali
manual_verifications = {
    '38201-3815683-8': {'NameUrdu': 'سمیہ علی', 'FatherNameUrdu': 'زوجہ ایاز احمد خان'},
    '38201-9495135-4': {'NameUrdu': 'نفیسہ جمال', 'FatherNameUrdu': 'زوجہ محمد فیصل'},
}

for cnic, f_v in fastocr_entries.items():
    if cnic not in json_map:
        continue
    v = json_map[cnic]
    
    old_n = v.get('NameUrdu', '')
    old_f = v.get('FatherNameUrdu', '')
    
    new_n = f_v['NameUrdu']
    new_f = f_v['FatherNameUrdu']
    
    # Apply manual verification if present
    if cnic in manual_verifications:
        new_n = manual_verifications[cnic]['NameUrdu']
        new_f = manual_verifications[cnic]['FatherNameUrdu']
        
    changed = False
    if new_n and new_n != old_n and not new_n.startswith('زوجہ ') and not new_n.startswith('دختر '):
        v['NameUrdu'] = new_n
        names_updated += 1
        changed = True
        
    if new_f and new_f != old_f:
        v['FatherNameUrdu'] = new_f
        fathers_updated += 1
        changed = True
        
    if changed:
        total_updated += 1

# Ensure manual verifications are applied even if CNIC parsing missed it
for scnic, mv in manual_verifications.items():
    if scnic in json_map:
        v = json_map[scnic]
        v['NameUrdu'] = mv['NameUrdu']
        v['FatherNameUrdu'] = mv['FatherNameUrdu']

print(f"Total voter records updated: {total_updated}")
print(f"  - NameUrdu updates:       {names_updated}")
print(f"  - FatherNameUrdu updates: {fathers_updated}\n")

# Save updated ALL_VOTERS_COMBINED_FINAL.json
json_path = 'voter-app/ALL_VOTERS_COMBINED_FINAL.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)
print(f"[OK] Master database updated: {json_path}")

# Sync voter_data_final.json across public, src, dist
voter_data_paths = [
    'voter-app/public/voter_data_final.json',
    'voter-app/src/voter_data_final.json',
    'voter-app/dist/voter_data_final.json'
]

for p in voter_data_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(json_voters, f, ensure_ascii=False, indent=2)
    print(f"[OK] Synced voter file: {p}")

# Rebuild family_data.json across public, src, dist
family_dict = {}
for v in json_voters:
    fam_id = v.get('FamilyId')
    if not fam_id:
        block = v.get('BlockCode', '266010901')
        gharana = v.get('GharanaNo', '1')
        fam_id = f"{block}_{gharana}"
        v['FamilyId'] = fam_id
        
    if fam_id not in family_dict:
        family_dict[fam_id] = {
            'id': fam_id,
            'blockCode': v.get('BlockCode', ''),
            'gharanaNo': v.get('GharanaNo', ''),
            'members': []
        }
    family_dict[fam_id]['members'].append(v)

family_paths = [
    'voter-app/public/family_data.json',
    'voter-app/src/family_data.json',
    'voter-app/dist/family_data.json'
]

for p in family_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(family_dict, f, ensure_ascii=False, indent=2)
    print(f"[OK] Synced family file ({len(family_dict)} families): {p}")

print("\n=========================================================================")
print("  100% FASTOCR DATA SYNC COMPLETE!")
print("=========================================================================")
