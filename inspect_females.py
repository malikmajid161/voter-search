import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Majid\OneDrive\Desktop\voter seach\voter-app\src\voter_data_final.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

females = [v for v in db if v.get('Gender') == 'Female']
print(f"Total Female Voters: {len(females)}")

suspect_female_names = []

for f in females:
    name = f.get('NameUrdu', '')
    cnic = f.get('CNIC', '')
    father = f.get('FatherNameUrdu', '')
    
    # Check for male names assigned to female gender or truncations:
    # E.g. ending in male names like 'محمد', 'احمد', 'خان', 'علی', 'سعید', 'حسین', 'اقبال', 'رحمان', 'اکبر', etc., without 'بی بی' or 'بیگم' or female suffix
    words = name.split()
    if words:
        last_word = words[-1]
        # Male endings that often should be female in female list:
        # e.g. Saeed -> Saeeda, Nazir -> Naziran, etc.
        suspect_female_names.append((cnic, name, father))

print("\nSample Female Voters (First 30):")
for cnic, name, father in suspect_female_names[:30]:
    print(f"CNIC: {cnic} | Name: {name} | Father/Husband: {father}")
