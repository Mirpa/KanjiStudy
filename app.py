import random
import customtkinter as ctk
from data.n5 import KANJI_N5
from utils.renderer import render_kanji_image


class KanjiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KanjiStudy")
        self.geometry("420x540")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.mazo = KANJI_N5.copy()
        random.shuffle(self.mazo)
        self.indice = 0
        self.volteada = False
        self.score = {"sabidos": 0, "repasar": 0}
        self._img_ref = None

        self._construir_ui()
        self._mostrar_tarjeta()

    def _construir_ui(self):
        self.label_progreso = ctk.CTkLabel(self, text="", font=("", 13), text_color="gray")
        self.label_progreso.pack(pady=(20, 4))

        self.progressbar = ctk.CTkProgressBar(self, width=340)
        self.progressbar.pack(pady=(0, 20))

        self.frame_tarjeta = ctk.CTkFrame(self, width=340, height=240, corner_radius=16)
        self.frame_tarjeta.pack(pady=(0, 20))
        self.frame_tarjeta.pack_propagate(False)

        self.label_kanji = ctk.CTkLabel(self.frame_tarjeta, text="", image=None)
        self.label_kanji.place(relx=0.5, rely=0.42, anchor="center")

        self.label_hint = ctk.CTkLabel(self.frame_tarjeta, text="Haz clic para ver el significado",
                                       font=("", 12), text_color="gray")
        self.label_hint.place(relx=0.5, rely=0.85, anchor="center")

        self.label_significado = ctk.CTkLabel(self.frame_tarjeta, text="", font=("", 22, "bold"))
        self.label_onyomi      = ctk.CTkLabel(self.frame_tarjeta, text="", font=("", 13), text_color="#185FA5")
        self.label_kunyomi     = ctk.CTkLabel(self.frame_tarjeta, text="", font=("", 13), text_color="#3B6D11")

        self.frame_tarjeta.bind("<Button-1>", lambda e: self._voltear())
        self.label_kanji.bind("<Button-1>", lambda e: self._voltear())
        self.label_hint.bind("<Button-1>", lambda e: self._voltear())
        self.bind("<space>", lambda e: self._voltear())

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack()

        self.btn_repasar = ctk.CTkButton(self.frame_botones, text="No lo sabía", width=150,
                                          fg_color="#E24B4A", hover_color="#A32D2D",
                                          command=lambda: self._marcar(False))
        self.btn_repasar.grid(row=0, column=0, padx=8)

        self.btn_sabido = ctk.CTkButton(self.frame_botones, text="Lo sabía", width=150,
                                         fg_color="#639922", hover_color="#3B6D11",
                                         command=lambda: self._marcar(True))
        self.btn_sabido.grid(row=0, column=1, padx=8)

        self.btn_siguiente = ctk.CTkButton(self, text="Siguiente →", width=310,
                                            command=self._siguiente)
        self.btn_siguiente.pack(pady=14)

        self._ocultar_reverso()

    def _mostrar_tarjeta(self):
        c = self.mazo[self.indice]
        img = render_kanji_image(c["kanji"])
        self._img_ref = img
        self.label_kanji.configure(image=img, text="")
        self.label_kanji.place(relx=0.5, rely=0.42, anchor="center")
        self.label_hint.configure(text="Haz clic para ver el significado")
        total = len(self.mazo)
        self.label_progreso.configure(text=f"Tarjeta {self.indice + 1} de {total}")
        self.progressbar.set((self.indice + 1) / total)
        self._ocultar_reverso()
        self.volteada = False

    def _voltear(self):
        if self.volteada:
            return
        self.volteada = True
        self.label_kanji.place_forget()
        c = self.mazo[self.indice]
        self.label_significado.configure(text=c["significado"])
        self.label_onyomi.configure(text=f"On'yomi: {c['onyomi']}")
        self.label_kunyomi.configure(text=f"Kun'yomi: {c['kunyomi']}")
        self.label_hint.configure(text="")
        self.label_significado.place(relx=0.5, rely=0.38, anchor="center")
        self.label_onyomi.place(relx=0.5,      rely=0.58, anchor="center")
        self.label_kunyomi.place(relx=0.5,     rely=0.72, anchor="center")
        self.btn_repasar.configure(state="normal")
        self.btn_sabido.configure(state="normal")

    def _ocultar_reverso(self):
        self.label_significado.place_forget()
        self.label_onyomi.place_forget()
        self.label_kunyomi.place_forget()
        self.btn_repasar.configure(state="disabled")
        self.btn_sabido.configure(state="disabled")
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
        ctk.CTkLabel(self, text=f"Sabidos: {self.score['sabidos']}   ·   A repasar: {self.score['repasar']}",
                     font=("", 14), text_color="gray").pack(pady=8)
        ctk.CTkButton(self, text="Volver a empezar", width=200,
                      command=self._reiniciar).pack(pady=20)

    def _reiniciar(self):
        for w in self.winfo_children():
            w.destroy()
        self.mazo = KANJI_N5.copy()
        random.sh