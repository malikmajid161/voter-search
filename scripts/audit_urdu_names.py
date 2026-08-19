import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

def normalize_urdu_text(text):
    if not text:
        return ""
    
    # 1. Normalize characters
    text = text.replace('ي', 'ی').replace('ى', 'ی').replace('ك', 'ک')
    text = text.replace('ه', 'ہ').replace('ۃ', 'ہ').replace('ٱ', 'ا')
    text = text.replace('ـ', '') # Remove tatweel/kashida
    
    # Remove Arabic diacritics
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    
    # Fix common misspellings/OCR errors in female words:
    # Fix 'خاتوں' -> 'خاتون'
    text = re.sub(r'\bخاتوں\b', 'خاتون', text)
    text = re.sub(r'\bخاتوو\b', 'خاتون', text)
    text = re.sub(r'\bخاتو\b', 'خاتون', text)
    
    # Fix 'بی بی' variations
    text = re.sub(r'\bبیبی\b', 'بی بی', text)
    text = re.sub(r'\bبی\s+ی\b', 'بی بی', text)
    text = re.sub(r'\bبی\s+پی\b', 'بی بی', text)
    
    # Fix 'بیگم' variations
    text = re.sub(r'\bبیگمر\b', 'بیگم', text)
    text = re.sub(r'\bبی\s+گم\b', 'بیگم', text)
    
    # Remove duplicate spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

with open(r'c:\Users\Majid\OneDrive\Desktop\voter seach\voter-app\src\voter_data_final.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f"Total voters in database: {len(db)}")

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
    'فہمید': 'فہمیدہ',
    'مبارک': 'مبارکہ',
    'شبیر': 'شبیراں',
    'نذیر': 'نذیراں',
    'وزیر': 'وزیراں',
    'کبیر': 'کبیراں',
    'امیر': 'امیراں',
}

changes_count = 0

for v in db:
    old_name = v.get('NameUrdu', '')
    old_father = v.get('FatherNameUrdu', '')
    
    # Normalize characters
    new_name = normalize_urdu_text(old_name)
    new_father = normalize_urdu_text(old_father)
    
    gender = v.get('Gender', '')
    is_female = (gender == 'Female') or ('زوجہ' in new_father) or ('دختر' in new_father) or ('بنت' in new_father)
    
    if is_female:
        v['Gender'] = 'Female'
        words = new_name.split()
        if words:
            # Check first word or last word for male root in female context
            if words[0] in female_suffix_map:
                words[0] = female_suffix_map[words[0]]
            elif words[-1] in female_suffix_map:
                words[-1] = female_suffix_map[words[-1]]
            new_name = " ".join(words)
            
    if new_name != old_name or new_father != old_father:
        changes_count += 1
        if changes_count <= 25:
            print(f"CNIC: {v.get('CNIC')} | Name: '{old_name}' -> '{new_name}' | Father: '{old_father}' -> '{new_father}'")
            
print(f"\nTotal voter records updated/normalized: {changes_count}")
