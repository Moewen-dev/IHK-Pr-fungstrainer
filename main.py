import sqlite3, sys, json, random, hashlib
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from admin_login import check_admin_login

sql_statements = ["""CREATE TABLE IF NOT EXISTS fragen (
    id INTEGER PRIMARY KEY,
    frage TEXT NOT NULL,
    A TEXT NOT NULL,
    B TEXT NOT NULL,
    C TEXT NOT NULL,
    antwort INTEGER NOT NULL);""",
    """CREATE TABLE IF NOT EXISTS userdata (
    user_id INTEGER PRIMARY KEY,
    is_admin INTEGER NOT NULL,
    username TEXT NOT NULL,
    pw_hash TEXT NOT NULL,
    fragen_total INTEGER NOT NULL,
    fragen_richtig INTEGER NOT NULL);"""]

db_name = "fragen.db"

def add_frage(con, cur, frage, A, B, C, antwort):
    cur.execute("INSERT INTO fragen (frage, A, B, C, antwort) VALUES (?, ?, ?, ?, ?)", (frage, A, B, C, antwort))
    con.commit()
       
def del_frage(con, cur):
    try:
        id = int(tk.simpledialog.askstring("Frage löschen", "Geben Sie die ID der zu löschenden Frage ein:"))
        cur.execute("DELETE FROM fragen WHERE id=?", (id,))
        con.commit()
    except TypeError as e:
        print(f"ERROR: {e}")
    except ValueError as e:
        print(f"ERROR: {e}")

def get_fragen(cur):
    cur.execute("SELECT * FROM fragen")
    db_data = cur.fetchall()
    fragen = []
    for data in db_data:
        frage = Frage(data[0], data[1], data[2], data[3], data[4], data[5])
        fragen.append(frage)
    return fragen

def import_fragen(con, cur, filename):
    with open(filename, "r") as f:
        fragen = json.load(f)
    for item in fragen["fragen"]:
        frage = item["frage"]
        A = item["A"]
        B = item["B"]
        C = item["C"]
        antwort = item["richtigeAntwort"]
        add_frage(con, cur, frage, A, B, C, antwort)

def add_user(con, cur, is_admin, username, pw_hash, fragen_total, fragen_richtig):
    cur.execute("INSERT INTO userdata (is_admin, username, pw_hash, fragen_total, fragen_richtig) VALUES (?, ?, ?, ?, ?)", (is_admin, username, pw_hash, fragen_total, fragen_richtig))
    con.commit()

# Gui Funktionen
# Hauptfenster und Inhalt vorbereiten
root = tk.Tk()
root.title("Vollbild GUI Vorlage")
root.attributes("-fullscreen", True)

inhalt_frame = tk.Frame(root)
inhalt_frame.pack(fill="both", expand=True)

def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)

def clear_inhalt():
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

def openfile():
    filename = askopenfilename() 
    return filename

def Admin():
    clear_inhalt()
    admin_frame = tk.Frame(inhalt_frame, bg="lightgray")
    admin_frame.pack(fill="both", expand=True)
    label = tk.Label(admin_frame, text="Adminbereich", font=("Arial", 30), bg="lightgray")
    label.pack(pady=100)
    #fragen_import = tk.Button(admin_frame, text="Zur Prüfungssimulation", font=("Arial", 14), command=import_fragen(openfile))
    #fragen_import.pack(pady=50)

def Prüfungsmodus():
    clear_inhalt()
    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)
    label = tk.Label(prüfungs_frame, text="Prüfungsmodus aktiv", font=("Arial", 30), bg="lightblue")
    label.pack(pady=100)
    
#Startet den Lernmodus mit den Fragen. Initalisiert Variabel und leitet weiter nach "zeige Fragen"
def Lernmodus():
    clear_inhalt()
    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)

    fragen = get_fragen(cur)
    random.shuffle(fragen)
    frageliste = fragen

    frage_index = 0
    alle_fragen = len(frageliste)

    auswahl = tk.StringVar(value="X")

    zeige_frage(frageliste, frage_index, auswahl, prüfungs_frame, alle_fragen)

#Hier werden die Fragen angezeigt und überprüft ob alle Fragen schonmal dran waren
def zeige_frage(frageliste, frage_index, auswahl, prüfungs_frame, alle_fragen):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    if frage_index < alle_fragen:

        aktuelle_frage = frageliste[frage_index]

        auswahl = tk.StringVar(value="X")

        Fortschirt_label = tk.Label(prüfungs_frame, text=f"Du bist bei Frage {frage_index +1} von {alle_fragen}")
        Fortschirt_label.pack(pady=25)

        Frage_label = tk.Label(prüfungs_frame, text=aktuelle_frage.frage)
        Frage_label.pack(pady=50)

        frageA = tk.Radiobutton(prüfungs_frame, text=aktuelle_frage.A, variable=auswahl, value="A")
        frageA.pack(pady=5) 

        frageB = tk.Radiobutton(prüfungs_frame, text=aktuelle_frage.B, variable=auswahl, value="B")
        frageB.pack(pady=5)

        frageC = tk.Radiobutton(prüfungs_frame, text=aktuelle_frage.C, variable=auswahl, value="C")
        frageC.pack(pady=5)

        submit_btn = tk.Button(prüfungs_frame,text="Antwort absenden",command=lambda: frage_überprüfen(auswahl, aktuelle_frage, frageliste, frage_index, prüfungs_frame, alle_fragen))
        submit_btn.pack(pady=30)
    else:
        Fertig_label = tk.Label(prüfungs_frame, text="Herzlichen Glückwunsch!\nDu hast alle Fragen beantwortet!")
        Fertig_label.pack(pady=50)

        statbtn = tk.Button(prüfungs_frame, text="Zurück zur Startseite", command=lambda:Startseite())
        statbtn.pack(padx=25)

        wiederholenbtn = tk.Button(prüfungs_frame, text="Nochmal alle Fragen durch gehen", command=lambda:Lernmodus())
        wiederholenbtn.pack(pady=25)

