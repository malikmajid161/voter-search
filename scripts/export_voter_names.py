import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Reading voter database...")
with open('voter-app/public/voter_data_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

output_file = 'ALL_VOTER_NAMES_AND_FATHER_NAMES.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    out.write('========================================================================================\n')
    out.write('                 MARDWAL ELECTORAL ROLL 2023 - EXTRACTED VOTER LIST                     \n')
    out.write('========================================================================================\n')
    out.write(f'Total Voters: {len(data)}\n\n')
    out.write(f'{"No.":<6} | {"CNIC":<17} | {"Voter Name (نام)":<32} | {"Father/Husband Name (ولدیت)":<38} | {"Gharana":<8} | {"Block Code"}\n')
    out.write('-'*125 + '\n')
    
    for i, v in enumerate(data):
        sno = str(i+1)
        cnic = str(v.get('CNIC', ''))
        name = str(v.get('NameUrdu', ''))
        father = str(v.get('FatherNameUrdu', ''))
        gharana = str(v.get('GharanaNo', ''))
        block = str(v.get('BlockCode', ''))
        out.write(f'{sno:<6} | {cnic:<17} | {name:<32} | {father:<38} | {gharana:<8} | {block}\n')

print(f"Successfully generated '{output_file}' with {len(data)} voter records!")
