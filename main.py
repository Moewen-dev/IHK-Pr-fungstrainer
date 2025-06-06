import sqlite3
import sys
import json
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

sql_statements = ["""CREATE TABLE IF NOT EXISTS fragen (
    id INTEGER PRIMARY KEY,
    frage TEXT NOT NULL,
    A TEXT NOT NULL,
    B TEXT NOT NULL,
    C TEXT NOT NULL,
    antwort INTEGER NOT NULL);""",]

db_name = "fragen.db"


def add_frage(con, cur, frage, A, B, C, antwort):
    cur.execute("INSERT INTO fragen (frage, A, B, C, antwort) VALUES (?, ?, ?, ?, ?)", (frage, A, B, C, antwort))
    con.commit()
    
    
def del_frage(con, cur, id):
    cur.execute("DELETE FROM fragen WHERE id=?", (id,))
    con.commit()
    
    
def get_fragen(cur):
    cur.execute("SELECT * FROM fragen")
    db_data = cur.fetchall()
    fragen = []
    for data in db_data:
        print("Data:", data)
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


# Gui Funktionen
def init(uebergebenes_root, uebergebenes_inhalt_frame, uebergebenes_con=None, uebergebenes_cur=None):
    global root, inhalt_frame, con, cur
    root = uebergebenes_root
    inhalt_frame = uebergebenes_inhalt_frame
    con = uebergebenes_con
    cur = uebergebenes_cur

def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

def end_fullscreen(event=None):
    root.attributes("-fullscreen", False)

def clear_inhalt():
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

def openfile():
    tk().withdraw() 
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
    
def Lernmodus():
    clear_inhalt()
    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)


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


class Frage:
    def __init__(self, id, frage, A, B, C, antwort):
        self.id = id
        self.frage = frage
        self.A = A
        self.B = B
        self.C = C
        self.antwort = antwort
        

def main(con, cur):    
    
    import_fragen(con, cur, "question.json")
    fragen = get_fragen(cur)
    
    print(fragen[5].frage)
    
    
    # Hauptfenster und Inhalt vorbereiten
    root = tk.Tk()
    root.title("Vollbild GUI Vorlage")
    root.attributes("-fullscreen", True)

    inhalt_frame = tk.Frame(root)
    inhalt_frame.pack(fill="both", expand=True)

    # Übergib root & inhalt_frame an das Modul
    # main.py
    init(root, inhalt_frame, con, cur)


    # Tastenkürzel
    root.bind("<Escape>", end_fullscreen)
    root.bind("<F11>", toggle_fullscreen)

    # Menü
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Startseite", command=Startseite)
    file_menu.add_command(label="Admin", command=Admin)
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
        
        
        