#Hier wird die abgegebene Antwort überprüft und jenachdem auch das angezeigt
def frage_überprüfen(auswahl, aktuelle_frage, frageliste, frage_index, prüfungs_frame, alle_fragen):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()
        
    if aktuelle_frage.antwort == auswahl.get():

        r_label = tk.Label(prüfungs_frame, text="Das war Richtig!", bg="Green")
        r_label.pack(pady=50)
    else:
        f_antwort = tk.Label(prüfungs_frame, text="Die Antwort war nicht richtig! Die Richtige Antwort ist:", bg="Red")
        f_antwort.pack(pady=50)

        richtige_antwort_text = getattr(aktuelle_frage, aktuelle_frage.antwort)
        l_antwort = tk.Label(prüfungs_frame, text=richtige_antwort_text)
        l_antwort.pack(pady=10)

    frage_index += 1

    weiter_btn = tk.Button(prüfungs_frame, text="Weiter", command=lambda: zeige_frage(frageliste, frage_index, auswahl, prüfungs_frame, alle_fragen))
    weiter_btn.pack(pady=20)

def Startseite():
    clear_inhalt()
    start_frame = tk.Frame(inhalt_frame, bg="white")
    start_frame.pack(fill="both", expand=True)
    label = tk.Label(start_frame, text="Willkommen!", font=("Arial", 30), bg="white")
    label.pack(pady=100)

    Lernbtn = tk.Button(start_frame, text="Weiter", font=("Arial", 14), command=Lernmodus)
    Lernbtn.pack(pady=100)

    Prüfungsbtn = tk.Button(start_frame, text="Zur Prüfungssimulation", font=("Arial", 14), command=Prüfungsmodus)
    Prüfungsbtn.pack(pady=50)
    
    Adminbtn = tk.Button(start_frame, text="Adminbereich", font=("Arial", 14), command=AdminLogin)
    Adminbtn.pack(pady=20)

# Admin Bereich Start

def AdminLogin():
    clear_inhalt()
    login_frame = tk.Frame(inhalt_frame, bg="lightgray")
    login_frame.pack(fill="both", expand=True)

    tk.Label(login_frame, text="Admin Login", font=("Arial", 24), bg="lightgray").pack(pady=20)

    tk.Label(login_frame, text="Benutzername:", bg="lightgray").pack(pady=(10, 0))
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)

    tk.Label(login_frame, text="Passwort:", bg="lightgray").pack(pady=(10, 0))
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        if check_admin_login(username, password):
            Admin()
        else:
            messagebox.showerror("Fehler", "Benutzername oder Passwort falsch!")

    login_button = tk.Button(login_frame, text="Login", command=handle_login)
    login_button.pack(pady=20)

def Admin():
    clear_inhalt()
    admin_frame = tk.Frame(inhalt_frame, bg="lightgray")
    admin_frame.pack(fill="both", expand=True)
    label = tk.Label(admin_frame, text="Adminbereich", font=("Arial", 30), bg="lightgray")
    label.pack(pady=100)
    fragen_import = tk.Button(admin_frame, text="Fragen importieren", font=("Arial", 14),
                              command=lambda: import_fragen(con, cur, openfile()))
    fragen_import.pack(pady=50)
    fragen_delete = tk.Button(admin_frame, text="Fragen löschen", font=("Arial", 14),
                                command=lambda: del_frage(con, cur))
    fragen_delete.pack(pady=40)
# Admin Bereich Ende

# Login Funktion
def login(cur, username, pw_hash):
    userdata = cur.execute("SELECT * FROM userdata").fetchall()
    for data in userdata:
        data_username = data[2]
        data_pw_hash = data[3] 
        if data_username == username and data_pw_hash == pw_hash:
            return data[0]
    return 0

class Frage:
    def __init__(self, id, frage, A, B, C, antwort):
        self.id = id
        self.frage = frage
        self.A = A
        self.B = B
        self.C = C
        self.antwort = antwort
    
class User:
    def __init__(self, user_id, is_admin, username, pw_hash, fragen_total, fragen_richtig):
        self.user_id = user_id
        self.is_admin = is_admin
        self.username = username
        self.pw_hash = pw_hash
        self.fragen_total = fragen_total        # anzahl insgesamt beantworteter Fragen
        self.fragen_richtig = fragen_richtig    # anzahl richtig beantworteter Fragen
        
def main(con, cur):

    # Tastenkürzel
    root.bind("<Escape>", end_fullscreen)
    root.bind("<F11>", toggle_fullscreen)

    # Menü
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Startseite", command=Startseite)
    file_menu.add_command(label="Adminbereich", command=AdminLogin)
    file_menu.add_command(label="Prüfungs Modus", command=Prüfungsmodus)
    file_menu.add_separator()
    file_menu.add_command(label="Beenden", command=root.quit)
    menubar.add_cascade(label="Datei", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Hilfe", menu=help_menu)

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
         