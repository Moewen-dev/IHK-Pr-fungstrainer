import sqlite3, sys, json, random, hashlib, datetime
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk

sql_statements = ["""CREATE TABLE IF NOT EXISTS fragen (
    id INTEGER PRIMARY KEY,
    frage TEXT NOT NULL,
    A TEXT NOT NULL,
    B TEXT NOT NULL,
    C TEXT NOT NULL,
    antwort INTEGER NOT NULL,
    kategorie TEXT NOT NULL);""",
    """CREATE TABLE IF NOT EXISTS userdata (
    user_id INTEGER PRIMARY KEY,
    is_admin INTEGER NOT NULL,
    username TEXT NOT NULL,
    pw_hash TEXT NOT NULL,
    fragen_total INTEGER,
    fragen_richtig INTEGER,
    fragen_falsch TEXT,
    stat_fragen_richtig TEXT,
    stat_fragen_falsch TEXT,
    pruefungen_total INT,
    pruefungen_bestanden INT,
    stat_pruefungen TEXT);"""]

# Datenbank Dateiname
db_name = "data.db"

# Funktion: add_frage
# Fügt eine neue Frage in die Datenbank ein.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
#   frage: Text der Frage
#   A, B, C: Antwortmöglichkeiten
#   antwort: Richtige Antwort (als Identifier)
#   kategorie: Optionale Kategorie (Standard "default")
def add_frage(con, cur, frage, A, B, C, antwort, kategorie="default"):  # default kategorie falls keine spezifiziert
    # Frage in die Datenbank hinzufügen
    cur.execute("INSERT INTO fragen (frage, A, B, C, antwort, kategorie) VALUES (?, ?, ?, ?, ?, ?)", (frage, A, B, C, antwort, kategorie))
    con.commit()
    
# Funktion: get_fragen
# Ruft alle Fragen aus der Datenbank ab und wandelt sie in Frage-Objekte um.
# Benötigt:
#   cur: Datenbankcursor
def get_fragen(cur):
    # Fragen aus der Datenbank holen
    cur.execute("SELECT * FROM fragen")
    db_data = cur.fetchall()
    fragen = []
    for data in db_data:
        frage = Frage(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
        fragen.append(frage)
    return fragen

# Funktion: import_fragen
# Importiert Fragen aus einer JSON-Datei in die Datenbank und fügt nur neue Fragen hinzu.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
#   filename: Pfad zur JSON-Datei mit Fragen
def import_fragen(con, cur, filename):
    # Fragen aus einer JSON Datei Importieren
    try:
        with open(filename, "r", encoding="utf-8") as f:
            neue_fragen = json.load(f)
        fragen = []
        db_fragen = get_fragen(cur)
        for item in neue_fragen["fragen"]:
            fragen.append(Frage(0, item["frage"], item["A"], item["B"], item["C"], item["richtigeAntwort"], item["kategorie"]))
        if db_fragen == []:         # Wenn keine Fragen in der Datenbank sind, füge einfach die ganze Datei an Fragen ein.
            for neue_frage in fragen:
                add_frage(con, cur, neue_frage.frage, neue_frage.A, neue_frage.B, neue_frage.C, neue_frage.antwort, neue_frage.kategorie)
        else:                       # Wenn Fragen vorhanden sind, prüfen, ob die zu importierenden schon vorhanden sind und füge nur die hinzu,
                                    # die noch nicht in der Datenbank sind
            db_fragen_liste = []
            for db_frage in db_fragen:
                db_fragen_liste.append(db_frage.frage)
            for frage in fragen:
                if frage.frage not in db_fragen_liste:
                    add_frage(con, cur, frage.frage, frage.A, frage.B, frage.C, frage.antwort, frage.kategorie)
    except TypeError as e:
        print(f"Error: {e}")

# Funktion: export_fragen
# Exportiert alle Fragen aus der Datenbank in eine JSON-Datei.
# Benötigt:
#   cur: Datenbankcursor
def export_fragen(cur):
    # Fragen werden hier in eine JSON Datei exportiert, dies dient dazu evtl jemanden seine Fragen zu schicken oder sich selber verschiedene Fragensätze zu speichern
    if messagebox.askyesno("Fragen exportieren", "Möchtest du deine gespeicherte Fragen exportieren?"):
        try:
            fragen = get_fragen(cur)
            to_export = {"fragen": []}
            for frage in fragen:
                to_export["fragen"].append(frage.export())
            with open("fragen_export.json", "wt", encoding="utf-8") as file:
                file.write(json.dumps(to_export, ensure_ascii=False))
            messagebox.showinfo("Fragen export", "Fragen erfolgreich exportiert")
        except:
            messagebox.showerror("Fragen export", "Fragen export nicht erfolgreich")
    else:
        Admin()

# Funktion: manuell_fragen
# Öffnet ein Fenster, um eine einzelne Frage manuell hinzuzufügen.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
def manuell_fragen(con, cur):
    # Neues Fenster öffnen
    add_window = tk.Toplevel()
    add_window.title("Frage hinzufügen")
    add_window.geometry("500x600")

    eingabe_rahmen = ttk.LabelFrame(add_window, text="Frage erstellen")
    eingabe_rahmen.pack(padx=20, pady=20, fill="both", expand=True)

    # Wie lautet die Frage?
    ttk.Label(eingabe_rahmen, text="Frage:").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    frage_entry = ttk.Entry(eingabe_rahmen, width=50)
    frage_entry.grid(row=1, column=0, padx=10, pady=5)

    # Standardmäßig Antwort A als richtig markieren
    antwort_var = tk.StringVar(value="A")

    # Antwort A definieren
    ttk.Label(eingabe_rahmen, text="Antwort A:").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
    a_entry = ttk.Entry(eingabe_rahmen, width=40)
    a_entry.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    a_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="A")
    a_radio.grid(row=3, column=1, padx=10, sticky="w")

    # Antwort B definieren
    ttk.Label(eingabe_rahmen, text="Antwort B:").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
    b_entry = ttk.Entry(eingabe_rahmen, width=40)
    b_entry.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    b_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="B")
    b_radio.grid(row=5, column=1, padx=10, sticky="w")

    # Antwort C definieren
    ttk.Label(eingabe_rahmen, text="Antwort C:").grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
    c_entry = ttk.Entry(eingabe_rahmen, width=40)
    c_entry.grid(row=7, column=0, padx=10, pady=5, sticky="w")
    c_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="C")
    c_radio.grid(row=7, column=1, padx=10, sticky="w")

    # Kategorie (nur Eingabefeld, kein Dropdown)
    ttk.Label(eingabe_rahmen, text="Kategorie:").grid(row=8, column=0, sticky="w", padx=10, pady=(10, 0))
    kat_entry = ttk.Entry(eingabe_rahmen, width=40)
    kat_entry.grid(row=9, column=0, padx=10, pady=5, sticky="w")

    # Frage speichern und Feedback
    def save_frage():
        frage = frage_entry.get()
        A = a_entry.get()
        B = b_entry.get()
        C = c_entry.get()
        antwort = antwort_var.get()
        kat = kat_entry.get() 

        # Frage wird gespeichert
        add_frage(con, cur, frage, A, B, C, antwort, kat)
        messagebox.showinfo("Erfolg", f"Frage \"{frage}\" erfolgreich unter \"{kat}\" hinzugefügt.")
        add_window.destroy()

        # Weitere Frage hinzufügen oder zurück zum Adminbereich?
        if messagebox.askyesno("Fragen hinzufügen", "Möchtest du eine weitere Frage hinzufügen?"):
            manuell_fragen(con, cur)
        else:
            Admin()

    save_btn = ttk.Button(add_window, text="Frage speichern", command=save_frage)
    save_btn.pack(pady=20)

