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

# Words to ignore for voter names
noise_words = [
    'صفحہ', 'کتاب', 'پر نٹنگ', 'دستخط', 'انتخابی', 'شماریاتی', 'سلسلہ', 'گھرانہ',
    'قومی شناختی', 'پتہ', 'عمر', 'موقع', 'تحصیل', 'ضلع', 'مردوال', 'محلہ', 'پٹوار',
    'حتمی', 'فہرست', 'مرد', 'خواتین', 'میزان', 'تاریخ', 'آفیسر', 'لوکل گورنمنٹ',
    'رائے دہندگان', 'ڈاک', 'خانہ'
]

# Caste words that often follow father names
caste_words = ['کڑوگ', 'قصائی', 'نوچی', 'انصاری', 'توپی', 'ڈٹا', 'کلچه', 'رجیال', 'ہما سے را', 'قاضی', 'مشتری', 'کون دا', 'شیر دا', 'سلی']

def is_noise_line(line):
    if any(k in line for k in noise_words):
        return True
    if 'سال' in line or re.search(r'\d+\s*سال', line):
        return True
    return False

def clean_name(s):
    if not s:
        return ""
    # Strip leading digits and space
    s = re.sub(r'^\d+[\s\d]*', '', s)
    s = s.replace('"', '').replace("'", '').strip()
    return s

lines = [l.strip() for l in text.splitlines() if l.strip()]

# Extract entries with high accuracy
extracted = {}

for idx, line in enumerate(lines):
    m = cnic_re.search(line)
    if not m:
        continue
    cnic = m.group(1)
    
    # Look backward up to 6 lines
    cand = []
    for b in range(idx-1, max(-1, idx-6), -1):
        pl = lines[b]
        if cnic_re.search(pl):
            break
        if is_noise_line(pl):
            continue
        if re.match(r'^\d+$', pl):
            continue
        c_clean = clean_name(pl)
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

print(f"Extracted candidate details for {len(extracted)} CNICs.")

# Check updates to JSON
proposed_updates = {}
for cnic, t_v in extracted.items():
    if cnic not in json_map:
        continue
    j_v = json_map[cnic]
    j_n = j_v.get('NameUrdu', '').strip()
    j_f = j_v.get('FatherNameUrdu', '').strip()
    
    t_n = t_v['NameUrdu'].strip()
    t_f = t_v['FatherNameUrdu'].strip()
    
    # Check if there is meaningful difference
    name_changed = False
    father_changed = False
    
    new_n = j_n
    new_f = j_f
    
    # If TXT name is valid and different, update
    if t_n and t_n != j_n and len(t_n) >= 2:
        # Check if t_n is not just father name shifted
        if t_n != j_f:
            new_n = t_n
            name_changed = True
            
    if t_f and t_f != j_f and len(t_f) >= 2:
        if t_f != j_n:
            new_f = t_f
            father_changed = True
            
    if name_changed or father_changed:
        proposed_updates[cnic] = {
            'old_name': j_n,
            'new_name': new_n,
            'old_father': j_f,
            'new_father': new_f,
            'silsila': j_v.get('SilsilaNo'),
            'block': j_v.get('BlockCode')
        }

print(f"Total proposed voter updates: {len(proposed_updates)}")

print("\nSample 40 Proposed Updates:")
count = 0
for cnic, u in list(proposed_updates.items())[:40]:
    print(f"CNIC: {cnic} (Silsila {u['silsila']}, Block {u['block']})")
    if u['old_name'] != u['new_name']:
        print(f"  Name:   '{u['old_name']}'  ==>  '{u['new_name']}'")
    if u['old_father'] != u['new_father']:
        print(f"  Father: '{u['old_father']}'  ==>  '{u['new_father']}'")
    print("-" * 50)
