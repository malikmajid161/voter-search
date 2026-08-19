import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load main database
json_path = r'c:\Users\Majid\OneDrive\Desktop\voter seach\voter-app\src\voter_data_final.json'
with open(json_path, 'r', encoding='utf-8') as f:
    voters = json.load(f)

print(f"Loaded {len(voters)} voters from database.")

# Exact OCR fixes map for specific CNICs if needed
exact_fixes = {
    '38201-9495135-4': {'NameUrdu': 'نصیرہ جمال'},
    '38201-15683-8': {'NameUrdu': 'سمیہ علی'},
    '38201-1166179-0': {'NameUrdu': 'جنت خاتون'},
    '38201-1101134-0': {'NameUrdu': 'نور خاتون'},
    '38201-4609450-4': {'NameUrdu': 'زینب خاتون'},
    '38201-9971980-8': {'NameUrdu': 'اسلم خاتون'},
    '38201-1101696-8': {'NameUrdu': 'زینب خاتون'},
    '38201-1173829-8': {'NameUrdu': 'زینب خاتون'},
    '38201-4169100-0': {'NameUrdu': 'رحمت خاتون'},
}

# General word normalization function
def clean_urdu_string(text, is_female=False):
    if not text:
        return ""
    
    # Character normalization
    text = text.replace('ي', 'ی').replace('ى', 'ی').replace('ك', 'ک')
    text = text.replace('ه', 'ہ').replace('ۃ', 'ہ').replace('ٱ', 'ا')
    text = text.replace('ـ', '') # Remove kashida
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text) # Remove diacritics
    
    # Spacing and typos
    text = re.sub(r'\bخاتوں\b', 'خاتون', text)
    text = re.sub(r'\bخاتوو\b', 'خاتون', text)
    text = re.sub(r'\bخاتو\b', 'خاتون', text)
    
    text = re.sub(r'\bبیبی\b', 'بی بی', text)
    text = re.sub(r'\bبی\s+ی\b', 'بی بی', text)
    text = re.sub(r'\bبی\s+پی\b', 'بی بی', text)
    text = re.sub(r'\bپی\s+پی\b', 'بی بی', text)
    
    text = re.sub(r'\bبیگمر\b', 'بیگم', text)
    text = re.sub(r'\bبی\s+گم\b', 'بیگم', text)
    
    text = re.sub(r'\bزو\s+جہ\b', 'زوجہ', text)
    text = re.sub(r'\bزوجه\b', 'زوجہ', text)
    text = re.sub(r'\bدختر\s+ہ\b', 'دختر', text)
    text = re.sub(r'\bمرحومه\b', 'مرحومہ', text)

    # Female specific name endings before 'خاتون' or 'بی بی' or 'بیگم'
    # E.g. 'شریف خاتون' -> 'شریفہ خاتون'
    if is_female:
        text = re.sub(r'\bشریف\s+خاتون\b', 'شریفہ خاتون', text)
        text = re.sub(r'\bسعید\s+خاتون\b', 'سعیدہ خاتون', text)
        text = re.sub(r'\bحمید\s+خاتون\b', 'حمیدہ خاتون', text)
        text = re.sub(r'\bنصیر\s+خاتون\b', 'نصیرہ خاتون', text)
        text = re.sub(r'\bساجد\s+خاتون\b', 'ساجدہ خاتون', text)
        text = re.sub(r'\bطاہر\s+خاتون\b', 'طاہرہ خاتون', text)
        text = re.sub(r'\bعابد\s+خاتون\b', 'عابدہ خاتون', text)
        text = re.sub(r'\bخالد\s+خاتون\b', 'خالدہ خاتون', text)
        text = re.sub(r'\bمجید\s+خاتون\b', 'مجیدہ خاتون', text)
        text = re.sub(r'\bرشید\s+خاتون\b', 'رشیدہ خاتون', text)
        text = re.sub(r'\bوحید\s+خاتون\b', 'وحیدہ خاتون', text)
        text = re.sub(r'\bزاہد\s+خاتون\b', 'زاہدہ خاتون', text)
        text = re.sub(r'\bبشیر\s+خاتون\b', 'بشیرہ خاتون', text)
        text = re.sub(r'\bمنیر\s+خاتون\b', 'منیرہ خاتون', text)
        text = re.sub(r'\bقدیر\s+خاتون\b', 'قدیرہ خاتون', text)
        text = re.sub(r'\bعارف\s+خاتون\b', 'عارفہ خاتون', text)
        text = re.sub(r'\bلطیف\s+خاتون\b', 'لطیفہ خاتون', text)
        text = re.sub(r'\bحنیف\s+خاتون\b', 'حنیفہ خاتون', text)
        text = re.sub(r'\bتنویر\s+خاتون\b', 'تنویرہ خاتون', text)

    # Multi-space cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    return text

modified_count = 0

for v in voters:
    cnic = v.get('CNIC', '')
    gender = (v.get('Gender') or '').strip()
    father = v.get('FatherNameUrdu', '')
    is_female = (gender.lower() == 'female') or ('زوجہ' in father) or ('دختر' in father) or ('بنت' in father)
    
    if is_female:
        v['Gender'] = 'Female'
        
    old_name = v.get('NameUrdu', '')
    old_father = father
    
    new_name = clean_urdu_string(old_name, is_female=is_female)
    new_father = clean_urdu_string(old_father, is_female=False)
    
    # Apply exact fixes if match
    for k, fix_dict in exact_fixes.items():
        if k in cnic:
            if 'NameUrdu' in fix_dict:
                new_name = fix_dict['NameUrdu']
            if 'FatherNameUrdu' in fix_dict:
                new_father = fix_dict['FatherNameUrdu']

    if new_name != old_name or new_father != old_father:
        modified_count += 1
        if modified_count <= 25:
            print(f"Fixed: CNIC {cnic} | Name: '{old_name}' -> '{new_name}' | Father: '{old_father}' -> '{new_father}'")
        v['NameUrdu'] = new_name
        v['FatherNameUrdu'] = new_father

print(f"\nTotal voter records modified: {modified_count}")

# Save updated JSON files
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(voters, f, ensure_ascii=False, indent=2)

# Also update ALL_VOTERS_COMBINED_FINAL.json in voter-app if present
voter_app_combined = r'c:\Users\Majid\OneDrive\Desktop\voter seach\voter-app\ALL_VOTERS_COMBINED_FINAL.json'
with open(voter_app_combined, 'w', encoding='utf-8') as f:
    json.dump(voters, f, ensure_ascii=False, indent=2)

print("Saved updated voter database files!")