# Funktion: edit_fragen
# Öffnet ein Fenster, in dem existierende Fragen bearbeitet werden können.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
def edit_fragen(con, cur):
    edit_window = tk.Toplevel(bg="#d8d8d8")
    edit_window.title("Fragen bearbeiten")
    edit_window.geometry("500x600")

    # Header für das Bearbeitungsfenster
    header = ttk.Label(
        edit_window,
        text="Klicke auf eine Frage, um sie zu bearbeiten:",
        font=("Arial", 12, "bold"),
        background="#d8d8d8"
    )
    header.pack(pady=10)

    # Container für Scrollbar und Canvas
    container = ttk.Frame(edit_window)
    container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Canvas und Scrollbar für die Frage-Liste
    canvas = tk.Canvas(container, borderwidth=0, background="#d8d8d8", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    # Scrollbar und Canvas konfigurieren
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", on_frame_configure)
    scroll_frame.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # Funktion zum Bearbeiten einer Frage
    def frage_bearbeiten_fenster(frage, edit_window):
        edit_window.destroy()  # Aktuelles Fenster schließen
        # Neues Fenster für die Bearbeitung der Frage
        frage_edit = tk.Toplevel()
        frage_edit.title("Frage bearbeiten")
        frage_edit.geometry("500x500")

        eingabe_rahmen = ttk.LabelFrame(frage_edit, text="Frage bearbeiten")
        eingabe_rahmen.pack(padx=20, pady=20, fill="both", expand=True)

        # Eingabe für Frage
        ttk.Label(eingabe_rahmen, text="Frage:").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
        frage_entry = ttk.Entry(eingabe_rahmen, width=50)
        frage_entry.insert(0, frage.frage)
        frage_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Standardmäßig die aktuelle Antwort als richtig markieren
        antwort_var = tk.StringVar(value=frage.antwort)

        # Antwort A
        ttk.Label(eingabe_rahmen, text="Antwort A:").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        a_entry = ttk.Entry(eingabe_rahmen, width=40)
        a_entry.insert(0, frage.A)
        a_entry.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        a_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="A")
        a_radio.grid(row=3, column=1, padx=10, sticky="w")

        # Antwort B
        ttk.Label(eingabe_rahmen, text="Antwort B:").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
        b_entry = ttk.Entry(eingabe_rahmen, width=40)
        b_entry.insert(0, frage.B)
        b_entry.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        b_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="B")
        b_radio.grid(row=5, column=1, padx=10, sticky="w")

        # Antwort C
        ttk.Label(eingabe_rahmen, text="Antwort C:").grid(row=6, column=0, sticky="w", padx=10, pady=(10, 0))
        c_entry = ttk.Entry(eingabe_rahmen, width=40)
        c_entry.insert(0, frage.C)
        c_entry.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        c_radio = ttk.Radiobutton(eingabe_rahmen, text="Richtig", variable=antwort_var, value="C")
        c_radio.grid(row=7, column=1, padx=10, sticky="w")

        # Speichern-Button
        def speichern():
            neue_frage = frage_entry.get() # Frage aktualisieren
            neue_A = a_entry.get() # Antwort A aktualisieren
            neue_B = b_entry.get() # Antwort B aktualisieren
            neue_C = c_entry.get() # Antwort C aktualisieren
            neue_antwort = antwort_var.get() # Richtige Antwort aktualisieren

            cur.execute("""
                UPDATE fragen
                SET frage = ?, A = ?, B = ?, C = ?, antwort = ?
                WHERE id = ?
            """, (neue_frage, neue_A, neue_B, neue_C, neue_antwort, frage.id))
            con.commit() # Änderungen speichern

            messagebox.showinfo("Erfolg", f'Frage \"{neue_frage}\" erfolgreich aktualisiert.') # Feedback geben
            frage_edit.destroy()
            fortfahren = messagebox.askyesno("Bestätigung", "Möchtest du weitere Fragen bearbeiten?") # Sollen weitere Fragen bearbeitet werden?
            if not fortfahren: # Wenn nicht, dann zurück zum Adminbereich
                return
            edit_fragen(con, cur)  # aktualisierte Bearbeitungsliste erneut laden

        speichern_btn = ttk.Button(frage_edit, text="Änderungen speichern", command=speichern)
        speichern_btn.pack(pady=20)

    # Frage-Liste aus DB holen
    fragen = get_fragen(cur)

    # Keine Fragen in der DB
    if not fragen:
        ttk.Label(scroll_frame, text="Keine Fragen in der Datenbank.", foreground="red").pack(pady=20)
        return

    # Buttons für jede Frage erstellen
    for frage in fragen:
        try:
            text = frage.frage.strip()
            if len(text) > 80:
                text = text[:77] + "..."

            btn = ttk.Button(scroll_frame, text=frage.frage, command=lambda f=frage: frage_bearbeiten_fenster(f, edit_window)) # Button zum Bearbeiten der Frage
            btn.pack(fill="x", padx=10, pady=5)
        except Exception as e: # Fehler beim Anzeigen einer Frage
            print(f"Fehler beim Anzeigen einer Frage: {e}")

