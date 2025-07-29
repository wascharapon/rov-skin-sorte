# core.py
import pytesseract
from PIL import Image
import re
import json
from rapidfuzz import process

remove_words = {
    "fe", "SU", "cruise", "Ponies", "fnsumu", "Q", "11", "7207", "B20",
    "EVO", "nan", "Twaines", "oaereu", "Swwesa",
    "ust", "ni", "nuzun", "als",
    "meiunu", "M200", "md", "SUM", "Ayn", "i", "wuzuA", "y", "ania", "Lito"
}

def extract_text_from_image(img: Image.Image) -> str:
    return pytesseract.image_to_string(img)

def filter_words(text: str) -> list[str]:
    words = re.findall(r'[A-Za-z0-9]+', text)

    def should_remove(word):
        return (word in remove_words) or word.endswith("ins")

    filtered = [w for w in words if not should_remove(w)]
    for i, w in enumerate(filtered):
        if w.startswith("afu"):
            filtered = filtered[:i]
            break
    return filtered

def group_skins(skins: list[str], group_size: int = 2) -> list[str]:
    if len(skins) < group_size:
        return [' '.join(skins)]
    return [' '.join(skins[i:i + group_size]) for i in range(0, len(skins), group_size)]

def create_hero_skin_pairs(heroes: list[str], skins: list[str]) -> list[dict]:
    pair_count = min(len(heroes), len(skins))
    return [{"base": heroes[i], "name": skins[i]} for i in range(pair_count)]

def match_ocr_to_database(ocr_results, database):
    db_names = [item["name"] for item in database]
    matched_results = []

    for ocr_item in ocr_results:
        query = f"{ocr_item['base']} {ocr_item['name']}"
        match = process.extractOne(query, db_names)
        if match:
            _, _, index = match
            matched_data = database[index]
            result = {
                "id": matched_data["id"],
                "base": matched_data["base"],
                "name": matched_data["name"],
                "image": matched_data["image"],
            }
            if "position" in matched_data:
                result["position"] = matched_data["position"]
            matched_results.append(result)

    return matched_results
