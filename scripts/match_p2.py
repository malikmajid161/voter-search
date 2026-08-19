import fitz
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open('Voting List Full 2023.pdf')
page2 = doc[1] # Page 2

words = page2.get_text('words')
cnic_pat = re.compile(r'\b\d{5}-\d{7}-\d\b')
cnic_words = [cw for cw in words if cnic_pat.match(cw[4])]
cnic_words.sort(key=lambda cw: cw[1])

print(f"PyMuPDF extracted {len(cnic_words)} CNICs from Page 2:")
for i, cw in enumerate(cnic_words, 1):
    print(f"Row {i:02d}: CNIC={cw[4]} at Y={cw[1]:.1f}")

with open('voter-app/public/voter_data_final.json', encoding='utf-8') as f:
    voters = json.load(f)

p2_db = [v for v in voters if v.get('PageNo') == 2]
p2_db.sort(key=lambda v: int(v.get('SilsilaNo', 0)))

print(f"\nDB has {len(p2_db)} voters for Page 2:")
for i, v in enumerate(p2_db, 1):
    print(f"DB Row {i:02d} (Silsila {v.get('SilsilaNo')}): DB CNIC={v.get('CNIC')} | Name={v.get('NameUrdu')}")