# Funktion: del_frage
# Zeigt ein Fenster, in dem mehrere Fragen ausgewählt und anschließend gelöscht werden können.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
def del_frage(con, cur):
    # Hier werden alle Fragen angezeigt. Anschließend kann man mehrere auswählen und anschließend löschen
    del_window = tk.Toplevel(bg="#d8d8d8")  # Die Hintergrundfarbe wird Festgelegt
    del_window.title("Fragen löschen")        # Der Fenstertitel wird Festgelegt
    del_window.geometry("500x600")            # Die Fenstergröße wird Festgelegt

    # Es wird die Überschrift erstellt
    header = ttk.Label(del_window, text="Wähle die Fragen aus, die du löschen möchtest:", font=("Arial", 12, "bold"), background="#d8d8d8")
    header.pack(pady=10)
    
    # Es wird ein Rahmen erstellt
    container = ttk.Frame(del_window)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(container, borderwidth=0, background="#d8d8d8", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas, style="TFrame")

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", on_frame_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scroll_frame.bind_all("<MouseWheel>", _on_mousewheel)

    fragen = get_fragen(cur)
    for frage in fragen:
        checkbox = ttk.Checkbutton(scroll_frame, text=frage.frage, variable=frage.delete)
        checkbox.pack(anchor="w", padx=10, pady=5)

    def delete_selected():
        auszuwählen = [frage for frage in fragen if frage.delete.get()]
        if not auszuwählen:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle mindestens eine Frage aus.")
            del_window.lift()
            del_window.focus_force()
            return
        fortfahren = messagebox.askyesno("Bestätigung", "Möchtest du die ausgewählten Fragen wirklich löschen?")
        if not fortfahren:
            return
        for frage in auszuwählen:
            cur.execute("DELETE FROM fragen WHERE id=?", (frage.id,))
        con.commit()
        messagebox.showinfo("Erfolg", "Ausgewählte Fragen wurden gelöscht.")
        del_window.destroy()

    ttk.Button(del_window, text="Ausgewählte Fragen löschen", command=delete_selected).pack(pady=15)

# Funktion: add_user
# Fügt einen neuen Benutzer in die Datenbank ein.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
#   is_admin: Gibt an, ob der Benutzer Adminrechte erhält
#   username: Benutzername
#   pw_hash: Passwort-Hash
def add_user(con, cur, is_admin, username, pw_hash):
    cur.execute("INSERT INTO userdata (is_admin, username, pw_hash) VALUES (?, ?, ?)", (is_admin, username, pw_hash))
    con.commit()

# Funktion: current_datetime
# Liefert das aktuelle Datum und die aktuelle Uhrzeit im angegebenen Format.
# Benötigt:
#   format: Optionaler Formatstring (Standard "%d.%m.%Y %H:%M:%S")
def current_datetime(format = "%d.%m.%Y %H:%M:%S"):
    return datetime.datetime.now().strftime(format)

# Gui Funktionen
# Hauptfenster und Inhalt vorbereiten
root = ThemedTk(theme="scidgreen")
root.title("Prüfungstrainer")
root.geometry("500x600")

inhalt_frame = ttk.Frame(root, padding=(3,3,12,12))
inhalt_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W)) # type: ignore

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
inhalt_frame.columnconfigure(0, weight=3)
inhalt_frame.columnconfigure(1, weight=3)
inhalt_frame.columnconfigure(3, weight=3)
inhalt_frame.rowconfigure(0, weight=3)
inhalt_frame.rowconfigure(1, weight=3)

# Funktion: toggle_fullscreen
# Schaltet das Fenster in den oder aus dem Vollbildmodus.
# Benötigt:
#   event: (Optionales) Ereignisobjekt
def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

# Funktion: end_fullscreen
# Beendet den Vollbildmodus.
# Benötigt:
#   event: (Optionales) Ereignisobjekt
def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)

# Funktion: clear_inhalt
# Löscht alle Widgets im Hauptinhalt-Frame.
def clear_inhalt():
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

# Funktion: openfile
# Öffnet den Dateidialog und gibt den ausgewählten Dateipfad zurück.
def openfile():
    filename = askopenfilename() 
    return filename

# Funktion: Prüfungsmodus
# Initialisiert und zeigt den Prüfungsmodus, in dem 30 zufällige Fragen gestellt werden.
def Prüfungsmodus():
    # Hier wird das Prüfungsmodus Fenster erstellt
    if user.user_id == 0:       # Als erster wird überprüft ob der User angemeldet ist. Wenn nicht wird er zurück zur Startseite geschickt.
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich an, um den Prüfungsmodus zu nutzen.")
        Startseite()
        return

    clear_inhalt()
    prüfungs_frame = ttk.Frame(inhalt_frame)
    prüfungs_frame.pack(fill="both", expand=True)
    Begrüßungs_label = ttk.Label(prüfungs_frame, 
                                text="Dies ist der Prüfungsmodus.\nDu wirst 30 Fragen erhalten, welche zufällig aus allen Fragen genommen werden.\nDas Ergebnis was du erziehlst hast, erhälst du wenn du alle Fragen beatnwortet hast.")
    Begrüßungs_label.grid(row=0, column=0, pady=50)

    Start_Btn = ttk.Button(prüfungs_frame, text="Prüfung starten", command=lambda: Starte_Prüfung(prüfungs_frame))
    Start_Btn.grid(row=1, column=0, pady=50)

