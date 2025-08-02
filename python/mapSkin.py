from PIL import Image, ImageEnhance, ImageFilter
import os
import pytesseract
import json
from rapidfuzz import process
import shutil
import re

max_files = 5  # จำนวนไฟล์สูงสุดที่ต้องการประมวลผล (ตั้งเป็น None สำหรับไฟล์ทั้งหมด)
# กำหนด path
crop_areas = [
    # (x, y, width, height)
    (140, 1500, 900, 150),
]
base_dir = os.path.dirname(os.path.abspath(__file__))
skin_folder = os.path.join(base_dir, "images", "web")
stringIsHas = ["มีแล้ว", "ยีแล้ว", "บีแล้ว", "ปีแล้ว"]

def extract_text_from_image(image: Image.Image) -> str:
    """ดึงข้อความจากภาพโดยใช้ OCR พร้อมปรับภาพ"""
    # แปลงภาพเป็นขาวดำก่อนทำ OCR
    grayscale_image = image.convert('L')
    # ปรับภาพขาวให้เป็นดำ แล้วก็ดำเป็นขาว
    return pytesseract.image_to_string(grayscale_image, lang="eng", config="--psm 6")


def crop_images(img: Image.Image, crop_areas):
    """ตัดภาพตามตำแหน่งที่กำหนด"""
    cropped_images = []
    for x, y, w, h in crop_areas:
        crop_box = (x, y, x + w, y + h)
        cropped_img = img.crop(crop_box)
        cropped_images.append(cropped_img)
    return cropped_images


def process_ocr_from_images(images):
    """รับภาพที่ crop แล้ว แล้วแยกเป็น base และ name"""
    heroes = []
    skins = []
    for img in images:
        text = extract_text_from_image(img)
        processed_text = " ".join(text.split())  # ลบช่องว่างเกิน, ขึ้นบรรทัดใหม่
        parts = processed_text.split(" ", 1)
        base = parts[0]
        name = parts[1] if len(parts) > 1 else ""
        heroes.append(base)
        skins.append(name)
    return heroes, skins


def match_ocr_to_database(ocr_results, database, filename=None):
    base_from_filename = ""
    if filename:
        base_name = filename.replace(".png", "").replace(".jpg", "")
        if "_" in base_name:
            base_from_filename = base_name.split("_")[0]
    
    db_names = [f"{item['base']} {item['name']}".lower() for item in database]
    matched_results = []
    for i, ocr_item in enumerate(ocr_results):
        # รวม base จากชื่อไฟล์กับ name ที่ OCR ได้
        query = f"{base_from_filename} {ocr_item['name']}".lower().strip()
        match = process.extractOne(query, db_names)
        if match:
            _, _, index = match
            matched_data = database[index]
            matched_results.append(
                {
                    "id": matched_data["id"],
                    "base": matched_data["base"],
                    "name": matched_data["name"],
                    "image": matched_data["image"],
                }
            )
            if "position" in matched_data:
                matched_results[-1]["position"] = matched_data["position"]
    return matched_results


def process_single_file(file_path, filename):
    """ประมวลผลไฟล์เดียว"""
    heroes = []
    skins = []
    response = []
    
    print(f"\n📁 Processing file: {filename}")
    
    # เปิดภาพโดยไม่ต้อง resize
    with Image.open(file_path) as img:
        print(f"🖼️  Image size: {img.size}")

        for i, (x, y, w, h) in enumerate(crop_areas):
            crop_box = (x, y, x + w, y + h)
            cropped_img = img.crop(crop_box)
            output_filename = f"match-{filename}".replace("_", "-")
            output_path = os.path.join(base_dir, "images/processing", output_filename)
            cropped_img.save(output_path)
            
            text = extract_text_from_image(cropped_img)
            processed_text = " ".join(text.split())
            removeText = ['"', '\\', '/']
            replaceText = [" | "]
            for r in removeText:
                processed_text = processed_text.replace(r, "")
            for r in replaceText:
                processed_text = processed_text.replace(r, " ")
            # ลบอักขระพิเศษที่ไม่ใช่ตัวอักษรและตัวเลข
            processed_text = re.sub(r'[^\w\s]', '', processed_text)
                
            print(f"   📝 OCR Text: '{processed_text}'")
            skins.append(processed_text)

    for skin in skins:
        response.append({"name": skin})
    
    return response, file_path


