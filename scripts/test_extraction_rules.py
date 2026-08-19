import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = [l.strip() for l in text.splitlines() if l.strip()]

cnic_re = re.compile(r'(\d{5}-\d{7}-\d)')

# Load JSON
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

# Filter lines that are noise/headers
def is_noise(line):
    if re.search(r'صفحہ|کتاب|پر نٹنگ|دستخط|انتخابی|شماریاتی|سلسلہ|گھرانہ|قومی شناختی|پتہ|عمر|موقع|تحصیل|ضلع|مردوال|محلہ|پٹوار', line):
        return True
    return False

# Extract candidates
extracted = []
for idx, line in enumerate(lines):
    m = cnic_re.search(line)
    if m:
        cnic = m.group(1)
        # Look backwards for name and father name
        name_candidates = []
        back_idx = idx - 1
        while back_idx >= 0 and len(name_candidates) < 4:
            prev_line = lines[back_idx]
            # Ignore headers, digits, ages, addresses
            if not is_noise(prev_line) and not re.match(r'^\d+$', prev_line) and not cnic_re.search(prev_line) and not 'سال' in prev_line:
                name_candidates.append(prev_line)
            back_idx -= 1
            if is_noise(prev_line) or 'صفحہ' in prev_line:
                break
        
        extracted.append({
            'line_idx': idx,
            'cnic': cnic,
            'cnic_line': line,
            'candidates_backwards': name_candidates
        })

print(f"Extracted {len(extracted)} CNIC records.")

# Compare with JSON
differences = []
exact_matches = 0

for item in extracted:
    cnic = item['cnic']
    if cnic not in json_map:
        continue
    j_voter = json_map[cnic]
    j_name = j_voter.get('NameUrdu', '')
    j_father = j_voter.get('FatherNameUrdu', '')
    
    candidates = item['candidates_backwards']
    
    # Check if j_name and j_father appear in candidates or if candidates differ
    matched_n = any(j_name in c or c in j_name for c in candidates)
    matched_f = any(j_father in c or c in j_father for c in candidates)
    
    if matched_n and matched_f:
        exact_matches += 1
    else:
        differences.append({
            'cnic': cnic,
            'json_name': j_name,
            'json_father': j_father,
            'candidates': candidates
        })

print(f"Exact or close matches: {exact_matches}")
print(f"Total differences/conflicts to check: {len(differences)}")
print("\nFirst 20 differences:")
for d in differences[:20]:
    print(f"CNIC: {d['cnic']}")
    print(f"  JSON Name: {d['json_name']} | Father: {d['json_father']}")
    print(f"  TXT Candidates (backwards): {d['candidates']}")
    print("-" * 50)
