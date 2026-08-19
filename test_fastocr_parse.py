import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines()]

print(f"Total lines in OCR text: {len(lines)}")

# Let's inspect block headers and page splits
page_splits = []
curr_page = None
curr_block = None

for idx, line in enumerate(lines):
    b_match = re.search(r'2660109\d{2}', line)
    if b_match:
        curr_block = b_match.group(0)
    p_match = re.search(r'صفحہ نمبر\s*:\s*(\d+)', line)
    if p_match:
        curr_page = p_match.group(1)
        page_splits.append((idx, curr_block, curr_page))

print(f"Total page markers: {len(page_splits)}")
for idx, b, p in page_splits[:10]:
    print(f"Line {idx}: Block {b}, Page {p}")
