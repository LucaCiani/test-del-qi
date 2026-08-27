import os
import shutil
import sys
import subprocess
import tempfile
import tkinter as tk
from tkinter import messagebox


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

    def __init__(self, root):
        self.root = root
        self.root.title("QI // Protocollo di valutazione")
        self.root.configure(bg=self.BG)
        self.root.minsize(760, 560)
        self.root.geometry("980x680")
        self.index = 0
        self.score = 0
        self.answers = []
        self.choice = tk.IntVar(value=-1)
        self.build_chrome()
        self.show_question()

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
        tk.Label(body, text=question, font=("Segoe UI", 22, "bold"), wraplength=780,
                 justify="left", fg=self.TEXT, bg=self.CARD).pack(anchor="w", pady=(18, 38))

        for number, option in enumerate(options):
            tk.Radiobutton(body, text=f"{chr(65 + number)})  {option}", variable=self.choice,
                           value=number, command=self.enable_next, indicatoron=False,
                           anchor="w", padx=20, pady=14, font=("Segoe UI", 12),
                           fg=self.TEXT, bg="#293548", activebackground="#394963",
                           activeforeground=self.TEXT, selectcolor=self.ACCENT_DARK,
                           relief="flat", bd=0).pack(fill="x", pady=5)

        self.next_button = tk.Button(body, text="CONFERMA RISPOSTA  →", command=self.next_question,
                                     state="disabled", font=("Segoe UI", 11, "bold"),
                                     fg="white", bg="#374151", activebackground=self.ACCENT,
                                     activeforeground="white", relief="flat", bd=0, padx=20, pady=13)
        self.next_button.pack(anchor="e", pady=(28, 0))

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
                 fg="#fca5a5", bg=self.CARD).pack(expand=True, padx=40)
        self.root.update_idletasks()
        self.root.after(1400, lambda: self._launch_video(video))

    def _launch_video(self, video):
        try:
            playable_video = os.path.join(tempfile.gettempdir(), "test-del-qi-video.mp4")
            shutil.copy2(video, playable_video)
            self.root.withdraw()
            if sys.platform == "win32":
                os.startfile(playable_video)
            else:
                subprocess.Popen(["xdg-open", playable_video])
            self.root.after(5000, self.show_result)
        except OSError as error:
            self.root.deiconify()
            messagebox.showerror("Avvio video fallito", str(error))

    def show_result(self):
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
        summary.create_window((0, 0), window=rows, anchor="nw")
        summary.bind_all("<MouseWheel>",
                         lambda event: summary.yview_scroll(-int(event.delta / 120), "units"))
        for number, (question, options, correct_index) in enumerate(QUESTIONS):
            selected = self.answers[number]
            is_correct = selected == correct_index
            selected_text = options[selected] if selected >= 0 else "Nessuna risposta"
            marker = "✓ CORRETTA" if is_correct else "✗ SBAGLIATA"
            text = (
                f"{number + 1}. {question}\n"
                f"  Risposta data: {selected_text}\n"
                f"  Risposta corretta: {options[correct_index]}   —   {marker}\n"
                f"  Spiegazione: {EXPLANATIONS[number]}"
            )
            tk.Label(rows, text=text, font=("Segoe UI", 10), wraplength=790,
                     justify="left", anchor="w", fg=self.TEXT, bg="#293548",
                     padx=12, pady=9).pack(fill="x", pady=3)
        rows.bind("<Configure>", lambda event: summary.configure(scrollregion=summary.bbox("all")))
        tk.Button(body, text="CHIUDI", command=self.root.destroy, font=("Segoe UI", 11, "bold"),
                  fg="white", bg=self.ACCENT, activebackground=self.ACCENT_DARK,
                  activeforeground="white", relief="flat", bd=0, padx=24, pady=13).pack(
                      anchor="e", pady=(34, 0))


if __name__ == "__main__":
    root = tk.Tk()
    QiQuiz(root)
    root.mainloop()
