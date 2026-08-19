import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load existing JSON voters
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

# Map by normalized CNIC
cnic_map = {}
for v in json_voters:
    cnic = v.get('CNIC', '').strip()
    if cnic:
        cnic_map[cnic] = v

print(f"Total voters in JSON: {len(json_voters)}")
print(f"Unique CNICs in JSON: {len(cnic_map)}")

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines()]

# Pattern for CNIC
cnic_regex = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

cnic_occurrences = []
for idx, line in enumerate(lines):
    m = cnic_regex.findall(line)
    for cnic in m:
        cnic_occurrences.append((idx, cnic, line))

print(f"Found {len(cnic_occurrences)} CNIC occurrences in TXT file.")

# Check how many match JSON
matched_cnics = set(c[1] for c in cnic_occurrences if c[1] in cnic_map)
print(f"Matched CNICs in JSON: {len(matched_cnics)}")
