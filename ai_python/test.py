import pytesseract
from PIL import Image
import re
import json
import pprint
from rapidfuzz import process

remove_words = {
    "fe", "SU", "cruise", "Ponies", "fnsumu", "Q", "11", "7207", "B20",
    "EVO", "nan", "Twaines", "oaereu", "Swwesa",
    "ust", "ni", "nuzun", "als",
    "meiunu", "M200", "md", "SUM", "Ayn", "i", "wuzuA", "y", "ania", "Lito"
}

def extract_text_from_image(image_path: str) -> str:
    """อ่านข้อความจากภาพโดยใช้ pytesseract"""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def filter_words(text: str) -> list[str]:
    """กรองคำที่เป็นตัวอักษรและตัวเลข และตัดคำที่ไม่ต้องการออก"""
    words = re.findall(r'[A-Za-z0-9]+', text)

    def should_remove(word):
        return (word in remove_words) or word.endswith("ins")
    
    filtered = [w for w in words if not should_remove(w)]
    
    # ตัดคำหลังคำที่ขึ้นต้นด้วย 'afu'
    for i, w in enumerate(filtered):
        if w.startswith("afu"):
            filtered = filtered[:i]
            break
    
    return filtered

def group_skins(skins: list[str], group_size: int = 2) -> list[str]:
    """
    แบ่ง skins list เป็นกลุ่มละ group_size แล้วรวมแต่ละกลุ่มเป็น string เดียว
    ถ้าจำนวนน้อยกว่า group_size จะรวมทั้งหมดเป็นกลุ่มเดียว
    """
    if len(skins) < group_size:
        return [' '.join(skins)]
    skin_names = []
    for i in range(0, len(skins), group_size):
        group = skins[i:i+group_size]
        skin_names.append(' '.join(group))
    return skin_names

def create_hero_skin_pairs(heroes: list[str], skins: list[str]) -> list[dict]:
    """จับคู่ hero กับ skin ตามลำดับ (จำนวนคู่ตาม min ของทั้งสองฝั่ง)"""
    pair_count = min(len(heroes), len(skins))
    return [{"base": heroes[i], "name": skins[i]} for i in range(pair_count)]

def match_ocr_to_database(ocr_results, database):
    """เปรียบเทียบชื่อ hero+skin จาก OCR กับ database แล้วคืนค่าที่ match พร้อมตำแหน่ง"""
    db_names = [item["name"] for item in database]
    matched_results = []

    for i, ocr_item in enumerate(ocr_results):
        query = f"{ocr_item['base']} {ocr_item['name']}"
        match = process.extractOne(query, db_names)
        if match:
            _, _, index = match
            matched_data = database[index]
            matched_results.append({
                "id": matched_data["id"],
                "base": matched_data["base"],
                "name": matched_data["name"],
                "image": matched_data["image"],
            })
            if "position" in matched_data:
                matched_results[-1]["position"] = matched_data["position"]

    return matched_results

def main():
    text = extract_text_from_image("images/2.jpg")
    filtered_words = filter_words(text)
    
    num_heroes = 5
    heroes = filtered_words[:num_heroes]
    skins = filtered_words[num_heroes:]
    
    if len(skins) >= 10:
        skin_names = group_skins(skins, group_size=2)
    else:
        skin_names = [' '.join(skins)]
    
    print("Filtered text:")
    print(' '.join(filtered_words))
    print("\nResult:")
    print("hero =", ",".join(heroes))
    print("skin =", ",".join(skin_names))
    
    response = create_hero_skin_pairs(heroes, skin_names)
    print("\nJSON output:")
    print(json.dumps(response, indent=4, ensure_ascii=False))

    with open('lib/skin.json', 'r', encoding='utf-8') as f:
        rov = json.load(f)

    matched = match_ocr_to_database(response, rov)

    print("\nMatched Output:")
    print(json.dumps(matched, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
