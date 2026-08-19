import fitz
import re
import os

print("Generating Spacious, High-Clarity Calligraphy Crops for All 299 Pages...")

pdf_path = 'Voting List Full 2023.pdf'
doc = fitz.open(pdf_path)

cnic_pattern = re.compile(r'\b\d{5}-\d{7}-\d\b')
output_names_dir = 'voter-app/public/names'
os.makedirs(output_names_dir, exist_ok=True)

crops_count = 0

for p_idx in range(len(doc)):
    page = doc[p_idx]
    words = page.get_text('words')
    cnic_words = [w for w in words if cnic_pattern.match(w[4])]
    
    for cw in cnic_words:
        cnic = cw[4]
        y0, y1 = cw[1], cw[3]
        
        # Spacious, full-width crop box:
        # x from 280 (covers Father Name column completely) to 520 (covers Voter Name column completely)
        # y from y0 - 5 to y1 + 5 (gives full vertical breathing room for Urdu dots & accents)
        spacious_box = fitz.Rect(280, max(0, y0 - 5), 520, min(page.rect.height, y1 + 5))
        
        pix = page.get_pixmap(clip=spacious_box, dpi=250)
        img_path = os.path.join(output_names_dir, f"{cnic}.jpg")
        pix.save(img_path)
        crops_count += 1

print(f"Successfully generated {crops_count} high-clarity spacious crops in {output_names_dir}!")
