import requests
import os
import json
import re
from urllib.parse import urlparse, unquote

# Load ROV skin data from TypeScript file
with open('../lib/skin.ts', 'r', encoding='utf-8') as f:
    ts_content = f.read()

# Extract base names from TypeScript file
base_pattern = r"base:\s*'([^']+)'"
bases = list(set(re.findall(base_pattern, ts_content)))
print(f"Found {len(bases)} unique character bases")


def download_image_from_url(url, filename=None):
    """
    ดาวน์โหลดรูปภาพจาก URL และบันทึกไว้ใน ai_python/images/web/

    Args:
        url (str): URL ของรูปภาพ
        filename (str, optional): ชื่อไฟล์ที่ต้องการ หากไม่ระบุจะใช้ชื่อจาก URL

    Returns:
        str: path ของไฟล์ที่บันทึก หรือ None หากเกิดข้อผิดพลาด
    """
    try:
        # สร้างโฟลเดอร์หากยังไม่มี
        os.makedirs("images/web", exist_ok=True)

        # ถ้าไม่ระบุชื่อไฟล์ ให้ดึงจาก URL
        if not filename:
            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))
            if not filename or "." not in filename:
                filename = "image.png"  # ชื่อเริ่มต้น

        # ดาวน์โหลดรูปภาพ
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # บันทึกไฟล์
        file_path = os.path.join("images/web", filename)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"ดาวน์โหลดสำเร็จ: {file_path}")
        return file_path

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None


def download_character_skins():
    """
    ดาวน์โหลดรูปสกินของตัวละครทั้งหมดจาก bases
    """
    # เก็บรายชื่อ base ที่ดาวน์โหลดแล้ว
    downloaded_bases = set()
    
    for base_name in bases:
        
        # เช็คว่า base นี้ดาวน์โหลดแล้วหรือยัง
        if base_name in downloaded_bases:
            print(f"ข้าม {base_name} - ดาวน์โหลดแล้ว")
            continue
            
        print(f"กำลังดาวน์โหลดสกินของ {base_name}...")

        # เริ่มจากหมายเลข 001
        skin_number = 1

        while True:
            # สร้าง URL และชื่อไฟล์
            skin_number_str = f"{skin_number:03d}"  # 001, 002, 003...
            url = f"https://sortskin.com/_next/image?url=%2Fheros01%2F{base_name}%2F{skin_number_str}.png&w=3840&q=20"
            filename = f"{base_name.lower()}_{skin_number_str}.png"

            # พยายามดาวน์โหลด
            result = download_image_from_url(url, filename)

            if result is None:
                print(f"หยุดการดาวน์โหลดสำหรับ {base_name} ที่หมายเลข {skin_number_str}")
                break

            skin_number += 1

            # ป้องกันลูปไม่สิ้นสุด (จำกัดที่ 100 สกิน)
            if skin_number > 100:
                print(f"หยุดการดาวน์โหลดสำหรับ {base_name} - เกิน 100 สกิน")
                break
        
        # เพิ่ม base นี้เข้าไปในรายการที่ดาวน์โหลดแล้ว
        downloaded_bases.add(base_name)


# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    print(f"📊 Found {len(bases)} character bases from TypeScript file")
    download_character_skins()