# Funktion: Starte_Prüfung
# Löscht das Prüfungsfenster und startet die Prüfung mit 30 zufälligen Fragen.
# Benötigt:
#   prüfungs_frame: Das Frame, in dem die Prüfung stattfindet.
def Starte_Prüfung(prüfungs_frame):

    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    fragen = get_fragen(cur)
    if len(fragen) >= 1:
        prüfungsfragen = random.sample(fragen, 30)
    else:
        Fehler_label = ttk.Label(prüfungs_frame,
                                 text="Fehler! Es gibt nicht genug Fragen. Importieren sie welche, oder wenden sie sich einen Administrator!")
        weiterleit_Btn = ttk.Button(prüfungs_frame,
                                    text="Fragen Importieren",
                                    command=lambda: Admin())
        weiterleit_Btn.grid(row=2, column=0, pady=50)

        Fehler_label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        return

    frage_index = 0
    falsche_Prüfungsfragen = 0

    zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen)

# Funktion: zeige_Prüfungsfragen
# Zeigt die aktuelle Frage im Prüfungsmodus inklusive Fortschrittsanzeige und Antwortmöglichkeiten.
# Benötigt:
#   prüfungs_frame: Frame des Prüfungsmodus
#   frage_index: Index der aktuellen Frage
#   prüfungsfragen: Liste der Prüfungsfragen
#   falsche_Prüfungsfragen: Zähler für falsche Antworten
def zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    auswahl = tk.StringVar(value="X")

    if  frage_index < 30:
        aktuelle_frage = prüfungsfragen[frage_index]

        progress = tk.IntVar(value=frage_index + 1)  # Fortschritt aktualisieren
        progressbar = ttk.Progressbar(prüfungs_frame, maximum=30, variable=progress, length=400)
        progressbar.grid(row=0, column=0, padx=40, pady=5)

        Fortschirt_label = ttk.Label(prüfungs_frame, text=f"Du bist bei Frage {frage_index +1} von {len(prüfungsfragen)}")
        Fortschirt_label.grid(row=2, column=0)

        Frage_label = ttk.Label(prüfungs_frame, text=aktuelle_frage.frage)
        Frage_label.grid(row=3, column=0, pady=40)

        button_rahmen = ttk.LabelFrame(prüfungs_frame)
        button_rahmen.grid(row=4, column=0, padx=40, pady=5)

        frageA = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.A, variable=auswahl, value="A")
        frageA.grid(row=0, column=0, pady=10, padx=20)

        frageB = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.B, variable=auswahl, value="B")
        frageB.grid(row=1, column=0, pady=10, padx=20)

        frageC = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.C, variable=auswahl, value="C")
        frageC.grid(row=2, column=0, pady=10, padx=20)

        submit_btn = ttk.Button(prüfungs_frame,text="Antwort absenden",
                                command=lambda: prüffrage_überprüfen(auswahl, aktuelle_frage, prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen))
        submit_btn.grid(row=5, column=0)  
    else:
        prozent_anzahl = ((30 - falsche_Prüfungsfragen) / 30) * 100

        match prozent_anzahl:
            case p if p >= 92:
                note = f"1 - {prozent_anzahl:.2f}%"
            case p if p >= 81:
                note = f"2 - {prozent_anzahl:.2f}%"
            case p if p >= 67:
                note = f"3 - {prozent_anzahl:.2f}%"
            case p if p >= 50:
                note = f"4 - {prozent_anzahl:.2f}%"
            case p if p >= 30:
                note = f"5 - {prozent_anzahl:.2f}%"
            case _:
                note = f"6 - {prozent_anzahl:.2f}%"

        if prozent_anzahl >= 50:
            user.pruefungen_bestanden += 1
            user.pruefungen_total += 1
        else:
            user.pruefungen_total += 1
            
        user.stat_pruefungen.append([prozent_anzahl, current_datetime()])
        
        noten_label = ttk.Label(prüfungs_frame, text=(f"Deine Note beträgt: {note}"))
        noten_label.pack(pady=100)

# Funktion: prüffrage_überprüfen
# Überprüft die abgegebene Antwort im Prüfungsmodus und aktualisiert die Benutzerstatistik.
# Benötigt:
#   auswahl: Variable mit gewählter Antwort
#   aktuelle_frage: Das aktuelle Frage-Objekt
#   prüfungs_frame: Frame des Prüfungsmodus
#   frage_index: Index der aktuellen Frage
#   prüfungsfragen: Liste der Prüfungsfragen
#   falsche_Prüfungsfragen: Zähler für falsche Antworten
def prüffrage_überprüfen(auswahl, aktuelle_frage, prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen):

    if aktuelle_frage.antwort == auswahl.get():
        user.fragen_richtig += 1
        user.fragen_total += 1
        user.stat_fragen_richtig.append([aktuelle_frage.id, current_datetime()])

        if aktuelle_frage.id in user.fragen_falsch:     
             user.fragen_falsch.remove(aktuelle_frage.id)
    else:
        user.fragen_total += 1
        user.stat_fragen_falsch.append([aktuelle_frage.id, current_datetime()])
        if aktuelle_frage.id not in user.fragen_falsch:
            user.fragen_falsch.append(aktuelle_frage.id)
        falsche_Prüfungsfragen += 1

    user.save()

    frage_index += 1

    zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen)    

