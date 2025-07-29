import pytesseract
from PIL import Image

img = Image.open("images/1.jpg")
text = pytesseract.image_to_string(img)
print(text)
