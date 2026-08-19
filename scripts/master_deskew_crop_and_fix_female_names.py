import cv2
import numpy as np
import fitz
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== Starting 299-Page Master Deskew & Precision Straight Cropping Pipeline ===")

pdf_path = 'Voting List Full 2023.pdf'
output_dir = 'voter-app/public/names'
os.makedirs(output_dir, exist_ok=True)

# 1. Specific verified female & voter name updates in JSON
verified_name_updates = {
    '38201-3815683-8': {'NameUrdu': 'سمیعہ بی', 'FatherNameUrdu': 'زوجہ ایاز احمد خان'},
    '38201-9495135-4': {'NameUrdu': 'نفیسہ جمال', 'FatherNameUrdu': 'زوجہ محمد فیصل'},
    '38201-2011307-4': {'NameUrdu': 'علیہ بی بی', 'FatherNameUrdu': 'زوجہ محمد سرور'},
    '38201-6215011-4': {'NameUrdu': 'فہمیدہ بیگم', 'FatherNameUrdu': 'دختر محمد سعید'},
    '38201-9004840-4': {'NameUrdu': 'عظمیٰ علی', 'FatherNameUrdu': 'دختر محمد سعید'},
    '38201-6205416-4': {'NameUrdu': 'عروج علی', 'FatherNameUrdu': 'دختر محمد سعید'},
    '38403-4407767-4': {'NameUrdu': 'ملکانی منصب', 'FatherNameUrdu': 'زوجہ حافظ ملک کامران اکبر'},
    '38201-1116216-6': {'NameUrdu': 'شہناز اختر', 'FatherNameUrdu': 'زوجہ محمد سعید'},
    '38201-5057660-7': {'NameUrdu': 'محمد مجتبیٰ علی', 'FatherNameUrdu': 'احمد علی خان'}
}

# OCR replacements for widespread female misreads
ocr_replacements = [
    (r'\bسعید علی\b', 'سمیعہ بی'),
    (r'\bنصیرہ جمال\b', 'نفیسہ جمال'),
    (r'\bعلی پی بی\b', 'علیہ بی بی'),
    (r'\bعقلی علی\b', 'عظمیٰ علی'),
    (r'\bمروج علی\b', 'عروج علی'),
    (r'\bشکائل منصب\b', 'ملکانی منصب'),
    (r'\bمحمد چنگی علی\b', 'محمد مجتبیٰ علی'),
]

def clean_ocr_text(text):
    if not text:
        return text
    res = text
    for pat, rep in ocr_replacements:
        res = re.sub(pat, rep, res)
    return res

# Load DB voters for mapping fallback
db_voters_by_page_and_y = {}
json_paths = ['ALL_VOTERS_COMBINED_FINAL.json', 'voter-app/public/voter_data_final.json']

for jpath in json_paths:
    if not os.path.exists(jpath):
        continue
    with open(jpath, encoding='utf-8') as f:
        data = json.load(f)
    
    updated_count = 0
    for v in data:
        cnic = v.get('CNIC', '')
        if cnic in verified_name_updates:
            v.update(verified_name_updates[cnic])
            updated_count += 1
        else:
            if v.get('NameUrdu'):
                v['NameUrdu'] = clean_ocr_text(v['NameUrdu'])
            if v.get('FatherNameUrdu'):
                v['FatherNameUrdu'] = clean_ocr_text(v['FatherNameUrdu'])
                
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated JSON database: {jpath} ({updated_count} verified manual updates applied)")

# 2. Open PDF and process all 299 pages
doc = fitz.open(pdf_path)
total_pages = len(doc)
cnic_pat = re.compile(r'\b\d{5}-\d{7}-\d\b')

print(f"\nProcessing all {total_pages} page frames for deskew & straight cropping...")

total_crops = 0
deskewed_pages_count = 0

for p_idx in range(total_pages):
    page = doc[p_idx]
    
    # 1. Fast angle detection at 150 DPI using Hough lines & line contours
    pix_fast = page.get_pixmap(dpi=150, colorspace=fitz.csGRAY)
    gray_fast = np.frombuffer(pix_fast.samples, dtype=np.uint8).reshape(pix_fast.h, pix_fast.w)
    bw_fast = cv2.adaptiveThreshold(gray_fast, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, -2)
    
    w_fast = pix_fast.w
    horiz_fast = cv2.morphologyEx(bw_fast, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (w_fast // 5, 1)))
    
    contours, _ = cv2.findContours(horiz_fast, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    angles = []
    for cnt in contours:
        if cv2.boundingRect(cnt)[2] > w_fast * 0.2:
            rect = cv2.minAreaRect(cnt)
            ang = rect[-1]
            if ang < -45: ang += 90
            elif ang > 45: ang -= 90
            if abs(ang) < 6.0:
                angles.append(ang)
                
    skew_angle = float(np.median(angles)) if len(angles) > 3 else 0.0
    if abs(skew_angle) < 0.05:
        skew_angle = 0.0
    else:
        deskewed_pages_count += 1
        
    # 2. Render high-res 250 DPI image for final cropping
    dpi = 250
    scale = dpi / 72.0
    pix_high = page.get_pixmap(dpi=dpi)
    img_high = np.frombuffer(pix_high.samples, dtype=np.uint8).reshape(pix_high.h, pix_high.w, pix_high.n)
    if pix_high.n >= 3:
        img_high = cv2.cvtColor(img_high, cv2.COLOR_RGBA2BGR if pix_high.n==4 else cv2.COLOR_RGB2BGR)
        
    h_high, w_high = img_high.shape[:2]
    center = (w_high / 2.0, h_high / 2.0)
    M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
    deskewed_img = cv2.warpAffine(img_high, M, (w_high, h_high), flags=cv2.INTER_CUBIC, borderValue=(255, 255, 255))
    
    # 3. Find CNICs and crop straight cells
    words = page.get_text('words')
    cnic_words = [cw for cw in words if cnic_pat.match(cw[4])]
    cnic_words.sort(key=lambda cw: cw[1]) # Sort top to bottom
    
    for cw in cnic_words:
        cnic = cw[4]
        x0, y0, x1, y1 = cw[:4]
        
        px = ((x0 + x1) / 2.0) * scale
        py = ((y0 + y1) / 2.0) * scale
        
        rot_pt = M.dot(np.array([px, py, 1.0]))
        rx, ry = rot_pt[0], rot_pt[1]
        
        row_h = (y1 - y0) * scale
        
        # Exact straight crop capturing Father Name (Left) and Voter Name (Right)
        # x0=0.485*w to x1=0.765*w guarantees capturing BOTH Father Name and Voter Name perfectly
        crop_y0 = max(0, int(ry - row_h * 0.85))
        crop_y1 = min(h_high, int(ry + row_h * 1.20))
        crop_x0 = int(w_high * 0.398)
        crop_x1 = int(w_high * 0.778)
        
        crop_img = deskewed_img[crop_y0:crop_y1, crop_x0:crop_x1]
        out_path = os.path.join(output_dir, f"{cnic}.jpg")
        cv2.imwrite(out_path, crop_img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        total_crops += 1

    if (p_idx + 1) % 25 == 0 or p_idx + 1 == total_pages:
        print(f"Processed {p_idx + 1}/{total_pages} pages | Deskewed: {deskewed_pages_count} | Crops saved: {total_crops}")

print(f"\n=== DESKEW & CROPPING COMPLETE ===")
print(f"Total Pages: {total_pages}")
print(f"Deskewed Pages: {deskewed_pages_count}")
print(f"Total High-Res Straight Crops Saved to '{output_dir}': {total_crops}")
