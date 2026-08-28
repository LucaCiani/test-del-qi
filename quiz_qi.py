import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
import cv2
import pygame
from PIL import Image, ImageTk


QUESTIONS = [
    ("Quanti mesi all'anno hanno 28 giorni?", ["Solo 1 (Febbraio)", "Tutti e 12", "Dipende se è un anno bisestile"], 1),
    ("Il padre di Chiara ha cinque figlie: Nana, Nene, Nini, Nono. Come si chiama la quinta figlia?", ["Nunu", "Nina", "Chiara"], 2),
    ("Se partecipi a una corsa a piedi e superi il secondo, in che posizione arrivi?", ["Primo", "Secondo", "Terzo"], 1),
    ("Entri in uno chalet buio con un solo fiammifero. Ci sono una lampada ad olio e una candela. Cosa accendi per primo?", ["La candela", "La lampada ad olio", "Il fiammifero"], 2),
    ("Un pastore ha 17 pecore. Muoiono tutte tranne 9. Quante pecore gli rimangono vive?", ["8", "9", "0"], 1),
    ("Quanti animali di ogni specie portò Mosè sull'arca prima del diluvio?", ["2 (un maschio e una femmina)", "1 per specie", "Nessuno"], 2),
    ("Il medico ti dà 3 pillole da prendere tassativamente una ogni mezz'ora. Quanto durerà la cura in tutto?", ["Un'ora e mezza", "Un'ora", "Tre ore"], 1),
    ("Un gallo fa un uovo esattamente sul colmo del tetto spiovente di una cascina. Da che parte rotolerà l'uovo?", ["A destra verso il fienile", "A sinistra verso il cortile", "I galli non fanno le uova"], 2),
    ("Dividi il numero 30 per mezzo e aggiungi 10. Qual è il risultato finale?", ["25", "70", "50"], 1),
    ("Sei in una gara ciclistica e, con un colpo di reni, superi l'ultimo classificato. In che posizione ti trovi ora?", ["Penultimo", "Ultimo", "È impossibile"], 2),
    ("Quante volte puoi sottrarre il numero 10 dal numero 100?", ["10 volte", "1 volta", "Infinite volte"], 1),
    ("Cosa pesa di più in assoluto: un chilo di piume di struzzo o un chilo di piombo fuso?", ["Il piombo", "Le piume (per via del volume)", "Pesano esattamente uguale"], 2),
    ("Una piccola casa quadrata ha tutte e quattro le pareti esposte a sud. Un orso passa davanti alla finestra. Di che colore è l'orso?", ["Marrone", "Bianco", "Nero"], 1),
    ("Se scrivi a mano tutti i numeri interi da 1 a 100, quante volte scrivi la cifra 9?", ["10 volte", "11 volte", "20 volte"], 2),
]

EXPLANATIONS = [
    "Tutti i mesi hanno almeno 28 giorni.",
    "La quinta figlia è Chiara, come specificato nella domanda.",
    "Se superi il secondo classificato, prendi il suo posto: sei secondo.",
    "Prima di accendere qualsiasi cosa devi accendere il fiammifero.",
    "Restano vive le 9 pecore che non sono morte.",
    "Era Noè, non Mosè, a portare gli animali sull'arca.",
    "La prima pillola si prende subito, la seconda dopo 30 minuti e la terza dopo altri 30: un'ora.",
    "Un gallo non può fare uova.",
    "Dividere per mezzo equivale a moltiplicare per 2: 30 / 0,5 = 60, poi +10 = 70.",
    "Se superi l'ultimo, significa che non era davvero l'ultimo classificato.",
    "Dopo la prima sottrazione il numero diventa 90, quindi non stai più sottraendo da 100.",
    "Un chilo pesa un chilo, indipendentemente dal materiale.",
    "Una casa con tutte le pareti rivolte a sud si trova al Polo Nord: l'orso è bianco.",
    "La cifra 9 compare 10 volte nelle unità e 10 volte nelle decine: 20 volte.",
]


def app_directory():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