# Funktion: Lernmodus
# Initialisiert den Lernmodus, bei dem der Benutzer alle oder nur falsche Fragen wiederholen kann.
def Lernmodus():
    clear_inhalt()

    # Auswahl anzeigen
    wahl_var = tk.BooleanVar(value=True)

    button_rahmen = ttk.LabelFrame(inhalt_frame, text="Lernmodus Auswahl")
    button_rahmen.place(x=60, y=150)

    label = ttk.Label(button_rahmen, text="Welche Fragen möchtest du lernen?", font=("arial", 12, "bold"))
    label.grid(column=0, row=0, columnspan=2, pady=(10, 20), padx=10)

    gesamtfragen_btn = ttk.Radiobutton(button_rahmen, text="Alle Fragen lernen", variable=wahl_var, value=True)
    gesamtfragen_btn.grid(column=0, row=1, sticky=(tk.W), padx=10, pady=5)

    falsche_fragen_btn = ttk.Radiobutton(button_rahmen, text="Nur falsche Fragen wiederholen", variable=wahl_var, value=False)
    falsche_fragen_btn.grid(column=0, row=2, sticky=(tk.W), padx=10, pady=5)

    weiter_btn = ttk.Button(button_rahmen, text="Weiter", command=lambda: starte_fragen(wahl_var.get()))
    weiter_btn.grid(column=0, row=3, pady=20, padx=10)

# Funktion: starte_fragen
# Startet den Ablauf des Lernmodus, indem die Auswahl der Fragen getroffen und zufällig gemischt wird.
# Benötigt:
#   wahl: Boolean, ob alle Fragen oder nur falsche Fragen geübt werden sollen
def starte_fragen(wahl):
    clear_inhalt()

    prüfungs_frame = ttk.Frame(inhalt_frame)
    prüfungs_frame.pack(fill="both", expand=True)

    if wahl:
        
        fragen = get_fragen(cur)

        if len(fragen) >= 1:
            fragen = get_fragen(cur)
        else:
            Fehler_label = ttk.Label(prüfungs_frame,
                                    text="Fehler! Es gibt nicht genug Fragen. Importieren sie welche, oder wenden sie sich einen Administrator!")
            Fehler_label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

            weiterleit_Btn = ttk.Button(prüfungs_frame,
                                        text="Fragen Importieren",
                                        command=lambda: Admin())
            weiterleit_Btn.grid(row=2, column=0, pady=50)
    else:
        alle_fragen = get_fragen(cur)
        fragen = []
        for frage in alle_fragen:
            if frage.id in user.fragen_falsch:
                fragen.append(frage)

    random.shuffle(fragen)

    frage_index = 0

    zeige_frage(fragen, prüfungs_frame, frage_index)
    
# Frage, Prüfungs Frame, Fragen index | auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame, alle_fragen
# Hier werden die Fragen angezeigt und überprüft ob alle Fragen schonmal dran waren
def zeige_frage(fragen, prüfungs_frame, frage_index):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    auswahl = tk.StringVar(value="X")

    alle_fragen = len(fragen)

    if frage_index < alle_fragen:

        aktuelle_frage = fragen[frage_index]

        auswahl = tk.StringVar(value="X")

        progress = tk.IntVar(value=frage_index + 1)  # Fortschritt aktualisieren
        progressbar = ttk.Progressbar(prüfungs_frame, maximum=alle_fragen, variable=progress, length=400)
        progressbar.grid(row=0, column=0, padx=40, pady=5)  

        Fortschirt_label = ttk.Label(prüfungs_frame, text=f"Du bist bei Frage {frage_index +1} von {alle_fragen}")
        Fortschirt_label.grid(row=2, column=0) 

        Frage_label = ttk.Label(prüfungs_frame, text=aktuelle_frage.frage)
        Frage_label.grid(row=3, column=0, pady=40)  

        button_rahmen = ttk.LabelFrame(prüfungs_frame)
        button_rahmen.grid(row=4, column=0, padx=40, pady=5)

        frageA = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.A, variable=auswahl, value="A")
        frageA.grid(row=0, column=0, pady=10, padx=20)

        frageB = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.B, variable=auswahl, value="B")
        frageB.grid(row=1, column=0, pady=10, padx=20)

        frageC = ttk.Radiobutton(button_rahmen, text=aktuelle_frage.C, variable=auswahl, value="C")
        frageC.grid(row=2, column=0, pady=10, padx=20)

        submit_btn = ttk.Button(prüfungs_frame,text="Antwort absenden",command=lambda: frage_überprüfen(auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame))
        submit_btn.grid(row=5, column=0)
        
        def wirklich_Startseite():
            if messagebox.askyesno("Zurück zur Startseite", "Möchtest du wirklich zur Startseite zurückkehren?"):
                Startseite()

        Startbtn = ttk.Button(prüfungs_frame, text="Startseite", command=wirklich_Startseite)
        Startbtn.grid(row=10, column=0, pady=20)
        
    else: # Wenn alle Fragen beantwortet wurden, wird ein Rahmen mit der Option angezeigt, was als nächstes getan werden soll
        fertig_rahmen = ttk.LabelFrame(prüfungs_frame, text="Was möchtest du als Nächstes tun?")
        fertig_rahmen.pack(pady=50, padx=20)

        fertig_label = ttk.Label(fertig_rahmen, text="Herzlichen Glückwunsch!\nDu hast alle Fragen beantwortet!", font=("arial", 14, "bold"))
        fertig_label.grid(column=0, row=0, columnspan=2, pady=(10, 20))

        statbtn = ttk.Button(fertig_rahmen, text="Zurück zur Startseite", command=Menu)
        statbtn.grid(column=0, row=1, padx=10, pady=10)

        wiederholenbtn = ttk.Button(fertig_rahmen, text="Nochmal alle Fragen durchgehen", command=lambda: Lernmodus())
        wiederholenbtn.grid(column=1, row=1, padx=10, pady=10)

