import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('ALL_VOTERS_COMBINED_FINAL.json', encoding='utf-8') as f:
    data = json.load(f)

# Specific corrections requested by user
for v in data:
    cnic = v.get('CNIC', '')
    if cnic == '38201-9495135-4':
        v['NameUrdu'] = 'نصیرہ جمال'
    elif '15683-8' in cnic:
        v['NameUrdu'] = 'سمیہ علی'

female_suffix_map = {
    'سعید': 'سعیدہ',
    'نصیر': 'نصیرہ',
    'ساجد': 'ساجدہ',
    'طاہر': 'طاہرہ',
    'حمید': 'حمیدہ',
    'شاہد': 'شاہدہ',
    'رشید': 'رشیدہ',
    'وحید': 'وحیدہ',
    'زاہد': 'زاہدہ',
    'مجید': 'مجیدہ',
    'بشیر': 'بشیرہ',
    'منیر': 'منیرہ',
    'قدیر': 'قدیرہ',
    'عابد': 'عابدہ',
    'خالد': 'خالدہ',
    'رفیق': 'رفیقہ',
    'شفیق': 'شفیقہ',
    'فاروق': 'فاروقہ',
    'صدیق': 'صدیقہ',
    'عتیق': 'عتیقہ',
    'خالق': 'خالقہ',
    'عارف': 'عارفہ',
    'شریف': 'شریفہ',
    'لطیف': 'لطیفہ',
    'حنیف': 'حنیفہ',
    'تنویر': 'تنویرہ',
    'شبیر': 'شبیراں',
    'نذیر': 'نذیراں',
    'وزیر': 'وزیراں',
    'کبیر': 'کبیراں',
    'امیر': 'امیراں',
}

corrected_count = 0
for v in data:
    gender = v.get('Gender', '')
    fn = v.get('FatherNameUrdu', '')
    is_female = (gender == 'FEMALE') or ('زوجہ' in fn) or ('دختر' in fn) or ('بنت' in fn)
    
    if is_female:
        name = v.get('NameUrdu', '')
        words = name.split()
        if words:
            last_word = words[-1]
            first_word = words[0]
            
            # Check if first or last word matches a male ending in female context
            if first_word in female_suffix_map:
                words[0] = female_suffix_map[first_word]
                v['NameUrdu'] = " ".join(words)
                corrected_count += 1
                print(f"Fixed Female Name: {v['CNIC']} | '{name}' -> '{v['NameUrdu']}'")
            elif last_word in female_suffix_map:
                words[-1] = female_suffix_map[last_word]
                v['NameUrdu'] = " ".join(words)
                corrected_count += 1
                print(f"Fixed Female Name: {v['CNIC']} | '{name}' -> '{v['NameUrdu']}'")

print(f"Total female names automatically corrected: {corrected_count}")
