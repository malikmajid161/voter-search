import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize text lines
raw_lines = [l.strip() for l in text.splitlines() if l.strip()]

# Regex to find CNIC inside a line
cnic_re = re.compile(r'(\d{5}-\d{7}-\d)')

# Let's collect all CNICs and their line indices
cnic_entries = []
for idx, line in enumerate(raw_lines):
    m = cnic_re.search(line)
    if m:
        cnic = m.group(1)
        cnic_entries.append((idx, cnic, line))

print(f"Total CNIC lines found: {len(cnic_entries)}")

# Load JSON voters
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

# Let's test matching each CNIC line back to preceding lines for Name and FatherName
matched = 0
conflicts = []

for idx, cnic, line in cnic_entries:
    if cnic not in json_map:
        continue
    matched += 1
    v_json = json_map[cnic]
    
    # Look at preceding lines (up to 5 lines above) to see Name and FatherName candidate
    prev_lines = raw_lines[max(0, idx-6):idx]

print(f"Total JSON matched CNICs: {matched}")
