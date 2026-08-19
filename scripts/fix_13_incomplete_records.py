import fitz
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Fixing the 13 edge-case voter records with exact PDF text extraction...")

doc = fitz.open('Voting List Full 2023.pdf')
json_path = 'voter-app/ALL_VOTERS_COMBINED_FINAL.json'

with open(json_path, 'r', encoding='utf-8') as f:
    voters = json.load(f)

# Targets to clean up
targets = [
    {'cnic_raw': '37406-1257695-3', 'clean_cnic': '37406-1257695-3', 'page': 147, 'block': '266010906'},
    {'cnic_raw': "38201-1259465-9'", 'clean_cnic': '38201-1259465-9', 'page': 8, 'block': '266010901'},
    {'cnic_raw': '38201-1038860-4', 'clean_cnic': '38201-1038860-4', 'page': 12, 'block': '266010901'},
    {'cnic_raw': '38201-7499112-4', 'clean_cnic': '38201-7499112-4', 'page': 72, 'block': '266010903'},
    {'cnic_raw': '38201-1166651-4', 'clean_cnic': '38201-1166651-4', 'page': 75, 'block': '266010903'},
    {'cnic_raw': '37203-1520021-7', 'clean_cnic': '37203-1520021-7', 'page': 100, 'block': '266010904'},
    {'cnic_raw': '38201-8076629-0', 'clean_cnic': '38201-8076629-0', 'page': 138, 'block': '266010905'},
    {'cnic_raw': '38201-7450173-1', 'clean_cnic': '38201-7450173-1', 'page': 209, 'block': '266010908'},
    {'cnic_raw': '38201-0989012-5', 'clean_cnic': '38201-0989012-5', 'page': 225, 'block': '266010908'},
    {'cnic_raw': '38201-5275925-2-', 'clean_cnic': '38201-5275925-2', 'page': 253, 'block': '266010909'},
    {'cnic_raw': '38201-6316323-7', 'clean_cnic': '38201-6316323-7', 'page': 275, 'block': '266010909'},
    {'cnic_raw': '38201-1177971-1', 'clean_cnic': '38201-1177971-1', 'page': 285, 'block': '266010909'},
    {'cnic_raw': '38201-8202013-4', 'clean_cnic': '38201-8202013-4', 'page': 289, 'block': '266010909'}
]

target_map = {t['cnic_raw']: t for t in targets}

for v in voters:
    c_raw = v.get('CNIC', '')
    if c_raw in target_map:
        t = target_map[c_raw]
        v['CNIC'] = t['clean_cnic']
        v['BlockCode'] = t['block']
        v['FamilyId'] = f"{t['block']}_{v.get('GharanaNo', '1')}"
        
        # Search page text for words
        p_idx = t['page'] - 1
        if 0 <= p_idx < len(doc):
            page = doc[p_idx]
            words = page.get_text('words')
            # Get words on page
            cnic_words = [w for w in words if t['clean_cnic'] in w[4]]
            if cnic_words:
                cw = cnic_words[0]
                y0, y1 = cw[1], cw[3]
                y_center = (y0 + y1) / 2.0
                row_words = [w for w in words if abs(((w[1] + w[3]) / 2.0) - y_center) < 14]
                name_words = [w[4] for w in row_words if 320 <= (w[0]+w[2])/2.0 <= 485]
                if name_words:
                    full_name_text = ' '.join(name_words)
                    if not v.get('NameUrdu'):
                        v['NameUrdu'] = full_name_text
        print(f"Fixed entry: CNIC={v['CNIC']}, Name={v.get('NameUrdu')}, Block={v['BlockCode']}")

# Save master file
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(voters, f, ensure_ascii=False, indent=2)

# Sync voter_data_final.json
voter_data_paths = [
    'voter-app/public/voter_data_final.json',
    'voter-app/src/voter_data_final.json',
    'voter-app/dist/voter_data_final.json'
]

for p in voter_data_paths:
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(voters, f, ensure_ascii=False, indent=2)

# Rebuild family_data.json
family_dict = {}
for v in voters:
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
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(family_dict, f, ensure_ascii=False, indent=2)

print("\nEdge-case record fixes complete!")
