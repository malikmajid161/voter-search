import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    voters = json.load(f)

page13 = [v for v in voters if v.get('PageNo') == 13 or v.get('Page') == 13]
print(f"Total voters on Page 13: {len(page13)}")

for v in page13:
    print(f"Silsila {v.get('SilsilaNo'):<4} | CNIC: {v.get('CNIC'):<17} | Name: {v.get('NameUrdu'):<16} | Father: {v.get('FatherNameUrdu')}")