class QiQuiz:
    BG = "#111827"
    CARD = "#1f2937"
    TEXT = "#f8fafc"
    MUTED = "#94a3b8"
    ACCENT = "#8b5cf6"
    ACCENT_DARK = "#6d28d9"
    SUCCESS = "#34d399"
    ERROR = "#fb7185"

    def __init__(self, root):
        self.root = root
        self.root.title("QI // Protocollo di valutazione")
        self.root.configure(bg=self.BG)
        self.root.minsize(600, 440)
        self.root.geometry("980x680")
        self.root.state("zoomed")
        self.index = 0
        self.score = 0
        self.answers = []
        self.choice = tk.IntVar(value=-1)
        self.video_capture = None
        self.video_label = None
        self.audio_playing = False
        self.question_label = None
        self.option_buttons = []
        self.result_rows = []
        self.build_chrome()
        self.show_intro()

    def build_chrome(self):
        self.header = tk.Frame(self.root, bg=self.BG)
        self.header.pack(fill="x", padx=48, pady=(30, 0))
        tk.Label(self.header, text="QI // PROTOCOLLO", font=("Segoe UI", 11, "bold"),
                 fg="#c4b5fd", bg=self.BG).pack(side="left")
        self.counter = tk.Label(self.header, font=("Segoe UI", 11), fg=self.MUTED, bg=self.BG)
        self.counter.pack(side="right")
        self.progress = tk.Canvas(self.root, height=5, bg="#273449", highlightthickness=0)
        self.progress.pack(fill="x", padx=48, pady=(18, 28))

        self.card = tk.Frame(self.root, bg=self.CARD)
        self.card.pack(fill="both", expand=True, padx=48, pady=(0, 30))

    def show_intro(self):
        for child in self.card.winfo_children():
            child.destroy()
        self.counter.config(text="BENVENUTO")
        self.progress.delete("all")
        body = tk.Frame(self.card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=54, pady=70)
        tk.Label(body, text="GRAZIE PER LA PARTECIPAZIONE",
                 font=("Segoe UI", 24, "bold"), fg=self.TEXT, bg=self.CARD).pack(pady=(25, 18))
        tk.Label(body, text="Stai per iniziare il test del QI definitivo.\n"
                 "Quando avrai finito, condividilo con altri amici e confrontate i risultati!",
                 font=("Segoe UI", 14), justify="center", wraplength=700,
                 fg=self.MUTED, bg=self.CARD).pack(pady=(0, 38))
        tk.Button(body, text="INIZIA IL TEST  →", command=self.start_test,
                  font=("Segoe UI", 12, "bold"), fg="white", bg=self.ACCENT,
                  activebackground=self.ACCENT_DARK, activeforeground="white",
                  relief="flat", bd=0, padx=30, pady=15).pack()

    def start_test(self):
        self.index = 0
        self.score = 0
        self.answers = []
        self.show_question()

    def show_question(self):
        for child in self.card.winfo_children():
            child.destroy()
        self.choice.set(-1)
        self.counter.config(text=f"{self.index + 1:02d} / {len(QUESTIONS):02d}")
        self.progress.delete("all")
        self.progress.update_idletasks()
        width = max(self.progress.winfo_width(), 1)
        self.progress.create_rectangle(0, 0, width * (self.index + 1) / len(QUESTIONS), 5,
                                       fill=self.ACCENT, outline="")

        question, options, _ = QUESTIONS[self.index]
        body = tk.Frame(self.card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=54, pady=46)
        tk.Label(body, text=f"DOMANDA {self.index + 1}", font=("Segoe UI", 10, "bold"),
                 fg="#a78bfa", bg=self.CARD).pack(anchor="w")
        self.question_label = tk.Label(
            body, text=question, font=("Segoe UI", 22, "bold"), wraplength=780,
            justify="left", anchor="w", fg=self.TEXT, bg=self.CARD
        )
        self.question_label.pack(fill="x", pady=(18, 38))
        body.bind("<Configure>", self._resize_question)

        self.option_buttons = []
        for number, option in enumerate(options):
            option_button = tk.Radiobutton(
                body, text=f"{chr(65 + number)})  {option}", variable=self.choice,
                value=number, command=self.enable_next, indicatoron=False,
                anchor="w", padx=20, pady=14, font=("Segoe UI", 12),
                fg=self.TEXT, bg="#293548", activebackground="#394963",
                activeforeground=self.TEXT, selectcolor=self.ACCENT_DARK,
                relief="flat", bd=0
            )
            option_button.pack(fill="x", pady=5)
            self.option_buttons.append(option_button)

        self.next_button = tk.Button(body, text="CONFERMA RISPOSTA  →", command=self.next_question,
                                     state="disabled", font=("Segoe UI", 11, "bold"),
                                     fg="white", bg="#374151", activebackground=self.ACCENT,
                                     activeforeground="white", relief="flat", bd=0, padx=20, pady=13)
        self.next_button.pack(anchor="e", pady=(28, 0))

    def _resize_question(self, event):
        if self.question_label is None or event.width <= 0:
            return
        available_width = max(event.width - 10, 240)
        scale = self._responsive_scale(event.width, event.height)
        available_height = max(event.height - round(230 * scale), 80)
        question = self.question_label.cget("text")
        font_size = max(10, round(22 * scale))
        while font_size > 10:
            font = tkfont.Font(family="Segoe UI", size=font_size, weight="bold")
            line_count = 1
            line_width = 0
            for word in question.split():
                word_width = font.measure(word + " ")
                if line_width + word_width > available_width and line_width:
                    line_count += 1
                    line_width = word_width
                else:
                    line_width += word_width
            if line_count * font.metrics("linespace") <= available_height:
                break
            font_size -= 1
        self.question_label.configure(
            font=("Segoe UI", font_size, "bold"),
            wraplength=available_width,
            pady=0,
        )
        option_font_size = max(9, round(12 * scale))
        option_padx = max(10, round(20 * scale))
        option_pady = max(7, round(14 * scale))
        for option_button in self.option_buttons:
            option_button.configure(
                font=("Segoe UI", option_font_size),
                padx=option_padx,
                pady=option_pady,
            )
        if hasattr(self, "next_button"):
            self.next_button.configure(
                font=("Segoe UI", max(9, round(11 * scale)), "bold"),
                padx=max(12, round(20 * scale)),
                pady=max(8, round(13 * scale)),
            )

    @staticmethod
    def _responsive_scale(width, height):
        return min(max(min(width / 980, height / 680), 0.75), 1.5)

    def enable_next(self):
        self.next_button.config(state="normal", bg=self.ACCENT)

    def next_question(self):
        selected = self.choice.get()
        correct = selected == QUESTIONS[self.index][2]
        self.answers.append(selected)
        if correct:
            self.score += 1
        self.index += 1
        if self.index == len(QUESTIONS):
            self.show_final()
        else:
            self.show_question()

    def show_final(self):
        for child in self.card.winfo_children():
            child.destroy()
        self.counter.config(text="ANALISI COMPLETATA")
        self.progress.delete("all")
        self.progress.create_rectangle(0, 0, self.progress.winfo_width(), 5, fill=self.ACCENT, outline="")
        body = tk.Frame(self.card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=54, pady=46)
        tk.Label(body, text="ELABORAZIONE DATI IN CORSO...", font=("Segoe UI", 10, "bold"),
                 fg="#a78bfa", bg=self.CARD).pack(anchor="w")
        tk.Label(body, text="Il tuo profilo cognitivo definitivo è pronto.",
                 font=("Segoe UI", 22, "bold"), fg=self.TEXT, bg=self.CARD).pack(anchor="w", pady=(18, 8))
        tk.Label(body, text="Vuoi scoprire il tuo vero livello di intelligenza?",
                 font=("Segoe UI", 14), fg=self.MUTED, bg=self.CARD).pack(anchor="w", pady=(0, 34))
        buttons = [
            "CERTO, MOSTRAMI IL RISULTATO!",
            "RIVELAMI QUANTO SONO GENIO!",
            "VISUALIZZA IL MIO QI ESATTO",
        ]
        for text in buttons:
            tk.Button(body, text=text, command=self.play_video, font=("Segoe UI", 11, "bold"),
                      fg="white", bg=self.ACCENT, activebackground=self.ACCENT_DARK,
                      activeforeground="white", relief="flat", bd=0, padx=18, pady=13).pack(fill="x", pady=5)

    def play_video(self):
        video = os.path.join(app_directory(), "media", "videoplayback.mp4")
        if not os.path.isfile(video):
            messagebox.showerror("Media non trovato", f"Impossibile trovare il video:\n{video}")
            return
        for child in self.card.winfo_children():
            child.destroy()
        tk.Label(self.card, text="È RISULTATO CHE SEI STUPIDO IN CULO",
                 font=("Segoe UI", 25, "bold"), wraplength=760, justify="center",
                 fg="#fca5a5", bg=self.CARD).pack(pady=(30, 10), padx=40)
        self.video_label = tk.Label(self.card, bg="#000000")
        self.video_label.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        tk.Button(self.card, text="MOSTRA I RISULTATI  →", command=self.show_result,
                  font=("Segoe UI", 11, "bold"), fg="white", bg=self.ACCENT,
                  activebackground=self.ACCENT_DARK, activeforeground="white",
                  relief="flat", bd=0, padx=22, pady=11).pack(pady=(0, 20))
        self.root.update_idletasks()
        self.video_capture = cv2.VideoCapture(video)
        if not self.video_capture.isOpened():
            messagebox.showerror("Riproduzione fallita", "Impossibile aprire il video incorporato.")
            self.show_final()
            return
        audio = os.path.join(app_directory(), "media", "video_audio.wav")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio)
            pygame.mixer.music.play()
            self.audio_playing = True
        except pygame.error as error:
            self.video_capture.release()
            self.video_capture = None
            messagebox.showerror("Riproduzione audio fallita", str(error))
            self.show_final()
            return
        self.root.after(100, self._play_next_frame)

    def _play_next_frame(self):
        if self.video_capture is None:
            return
        success, frame = self.video_capture.read()
        if not success:
            self.video_capture.release()
            self.video_capture = None
            if self.audio_playing:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                self.audio_playing = False
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        video_width = max(self.video_label.winfo_width() - 10, 320)
        video_height = max(self.video_label.winfo_height() - 10, 180)
        image.thumbnail((video_width, video_height), Image.Resampling.LANCZOS)
        self.video_label.image = ImageTk.PhotoImage(image)
        self.video_label.configure(image=self.video_label.image)
        fps = self.video_capture.get(cv2.CAP_PROP_FPS) or 25
        self.root.after(max(1, round(1000 / fps)), self._play_next_frame)

    def show_result(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        if self.audio_playing:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.audio_playing = False
        self.root.deiconify()
        for child in self.card.winfo_children():
            child.destroy()
        self.counter.config(text="RISULTATO REALE")
        self.progress.delete("all")
        self.progress.create_rectangle(0, 0, self.progress.winfo_width(), 5,
                                       fill=self.ACCENT, outline="")
        body = tk.Frame(self.card, bg=self.CARD)
        body.pack(fill="both", expand=True, padx=35, pady=25)
        tk.Label(body, text="RISULTATO DEL TEST", font=("Segoe UI", 10, "bold"),
                 fg="#a78bfa", bg=self.CARD).pack(anchor="w")
        tk.Label(body, text=f"Hai risposto correttamente a {self.score} domande su {len(QUESTIONS)}.",
                 font=("Segoe UI", 18, "bold"), wraplength=780, justify="left",
                 fg=self.TEXT, bg=self.CARD).pack(anchor="w", pady=(18, 12))
        tk.Label(body, text=f"PUNTEGGIO REALE: {self.score}/{len(QUESTIONS)}",
                 font=("Segoe UI", 15, "bold"), fg="#c4b5fd", bg=self.CARD).pack(anchor="w")

        summary_frame = tk.Frame(body, bg=self.CARD)
        summary_frame.pack(fill="both", expand=True, pady=(18, 0))
        summary = tk.Canvas(summary_frame, bg=self.CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(summary_frame, orient="vertical", command=summary.yview)
        summary.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        summary.pack(side="left", fill="both", expand=True)
        rows = tk.Frame(summary, bg=self.CARD)
        self.result_rows = []
        rows_window = summary.create_window((0, 0), window=rows, anchor="nw")
        summary.bind_all("<MouseWheel>",
                         lambda event: summary.yview_scroll(-int(event.delta / 120), "units"))
        summary.bind(
            "<Configure>",
            lambda event: self._resize_summary(summary, rows, rows_window, event.width),
        )
        for number, (question, options, correct_index) in enumerate(QUESTIONS):
            selected = self.answers[number]
            is_correct = selected == correct_index
            selected_text = options[selected] if selected >= 0 else "Nessuna risposta"
            marker = "✓ CORRETTA" if is_correct else "✗ SBAGLIATA"
            status_color = self.SUCCESS if is_correct else self.ERROR
            row = tk.Frame(rows, bg="#293548", padx=16, pady=14)
            row.pack(fill="x", pady=3)
            status = tk.Label(
                row, text=marker, font=("Segoe UI", 10, "bold"),
                fg=status_color, bg="#293548", anchor="w"
            )
            status.pack(fill="x", pady=(0, 10))
            question_label = tk.Label(
                row, text=f"{number + 1}. {question}", font=("Segoe UI", 10, "bold"),
                justify="left", anchor="w", fg=self.TEXT, bg="#293548"
            )
            question_label.pack(fill="x", pady=(0, 12))
            given_label = tk.Label(
                row, text=f"Risposta data: {selected_text}", font=("Segoe UI", 10),
                justify="left", anchor="w", fg=status_color, bg="#293548"
            )
            given_label.pack(fill="x", pady=(0, 9))
            correct_label = tk.Label(
                row, text=f"Risposta corretta: {options[correct_index]}",
                font=("Segoe UI", 10), justify="left", anchor="w",
                fg=self.SUCCESS, bg="#293548"
            )
            correct_label.pack(fill="x", pady=(0, 9))
            explanation_label = tk.Label(
                row, text=f"Soluzione: {EXPLANATIONS[number]}", font=("Segoe UI", 10),
                justify="left", anchor="w", fg="#cbd5e1", bg="#293548"
            )
            explanation_label.pack(fill="x")
            self.result_rows.append(
                (row, status, question_label, given_label, correct_label, explanation_label)
            )
        rows.bind("<Configure>", lambda event: summary.configure(scrollregion=summary.bbox("all")))
        body.bind("<Configure>", self._resize_results)
        actions = tk.Frame(body, bg=self.CARD)
        actions.pack(fill="x", pady=(20, 0))
        tk.Button(actions, text="RIPETI IL TEST", command=self.restart_test,
                  font=("Segoe UI", 11, "bold"), fg="white", bg=self.ACCENT,
                  activebackground=self.ACCENT_DARK, activeforeground="white",
                  relief="flat", bd=0, padx=24, pady=13).pack(side="left")
        tk.Button(actions, text="CHIUDI", command=self.root.destroy,
                  font=("Segoe UI", 11, "bold"), fg="white", bg="#374151",
                  activebackground="#4b5563", activeforeground="white",
                  relief="flat", bd=0, padx=24, pady=13).pack(side="right")

    def _resize_summary(self, summary, rows, rows_window, width):
        content_width = max(width - 12, 300)
        summary.itemconfigure(rows_window, width=content_width)
        for row in rows.winfo_children():
            for child in row.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(wraplength=max(content_width - 32, 260))

    def _resize_results(self, event):
        if event.width <= 0 or event.height <= 0:
            return
        scale = self._responsive_scale(event.width, event.height)
        row_font_size = max(8, round(10 * scale))
        row_padx = max(8, round(12 * scale))
        row_pady = max(6, round(9 * scale))
        for row, status, question_label, given_label, correct_label, explanation_label in self.result_rows:
            row.configure(
                padx=row_padx,
                pady=row_pady,
            )
            status.configure(font=("Segoe UI", row_font_size, "bold"))
            question_label.configure(font=("Segoe UI", row_font_size, "bold"))
            given_label.configure(font=("Segoe UI", row_font_size))
            correct_label.configure(font=("Segoe UI", row_font_size))
            explanation_label.configure(font=("Segoe UI", row_font_size))

    def restart_test(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        if self.audio_playing:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.audio_playing = False
        self.index = 0
        self.score = 0
        self.answers = []
        self.show_intro()


if __name__ == "__main__":
    root = tk.Tk()
    QiQuiz(root)
    root.mainloop()
