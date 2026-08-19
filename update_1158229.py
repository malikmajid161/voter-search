import fitz
import json
import os

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic = '38201-1158229-1'

# 1. Update JSON files
for fpath in ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']:
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            data = json.load(f)
        for v in data:
            if v.get('CNIC') == cnic:
                v['FatherNameUrdu'] = 'محمد علی'
                print(f"Updated {fpath} for {cnic}")
                break
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 2. Crop fresh image snippet
for p_idx in range(len(doc)):
    page = doc[p_idx]
    rects = page.search_for(cnic)
    if rects:
        r = rects[0]
        tight_box = fitz.Rect(325, max(0, r.y0 - 1), 490, min(page.rect.height, r.y1 + 1))
        pix = page.get_pixmap(clip=tight_box, dpi=250)
        img_file = f'voter-app/public/names/{cnic}.jpg'
        pix.save(img_file)
        print(f"Cropped fresh image snippet for {cnic} on page {p_idx + 1}")
        break

print("Finished updating 38201-1158229-1!")
