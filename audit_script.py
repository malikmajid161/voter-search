import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('voter-app/public/voter_data_final.json', encoding='utf-8') as f:
    voters = json.load(f)

females = [v for v in voters if v.get('Gender') == 'Female' or 'زوجہ' in v.get('FatherNameUrdu','') or 'دختر' in v.get('FatherNameUrdu','')]
print(f"Total female voters in DB: {len(females)}")

by_page = defaultdict(list)
for f in females:
    by_page[f.get('PageNo', 0)].append(f)

print(f"Female pages count: {len(by_page)}")
female_pages = sorted(list(by_page.keys()))
print("Female pages:", female_pages)

print("\nAuditing Female Names for obvious OCR glitches or male name patterns:")
suspicious_female_names = []

female_keywords = ['بی بی', 'خاتون', 'بیگم', 'پروین', 'اختر', 'شاهین', 'شاہین', 'نسیم', 'یاسمین', 'کنول', 'فاطمہ', 'کوثر', 'جمال', 'سعیدہ', 'نصیرہ', 'سمیہ', 'سمیعہ', 'عروج', 'عظمیٰ', 'شریفہ', 'طاہرہ', 'ساجدہ', 'عابدہ', 'خالدہ', 'رشیدہ', 'حمیدہ', 'شاہدہ', 'مجیدہ', 'بشیرہ', 'منیرہ', 'قدیرہ', 'رفیقہ', 'شفیقہ', 'فاروقہ', 'صدیقہ', 'عتیقہ', 'خالقہ', 'عارفہ', 'لطیفہ', 'حنیفہ', 'تنویرہ', 'شبیراں', 'نذیراں', 'وزیراں', 'کبیراں', 'امیراں', 'دختر', 'زوجہ']

for v in females:
    name = v.get('NameUrdu', '')
    fname = v.get('FatherNameUrdu', '')
    cnic = v.get('CNIC', '')
    pno = v.get('PageNo', 0)
    
    # Check if female has male ending like 'علی' or 'احمد' or 'خان' without female keyword
    has_female_kw = any(kw in name for kw in female_keywords)
    if not has_female_kw and ('علی' in name or 'خان' in name or 'احمد' in name or 'محمد' in name or 'شاہ' in name):
        suspicious_female_names.append((pno, cnic, name, fname))

print(f"\nFound {len(suspicious_female_names)} female voters with potentially misread male-like names:")
for pno, cnic, name, fname in suspicious_female_names[:30]:
    print(f"Page {pno:03d} | CNIC: {cnic} | Name: '{name}' | Father/Husband: '{fname}'")
