# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import io
import json

from core import (
    extract_text_from_image,
    filter_words,
    group_skins,
    create_hero_skin_pairs,
    match_ocr_to_database,
)

app = FastAPI()

with open("lib/skin.json", "r", encoding="utf-8") as f:
    database = json.load(f)

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only .png, .jpg, .jpeg files are supported")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    text = extract_text_from_image(image)
    filtered_words = filter_words(text)

    num_heroes = 5
    heroes = filtered_words[:num_heroes]
    skins = filtered_words[num_heroes:]

    if len(skins) >= 10:
        skin_names = group_skins(skins, group_size=2)
    else:
        skin_names = [' '.join(skins)]

    response = create_hero_skin_pairs(heroes, skin_names)
    matched = match_ocr_to_database(response, database)

    return {
        "data": matched
    }