# Funktion: frage_überprüfen
# Überprüft die Antwort einer Frage im Lernmodus und gibt entsprechendes Feedback.
# Benötigt:
#   auswahl: Variable mit gewählter Antwort
#   aktuelle_frage: Das aktuelle Frage-Objekt
#   fragen: Liste der Fragen
#   frage_index: Index der aktuellen Frage
#   prüfungs_frame: Frame, in dem geprüft wird
def frage_überprüfen(auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()
        
    if aktuelle_frage.antwort == auswahl.get():

        r_label = ttk.Label(prüfungs_frame, text="Das war Richtig!")
        r_label.pack(pady=50)
        user.fragen_richtig += 1
        user.fragen_total += 1
        user.stat_fragen_richtig.append([aktuelle_frage.id, current_datetime()])

        if aktuelle_frage.id in user.fragen_falsch:
            user.fragen_falsch.remove(aktuelle_frage.id)
    else:
        f_antwort = ttk.Label(prüfungs_frame, text="Die Antwort war nicht richtig! Die Richtige Antwort ist:")
        f_antwort.pack(pady=50)

        richtige_antwort_text = getattr(aktuelle_frage, aktuelle_frage.antwort)
        l_antwort = ttk.Label(prüfungs_frame, text=richtige_antwort_text)
        l_antwort.pack(pady=10)
        user.fragen_total += 1
        user.stat_fragen_falsch.append([aktuelle_frage.id, current_datetime()])
        if aktuelle_frage.id not in user.fragen_falsch:
            user.fragen_falsch.append(aktuelle_frage.id)

    frage_index += 1
    
    user.save()
    
    weiter_btn = ttk.Button(prüfungs_frame, text="Weiter", command=lambda: zeige_frage(fragen, prüfungs_frame, frage_index))
    weiter_btn.pack(pady=20)

# Funktion: Startseite
# Zeigt die Startseite an, entweder mit Login/Registrierungsoption oder als Menü, wenn ein Benutzer angemeldet ist.
def Startseite():
    if user.user_id == 0:
        clear_inhalt()
        start_frame = ttk.Frame(inhalt_frame)
        start_frame.pack(fill="both", expand=True)
        label = ttk.Label(start_frame, text="Willkommen\nzum Prüfungstrainer!", font=("arial", 30, "bold"))
        label.place(x=0, y=0)

        button_rahmen = ttk.LabelFrame(start_frame, text="Benutzerzugang")
        button_rahmen.place(x=170, y=180)

        Loginbtn = ttk.Button(button_rahmen, text="Login", command=Guilogin)
        Loginbtn.pack(pady=20, padx=40)
        
        Registerbtn = ttk.Button(button_rahmen, text="Registrieren", command=Guiregister)
        Registerbtn.pack(pady=20, padx=40)
    else:
        Menu()

# Funktion: Menu
# Zeigt das Hauptmenü nach erfolgreicher Anmeldung mit verschiedenen Optionen (Lernmodus, Prüfung, Statistik, Adminbereich).
def Menu():
    clear_inhalt()
    menu_frame = ttk.Frame(inhalt_frame)

    button_rahmen = ttk.LabelFrame(inhalt_frame, text="Auswahl")
    button_rahmen.place(x=60, y=150)

    menu_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W)) # type: ignore
    label = ttk.Label(button_rahmen, text="Willkommen!\nIm Prüfungstrainer\nWie möchtest du fortfahren?", font=("arial", 15, "bold"))
    label.grid(column=0, row=0, columnspan=3, sticky=(tk.N), padx=5, pady=5)
    
    Lernbtn = ttk.Button(button_rahmen, text="Weiterlernen", command=Lernmodus)
    Lernbtn.grid(column=0, row=1, sticky=(tk.S, tk.W), padx=5, pady=10) # type: ignore

    Prüfungsbtn = ttk.Button(button_rahmen, text="Zur Prüfungssimulation", command=Prüfungsmodus)
    Prüfungsbtn.grid(column=1, row=1, sticky=(tk.S), padx=5, pady=10)
    
    Statistikbtn = ttk.Button(button_rahmen, text="Statistik", command=Statistik)
    Statistikbtn.grid(column=2, row=1, sticky=(tk.E), padx=5, pady=10)
    
    if user.is_admin == 1:
        Adminbtn = ttk.Button(button_rahmen, text="Adminbereich", command=Admin)
        Adminbtn.grid(column=3, row=1, sticky=(tk.S, tk.E), padx=5, pady=10) # type: ignore

