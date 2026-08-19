import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

paths = [
    'ALL_VOTERS_COMBINED_FINAL.json',
    'voter_data_final.json',
    'voter-app/public/voter_data_final.json',
    'voter-app/dist/voter_data_final.json',
    'voter-app/public/family_data.json',
    'voter-app/dist/family_data.json'
]

print("Checking JSON file locations and contents for 38201-5057660-7...")

for p in paths:
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                print(f"\nFile: {p} ({len(data)} voters)")
                for item in data:
                    cnic = item.get('CNIC', '')
                    name = item.get('NameUrdu', '')
                    if '5057660' in cnic or 'مجتبی' in name or 'چنگی' in name:
                        print(f"  CNIC: {cnic} | NameUrdu: {name} | FatherNameUrdu: {item.get('FatherNameUrdu')}")
            elif isinstance(data, dict):
                print(f"\nFile: {p} ({len(data)} families)")
                for fam_id, fam in data.items():
                    members = fam.get('members', [])
                    for m in members:
                        cnic = m.get('CNIC', '')
                        name = m.get('NameUrdu', '')
                        if '5057660' in cnic or 'مجتبی' in name or 'چنگی' in name:
                            print(f"  In Family {fam_id}: CNIC: {cnic} | NameUrdu: {name}")
