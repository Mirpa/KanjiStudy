import random
import tkinter as tk
import customtkinter as ctk
from PIL import ImageFont, ImageDraw, Image, ImageTk
from data.n5 import KANJI_N5

FONT_PATH  = "fonts/NotoSansJP-Regular.ttf"
FONT_BOLD  = "fonts/NotoSansJP-Bold.ttf"
CARD_W, CARD_H = 340, 260


def _rounded_bg(color, w=CARD_W, h=CARD_H, radius=20):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w-1, h-1], radius=radius, fill=color)
    return img


def render_frente(kanji):
    bg   = _rounded_bg("#EAF3DE")
    draw = ImageDraw.Draw(bg)

    # Kanji centrado
    font_k = ImageFont.truetype(FONT_PATH, 110)
    bb = draw.textbbox((0, 0), kanji, font=font_k)
    kw, kh = bb[2]-bb[0], bb[3]-bb[1]
    x = (CARD_W - kw) // 2 - bb[0]
    y = (CARD_H - kh) // 2 - bb[1] - 18
    draw.text((x, y), kanji, font=font_k, fill="#27500A")

    # Hint
    font_h = ImageFont.truetype(FONT_PATH, 13)
    hint   = "Toca para ver el significado"
    bb2    = draw.textbbox((0, 0), hint, font=font_h)
    draw.text(((CARD_W - (bb2[2]-bb2[0])) // 2, CARD_H - 32),
              hint, font=font_h, fill="#639922")
    return bg


def render_reverso(significado, kunyomi, onyomi):
    bg   = _rounded_bg("#E6F1FB")
    draw = ImageDraw.Draw(bg)

    # Significado
    font_sig = ImageFont.truetype(FONT_PATH, 24)
    bb  = draw.textbbox((0, 0), significado, font=font_sig)
    sw  = bb[2] - bb[0]
    draw.text(((CARD_W - sw) // 2 - bb[0], 40), significado,
              font=font_sig, fill="#0C447C")

    # Píldora helper
    def pill(text_left, text_right, y, bg_color, color_l, color_r):
        font_l = ImageFont.truetype(FONT_PATH, 13)
        font_r = ImageFont.truetype(FONT_BOLD if FONT_BOLD else FONT_PATH, 13)
        bb_l = draw.textbbox((0, 0), text_left,  font=font_l)
        bb_r = draw.textbbox((0, 0), text_right, font=font_r)
        pad_x, pad_y, gap = 14, 6, 4
        pill_w = (bb_l[2]-bb_l[0]) + gap + (bb_r[2]-bb_r[0]) + pad_x * 2
        pill_h = max(bb_l[3]-bb_l[1], bb_r[3]-bb_r[1]) + pad_y * 2
        px = (CARD_W - pill_w) // 2
        draw.rounded_rectangle([px, y, px+pill_w, y+pill_h], radius=pill_h//2, fill=bg_color)
        draw.text((px + pad_x - bb_l[0], y + pad_y - bb_l[1]),
                  text_left, font=font_l, fill=color_l)
        draw.text((px + pad_x + (bb_l[2]-bb_l[0]) + gap - bb_r[0], y + pad_y - bb_r[1]),
                  text_right, font=font_r, fill=color_r)

    pill("Kun ", kunyomi, 110, "#C0DD97", "#3B6D11", "#27500A")
    pill("On ",  onyomi,  165, "#B5D4F4", "#185FA5", "#0C447C")

    return bg


class KanjiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KanjiStudy")
        self.geometry("420x520")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.mazo = KANJI_N5.copy()
        random.shuffle(self.mazo)
        self.indice  = 0
        self.volteada = False
        self.score   = {"sabidos": 0, "repasar": 0}
        self._tk_img = None

        self._construir_ui()
        self._mostrar_tarjeta()

    def _construir_ui(self):
        # Cabecera
        cab = ctk.CTkFrame(self, fg_color="transparent")
        cab.pack(fill="x", padx=40, pady=(20, 4))
        ctk.CTkLabel(cab, text="N5", font=("", 11, "bold"),
                     fg_color="#7F77DD", text_color="#EEEDFE",
                     corner_radius=10, width=36, height=20).pack(side="left")
        self.label_contador = ctk.CTkLabel(cab, text="", font=("", 13), text_color="gray")
        self.label_contador.pack(side="right")

        self.progressbar = ctk.CTkProgressBar(self, width=340)
        self.progressbar.pack(pady=(0, 16))

        # Canvas = tarjeta completa
        self.canvas = tk.Canvas(self, width=CARD_W, height=CARD_H,
                                highlightthickness=0, bd=0, cursor="hand2")
        self.canvas.pack(pady=(0, 16))
        self.canvas.bind("<Button-1>", lambda e: self._voltear())
        self.bind("<space>", lambda e: self._voltear())

        # Botones
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=(0, 10))
        self.btn_repasar = ctk.CTkButton(
            frame_btns, text="✗  No lo sabía", width=150,
            fg_color="#E24B4A", hover_color="#A32D2D",
            command=lambda: self._marcar(False))
        self.btn_repasar.grid(row=0, column=0, padx=8)
        self.btn_sabido = ctk.CTkButton(
            frame_btns, text="✓  Lo sabía", width=150,
            fg_color="#639922", hover_color="#3B6D11",
            command=lambda: self._marcar(True))
        self.btn_sabido.grid(row=0, column=1, padx=8)

        self.btn_siguiente = ctk.CTkButton(
            self, text="Siguiente →", width=310,
            fg_color="#B5D4F4", hover_color="#85B7EB",
            text_color="#0C447C", command=self._siguiente)
        self.btn_siguiente.pack(pady=4)

        self._set_botones(False)

    def _draw(self, img):
        self._tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)

    def _mostrar_tarjeta(self):
        c = self.mazo[self.indice]
        self._draw(render_frente(c["kanji"]))
        total = len(self.mazo)
        self.label_contador.configure(text=f"{self.indice + 1} / {total}")
        self.progressbar.set((self.indice + 1) / total)
        self._set_botones(False)
        self.volteada = False

    def _voltear(self):
        if self.volteada:
            return
        self.volteada = True
        c = self.mazo[self.indice]
        self._draw(render_reverso(c["significado"], c["kunyomi"], c["onyomi"]))
        self.btn_repasar.configure(state="normal")
        self.btn_sabido.configure(state="normal")

    def _set_botones(self, activos):
        estado = "normal" if activos else "disabled"
        self.btn_repasar.configure(state=estado)
        self.btn_sabido.configure(state=estado)
        self.btn_siguiente.configure(state="disabled")

    def _marcar(self, sabido):
        if sabido:
            self.score["sabidos"] += 1
        else:
            self.score["repasar"] += 1
        self.btn_repasar.configure(state="disabled")
        self.btn_sabido.configure(state="disabled")
        self.btn_siguiente.configure(state="normal")

    def _siguiente(self):
        if self.indice < len(self.mazo) - 1:
            self.indice += 1
            self._mostrar_tarjeta()
        else:
            self._mostrar_resumen()

    def _mostrar_resumen(self):
        for w in self.winfo_children():
            w.destroy()
        ctk.CTkLabel(self, text="完了", font=("", 52)).pack(pady=(40, 8))
        ctk.CTkLabel(self, text="¡Sesión completada!", font=("", 20, "bold")).pack()
        ctk.CTkLabel(self,
            text=f"Sabidos: {self.score['sabidos']}   ·   A repasar: {self.score['repasar']}",
            font=("", 14), text_color="gray").pack(pady=8)
        ctk.CTkButton(self, text="Volver a empezar", width=200,
                      command=self._reiniciar).pack(pady=20)

    def _reiniciar(self):
        for w in self.winfo_children():
            w.destroy()
        self.mazo = KANJI_N5.copy()
        random.shuffle(self.mazo)
        self.indice  = 0
        self.volteada = False
        self.score   = {"sabidos": 0, "repasar": 0}
        self._construir_ui()
        self._mostrar_tarjeta()