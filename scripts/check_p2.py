import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('voter-app/public/voter_data_final.json', encoding='utf-8') as f:
    voters = json.load(f)

cnics = ['38201-7991516-9', '38201-7224970-3', '38201-9999177-3', '38201-1239625-1', '38201-7981816-9']
p2_voters = [v for v in voters if v.get('CNIC') in cnics or v.get('PageNo') == 2]

print(f"Found {len(p2_voters)} voters for Page 2 in DB:")
for v in p2_voters[:10]:
    print(f"CNIC: {v.get('CNIC')} | Name: '{v.get('NameUrdu')}' | Father: '{v.get('FatherNameUrdu')}' | Silsila: {v.get('SilsilaNo')}")
