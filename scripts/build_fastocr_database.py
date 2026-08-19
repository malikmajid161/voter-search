import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Load existing JSON voters
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

def is_header_or_noise(line):
    noise_keywords = [
        'صفحہ', 'کتاب', 'پر نٹنگ', 'دستخط', 'انتخابی', 'شماریاتی', 'سلسلہ', 'گھرانہ',
        'قومی شناختی', 'پتہ', 'عمر', 'موقع', 'تحصیل', 'ضلع', 'مردوال', 'محلہ', 'پٹوار',
        'حتمی', 'فہرست', 'مرد', 'خواتین', 'میزان', 'تاریخ', 'آفیسر'
    ]
    if any(k in line for k in noise_keywords):
        return True
    if re.match(r'^\d+\s*سال', line) or 'سال' in line:
        return True
    return False

sections = text.split('صفحہ نمبر')
extracted_txt_voters = {}

for s_idx, sec in enumerate(sections):
    raw_lines = [l.strip() for l in sec.splitlines() if l.strip()]
    if not raw_lines:
        continue
        
    cnic_matches = []
    for l_idx, l in enumerate(raw_lines):
        m = cnic_re.search(l)
        if m:
            cnic_matches.append((l_idx, m.group(1), l))
            
    if not cnic_matches:
        continue
        
    # Check if CNICs are grouped together in middle/end of section
    cnic_indices = [c[0] for c in cnic_matches]
    diffs = [cnic_indices[i+1] - cnic_indices[i] for i in range(len(cnic_indices)-1)] if len(cnic_indices) > 1 else [100]
    is_grouped = (sum(1 for d in diffs if d <= 3) / len(diffs) > 0.5) if diffs else False
    
    if is_grouped:
        # Grouped extraction: collect name/father pairs before first CNIC index
        first_cnic_idx = cnic_indices[0]
        top_lines = raw_lines[:first_cnic_idx]
        
        # Clean top_lines
        clean_name_lines = []
        for l in top_lines:
            if not is_header_or_noise(l) and not re.match(r'^\d+$', l):
                clean_name_lines.append(l)
                
        # Group name lines in pairs (Name, FatherName) or (Name, FatherName, Caste)
        # Match with list of CNICs in this section
        for i, c_tuple in enumerate(cnic_matches):
            cnic = c_tuple[1]
            # Try to pair with clean_name_lines
            if i*2+1 < len(clean_name_lines):
                n_candidate = clean_name_lines[i*2]
                f_candidate = clean_name_lines[i*2+1]
                extracted_txt_voters[cnic] = {
                    'NameUrdu': n_candidate,
                    'FatherNameUrdu': f_candidate,
                    'section': s_idx,
                    'type': 'grouped'
                }
    else:
        # Interleaved extraction: for each CNIC, find Name and Father immediately above it
        for c_idx, cnic, line in cnic_matches:
            back_lines = []
            for b in range(c_idx-1, -1, -1):
                pl = raw_lines[b]
                if cnic_re.search(pl):
                    break # Stop at previous CNIC
                if is_header_or_noise(pl) or 'صفحہ' in pl:
                    break
                if not re.match(r'^\d+$', pl):
                    back_lines.append(pl)
                if len(back_lines) >= 3:
                    break
                    
            if len(back_lines) >= 2:
                # back_lines[0] is father/husband name (or caste), back_lines[1] is voter name
                f_cand = back_lines[0]
                n_cand = back_lines[1]
                extracted_txt_voters[cnic] = {
                    'NameUrdu': n_cand,
                    'FatherNameUrdu': f_cand,
                    'section': s_idx,
                    'type': 'interleaved'
                }
            elif len(back_lines) == 1:
                extracted_txt_voters[cnic] = {
                    'NameUrdu': back_lines[0],
                    'FatherNameUrdu': '',
                    'section': s_idx,
                    'type': 'interleaved'
                }

print(f"Total voters successfully extracted from TXT: {len(extracted_txt_voters)}")

# Compare extracted voters with JSON voters
conflicts = []
matches = 0

for cnic, txt_v in extracted_txt_voters.items():
    if cnic not in json_map:
        continue
    j_v = json_map[cnic]
    j_n = j_v.get('NameUrdu', '').strip()
    j_f = j_v.get('FatherNameUrdu', '').strip()
    
    t_n = txt_v['NameUrdu'].strip()
    t_f = txt_v['FatherNameUrdu'].strip()
    
    # Check if exact match or conflict
    if j_n == t_n and j_f == t_f:
        matches += 1
    else:
        conflicts.append({
            'CNIC': cnic,
            'JSON_Name': j_n,
            'JSON_Father': j_f,
            'TXT_Name': t_n,
            'TXT_Father': t_f,
            'Type': txt_v['type']
        })

print(f"Exact Matches: {matches}")
print(f"Conflicts found: {len(conflicts)}")

print("\nSample 25 Conflicts:")
for c in conflicts[:25]:
    print(f"CNIC: {c['CNIC']} ({c['Type']})")
    print(f"  JSON: {c['JSON_Name']} | {c['JSON_Father']}")
    print(f"  TXT:  {c['TXT_Name']} | {c['TXT_Father']}")
    print("-" * 50)
