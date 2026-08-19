import re
import json
import os
import sys
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

print("=========================================================================")
print("  EXECUTING MASTER FASTOCR JSON UPDATE & FAMILY DATA REBUILD")
print("=========================================================================\n")

def similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

# Normalize Urdu characters for clean database storage
def normalize_urdu(text_str):
    if not text_str:
        return ""
    text_str = text_str.replace('ه', 'ہ').replace('ى', 'ی').replace('ك', 'ک')
    text_str = re.sub(r'^\d+[\s\d]*', '', text_str)
    text_str = text_str.replace('"', '').replace("'", '').strip()
    return text_str

# Read FastOCR text file
txt_path = 'Voting List Full 2023-ocr-fastocr.txt'
with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Load master JSON
json_path = 'voter-app/ALL_VOTERS_COMBINED_FINAL.json'
with open(json_path, 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

noise_words = [
    'صفحہ', 'کتاب', 'پر نٹنگ', 'دستخط', 'انتخابی', 'شماریاتی', 'سلسلہ', 'گھرانہ',
    'قومی شناختی', 'پتہ', 'عمر', 'موقع', 'تحصیل', 'ضلع', 'مردوال', 'محلہ', 'پٹوار',
    'حتمی', 'فہرست', 'مرد', 'خواتین', 'میزان', 'تاریخ', 'آفیسر', 'لوکل گورنمنٹ',
    'رائے دہندگان', 'ڈاک', 'خانہ'
]

caste_words = ['کڑوگ', 'قصائی', 'نوچی', 'انصاری', 'توپی', 'ڈٹا', 'کلچه', 'رجیال', 'ہما سے را', 'قاضی', 'مشتری', 'کون دا', 'شیر دا', 'سلی']

def is_noise_line(line):
    if any(k in line for k in noise_words):
        return True
    if 'سال' in line or re.search(r'\d+\s*سال', line):
        return True
    return False

lines = [l.strip() for l in text.splitlines() if l.strip()]

extracted = {}
for idx, line in enumerate(lines):
    m = cnic_re.search(line)
    if not m:
        continue
    cnic = m.group(1)
    
    cand = []
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
            cand.append(c_clean)
        if len(cand) >= 2:
            break
            
    if len(cand) >= 2:
        extracted[cnic] = {
            'NameUrdu': cand[1],
            'FatherNameUrdu': cand[0]
        }
    elif len(cand) == 1:
        extracted[cnic] = {
            'NameUrdu': cand[0],
            'FatherNameUrdu': ''
        }

# Filter and verify updates
applied_updates_count = 0
name_updates_count = 0
father_updates_count = 0

audit_log = []

for cnic, t_v in extracted.items():
    if cnic not in json_map:
        continue
    v = json_map[cnic]
    
    j_n = normalize_urdu(v.get('NameUrdu', ''))
    j_f = normalize_urdu(v.get('FatherNameUrdu', ''))
    
    t_n = normalize_urdu(t_v['NameUrdu'])
    t_f = normalize_urdu(t_v['FatherNameUrdu'])
    
    # Reject if t_n looks like father relationship string (e.g. starts with 'زوجہ' or 'دختر') unless old name was wrong
    if t_n.startswith('زوجہ ') or t_n.startswith('دختر '):
        continue
        
    name_to_apply = None
    father_to_apply = None
    
    # Check Name change
    if t_n and t_n != j_n:
        sim_n = similarity(j_n, t_n)
        if sim_n >= 0.40 or ('اکبر' in j_n and 'گلباز' in t_n) or ('ارشد' in j_n and 'طارق' in t_n):
            name_to_apply = t_n
            
    # Check Father change
    if t_f and t_f != j_f:
        sim_f = similarity(j_f, t_f)
        if sim_f >= 0.40 or ('اکبر' in j_f and 'گلباز' in t_f) or (t_f in j_f and len(t_f) >= 4):
            father_to_apply = t_f
            
    if name_to_apply or father_to_apply:
        applied_updates_count += 1
        log_entry = {'CNIC': cnic, 'old_name': j_n, 'old_father': j_f}
        
        if name_to_apply:
            v['NameUrdu'] = name_to_apply
            log_entry['new_name'] = name_to_apply
            name_updates_count += 1
        if father_to_apply:
            v['FatherNameUrdu'] = father_to_apply
            log_entry['new_father'] = father_to_apply
            father_updates_count += 1
            
        audit_log.append(log_entry)

print(f"Total voters updated from FastOCR: {applied_updates_count}")
print(f"  - NameUrdu updates:       {name_updates_count}")
print(f"  - FatherNameUrdu updates: {father_updates_count}\n")

# Save updated ALL_VOTERS_COMBINED_FINAL.json
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)

print(f"[OK] Updated master file: {json_path}")

# Sync voter_data_final.json paths
voter_data_paths = [
    'voter-app/public/voter_data_final.json',
    'voter-app/src/voter_data_final.json',
    'voter-app/dist/voter_data_final.json'
]

for p in voter_data_paths:
    if os.path.exists(os.path.dirname(p)):
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_voters, f, ensure_ascii=False, indent=2)
        print(f"[OK] Synced voter data to: {p}")

# Rebuild family_data.json
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
    if os.path.exists(os.path.dirname(p)):
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(family_dict, f, ensure_ascii=False, indent=2)
        print(f"[OK] Synced family database ({len(family_dict)} families) to: {p}")

print("\n=========================================================================")
print("  MASTER UPDATE & FAMILY DATA SYNC COMPLETE!")
print("=========================================================================")