# Funktion: Statistik
# Zeigt die Statistik des Benutzers an, z. B. Anzahl der beantworteten Fragen und falscher Fragen.
def Statistik():
    clear_inhalt()
    statistik_frame = ttk.Frame(inhalt_frame)
    statistik_frame.pack(fill="both", expand=True)
    
    label = ttk.Label(statistik_frame, text="Statistiken", font=("arial", 15, "bold"))
    label.grid(column=0, row=0, sticky=(tk.N))
    
    text = ttk.Label(statistik_frame, text="Fragen Beantwortet insgesamt:", padding=(5,5,10,10))
    text.grid(column=0, row=1, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(statistik_frame, text=user.fragen_total, padding=(5,5,10,10))
    text.grid(column=1, row=1, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(statistik_frame, text="Fragen Beantwortet Falsch:", padding=(5,5,10,10))
    text.grid(column=0, row=2, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(statistik_frame, text=len(user.fragen_falsch), padding=(5,5,10,10))
    text.grid(column=1, row=2, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(statistik_frame, text="Fragen Beantwortet Richtig:", padding=(5,5,10,10))
    text.grid(column=0, row=3, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(statistik_frame, text=user.fragen_richtig, padding=(5,5,10,10))
    text.grid(column=1, row=3, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(statistik_frame, text="Falsche Fragen:", padding=(5,5,10,10))
    text.grid(column=0, row=4)
    
    i = 5
    fragen = get_fragen(cur)
    for item in user.stat_fragen_falsch:
        text = ttk.Label(statistik_frame, text=f"Uhrzeit: {item[1]} Frage: {fragen[item[0]].frage}")
        text.grid(column=0, row=i, columnspan=2, sticky=(tk.W))
        i += 1

# Funktion: Guilogin
# Zeigt das Login-Fenster an und verarbeitet die Benutzereingaben für die Anmeldung.
def Guilogin():
    clear_inhalt()
    login_frame = ttk.Frame(inhalt_frame)
    login_frame.pack(fill="both", expand=True)
    label = ttk.Label(login_frame, text="Loginbereich", font=("arial", 30, "bold"))
    label.pack(pady=100)
    
    button_rahmen = ttk.LabelFrame(login_frame, text="Anmelden")
    button_rahmen.place(x=170, y=180)

    ttk.Label(button_rahmen, text="Benutzername:").pack(pady=(10, 0))
    username_entry = ttk.Entry(button_rahmen)
    username_entry.pack(pady=0)
    
    ttk.Label(button_rahmen, text="Passwort:").pack(pady=(10, 0))
    password_entry = ttk.Entry(button_rahmen, show="*")
    password_entry.pack(pady=0)
    
    def handle_login():
        username = username_entry.get()
        pw_hash = hashlib.sha256(password_entry.get().encode()).hexdigest()
        if login(cur, username, pw_hash):
            Menu()
            return
        else:
            messagebox.showerror("Login fehlgeschlagen", "Benutzername oder Passwort ist falsch.")
    
    loginbtn = ttk.Button(button_rahmen, text="Login", command=handle_login)
    loginbtn.pack(pady=20, padx=40)
    
    # Register-Button außerhalb des Rahmens
    register_label = ttk.Button(login_frame, text="Noch kein Konto?", command=Guiregister)
    register_label.place(x=185, y=390) 

# Funktion: Guiregister
# Zeigt das Registrierungsfenster an und verarbeitet die Eingaben, um einen neuen Benutzer anzulegen.
def Guiregister():
    clear_inhalt()
    register_frame = ttk.Frame(inhalt_frame)
    register_frame.pack(fill="both", expand=True)

    button_rahmen = ttk.LabelFrame(register_frame, text="Registrierung")
    button_rahmen.place(x=100, y=100)

    label = ttk.Label(button_rahmen, text="Benutzerkonto erstellen", font=("arial", 15, "bold"))
    label.grid(column=0, row=0, columnspan=2, pady=(10, 20), padx=10)

    ttk.Label(button_rahmen, text="Benutzername:").grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
    username_entry = ttk.Entry(button_rahmen)
    username_entry.grid(column=1, row=1, padx=10, pady=5)

    ttk.Label(button_rahmen, text="Passwort:").grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
    password_entry = ttk.Entry(button_rahmen, show="*")
    password_entry.grid(column=1, row=2, padx=10, pady=5)

    is_admin = tk.IntVar()
    ttk.Label(button_rahmen, text="Adminrechte:").grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
    is_admin_entry = ttk.Checkbutton(button_rahmen, text="Admin", variable=is_admin)
    is_admin_entry.grid(column=1, row=3, padx=10, pady=5)

    def handle_register():
        username = username_entry.get()
        pw_hash = hashlib.sha256(password_entry.get().encode()).hexdigest()
        add_user(con, cur, is_admin.get(), username, pw_hash)
        messagebox.showinfo("Erfolg", f"Benutzer erfolgreich registriert. Ihr Benutzername lautet: {username}")
        Guilogin()
        
    registerbtn = ttk.Button(button_rahmen, text="Registrieren", command=handle_register)
    registerbtn.grid(column=0, row=4, columnspan=2, pady=20)
    
    loginbtn = ttk.Button(register_frame, text="Bereits registriert?", command=Guilogin)
    loginbtn.place(x=175, y=370)
    
# Funktion: Admin
# Zeigt den Adminbereich an, in dem Fragen verwaltet (hinzufügen, importieren, bearbeiten, exportieren, löschen) werden können.
def Admin():
    if user.user_id == 0: # Ist der User nicht angemeldet, wird er zurück zur Startseite geschickt
        Startseite()
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich als Admin an, um den Adminbereich zu nutzen.")
        return
    elif user.is_admin != 1: # Ist der User kein Admin, wird er nicht weitergeleitet und erhält eine Fehlermeldung
        messagebox.showerror("Keine Admin-Berechtigung", "Bitte melden Sie sich mit einem Admin-Konto an, um den Adminbereich zu nutzen.")
        return
    clear_inhalt()

    admin_frame = ttk.Frame(inhalt_frame) # Admin Frame wird erstellt
    admin_frame.pack(fill="both", expand=True)
    label = ttk.Label(admin_frame, text="Adminbereich", font=("arial", 30, "bold")) # Admin Label wird erstellt
    label.pack(pady=40)
    button_rahmen = ttk.LabelFrame(admin_frame, text="Fragenverwaltung")
    button_rahmen.pack(pady=20, padx=20)

    # Buttons für die Fragenverwaltung
    # Frage einzeln einfügen, Fragen importieren, Fragen exportieren, Fragen löschen
    fragen_add = ttk.Button(button_rahmen, text="Frage hinzufügen", command=lambda: manuell_fragen(con, cur))
    fragen_add.grid(column=0, row=0, padx=10, pady=10)
    fragen_import = ttk.Button(button_rahmen, text="Fragen importieren", command=lambda: import_fragen(con, cur, openfile()))
    fragen_import.grid(column=1, row=0, padx=10, pady=10)
    fragen_edit = ttk.Button(button_rahmen, text="Fragen bearbeiten", command=lambda: edit_fragen(con, cur))
    fragen_edit.grid(column=0, row=1, padx=10, pady=10)

    fragen_export = ttk.Button(button_rahmen, text="Fragen exportieren", command=lambda: export_fragen(cur))
    fragen_export.grid(column=1, row=1, padx=10, pady=10)
    fragen_delete = ttk.Button(button_rahmen, text="Fragen löschen", command=lambda: del_frage(con, cur))
    fragen_delete.grid(column=0, row=2, padx=10, pady=10)
    
    Startbtn = ttk.Button(admin_frame, text="Startseite", command=Startseite)
    Startbtn.pack(pady=20)

# Funktion: login
# Überprüft die Anmeldedaten eines Benutzers und lädt die zugehörigen Daten, falls diese korrekt sind.
# Benötigt:
#   cur: Datenbankcursor
#   username: Eingebener Benutzername
#   pw_hash: Eingebener Passwort-Hash
def login(cur, username, pw_hash):
    userdata = cur.execute("SELECT * FROM userdata").fetchall()
    for data in userdata:
        data_username = data[2]
        data_pw_hash = data[3] 
        if data_username == username and data_pw_hash == pw_hash:
            user.user_id = data[0]
            user.is_admin = data[1]
            user.pw_hash = pw_hash
            user.username = username
            if data[5] != None:
                user.fragen_richtig = data[5]
            else:
                user.fragen_richtig = 0
            if data[4] != None:
                user.fragen_total = data[4]
            else:
                user.fragen_total = 0
            if data[6] != None:
                user.fragen_falsch = json.loads(data[6])
            if data[7] != None:
                user.stat_fragen_richtig = json.loads(data[7])
            if data[8] != None:
                user.stat_fragen_falsch = json.loads(data[8])
            if data[9] != None:
                user.pruefungen_total = data[9]
            if data[10] != None:
                user.pruefungen_bestanden = data[10]
            if data[11] != None:
                user.stat_pruefungen = json.loads(data[11])
            return True
    return False

# Funktion: abmelden
# Meldet den aktuellen Benutzer ab, setzt das user-Objekt zurück und zeigt die Startseite an.
def abmelden():
    global user
    if user.user_id != 0:
        user = User(0, 0, 0, 0, 0, 0)
        Startseite()
        messagebox.showinfo("Abmeldung", "Sie wurden erfolgreich abgemeldet.")
    else:
        messagebox.showwarning("Abmeldung nicht möglich", "Sie sind nicht angemeldet.")

class Frage:
    # __init__: Initialisiert ein Frage-Objekt.
    # Benötigt:
    #   id: Eindeutige Identifikation der Frage
    #   frage: Fragetext
    #   A, B, C: Antwortoptionen
    #   antwort: Richtige Antwort
    #   kategorie: Optionale Kategorie (Standard "default")
    def __init__(self, id, frage, A, B, C, antwort, kategorie="default"):
        self.id = id
        self.frage = frage
        self.A = A
        self.B = B
        self.C = C
        self.antwort = antwort
        self.kategorie = kategorie
        self.delete = tk.BooleanVar()
    
    # gebe nur ID aus wenn mit repr(Frage) gecallt für Debug 
    def __repr__(self):
        return f"\"ID: {self.id}\""
    
    # export: Gibt ein Dictionary mit Frageinformationen zurück, geeignet für JSON-Export.
    def export(self):
        return {
            "frage" : self.frage,
            "A" : self.A,
            "B" : self.B,
            "C" : self.C,
            "richtigeAntwort" : self.antwort,
            "kategorie" : self.kategorie
            }
    
class User:
    # __init__: Initialisiert ein User-Objekt.
    # Benötigt:
    #   user_id, is_admin, username, pw_hash, fragen_total, fragen_richtig
    def __init__(self, user_id, is_admin, username, pw_hash, fragen_total, fragen_richtig):
        self.user_id = user_id
        self.is_admin = is_admin
        self.username = username
        self.pw_hash = pw_hash
        self.fragen_total = fragen_total        # anzahl insgesamt beantworteter Fragen
        self.fragen_richtig = fragen_richtig    # anzahl richtig beantworteter Fragen
        self.fragen_falsch = []
        self.stat_fragen_falsch = []            # nur für Statistiken
        self.stat_fragen_richtig = []           # nur für Statistiken
        self.pruefungen_total = 0
        self.pruefungen_bestanden = 0
        self.stat_pruefungen = []               # Liste [Note, Datum+Uhrzeit] Index 0 von dieser liste = erste Prüfung
    
    # Speicher aktuellen Datenstand in die Datenbank 
    def save(self):
        save_statement = "UPDATE userdata SET fragen_total = ?, fragen_richtig = ?, fragen_falsch = ?, stat_fragen_richtig = ?, stat_fragen_falsch = ?, pruefungen_total = ?, pruefungen_bestanden = ?, stat_pruefungen = ? WHERE user_id = ?"
        cur.execute(save_statement, (self.fragen_total, 
                                     self.fragen_richtig, 
                                     json.dumps(self.fragen_falsch, indent=None), 
                                     json.dumps(self.stat_fragen_richtig, indent=None), 
                                     json.dumps(self.stat_fragen_falsch),
                                     self.pruefungen_total,
                                     self.pruefungen_bestanden,
                                     json.dumps(self.stat_pruefungen), 
                                     self.user_id))
        con.commit()
        
# Funktion: main
# Startet die Anwendung, initialisiert den Benutzer und die GUI, und öffnet die Datenbank.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
def main(con, cur):
    # Benutzer Initialisieren
    global user
    user = User(0, 0, 0, 0, 0, 0)
    
    # Tastenkürzel
    root.bind("<Escape>", end_fullscreen)
    root.bind("<F11>", toggle_fullscreen)

    # Menü
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Startseite", command=Startseite)
    file_menu.add_command(label="Adminbereich", command=Admin)
    file_menu.add_command(label="Prüfungsmodus", command=Prüfungsmodus)
    file_menu.add_separator()
    file_menu.add_command(label="Abmelden", command=abmelden)
    file_menu.add_command(label="Beenden", command=root.quit)
    menubar.add_cascade(label="Datei", menu=file_menu)

    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="Dark Mode", command=lambda: root.set_theme("equilux"))
    theme_menu.add_command(label="Light Mode", command=lambda: root.set_theme("scidgreen"))
    theme_menu.add_command(label="Holz Mode", command=lambda: root.set_theme("kroc"))
    menubar.add_cascade(label="Theme", menu=theme_menu)

    root.config(menu=menubar)
    # Startansicht
    Startseite()

    # Gui öffnen
    root.mainloop()
    
if __name__ == "__main__":
    try:
        with sqlite3.connect(db_name) as con:
            cur = con.cursor()

            for statement in sql_statements:
                cur.execute(statement)

            con.commit()

            main(con, cur)

        sys.exit(0)
    except sqlite3.OperationalError as e:
        print(f"Failed to Open Database: {e}")
        sys.exit(1)
