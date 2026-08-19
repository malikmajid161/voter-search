import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Applying 100% precise Page 12 female voter data updates...")

page12_voters = [
    {'cnic': '38201-1180078-2', 'NameUrdu': 'نعیمہ خاتون', 'FatherNameUrdu': 'زوجہ محمد عبداللہ', 'silsila': '1', 'gharana': '1'},
    {'cnic': '38201-1075990-2', 'NameUrdu': 'بادشاہ بی بی', 'FatherNameUrdu': 'زوجہ خیر محمد', 'silsila': '2', 'gharana': '2'},
    {'cnic': '38201-9023879-6', 'NameUrdu': 'مریم النساء', 'FatherNameUrdu': 'دختر خیر محمد', 'silsila': '3', 'gharana': '2'},
    {'cnic': '38201-1166179-0', 'NameUrdu': 'جنت خاتون', 'FatherNameUrdu': 'زوجہ محمد ابراہیم', 'silsila': '4', 'gharana': '3'},
    {'cnic': '38201-1166177-4', 'NameUrdu': 'پروین اختر', 'FatherNameUrdu': 'زوجہ محمد ابراہیم', 'silsila': '5', 'gharana': '3'},
    {'cnic': '38201-0609088-8', 'NameUrdu': 'نہرین بی بی', 'FatherNameUrdu': 'دختر محمد ابراہیم', 'silsila': '6', 'gharana': '3'},
    {'cnic': '38201-2585405-4', 'NameUrdu': 'حافظہ آسیہ نسیم', 'FatherNameUrdu': 'دختر محمد نسیم', 'silsila': '7', 'gharana': '3'},
    {'cnic': '38201-4203147-6', 'NameUrdu': 'الشبہ نسیم', 'FatherNameUrdu': 'دختر محمد نسیم', 'silsila': '8', 'gharana': '3'},
    {'cnic': '38201-1048639-8', 'NameUrdu': 'رحمت بی بی', 'FatherNameUrdu': 'زوجہ غلام حیدر', 'silsila': '9', 'gharana': '4'},
    {'cnic': '37203-1484582-2', 'NameUrdu': 'ثریا خاتون', 'FatherNameUrdu': 'دختر عبد الرزاق', 'silsila': '10', 'gharana': '4'},
    {'cnic': '38201-9535575-2', 'NameUrdu': 'عصمت یاسمین', 'FatherNameUrdu': 'دختر غلام حیدر', 'silsila': '11', 'gharana': '4'},
    {'cnic': '37203-4551076-4', 'NameUrdu': 'نازیہ کنول', 'FatherNameUrdu': 'دختر عبد الرزاق', 'silsila': '12', 'gharana': '4'},
    {'cnic': '37203-8102023-0', 'NameUrdu': 'عالیہ کنول', 'FatherNameUrdu': 'دختر عبد الرزاق', 'silsila': '13', 'gharana': '4'},
    {'cnic': '38201-1063584-8', 'NameUrdu': 'نہرین بی بی', 'FatherNameUrdu': 'زوجہ فاروق احمد', 'silsila': '14', 'gharana': '5'},
    {'cnic': '38201-9799606-0', 'NameUrdu': 'شائستہ پروین', 'FatherNameUrdu': 'دختر فاروق احمد', 'silsila': '15', 'gharana': '5'},
    {'cnic': '38201-1116216-6', 'NameUrdu': 'شہناز اختر', 'FatherNameUrdu': 'زوجہ محمد سعید', 'silsila': '16', 'gharana': '6'},
    {'cnic': '38201-9004840-4', 'NameUrdu': 'عظمیٰ علی', 'FatherNameUrdu': 'دختر محمد سعید', 'silsila': '17', 'gharana': '6'},
    {'cnic': '38201-6205416-4', 'NameUrdu': 'عروج علی', 'FatherNameUrdu': 'دختر محمد سعید', 'silsila': '18', 'gharana': '6'},
    {'cnic': '38201-6215011-4', 'NameUrdu': 'فہمیدہ بیگم', 'FatherNameUrdu': 'دختر محمد سعید', 'silsila': '19', 'gharana': '6'},
    {'cnic': '38201-1038860-4', 'NameUrdu': 'مریم خاتون', 'FatherNameUrdu': 'زوجہ احمد خان جمالی دا', 'silsila': '20', 'gharana': '7'},
    {'cnic': '37203-6358512-0', 'NameUrdu': 'شمیم اختر', 'FatherNameUrdu': 'زوجہ احمد خان', 'silsila': '21', 'gharana': '8'},
    {'cnic': '38201-6042734-4', 'NameUrdu': 'رفعت پروین', 'FatherNameUrdu': 'دختر احمد خان', 'silsila': '22', 'gharana': '8'},
    {'cnic': '38201-1078092-6', 'NameUrdu': 'شہناز اختر', 'FatherNameUrdu': 'زوجہ غلام مصطفیٰ', 'silsila': '23', 'gharana': '9'},
    {'cnic': '38201-1101134-0', 'NameUrdu': 'قمر النساء', 'FatherNameUrdu': 'زوجہ غلام مصطفیٰ', 'silsila': '24', 'gharana': '9'}
]

page12_map = {v['cnic']: v for v in page12_voters}

json_path = 'voter-app/ALL_VOTERS_COMBINED_FINAL.json'
with open(json_path, 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

updated_count = 0
for v in json_voters:
    c = v.get('CNIC', '').strip()
    if c in page12_map:
        info = page12_map[c]
        v['NameUrdu'] = info['NameUrdu']
        v['FatherNameUrdu'] = info['FatherNameUrdu']
        v['SilsilaNo'] = info['silsila']
        v['GharanaNo'] = info['gharana']
        v['PageNo'] = 12
        v['Page'] = 12
        updated_count += 1
        print(f"Updated Page 12 Silsila #{info['silsila']}: {c} -> {info['NameUrdu']} ({info['FatherNameUrdu']})")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_voters, f, ensure_ascii=False, indent=2)

# Sync voter_data_final.json across public, src, dist
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

print(f"\nSuccessfully updated {updated_count} Page 12 female voter records!")
