import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = [l.strip() for l in text.splitlines()]

# Let's write a robust page splitter
# Header markers in fastocr text: 'کتاب نمبر', 'صفحہ نمبر', 'شماریاتی بلاک کوڈ', 'حتمی انتخابی فہرست'
pages = []
curr_lines = []
curr_block = '266010901'
curr_page_num = 1

for line in lines:
    b_match = re.search(r'2660109\d{2}', line)
    if b_match:
        curr_block = b_match.group(0)
    p_match = re.search(r'صفحہ نمبر\s*:\s*(\d+)', line)
    if p_match:
        if curr_lines:
            pages.append({'block': curr_block, 'page': curr_page_num, 'lines': curr_lines})
            curr_lines = []
        curr_page_num = int(p_match.group(1))
    curr_lines.append(line)

if curr_lines:
    pages.append({'block': curr_block, 'page': curr_page_num, 'lines': curr_lines})

print(f"Total pages extracted: {len(pages)}")

# Sample page analysis
for p in pages[:5]:
    print(f"--- Block {p['block']}, Page {p['page']} ({len(p['lines'])} lines) ---")
    cnics = [l for l in p['lines'] if re.search(r'\d{5}-\d{7}-\d', l)]
    print(f"CNICs in page ({len(cnics)}): {cnics[:3]}...")