def main():
    print("=" * 60)
    print("🔍 ROV SKIN OCR ANALYZER - BATCH PROCESSING")
    print("=" * 60)
    
    # ดึงรายการไฟล์ภาพทั้งหมดจากโฟลเดอร์ skin
    if not os.path.exists(skin_folder):
        print(f"❌ Folder not found: {skin_folder}")
        return
    
    # กรองไฟล์ภาพ
    image_extensions = ['.png', '.jpg', '.jpeg']
    all_files = [f for f in os.listdir(skin_folder) 
                if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    # จำกัดจำนวนไฟล์ตาม max_files
    if max_files and len(all_files) > max_files:
        all_files = all_files[:max_files]
    
    print(f"📂 Found {len(all_files)} image files in skin folder")
    if max_files:
        print(f"📊 Processing limit: {max_files} files")
    print("=" * 40)
    
    if not all_files:
        print("❌ No image files found")
        return
    
    # โหลดฐานข้อมูลจาก lib/skin.ts
    from convert_skin import extract_field_value
    import re
    
    ts_path = os.path.join(os.path.dirname(base_dir), "lib", "skin.ts")
    
    print(f"🔍 Reading TypeScript file: {ts_path}")
    
    if not os.path.exists(ts_path):
        print(f"❌ File not found: {ts_path}")
        return
    
    # อ่านไฟล์ TypeScript
    with open(ts_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # แยกเนื้อหาของ array
    pattern = r'export const rov: IRovSkin\[\] = \[(.*)\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find skin data in TypeScript file")
        return
    
    array_content = match.group(1)
    
    # แยกข้อมูลแต่ละ object
    rov = []
    objects = re.split(r'\},\s*\n\s*\{', array_content)
    
    print(f"🔄 Processing {len(objects)} objects from TypeScript...")
    
    for i, obj_str in enumerate(objects):
        # ทำความสะอาด object string
        if i == 0:
            obj_str = obj_str.strip().lstrip('{')
        if i == len(objects) - 1:
            obj_str = obj_str.strip().rstrip('}')
        
        # แยกข้อมูลแต่ละ field
        skin = {}
        
        skin_id = extract_field_value(obj_str, 'id', 'number')
        if skin_id:
            skin['id'] = skin_id
        
        name = extract_field_value(obj_str, 'name', 'string')
        if name:
            skin['name'] = name
        
        base = extract_field_value(obj_str, 'base', 'string')
        if base:
            skin['base'] = base
        
        image = extract_field_value(obj_str, 'image', 'image')
        if image:
            skin['image'] = image
        
        position = extract_field_value(obj_str, 'position', 'position')
        if position is not None:
            skin['position'] = position
        
        if skin and 'id' in skin:
            rov.append(skin)
    
    print(f"📊 Database loaded: {len(rov)} skins from TypeScript")
    
    # สร้างโฟลเดอร์ mapSkin หากยังไม่มี
    map_skin_dir = os.path.join(base_dir, "images", "mapSkin")
    os.makedirs(map_skin_dir, exist_ok=True)
    
    all_matched_results = []
    total_matches = 0
    
    # ประมวลผลไฟล์ทีละไฟล์
    for file_index, filename in enumerate(all_files, 1):
        file_path = os.path.join(skin_folder, filename)
        
        print(f"\n{'='*40}")
        print(f"🔄 Processing {file_index}/{len(all_files)}")
        print(f"{'='*40}")
        
        try:
            # ประมวลผลไฟล์
            response, current_file_path = process_single_file(file_path, filename)
            
            if response:
                # จับคู่กับฐานข้อมูล
                matched_results = match_ocr_to_database(response, database=rov, filename=filename)
                
                if matched_results:
                    total_matches += len(matched_results)
                    print(f"\n✅ Found {len(matched_results)} matches:")
                    print("-" * 30)
                    
                    for i, match in enumerate(matched_results, 1):
                        print(f"{i}. {match['base']} - {match['name']}")
                        print(f"   🆔 ID: {match['id']}")
                        print(f"   🖼️  Image: {match['image']}")
                        
                        # คัดลอกไฟล์รูปไปยัง mapSkin (ข้าม evo)
                        try:
                            target_filename = os.path.basename(match['image'])
                            if 'evo' in target_filename.lower():
                                print(f"   ⏭️  Skipped (contains 'evo'): {target_filename}")
                            else:
                                target_path = os.path.join(map_skin_dir, target_filename)
                                shutil.copy2(current_file_path, target_path)
                                print(f"   📁 Copied to: images/mapSkin/{target_filename}")
                        except Exception as e:
                            print(f"   ❌ Copy failed: {e}")
                        print()
                    
                    all_matched_results.extend(matched_results)
                else:
                    print("❌ No matches found for this file")
            else:
                print("❌ No text extracted from this file")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    # สรุปผลลัพธ์
    print("\n" + "=" * 60)
    print("📋 BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"📂 Total files processed: {len(all_files)}")
    print(f"✅ Total matches found: {total_matches}")
    print(f"📁 Files copied to mapSkin: {total_matches}")
    
    # if all_matched_results:
    #     print("\n" + "=" * 40)
    #     print("📋 ALL MATCHED RESULTS (JSON)")
    #     print("=" * 40)
    #     print(json.dumps(all_matched_results, indent=2, ensure_ascii=False))

main()
