import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Fixing all reported voters in JSON database...")

master_fixes = {
    '38403-4407767-4': {
        'NameUrdu': 'شکلائل منصب',
        'FatherNameUrdu': 'زوجہ حافظ ملک کامران اکبر',
        'SilsilaNo': '256',
        'GharanaNo': '164'
    },
    '38201-4203147-6': {
        'NameUrdu': 'الشبہ نسیم',
        'FatherNameUrdu': 'دختر محمد نسیم'
    },
    '38201-9495135-4': {
        'NameUrdu': 'نصیرہ جمال',
        'FatherNameUrdu': 'زوجہ محمد فیصل'
    },
    '38201-1158229-1': {
        'NameUrdu': 'احمد علی خان',
        'FatherNameUrdu': 'محمد علی'
    },
    '38201-15683-8': {
        'NameUrdu': 'سمیہ علی',
        'FatherNameUrdu': 'زوجہ ایاز احمد خان'
    }
}

json_files = ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']

for fpath in json_files:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
            
        for v in data:
            cnic = v.get('CNIC', '')
            for target_cnic, updates in master_fixes.items():
                if target_cnic in cnic:
                    v.update(updates)
                    print(f"Applied fix for {cnic} in {fpath}: {updates}")
                    
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON files successfully updated!")
