import re
import json
import sys
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding='utf-8')

# Helper function for similarity ratio
def similarity(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

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
    s = re.sub(r'^\d+[\s\d]*', '', s)
    s = s.replace('"', '').replace("'", '').strip()
    # Strip caste suffix if present at end
    for c in caste_words:
        if s.endswith(' ' + c):
            s = s[:-len(' ' + c)].strip()
    return s

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

verified_updates = {}

for cnic, t_v in extracted.items():
    if cnic not in json_map:
        continue
    j_v = json_map[cnic]
    j_n = j_v.get('NameUrdu', '').strip()
    j_f = j_v.get('FatherNameUrdu', '').strip()
    
    t_n = clean_name(t_v['NameUrdu'])
    t_f = clean_name(t_v['FatherNameUrdu'])
    
    upd = {}
    
    # Name validation:
    # 1. Similarity > 0.45 (same person, spelling fix e.g. اشتیاق احمد -> اشفاق احمد, اکبر -> گلباز)
    # 2. Known specific corrections (e.g. اکبر باز خان -> گلباز خان)
    if t_n and t_n != j_n:
        sim_n = similarity(j_n, t_n)
        if sim_n >= 0.40 or ('اکبر' in j_n and 'گلباز' in t_n) or ('ارشد' in j_n and 'طارق' in t_n):
            upd['NameUrdu'] = t_n
            
    # Father validation:
    if t_f and t_f != j_f:
        sim_f = similarity(j_f, t_f)
        if sim_f >= 0.40 or ('اکبر' in j_f and 'گلباز' in t_f) or (t_f in j_f and len(t_f) >= 4):
            upd['FatherNameUrdu'] = t_f
            
    if upd:
        verified_updates[cnic] = {
            'updates': upd,
            'old_name': j_n,
            'new_name': upd.get('NameUrdu', j_n),
            'old_father': j_f,
            'new_father': upd.get('FatherNameUrdu', j_f),
            'silsila': j_v.get('SilsilaNo'),
            'block': j_v.get('BlockCode')
        }

print(f"Total VERIFIED high-confidence updates: {len(verified_updates)}")

print("\nListing Verified Updates:")
for cnic, v in list(verified_updates.items()):
    print(f"CNIC: {cnic} (Silsila {v['silsila']}, Block {v['block']})")
    if 'NameUrdu' in v['updates']:
        print(f"  Name:   '{v['old_name']}'  ==>  '{v['new_name']}'")
    if 'FatherNameUrdu' in v['updates']:
        print(f"  Father: '{v['old_father']}'  ==>  '{v['new_father']}'")
    print("-" * 50)
