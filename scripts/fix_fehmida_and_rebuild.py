import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Fixing CNIC 38201-6215011-4 to match physical scanned PDF text (فہمیدہ علی)...")

corrections = {
    '38201-6215011-4': {
        'NameUrdu': 'فہمیدہ علی',
        'FatherNameUrdu': 'دختر محمد سعید',
        'SilsilaNo': '19',
        'GharanaNo': '6',
        'Age': '23',
        'Gender': 'Female'
    }
}

json_files = ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']

for fpath in json_files:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            voter_db = json.load(f)
            
        for v in voter_db:
            cnic = v.get('CNIC', '')
            if '38201-6215011-4' in cnic:
                v.update(corrections['38201-6215011-4'])
                print(f"Updated {cnic} in {fpath}: {v['NameUrdu']} | {v['FatherNameUrdu']}")
                
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(voter_db, f, ensure_ascii=False, indent=2)

print("Running complete family database sync script...")
import subprocess
subprocess.run(['python', 'rebuild_perfect_voter_and_family_db.py'], check=True)

print("Rebuilding frontend production bundle with npm run build...")
os.chdir('voter-app')
subprocess.run(['npm.cmd', 'run', 'build'], check=True)
print("Complete fix deployed!")
