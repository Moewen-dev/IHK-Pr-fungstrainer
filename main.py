import sqlite3, sys, json, random, hashlib, datetime
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    fragen_richtig INT,
    fragen_falsch TEXT,
    stat_fragen_richtig TEXT,
    stat_fragen_falsch TEXT,
    pruefungen_total INT,
    pruefungen_bestanden INT,
    stat_pruefungen TEXT,
    alzeit_fragen_falsch,
    alzeit_fragen_richtig);"""]

# Datenbank Dateiname
db_name = "data.db"

# Funktion: add_frage
# Fügt eine neue Frage in die Datenbank ein.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
#   frage: Text der Frage
#   A, B, C: Antwortmöglichkeiten
#   antwort: Richtige Antwort (als Identifier, z.B. "A")
#   kategorie: Optionale Kategorie (Standard "default")
def add_frage(con, cur, frage, A, B, C, antwort, kategorie="default"):  # default kategorie falls keine spezifiziert
    # Frage in die Datenbank hinzufügen
    cur.execute("INSERT INTO fragen (frage, A, B, C, antwort, kategorie) VALUES (?, ?, ?, ?, ?, ?)", (frage, A, B, C, antwort, kategorie))
    con.commit()
    log(f"Frage in Datenbank hinzugefügt: {frage}")

# Funktion: get_fragen
# Ruft alle Fragen aus der Datenbank ab und wandelt sie in Frage-Objekte um.
# Benötigt:
#   cur: Datenbankcursor
# Gibt zurück:
#   fragen: Eine Liste von Frage-Objekten
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
# Importiert Fragen aus einer JSON-Datei in die Datenbank. Es werden nur Fragen hinzugefügt,
# die noch nicht anhand ihres Fragetextes in der Datenbank vorhanden sind.
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

        messagebox.showinfo("Erfolg", 'Fragen wurden erfolgreich Importiert!') # MessageBox nach erfolgreichem Fragenimport
        log(f"Fragen aus {filename} erfolgreich importiert")
    except TypeError as e:
        print(f"Error: {e}")
        messagebox.showinfo("Fehler", 'Fragen wurden nicht Importiert!\n\nPrüfe ob die .json Datei dem korrekten Format entspricht!') # MessageBox wenn import Fehlgeschlagen
        log(f"Fragen aus {filename} konnten nicht importiert werden", 2)

# Funktion: export_fragen
# Exportiert alle Fragen aus der Datenbank in eine JSON-Datei namens "fragen_export.json".
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
            log(f"Fragen in fragen_export.json exportiert")
        except:
            messagebox.showerror("Fragen export", "Fragen export nicht erfolgreich")
            log(f"Fragen export nicht erfolgreich", 2)
    else:
        Admin()

# Funktion: manuell_fragen
# Öffnet ein neues Fenster (Toplevel), um eine einzelne Frage manuell mit ihren Antworten und Kategorie
# einzugeben und in die Datenbank zu speichern.
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

    # Kategorie (nur Eingabefeld, eventuell später als Dropdown?)
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
# Öffnet ein Fenster (Toplevel) zur Bearbeitung existierender Fragen.
# Zeigt eine Liste aller Fragen an. Durch Klick auf eine Frage öffnet sich ein weiteres Fenster
# zur Bearbeitung der ausgewählten Frage.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
def edit_fragen(con, cur):
    edit_window = tk.Toplevel(bg="#d8d8d8")
    edit_window.title("Fragen bearbeiten")
    edit_window.geometry("500x600")

    header = ttk.Label(
        edit_window,
        text="Klicke auf eine Frage, um sie zu bearbeiten:",
        font=("Arial", 12, "bold"),
        background="#d8d8d8"
    )
    header.pack(pady=10)

    # Container
    container = ttk.Frame(edit_window)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    # Canvas + Scrollbar
    canvas = tk.Canvas(container, background="#d8d8d8", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = ttk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # Events & Scrollhandling
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scroll_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    scroll_frame.bind("<Enter>", lambda e: scroll_frame.bind_all("<MouseWheel>", _on_mousewheel))
    scroll_frame.bind("<Leave>", lambda e: scroll_frame.unbind_all("<MouseWheel>"))


    # Frage-Bearbeitungsfenster
    # Öffnet ein neues Fenster (Toplevel) zum Bearbeiten der übergebenen Frage.
    # Benötigt:
    #   frage: Das zu bearbeitende Frage-Objekt
    #   edit_window: Das übergeordnete Fenster, das geschlossen wird
    def frage_bearbeiten_fenster(frage, edit_window):
        edit_window.destroy()

        frage_edit = tk.Toplevel()
        frage_edit.title("Frage bearbeiten")
        frage_edit.geometry("500x500")

        eingabe_rahmen = ttk.LabelFrame(frage_edit, text="Frage bearbeiten")
        eingabe_rahmen.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(eingabe_rahmen, text="Frage:").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
        frage_entry = ttk.Entry(eingabe_rahmen, width=50)
        frage_entry.insert(0, frage.frage)
        frage_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

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

        # Kategorie
        ttk.Label(eingabe_rahmen, text="Kategorie:").grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
        kat_entry = ttk.Entry(eingabe_rahmen, width=50)
        kat_entry.insert(0, frage.kategorie)
        kat_entry.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Speichert die geänderten Fragendetails in der Datenbank.
        def speichern():
            neue_frage = frage_entry.get()
            neue_A = a_entry.get()
            neue_B = b_entry.get()
            neue_C = c_entry.get()
            neue_antwort = antwort_var.get()
            neue_kat = kat_entry.get()

            cur.execute("""
                UPDATE fragen
                SET frage = ?, A = ?, B = ?, C = ?, antwort = ?, kategorie = ?
                WHERE id = ?
            """, (neue_frage, neue_A, neue_B, neue_C, neue_antwort, neue_kat, frage.id))
            con.commit()

            messagebox.showinfo("Erfolg", f'Frage "{neue_frage}" erfolgreich aktualisiert.')
            log(f"Frage {neue_frage} aktualisiert")
            frage_edit.destroy()

            if messagebox.askyesno("Bestätigung", "Möchtest du weitere Fragen bearbeiten?"):
                edit_fragen(con, cur)

        speichern_btn = ttk.Button(frage_edit, text="Änderungen speichern", command=speichern)
        speichern_btn.pack(pady=20)

    # Fragen aus DB anzeigen
    fragen = get_fragen(cur)

    if not fragen:
        ttk.Label(scroll_frame, text="Keine Fragen in der Datenbank.", foreground="red").pack(pady=20)
        return

    for frage in fragen:
        try:
            text = frage.frage.strip()
            if len(text) > 80:
                text = text[:77] + "..."

            btn = ttk.Button(scroll_frame, text=text, command=lambda f=frage: frage_bearbeiten_fenster(f, edit_window))
            btn.pack(fill="x", padx=10, pady=5)
        except Exception as e: # Fehler beim Anzeigen einer Frage
            print(f"Fehler beim Anzeigen einer Frage: {e}")
            log(f"Anzeigefehler einer Frage: {e}")


# Funktion: del_frage
# Öffnet ein Fenster (Toplevel), in dem Fragen aus einer Liste ausgewählt und gelöscht werden können.
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
    
    # Container
    container = ttk.Frame(del_window)
    container.pack(fill="both", expand=True, padx=10, pady=10)

    # Canvas + Scrollbar
    canvas = tk.Canvas(container, background="#d8d8d8", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scroll_frame = ttk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    # Events & Scrollhandling
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scroll_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    scroll_frame.bind("<Enter>", lambda e: scroll_frame.bind_all("<MouseWheel>", _on_mousewheel))
    scroll_frame.bind("<Leave>", lambda e: scroll_frame.unbind_all("<MouseWheel>"))

    fragen = get_fragen(cur)
    for frage in fragen:
        checkbox = ttk.Checkbutton(scroll_frame, text=frage.frage, variable=frage.delete)
        checkbox.pack(anchor="w", padx=10, pady=5)

    # Löscht die ausgewählten Fragen aus der Datenbank.
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
            log(f"Frage mit ID {frage.id} gelöscht")

        con.commit()
        messagebox.showinfo("Erfolg", "Ausgewählte Fragen wurden gelöscht.")
        del_window.destroy()

    ttk.Button(del_window, text="Ausgewählte Fragen löschen", command=delete_selected).pack(pady=15)

# Funktion: add_user
# Fügt einen neuen Benutzer mit Admin-Status, Benutzernamen und Passwort-Hash in die Datenbank ein.
# Benötigt:
#   con: Datenbankverbindung
#   cur: Datenbankcursor
#   is_admin: Integer (0 oder 1), der angibt, ob der Benutzer Adminrechte hat
#   username: Der Benutzername des neuen Benutzers
#   pw_hash: Der gehashte Passwortstring des neuen Benutzers
def add_user(con, cur, is_admin, username, pw_hash):
    cur.execute("INSERT INTO userdata (is_admin, username, pw_hash) VALUES (?, ?, ?)", (is_admin, username, pw_hash))
    con.commit()
    log(f"Benutzer {username} erstellt. Admin {is_admin}")

# Funktion: konto_einstellungen
# Zeigt die Kontoeinstellungen für den angemeldeten Benutzer an.
# Ermöglicht das Ändern des Passworts, des Benutzernamens oder das Löschen des Kontos.
# Leitet zur Startseite weiter, wenn kein Benutzer angemeldet ist.
def konto_einstellungen():
    if user.user_id == 0:
        Startseite()
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich an, um Ihre Kontoeinstellungen zu ändern.")
        return

    clear_inhalt()
    konto_frame = ttk.Frame(inhalt_frame)
    konto_frame.pack(fill="both", expand=True)

    # Titel der Seite
    ttk.Label(konto_frame, text="Kontoeinstellungen", font=("arial", 30, "bold")).pack(pady=40)

    # Benutzerinfo-Rahmen (enthält Benutzernamen)
    benutzerinfo_rahmen = ttk.LabelFrame(konto_frame, text="Benutzerinfo")
    benutzerinfo_rahmen.pack(pady=10, padx=20)

    benutzername_label = ttk.Label(benutzerinfo_rahmen, font=("Arial", 10))
    benutzername_label.pack(padx=10, pady=10)

    # Funktion zur Aktualisierung der Benutzeranzeige
    # Aktualisiert das Label, das den angemeldeten Benutzernamen anzeigt.
    def aktualisiere_kontoinformationen():
        benutzername_label.config(text=f"Angemeldet als: {user.username}")

    aktualisiere_kontoinformationen() # Ruft die Aktualisierung der Kontoinformationen auf

    # Fenster für Passwortänderung
    # Öffnet ein neues Fenster (Toplevel) zur Änderung des Benutzerpassworts.
    def open_change_password_window():
        win_change_pw = tk.Toplevel()
        win_change_pw.title("Passwort ändern")
        win_change_pw.geometry("500x600")

        frame = ttk.Frame(win_change_pw)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Passwort ändern", font=("arial", 30, "bold")).pack(pady=40)

        form_frame = ttk.LabelFrame(frame, text="Neues Passwort")
        form_frame.pack(pady=20, padx=20)

        ttk.Label(form_frame, text="Neues Passwort:").grid(row=0, column=0, padx=10, pady=5)
        new_pw_entry = ttk.Entry(form_frame, show="*")
        new_pw_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Neues Passwort bestätigen:").grid(row=1, column=0, padx=10, pady=5)
        confirm_pw_entry = ttk.Entry(form_frame, show="*")
        confirm_pw_entry.grid(row=1, column=1, padx=10, pady=5)

        def handle_change_password(): # Funktion zum Verarbeiten der Passwortänderung
            new_pw = new_pw_entry.get()
            confirm_pw = confirm_pw_entry.get()
            if not new_pw:
                messagebox.showerror("Fehler", "Das Passwort darf nicht leer sein.", parent=win_change_pw)
                return
            if new_pw != confirm_pw:
                messagebox.showerror("Fehler", "Die Passwörter stimmen nicht überein.", parent=win_change_pw)
                return
            new_pw_hash = hashlib.sha256(new_pw.encode()).hexdigest()
            update_password(con, cur, user.user_id, new_pw_hash)
            messagebox.showinfo("Erfolg", "Passwort erfolgreich geändert.", parent=win_change_pw)
            win_change_pw.destroy()

        # Hilfsfunktion zum Aktualisieren des Passwort-Hashes in der Datenbank.
        # Benötigt:
        #   con: Datenbankverbindung
        #   cur: Datenbankcursor
        #   user_id: ID des Benutzers, dessen Passwort geändert wird
        #   pw_hash: Der neue Passwort-Hash
        def update_password(con, cur, user_id, pw_hash):
            cur.execute("UPDATE userdata SET pw_hash = ? WHERE user_id = ?", (pw_hash, user_id))
            con.commit()
            log(f"Passwort für {user.username} mit ID {user_id} geändert")

        ttk.Button(form_frame, text="Passwort ändern", command=handle_change_password).grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        ttk.Button(frame, text="Abbrechen", command=win_change_pw.destroy).pack(pady=10)

    # Fenster für Benutzername-Änderung
    # Öffnet ein neues Fenster (Toplevel) zur Änderung des Benutzernamens.
    def open_change_username_window():
        win_change_user = tk.Toplevel()
        win_change_user.title("Benutzername ändern")
        win_change_user.geometry("500x600")

        frame = ttk.Frame(win_change_user)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Benutzername ändern", font=("arial", 30, "bold")).pack(pady=40)

        form_frame = ttk.LabelFrame(frame, text="Neuer Benutzername")
        form_frame.pack(pady=20, padx=20)

        ttk.Label(form_frame, text="Neuer Benutzername:").grid(row=0, column=0, padx=10, pady=5)
        new_username_entry = ttk.Entry(form_frame)
        new_username_entry.grid(row=0, column=1, padx=10, pady=5)

        def handle_change_username(): # Funktion zum Verarbeiten der Benutzernamen-Änderung
            new_username = new_username_entry.get().strip()
            if not new_username:
                messagebox.showerror("Fehler", "Der Benutzername darf nicht leer sein.", parent=win_change_user)
                return
            if username_exists(cur, new_username):
                messagebox.showerror("Fehler", "Dieser Benutzername ist bereits vergeben.", parent=win_change_user)
                return
            update_username(con, cur, new_username)
            user.username = new_username  # Benutzerobjekt aktualisieren
            aktualisiere_kontoinformationen()  # Anzeige aktualisieren
            messagebox.showinfo("Erfolg", f"Benutzername erfolgreich zu \"{new_username}\" geändert.", parent=win_change_user)
            win_change_user.destroy()

        # Hilfsfunktion zum Aktualisieren des Benutzernamens in der Datenbank.
        # Benötigt:
        #   con: Datenbankverbindung
        #   cur: Datenbankcursor
        #   new_username: Der neue Benutzername
        def update_username(con, cur, new_username): # Hilfsfunktion zum Aktualisieren des Benutzernamens in der Datenbank
            cur.execute("UPDATE userdata SET username = ? WHERE user_id = ?", (new_username, user.user_id))
            con.commit()
            log(f"Username bei Id {user.user_id} zu {new_username} geändert")

        ttk.Button(form_frame, text="Benutzername ändern", command=handle_change_username).grid(row=1, column=0, columnspan=2,padx=10, pady=5)
        ttk.Button(frame, text="Abbrechen", command=win_change_user.destroy).pack(pady=10)

    # Fenster für Kontolöschung
    # Zeigt eine Bestätigungsdialogbox zur Löschung des Benutzerkontos an.
    # Bei Bestätigung werden die Benutzerdaten entfernt und der Benutzer abgemeldet.
    def open_delete_account_window():
        root = tk.Tk()
        root.withdraw()  

        confirmed = messagebox.askyesno(
            "Konto löschen",
            "Sind Sie sicher, dass Sie Ihr Konto dauerhaft löschen möchten?\nDies kann nicht rückgängig gemacht werden."
        )

        if not confirmed: # Wenn der Benutzer die Löschung nicht bestätigt, wird das Fenster geschlossen
            return
        try: # Versuche, das Konto zu löschen
            remove_user_data(con, cur, user.user_id)
            messagebox.showinfo("Erfolg", "Konto erfolgreich gelöscht.")
            logout_user()
            Startseite()
        except Exception as e: # Wenn ein Fehler auftritt, wird eine Fehlermeldung angezeigt
            messagebox.showerror("Fehler", f"Beim Löschen des Kontos ist ein Fehler aufgetreten: {e}")

    # Funktion zum Abmelden des Benutzers. Setzt die user_id im globalen user-Objekt auf 0.
    def logout_user():
        user.user_id = 0

    # Hilfsfunktion zum Entfernen der Benutzerdaten aus der Datenbank.
    # Benötigt:
    #   con: Datenbankverbindung
    #   cur: Datenbankcursor
    #   user_id: ID des zu löschenden Benutzers
    def remove_user_data(con, cur, user_id): 
        cur.execute("DELETE FROM userdata WHERE user_id = ?", (user_id,))
        con.commit()
        log(f"Benutzer mit ID {user_id} entfernt")

    # Einstellungen-Rahmen 
    einstellungen_rahmen = ttk.LabelFrame(konto_frame, text="Einstellungen")
    einstellungen_rahmen.pack(pady=20, padx=20)

    ttk.Button(einstellungen_rahmen, text="Passwort ändern", command=open_change_password_window).grid(column=0, row=0, padx=10, pady=10)
    ttk.Button(einstellungen_rahmen, text="Benutzername ändern", command=open_change_username_window).grid(column=1, row=0, padx=10, pady=10)
    ttk.Button(einstellungen_rahmen, text="Konto löschen", command=open_delete_account_window).grid(column=0, row=1, padx=10, pady=10,columnspan=2)

    # Zurück zur Startseite
    ttk.Button(konto_frame, text="Startseite", command=Startseite).pack(pady=20)

# Funktion: Existiert der  Benutzername bereits?
def username_exists(cur, username): # Überprüft, ob der Benutzername bereits in der Datenbank existiert
    cur.execute("SELECT COUNT(*) FROM userdata WHERE username = ?", (username,))
    return cur.fetchone()[0] > 0

# Funktion: current_datetime
# Gibt das aktuelle Datum und die Uhrzeit als formatierten String zurück.
# Benötigt:
#   format: Ein optionaler strftime-Formatstring (Standard: "%d.%m.%Y %H:%M:%S")
# Gibt zurück:
#   Einen String, der das aktuelle Datum und die Uhrzeit darstellt.
def current_datetime(format = "%d.%m.%Y %H:%M:%S"):
    return datetime.datetime.now().strftime(format)

# log funktion
# Schreibt eine Log-Nachricht in eine Datei. Der Dateiname enthält das aktuelle Datum.
# Benötigt:
#   message: Die zu loggende Nachricht (String)
#   level: Das Log-Level (Integer: 1 für Info, 2 für Warnung, 3 für Kritisch)
def log(message: str, level: int = 1):
    log_level = {1 : "Info",
                 2 : "Warn",
                 3 : "Crit"}
    with open(f"log_{current_datetime('%d%m%Y')}.log", "a", encoding="utf-8") as logfile:
        logfile.write(f"[{current_datetime()} - {log_level[level]}] {message}\n")

# Gui Funktionen
# Hauptfenster und Inhalt vorbereiten
root = ThemedTk(theme="breeze")
root.title("Prüfungstrainer")
root.geometry("500x700")

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
# Schaltet den Vollbildmodus des Hauptfensters um.
# Benötigt:
#   event: (Optionales) Tkinter-Ereignisobjekt
def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))
    log(f"Fullscreen Toggled")

# Funktion: end_fullscreen
# Beendet den Vollbildmodus des Hauptfensters.
# Benötigt:
#   event: (Optionales) Tkinter-Ereignisobjekt
def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)

# Funktion: clear_inhalt
# Entfernt alle Widgets aus dem Hauptinhalt-Frame (inhalt_frame).
def clear_inhalt():
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

# Funktion: openfile
# Öffnet einen Standard-Dateidialog, um eine Datei auszuwählen.
# Gibt zurück:
#   Den Pfad zur ausgewählten Datei als String oder einen leeren String, wenn keine Datei ausgewählt wurde.
def openfile():
    filename = askopenfilename() 
    return filename

# Funktion: Fragen_Analyse
# Analysiert die vom Benutzer falsch beantworteten Fragen und wählt eine gewichtete Auswahl
# von 30 Fragen für den Prüfungsmodus aus. Fragen, die häufiger falsch beantwortet wurden,
# haben eine höhere Wahrscheinlichkeit, ausgewählt zu werden.
# Stellt sicher, dass insgesamt 30 Fragen zurückgegeben werden, falls genügend Fragen vorhanden sind.
# Gibt zurück:
#   Eine Liste von bis zu 30 Frage-Objekten für den Prüfungsmodus oder None, wenn nicht genügend Fragen vorhanden sind.
def Fragen_Analyse():
    fragen = get_fragen(cur)
    alle_fragen_IDs = [str(i.id) for i in fragen]

    falsch_prozent = random.randint(50, 75)
    anzahl_falsche_fragen = round(falsch_prozent / 100 * 30)

    falsche_fragen = user.alzeit_fragen_falsch
    gewichtete_IDs = []
    fragen_gewichtigt = []

    for i in alle_fragen_IDs:
        fehler = falsche_fragen.get(i, 0)
        if fehler > 0:
            gewichtete_IDs.append(i)
            fragen_gewichtigt.append(1 + fehler)

    if not gewichtete_IDs:
        gewichtete_auswahl = []
    elif len(gewichtete_IDs) <= anzahl_falsche_fragen:
        gewichtete_auswahl = gewichtete_IDs.copy()
    else:
        gewichtete_auswahl = []
        while len(gewichtete_auswahl) < anzahl_falsche_fragen:
            ziehung = random.choices(gewichtete_IDs, weights=fragen_gewichtigt, k=1)[0]
            if ziehung not in gewichtete_auswahl:
                gewichtete_auswahl.append(ziehung)

    gewichtete_auswahl = list(set(gewichtete_auswahl))
    anzahl_falsche_fragen_effektiv = len(gewichtete_auswahl)
    anzahl_richtige_fragen = 30 - anzahl_falsche_fragen_effektiv

    alle_fragen = list(set(alle_fragen_IDs) - set(gewichtete_auswahl))

    if len(alle_fragen) <= anzahl_richtige_fragen:
        zufällige_auswahl = alle_fragen.copy()
    else:
        zufällige_auswahl = random.sample(alle_fragen, anzahl_richtige_fragen)

    prüfungsmodus_fragen = gewichtete_auswahl + zufällige_auswahl
    
    if len(prüfungsmodus_fragen) < 30:
        fehlende_anzahl = 30 - len(prüfungsmodus_fragen)
        restliche_kandidaten = list(set(alle_fragen_IDs) - set(prüfungsmodus_fragen))
        nachschub = random.sample(restliche_kandidaten, min(fehlende_anzahl, len(restliche_kandidaten)))
        prüfungsmodus_fragen += nachschub

    finale_fragen = [i for i in fragen if str(i.id) in prüfungsmodus_fragen]

    if len(finale_fragen) < 30:
        print("Warnung: Weniger als 30 Fragen vorhanden!")
    else:
        return finale_fragen

# Funktion: Prüfungsmodus
# Initialisiert die Ansicht für den Prüfungsmodus.
# Überprüft, ob der Benutzer angemeldet ist. Zeigt eine Informationsseite an,
# bevor die Prüfung gestartet wird.
def Prüfungsmodus():
    # Hier wird das Prüfungsmodus Fenster erstellt
    if user.user_id == 0:       # Als erster wird überprüft ob der User angemeldet ist. Wenn nicht wird er zurück zur Startseite geschickt.
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich an, um den Prüfungsmodus zu nutzen.")
        Startseite()
        return

    clear_inhalt()
    prüfungs_frame = ttk.Frame(inhalt_frame)
    prüfungs_frame.pack(fill="both", expand=True)

    begrüßung_rahmen = ttk.LabelFrame(prüfungs_frame, text="Informationen zum Prüfungsmodus")
    begrüßung_rahmen.place(y=160,x=80)

    begrüßungs_label = ttk.Label(begrüßung_rahmen, text="Du wirst 30 Fragen erhalten, welche zufällig\naus allen Fragen genommen werden.\n"
            "Das Ergebnis, das du erzielt hast,\nerhältst du, wenn du alle Fragen beantwortet hast.")
    begrüßungs_label.pack(padx=20, pady=20)

    start_Btn = ttk.Button(prüfungs_frame, text="Prüfung starten", command=lambda: Starte_Prüfung(prüfungs_frame))
    start_Btn.place(y=300,x=180)

weitermachen_var = tk.BooleanVar(value=False)

def Fehlermeldung_zu_wenig_Gelernt(prüfungs_frame):
    def weiter_trotz_warnung():
        weitermachen_var.set(True)
        Starte_Prüfung(prüfungs_frame)

    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    fehler_rahmen = ttk.LabelFrame(prüfungs_frame, text="Fehlermeldung", padding=(10, 10))
    fehler_rahmen.place(y=160,x=80)

    fehler_label = ttk.Label(
        fehler_rahmen,
        text=(
            "Sind Sie sich sicher, dass Sie eine Prüfung machen wollen?\n"
            "Sie haben noch nicht genug gelernt. Gehen Sie zuerst in den Lernmodus."
        ),
        wraplength=300, justify="center"
    )
    fehler_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

    lernen_btn = ttk.Button(
        fehler_rahmen,
        text="Fragen lernen",
        command=Lernmodus
    )
    lernen_btn.grid(row=1, column=0, padx=10, pady=10)

    prüfung_btn = ttk.Button(
        fehler_rahmen,
        text="Trotzdem mit der Prüfung fortfahren",
        command=weiter_trotz_warnung
    )
    prüfung_btn.grid(row=2, column=0, padx=10, pady=10)


def Starte_Prüfung(prüfungs_frame):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    fragen = get_fragen(cur)

    anzahl_falsch = sum(user.alzeit_fragen_falsch.values())
    anzahl_richtig = sum(user.alzeit_fragen_richtig.values())

    if not weitermachen_var.get():
        if anzahl_falsch == 0 and anzahl_richtig == 0:
            Fehlermeldung_zu_wenig_Gelernt(prüfungs_frame)
            return
        elif anzahl_falsch <= 25 and anzahl_richtig <= 60:
            Fehlermeldung_zu_wenig_Gelernt(prüfungs_frame)
            return

    if len(fragen) >= 1:
        prüfungsfragen = Fragen_Analyse()
        weitermachen_var.set(False)
    else:
        fehler_rahmen = ttk.LabelFrame(prüfungs_frame, text="Fehlermeldung", padding=(10, 10))
        fehler_rahmen.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        fehler_label = ttk.Label(
            fehler_rahmen,
            text="Fehler! Es gibt nicht genug Fragen.\nImportieren Sie welche oder wenden Sie sich an einen Administrator!",
            foreground="red", wraplength=300, justify="center"
        )
        fehler_label.grid(row=0, column=0, padx=10, pady=(0, 10))

        weiterleit_btn = ttk.Button(fehler_rahmen, text="Fragen importieren", command=Admin)
        weiterleit_btn.grid(row=1, column=0, pady=10, sticky="ew")

        startseite_btn = ttk.Button(fehler_rahmen, text="Zurück zur Startseite", command=Startseite)
        startseite_btn.grid(row=2, column=0, pady=10, sticky="ew")
        return

    # Starte die Prüfungsanzeige
    frage_index = 0
    falsche_Prüfungsfragen = 0

    zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen)

# Funktion: zeige_Prüfungsfragen
# Zeigt die aktuelle Frage im Prüfungsmodus inklusive Fortschrittsanzeige und Antwortmöglichkeiten.
# Wenn alle 30 Fragen beantwortet wurden, wird das Ergebnis (Note) angezeigt.
# Benötigt:
#   prüfungs_frame: Frame des Prüfungsmodus
#   frage_index: Index der aktuellen Frage in der Liste der Prüfungsfragen
#   prüfungsfragen: Liste der Frage-Objekte für die aktuelle Prüfung
#   falsche_Prüfungsfragen: Zähler für die Anzahl der falsch beantworteten Fragen in der aktuellen Prüfung
def zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    auswahl = tk.StringVar(value="X")

    if  frage_index < 30:
        aktuelle_frage = prüfungsfragen[frage_index]

        progress = tk.IntVar(value=frage_index + 1)  
        progressbar = ttk.Progressbar(prüfungs_frame, maximum=30, variable=progress, length=400)
        progressbar.grid(row=0, column=0, padx=40, pady=5)

        fortschirt_label = ttk.Label(prüfungs_frame, text=f"Du bist bei Frage {frage_index +1} von {len(prüfungsfragen)}")
        fortschirt_label.grid(row=2, column=0)

        frage_label = ttk.Label(prüfungs_frame, text=aktuelle_frage.frage)
        frage_label.grid(row=3, column=0, pady=40)

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

        user.save()
        
        noten_label = ttk.Label(prüfungs_frame, text=(f"Deine Note beträgt: {note}"))
        noten_label.grid(row=0, column=0, pady=20)

        weiterleit_Btn = ttk.Button(prüfungs_frame, text="Zurück zur Startseite", command=lambda: Startseite())
        weiterleit_Btn.grid(row=1, column=0, pady=20)

# Funktion: prüffrage_überprüfen
# Überprüft die vom Benutzer im Prüfungsmodus gegebene Antwort.
# Aktualisiert die Benutzerstatistiken (Gesamtzahl Fragen, richtig/falsch Statistiken,
# Zähler für falsch beantwortete Fragen in der aktuellen Prüfung).
# Speichert den Benutzerfortschritt und zeigt die nächste Frage an.
# Benötigt:
#   auswahl: Tkinter-StringVar, das die vom Benutzer gewählte Antwort ("A", "B" oder "C") enthält
#   aktuelle_frage: Das Frage-Objekt der aktuell angezeigten Frage
#   prüfungs_frame: Frame des Prüfungsmodus
#   frage_index: Index der aktuellen Frage
#   prüfungsfragen: Liste der Prüfungsfragen
#   falsche_Prüfungsfragen: Zähler für falsche Antworten in der aktuellen Prüfung
def prüffrage_überprüfen(auswahl, aktuelle_frage, prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen):

    if aktuelle_frage.antwort == auswahl.get():

        if aktuelle_frage.id in user.alzeit_fragen_richtig:
            user.alzeit_fragen_richtig[aktuelle_frage.id] += 1
        else:
            user.alzeit_fragen_richtig[aktuelle_frage.id] = 1

        user.stat_fragen_richtig.append([aktuelle_frage.id, current_datetime()])

        user.fragen_total += 1

    else:

        if aktuelle_frage.id in user.alzeit_fragen_falsch:
            user.alzeit_fragen_falsch[aktuelle_frage.id] += 1
        else:
            user.alzeit_fragen_falsch[aktuelle_frage.id] = 1

        if aktuelle_frage.id not in user.fragen_falsch:
            user.fragen_falsch.append(aktuelle_frage.id)

        user.stat_fragen_falsch.append([aktuelle_frage.id, current_datetime()])

        user.fragen_total += 1
        falsche_Prüfungsfragen += 1

    user.save()

    frage_index += 1

    zeige_Prüfungsfragen(prüfungs_frame, frage_index, prüfungsfragen, falsche_Prüfungsfragen)    

# Funktion: Lernmodus
# Initialisiert die Ansicht für den Lernmodus.
# Der Benutzer kann wählen, ob er alle Fragen oder nur die bisher falsch beantworteten Fragen lernen möchte.
def Lernmodus():
    clear_inhalt()

    # Auswahl anzeigen
    wahl_var = tk.BooleanVar(value=True)

    button_rahmen = ttk.LabelFrame(inhalt_frame, text="Lernmodus Auswahl")
    button_rahmen.place(x=100, y=150)

    label = ttk.Label(button_rahmen, text="Welche Fragen möchtest du lernen?", font=("arial", 12, "bold"))
    label.grid(column=0, row=0, columnspan=2, pady=(10, 20), padx=10)

    gesamtfragen_btn = ttk.Radiobutton(button_rahmen, text="Alle Fragen lernen", variable=wahl_var, value=True)
    gesamtfragen_btn.grid(column=0, row=1, sticky=(tk.W), padx=10, pady=5)

    falsche_fragen_btn = ttk.Radiobutton(button_rahmen, text="Nur falsche Fragen wiederholen", variable=wahl_var, value=False)
    falsche_fragen_btn.grid(column=0, row=2, sticky=(tk.W), padx=10, pady=5)

    weiter_btn = ttk.Button(button_rahmen, text="Weiter", command=lambda: starte_fragen(wahl_var.get()))
    weiter_btn.grid(column=0, row=3, pady=20, padx=10)

# Funktion: starte_fragen
# Startet den Lernzyklus basierend auf der Benutzerauswahl (alle Fragen oder nur falsch beantwortete).
# Lädt die entsprechenden Fragen, mischt sie zufällig und zeigt die erste Frage an.
# Benötigt:
#   wahl: Boolean; True, um alle Fragen zu lernen, False, um nur falsch beantwortete Fragen zu lernen.
def starte_fragen(wahl):
    clear_inhalt()

    prüfungs_frame = ttk.Frame(inhalt_frame)
    prüfungs_frame.pack(fill="both", expand=True)

    if wahl:
        
        fragen = get_fragen(cur)

        if len(fragen) >= 1:
            fragen = get_fragen(cur)
        else:
            fehler_label = ttk.Label(prüfungs_frame,
                                    text="Fehler! Es gibt nicht genug Fragen. Importieren sie welche, oder wenden sie sich einen Administrator!")
            fehler_label.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W)) # type: ignore

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

        startbtn = ttk.Button(prüfungs_frame, text="Startseite", command=wirklich_Startseite)
        startbtn.grid(row=10, column=0, pady=20)
        
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
# Überprüft die Antwort einer Frage im Lernmodus.
# Gibt Feedback (richtig/falsch), aktualisiert die Benutzerstatistiken
# (Gesamtzahl Fragen, Listen der richtig/falsch beantworteten Fragen, Allzeit-Statistiken).
# Speichert den Benutzerfortschritt und zeigt die nächste Frage an.
# Benötigt:
#   auswahl: Tkinter-StringVar, das die vom Benutzer gewählte Antwort ("A", "B" oder "C") enthält
#   aktuelle_frage: Das Frage-Objekt der aktuell angezeigten Frage
#   fragen: Liste der Fragen im aktuellen Lernzyklus
#   frage_index: Index der aktuellen Frage
#   prüfungs_frame: Frame, in dem das Feedback und die nächste Frage angezeigt werden
def frage_überprüfen(auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()
        
    if aktuelle_frage.antwort == auswahl.get():

        r_label = ttk.Label(prüfungs_frame, text="Das war Richtig!")
        r_label.pack(pady=50)

        if aktuelle_frage.id in user.alzeit_fragen_richtig:
            user.alzeit_fragen_richtig[aktuelle_frage.id] += 1
        else:
            user.alzeit_fragen_richtig[aktuelle_frage.id] = 1

        if aktuelle_frage.id in user.fragen_falsch:
            user.fragen_falsch.remove(aktuelle_frage.id)

        user.fragen_total += 1

        user.stat_fragen_richtig.append([aktuelle_frage.id, current_datetime()])

    else:
        f_antwort = ttk.Label(prüfungs_frame, text="Die Antwort war nicht richtig! Die Richtige Antwort ist:")
        f_antwort.pack(pady=50)

        richtige_antwort_text = getattr(aktuelle_frage, aktuelle_frage.antwort)

        l_antwort = ttk.Label(prüfungs_frame, text=richtige_antwort_text)
        l_antwort.pack(pady=10)

        user.fragen_total += 1

        user.stat_fragen_falsch.append([aktuelle_frage.id, current_datetime()])

        if aktuelle_frage.id in user.alzeit_fragen_falsch:
            user.alzeit_fragen_falsch[aktuelle_frage.id] += 1
        else:
            user.alzeit_fragen_falsch[aktuelle_frage.id] =1

        if aktuelle_frage.id not in user.fragen_falsch:
            user.fragen_falsch.append(aktuelle_frage.id)

    frage_index += 1
    
    user.save()
    
    weiter_btn = ttk.Button(prüfungs_frame, text="Weiter", command=lambda: zeige_frage(fragen, prüfungs_frame, frage_index))
    weiter_btn.pack(pady=20)

# Funktion: Startseite
# Zeigt die Startseite an, entweder mit login/Registrierungsoption oder als Menü, wenn ein Benutzer angemeldet ist.
def Startseite():
    if user.user_id == 0:
        clear_inhalt()
        start_frame = ttk.Frame(inhalt_frame)
        start_frame.pack(fill="both", expand=True)
        
        center_frame = ttk.Frame(start_frame) # Frame für zentrierten Inhalt
        center_frame.place(relx=0.5, rely=0.5, anchor="center")  # Zentriert in start_frame

        label = ttk.Label(center_frame, text="Willkommen\nzum Prüfungstrainer!", font=("arial", 30, "bold"), justify="center")
        label.pack(pady=(0, 20))  # Abstand unter dem Text

        button_rahmen = ttk.LabelFrame(center_frame, text="Benutzerzugang") # Rahmen definieren
        button_rahmen.pack()
        # Buttons für login und Registrierung
        loginbtn = ttk.Button(button_rahmen, text="login", command=Guilogin)
        loginbtn.pack(pady=20, padx=40)
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
    button_rahmen.place(x=5, y=150)

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
# Zeigt die Lernstatistiken des angemeldeten Benutzers an.
# Beinhaltet Gesamtanzahl beantworteter Fragen, Anzahl falscher/richtiger Antworten
# sowie Diagramme zur Veranschaulichung (Verhältnis richtig/falsch, Antworten pro Tag).
def Statistik():
    clear_inhalt()
    
    statistik_frame = ttk.Frame(inhalt_frame)
    statistik_frame.pack(fill="both", expand=True)
    button_rahmen = ttk.LabelFrame(statistik_frame, text="Statistiken Gesamt")
    button_rahmen.grid(column=0, row=0, rowspan=2, sticky=(tk.N)) # type: ignore
    
    text = ttk.Label(button_rahmen, text="Fragen Beantwortet insgesamt:", padding=(5,5,10,10))
    text.grid(column=0, row=1, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(button_rahmen, text=user.fragen_total, padding=(5,5,10,10))
    text.grid(column=1, row=1, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(button_rahmen, text="Fragen Beantwortet Falsch:", padding=(5,5,10,10))
    text.grid(column=0, row=2, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(button_rahmen, text=len(user.stat_fragen_falsch), padding=(5,5,10,10))
    text.grid(column=1, row=2, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(button_rahmen, text="Fragen Beantwortet Richtig:", padding=(5,5,10,10))
    text.grid(column=0, row=3, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(button_rahmen, text=len(user.stat_fragen_richtig), padding=(5,5,10,10))
    text.grid(column=1, row=3, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(button_rahmen, text="Prüfungen erledigt:", padding=(5,5,10,10))
    text.grid(column=0, row=4, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(button_rahmen, text=user.pruefungen_total, padding=(5,5,10,10))
    text.grid(column=1, row=4, sticky=(tk.W)) # type: ignore
    
    text = ttk.Label(button_rahmen, text="Prüfungen bestanden:", padding=(5,5,10,10))
    text.grid(column=0, row=5, sticky=(tk.W, tk.S)) # type: ignore
    text = ttk.Label(button_rahmen, text=user.pruefungen_bestanden, padding=(5,5,10,10))
    text.grid(column=1, row=5, sticky=(tk.W)) # type: ignore
    
    #erstes diagramm
    labels = ['Richtig', 'Falsch']
    sizes = [len(user.stat_fragen_richtig), len(user.stat_fragen_falsch)]
    
    button_rahmen1 = ttk.LabelFrame(statistik_frame, text="Statistiken Gesamt")
    button_rahmen1.grid(column=1, row=0, columnspan=2, sticky=("nswe"), padx=5)

    # Matplotlib-Figur erstellen
    fig = Figure(figsize=(2, 1), dpi=100)
    ax = fig.add_subplot(111)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Kreisförmig

    # Canvas in Tkinter einbetten
    canvas = FigureCanvasTkAgg(fig, master=button_rahmen1)
    canvas.draw()
    canvas.get_tk_widget().grid(column=4, row=1, columnspan=2, pady=20, sticky="nswe")

    # Zweites Diagramm
    tages_statistik = {}
    
    for _, datums_string in user.stat_fragen_richtig:
        # Nur ddmmYYYY extrahieren
        datum = datums_string.split(" ")[0]
        # prüfe ob datum in tagesstatisktik ist. wenn nicht füge es hinzu
        if datum not in tages_statistik:
            tages_statistik[datum] = {"richtig" : 0, "falsch" : 0}
        # erhöhe zähler für richtige fragen
        tages_statistik[datum]["richtig"] += 1
        
    for _, datums_string in user.stat_fragen_falsch:
        datum = datums_string.split(" ")[0]
        if datum not in tages_statistik:
            tages_statistik[datum] = {"richtig" : 0, "falsch" : 0}
        tages_statistik[datum]["falsch"] += 1
        
    sortierte_daten = sorted(tages_statistik.keys(), key=lambda d: datetime.datetime.strptime(d, "%d.%m.%Y"))
    
    daten = sortierte_daten     
    richtig = [tages_statistik[d]["richtig"]for d in sortierte_daten]
    falsch = [tages_statistik[d]["falsch"]for d in sortierte_daten]

    button_rahmen2 = ttk.LabelFrame(statistik_frame, text="Statistiken pro Tag", padding=(10,10,10,10))
    button_rahmen2.grid(column=0, row=2, columnspan=2,sticky=(tk.N)) # type: ignore

    fig1 = Figure(figsize=(4, 4), dpi=100)
    ax1 = fig1.add_subplot(111)

    ax1.set_title('Richtig/Falsch pro Tag')
    ax1.set_xlabel('Datum')
    ax1.set_ylabel('Antworten')
    ax1.plot(daten, richtig, color="green", label='Richtige Antworten', marker="o")
    ax1.plot(daten, falsch, color="red", label='Falsche Antworten', marker="o")
    ax1.legend()
    # Rotiert die Datums-Labels für bessere Lesbarkeit, falls sie sich überlappen
    fig1.autofmt_xdate(rotation=45)

    canvas1 = FigureCanvasTkAgg(fig1, master=button_rahmen2)
    canvas1.draw()
    canvas1.get_tk_widget().grid(column=0, row=2, columnspan=2, pady=20)

# Funktion: Guilogin
# Zeigt das login-Fenster an und verarbeitet die Benutzereingaben für die Anmeldung.
def Guilogin():
    clear_inhalt()
    login_frame = ttk.Frame(inhalt_frame)
    login_frame.pack(fill="both", expand=True)
    label = ttk.Label(login_frame, text="loginbereich", font=("arial", 30, "bold"))
    label.pack(pady=100)
    
    button_rahmen = ttk.LabelFrame(login_frame, text="Anmelden")
    button_rahmen.place(x=120, y=180)
    # Eingabefeld für den Benutzernamen
    ttk.Label(button_rahmen, text="Benutzername:").grid(column=0, row=0)
    username_entry = ttk.Entry(button_rahmen)
    username_entry.grid(column=1, row=0)
    # Passwort-Eingabefeld
    ttk.Label(button_rahmen, text="Passwort:").grid(column=0, row=1)
    password_entry = ttk.Entry(button_rahmen, show="*")
    password_entry.grid(column=1, row=1)
    
    # Verarbeitet die Anmeldeeingaben. Hashes das eingegebene Passwort
    # und ruft die login()-Funktion auf. Zeigt bei Erfolg das Menü, sonst eine Fehlermeldung.
    def handle_login(): # Verarbeitet die login-Eingaben und meldet den Benutzer an, wenn die Anmeldedaten korrekt sind.
        username = username_entry.get()
        pw_hash = hashlib.sha256(password_entry.get().encode()).hexdigest()
        if login(cur, username, pw_hash):
            Menu()
            return
        else:
            messagebox.showerror("login fehlgeschlagen", "Benutzername oder Passwort ist falsch.")
    
    loginbtn = ttk.Button(button_rahmen, text="login", command=handle_login)
    loginbtn.grid(column=0, row=2, columnspan=2, pady=10)
    
    # Register-Button außerhalb des Rahmens
    register_label = ttk.Button(login_frame, text="Noch kein Konto?", command=Guiregister)
    register_label.place(x=180, y=395) 
    
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
    # Eingabefeld für den Benutzernamen
    ttk.Label(button_rahmen, text="Benutzername:").grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
    username_entry = ttk.Entry(button_rahmen)
    username_entry.grid(column=1, row=1, padx=10, pady=5)
    # Eingabefeld für das Passwort
    ttk.Label(button_rahmen, text="Passwort:").grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
    password_entry = ttk.Entry(button_rahmen, show="*")
    password_entry.grid(column=1, row=2, padx=10, pady=5)
    # Checkbox für Adminrechte
    # Standardmäßig ist der Benutzer kein Admin
    is_admin = tk.IntVar()
    ttk.Label(button_rahmen, text="Adminrechte:").grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
    is_admin_entry = ttk.Checkbutton(button_rahmen, text="Admin", variable=is_admin)
    is_admin_entry.grid(column=1, row=3, padx=10, pady=5)

    # Verarbeitet die Registrierung eines neuen Benutzers.
    # Überprüft auf leere Felder und bereits existierende Benutzernamen.
    # Hashes das Passwort und fügt den Benutzer über add_user() zur Datenbank hinzu.
    def handle_register(): # Verarbeitet die Registrierung eines neuen Benutzers
        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Fehler", "Benutzername und Passwort dürfen nicht leer sein.")
            return

        if username_exists(cur, username): # Überprüft, ob der Benutzername bereits existiert
            messagebox.showerror("Fehler", "Benutzername existiert bereits. Bitte wählen Sie einen anderen.")
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest() # Hashing des Passworts
        add_user(con, cur, is_admin.get(), username, pw_hash) # Fügt den neuen Benutzer in die Datenbank ein
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
    fragen_delete.grid(column=0, row=2, padx=10, pady=10,columnspan=2)
    
    Startbtn = ttk.Button(admin_frame, text="Startseite", command=Startseite)
    Startbtn.pack(pady=20)

# Funktion: login
# Überprüft die Anmeldedaten eines Benutzers gegen die in der Datenbank gespeicherten Daten.
# Bei erfolgreicher Anmeldung werden die Benutzerdaten (ID, Admin-Status, Statistiken etc.)
# in das globale 'user'-Objekt geladen.
# Benötigt:
#   cur: Datenbankcursor
#   username: Der eingegebene Benutzername
#   pw_hash: Der Hash des eingegebenen Passworts
# Gibt zurück:
#   True bei erfolgreicher Anmeldung, sonst False.
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
            if data[12] != None:
                user.alzeit_fragen_falsch = json.loads(data[12])
            if data[13] != None:
                user.alzeit_fragen_richtig = json.loads(data[13])
            log(f"Benutzer: {username} angemeldet")
            return True
    return False

# Funktion: abmelden
# Meldet den aktuellen Benutzer ab.
# Setzt das globale 'user'-Objekt auf einen Standardzustand zurück (nicht angemeldet)
# und zeigt die Startseite an. Gibt eine Erfolgs- oder Warnmeldung aus.
def abmelden():
    global user
    if user.user_id != 0:
        log(f"Benutzer {user.username} abgemeldet")
        user = User(0, 0, 0, 0, 0, 0)
        Startseite()
        messagebox.showinfo("Abmeldung", "Sie wurden erfolgreich abgemeldet.")
    else:
        messagebox.showwarning("Abmeldung nicht möglich", "Sie sind nicht angemeldet.")

class Frage:
    # __init__: Initialisiert ein Frage-Objekt.
    # Benötigt:
    #   id: Eindeutige Identifikation der Frage aus der Datenbank
    #   frage: Der Text der Frage
    #   A, B, C: Die Texte der Antwortoptionen
    #   antwort: Der Buchstabe der korrekten Antwort ("A", "B" oder "C")
    #   kategorie: Die Kategorie der Frage (Standard: "default")
    def __init__(self, id, frage, A, B, C, antwort, kategorie="default"):
        self.id = id
        self.frage = frage
        self.A = A
        self.B = B
        self.C = C
        self.antwort = antwort
        self.kategorie = kategorie
        self.delete = tk.BooleanVar()
    
    # __repr__: Gibt eine String-Repräsentation des Frage-Objekts zurück (primär für Debugging).
    # Zeigt nur die ID der Frage an.
    def __repr__(self):
        return f"\"ID: {self.id}\""
    
    # export: Gibt ein Dictionary mit den Frageinformationen zurück,
    # das für den Export in eine JSON-Datei geeignet ist.
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
    # Speichert alle relevanten Benutzerdaten und Statistiken.
    # Benötigt:
    #   user_id: Eindeutige ID des Benutzers
    #   is_admin: Integer (0 oder 1), der Admin-Status
    #   username: Benutzername
    #   pw_hash: Gehashtes Passwort
    #   fragen_total: Gesamtanzahl der beantworteten Fragen
    #   fragen_richtig: Anzahl der insgesamt richtig beantworteten Fragen (dieses Attribut scheint nicht konsistent verwendet zu werden, oft als Liste/JSON-String in DB)
    def __init__(self, user_id, is_admin, username, pw_hash, fragen_total, fragen_richtig):
        self.user_id = user_id
        self.is_admin = is_admin
        self.username: str = username
        self.pw_hash = pw_hash
        self.fragen_total = fragen_total        # anzahl insgesamt beantworteter Fragen
        self.fragen_richtig: int = fragen_richtig    # anzahl richtig beantworteter Fragen
        self.fragen_falsch = []
        self.stat_fragen_falsch = []            # nur für Statistiken
        self.stat_fragen_richtig = []           # nur für Statistiken
        self.pruefungen_total = 0
        self.pruefungen_bestanden = 0
        self.stat_pruefungen = []               # Liste [Note, Datum+Uhrzeit] Index 0 von dieser liste = erste Prüfung
        self.alzeit_fragen_falsch = {}              
        self.alzeit_fragen_richtig = {}
    
    # Speicher aktuellen Datenstand in die Datenbank 
    def save(self):
        save_statement = "UPDATE userdata SET fragen_total = ?, fragen_richtig = ?, fragen_falsch = ?, stat_fragen_richtig = ?, stat_fragen_falsch = ?, pruefungen_total = ?, pruefungen_bestanden = ?, stat_pruefungen = ?, alzeit_fragen_falsch = ?, alzeit_fragen_richtig = ? WHERE user_id = ?"
        cur.execute(save_statement, (self.fragen_total, 
                                     self.fragen_richtig, 
                                     json.dumps(self.fragen_falsch, indent=None), 
                                     json.dumps(self.stat_fragen_richtig, indent=None), 
                                     json.dumps(self.stat_fragen_falsch, indent=None),
                                     self.pruefungen_total,
                                     self.pruefungen_bestanden,
                                     json.dumps(self.stat_pruefungen, indent=None),
                                     json.dumps(self.alzeit_fragen_falsch, indent=None),
                                     json.dumps(self.alzeit_fragen_richtig, indent=None),
                                     self.user_id))
        con.commit()
        log(f"Userdata in Datenbank gespeichert")
        
# Funktion: main
# Hauptfunktion der Anwendung. Initialisiert das globale Benutzerobjekt,
# konfiguriert Tastenkürzel und das Menü des Hauptfensters, zeigt die Startseite an
# und startet die Tkinter-Hauptschleife.
# Benötigt:
#   con: Datenbankverbindungsobjekt
#   cur: Datenbankcursorobjekt
def main(con, cur):
    # Globales Benutzerobjekt initialisieren (Standardbenutzer, nicht angemeldet)
    global user
    user = User(0, 0, 0, 0, 0, 0)
    
    # Tastenkürzel für Vollbildmodus definieren
    root.bind("<Escape>", end_fullscreen) # Beendet den Vollbildmodus
    root.bind("<F11>", toggle_fullscreen) # Schaltet den Vollbildmodus um

    # Hauptmenüleiste erstellen
    menubar = tk.Menu(root)

    # Datei-Menü erstellen und Einträge hinzufügen
    file_menu = tk.Menu(menubar, tearoff=0) # tearoff=0 verhindert, dass das Menü abgerissen werden kann
    file_menu.add_command(label="Startseite", command=Startseite)
    file_menu.add_command(label="Adminbereich", command=Admin)
    file_menu.add_command(label="Prüfungsmodus", command=Prüfungsmodus)
    file_menu.add_separator() # Trennlinie im Menü
    file_menu.add_command(label="Abmelden", command=abmelden)
    file_menu.add_command(label="Beenden", command=root.quit) # Beendet die Anwendung
    menubar.add_cascade(label="Datei", menu=file_menu) # Datei-Menü zur Menüleiste hinzufügen

    # Konto-Menü erstellen und Einträge hinzufügen
    account_menu = tk.Menu(menubar, tearoff=0)
    account_menu.add_command(label="Kontoeinstellungen", command=lambda: konto_einstellungen())
    menubar.add_cascade(label="Konto", menu=account_menu) # Konto-Menü zur Menüleiste hinzufügen

    # Theme-Menü erstellen und Einträge hinzufügen
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="Dark Mode", command=lambda: root.set_theme("equilux"))
    theme_menu.add_command(label="Light Mode", command=lambda: root.set_theme("breeze"))
    theme_menu.add_command(label="Holz Mode", command=lambda: root.set_theme("kroc")) # Beispiel für ein weiteres Theme
    menubar.add_cascade(label="Theme", menu=theme_menu) # Theme-Menü zur Menüleiste hinzufügen

    # Menüleiste dem Hauptfenster zuweisen
    root.config(menu=menubar)

    # Startansicht der Anwendung laden
    Startseite()

    # GUI-Hauptschleife starten (hält das Fenster offen und verarbeitet Ereignisse)
    root.mainloop()
    
# Dieser Block wird ausgeführt, wenn das Skript direkt gestartet wird.
# Stellt die Datenbankverbindung her, führt initiale SQL-Anweisungen aus (z.B. Tabellenerstellung)
# und ruft dann die main()-Funktion auf. Beinhaltet Fehlerbehandlung für Datenbankprobleme.
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
