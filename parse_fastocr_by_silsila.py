import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Load JSON voters map by CNIC
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_cnic_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

def is_noise(line):
    noise_keywords = [
        'صفحہ', 'کتاب', 'پر نٹنگ', 'دستخط', 'انتخابی', 'شماریاتی', 'سلسلہ', 'گھرانہ',
        'قومی شناختی', 'پتہ', 'عمر', 'موقع', 'تحصیل', 'ضلع', 'مردوال', 'محلہ', 'پٹوار',
        'حتمی', 'فہرست', 'مرد', 'خواتین', 'میزان', 'تاریخ', 'آفیسر', 'لوکل گورنمنٹ',
        'رائے دہندگان', 'کون دا'
    ]
    if any(k in line for k in noise_keywords):
        return True
    if re.match(r'^\d+\s*سال', line) or 'سال' in line:
        return True
    return False

# Parse text page by page
sections = text.split('صفحہ نمبر')
all_parsed = {}

for s_idx, sec in enumerate(sections):
    lines = [l.strip() for l in sec.splitlines() if l.strip()]
    if not lines:
        continue
        
    # Extract CNICs in this section
    cnic_matches = []
    for l_idx, l in enumerate(lines):
        m = cnic_re.search(l)
        if m:
            cnic_matches.append((l_idx, m.group(1), l))
            
    if not cnic_matches:
        continue
        
    cnic_indices = [c[0] for c in cnic_matches]
    first_cnic_idx = cnic_indices[0]
    
    # Check if section has top voter blocks (Gharana/Silsila/Name/Father)
    top_lines = lines[:first_cnic_idx]
    
    voter_blocks = []
    curr_block = []
    
    for l in top_lines:
        if is_noise(l):
            continue
        # Check if line is purely integer (Silsila or Gharana number)
        if re.match(r'^\d+$', l):
            val = int(l)
            if val < 500: # Typical silsila or gharana number range
                if len(curr_block) >= 2:
                    voter_blocks.append(curr_block)
                    curr_block = []
                continue
        curr_block.append(l)
        
    if len(curr_block) >= 2:
        voter_blocks.append(curr_block)
        
    # If number of voter_blocks matches or is close to number of CNICs
    if len(voter_blocks) >= len(cnic_matches) - 2 and len(voter_blocks) > 0:
        for i, c_tuple in enumerate(cnic_matches):
            cnic = c_tuple[1]
            if i < len(voter_blocks):
                vb = voter_blocks[i]
                n_cand = vb[0]
                f_cand = vb[1] if len(vb) > 1 else ''
                all_parsed[cnic] = {
                    'NameUrdu': n_cand,
                    'FatherNameUrdu': f_cand,
                    'section': s_idx,
                    'method': 'blocks_grouped'
                }
    else:
        # Fallback to interleaved lookup
        for c_idx, cnic, line in cnic_matches:
            back_lines = []
            for b in range(c_idx-1, -1, -1):
                pl = lines[b]
                if cnic_re.search(pl):
                    break
                if is_noise(pl) or 'صفحہ' in pl:
                    break
                if not re.match(r'^\d+$', pl):
                    back_lines.append(pl)
                if len(back_lines) >= 2:
                    break
            if len(back_lines) >= 2:
                all_parsed[cnic] = {
                    'NameUrdu': back_lines[1],
                    'FatherNameUrdu': back_lines[0],
                    'section': s_idx,
                    'method': 'interleaved'
                }
            elif len(back_lines) == 1:
                all_parsed[cnic] = {
                    'NameUrdu': back_lines[0],
                    'FatherNameUrdu': '',
                    'section': s_idx,
                    'method': 'interleaved'
                }

print(f"Total parsed voters: {len(all_parsed)}")

# Compare with JSON
matches = 0
conflicts = []

for cnic, t_v in all_parsed.items():
    if cnic not in json_cnic_map:
        continue
    j_v = json_cnic_map[cnic]
    j_n = j_v.get('NameUrdu', '').strip()
    j_f = j_v.get('FatherNameUrdu', '').strip()
    
    t_n = t_v['NameUrdu'].strip()
    t_f = t_v['FatherNameUrdu'].strip()
    
    if j_n == t_n and j_f == t_f:
        matches += 1
    else:
        conflicts.append({
            'CNIC': cnic,
            'JSON_Name': j_n,
            'JSON_Father': j_f,
            'TXT_Name': t_n,
            'TXT_Father': t_f,
            'Method': t_v['method']
        })

print(f"Exact Matches: {matches}")
print(f"Conflicts / Differences: {len(conflicts)}")

print("\nFirst 25 Conflicts:")
for c in conflicts[:25]:
    print(f"CNIC: {c['CNIC']} ({c['Method']})")
    print(f"  JSON: {c['JSON_Name']} | {c['JSON_Father']}")
    print(f"  TXT:  {c['TXT_Name']} | {c['TXT_Father']}")
    print("-" * 50)
