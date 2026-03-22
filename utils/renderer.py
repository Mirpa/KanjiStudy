from PIL import ImageFont, ImageDraw, Image
import customtkinter as ctk
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSansJP-Regular.ttf")

def render_kanji_image(char, size=90, color=(30, 30, 30)):
    font = ImageFont.truetype(FONT_PATH, size)
    img = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 4), char, font=font, fill=color)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size + 20, size + 20))