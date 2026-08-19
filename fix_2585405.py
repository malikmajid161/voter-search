import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Fixing CNIC 38201-2585405-4 in all JSON database files...")

json_path = 'voter-app/ALL_VOTERS_COMBINED_FINAL.json'
with open(json_path, 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

for v in json_voters:
    if v.get('CNIC') == '38201-2585405-4':
        v['NameUrdu'] = 'حافظہ آسیہ نسیم'
        v['FatherNameUrdu'] = 'دختر محمد نسیم'
        print("Updated 38201-2585405-4:", v)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)

voter_data_paths = [
    'voter-app/public/voter_data_final.json',
    'voter-app/src/voter_data_final.json',
    'voter-app/dist/voter_data_final.json'
]

for p in voter_data_paths:
    if os.path.exists(os.path.dirname(p)):
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_voters, f, ensure_ascii=False, indent=2)

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

print("CNIC 38201-2585405-4 update complete!")
