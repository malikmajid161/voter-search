import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('Voting List Full 2023-ocr-fastocr.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Load JSON voters map by CNIC
with open('voter-app/ALL_VOTERS_COMBINED_FINAL.json', 'r', encoding='utf-8') as f:
    json_voters = json.load(f)

json_cnic_map = {v['CNIC']: v for v in json_voters if v.get('CNIC')}

# Split text by page headers or page numbers
pages_raw = text.split('صفحہ نمبر')
print(f"Total page sections split: {len(pages_raw)}")

# Pattern for CNIC
cnic_re = re.compile(r'\b(?:\d{1,2})?(\d{5}-\d{7}-\d)\b')

parsed_voters = []

for section_idx, page_str in enumerate(pages_raw):
    lines = [l.strip() for l in page_str.splitlines() if l.strip()]
    if not lines:
        continue
    
    # Extract block code if present
    block_code = '266010901'
    for line in lines:
        b_m = re.search(r'2660109\d{2}', line)
        if b_m:
            block_code = b_m.group(0)
            break
            
    # Extract page number
    page_num = section_idx
    p_m = re.search(r'^\s*:\s*(\d+)', lines[0])
    if p_m:
        page_num = int(p_m.group(1))

    # Collect CNIC lines and non-CNIC lines
    cnics = []
    for l_idx, line in enumerate(lines):
        m = cnic_re.search(line)
        if m:
            cnics.append((l_idx, m.group(1), line))
            
    # If no CNICs found in this section, skip
    if not cnics:
        continue
        
    # Check layout: If all CNICs are grouped together in a sequence of lines
    cnic_line_indices = [c[0] for c in cnics]
    is_grouped = False
    if len(cnic_line_indices) > 3:
        diffs = [cnic_line_indices[i+1] - cnic_line_indices[i] for i in range(len(cnic_line_indices)-1)]
        if sum(1 for d in diffs if d <= 3) / len(diffs) > 0.6:
            is_grouped = True
            
    # Print sample analysis for first 10 pages
    if section_idx <= 10:
        print(f"Page Section {section_idx} (Block {block_code}, Page {page_num}): {len(lines)} lines, {len(cnics)} CNICs, Grouped={is_grouped}")
