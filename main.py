import sqlite3
import sys
import json
import tkinter as tk
from tkinter import ttk
import gui_funktionen

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
        frage = Frage(data[0], data[1], data[2], data[3], data[4], data[5])
        fragen.append(frage)
        print("Data:" + data)
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
    
    # Hauptfenster und Inhalt vorbereiten
    root = tk.Tk()
    root.title("Vollbild GUI Vorlage")
    root.attributes("-fullscreen", True)

    inhalt_frame = tk.Frame(root)
    inhalt_frame.pack(fill="both", expand=True)

    # Übergib root & inhalt_frame an das Modul
    # main.py
    gui_funktionen.init(root, inhalt_frame, con, cur)


    # Tastenkürzel
    root.bind("<Escape>", gui_funktionen.end_fullscreen)
    root.bind("<F11>", gui_funktionen.toggle_fullscreen)

    # Menü
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Startseite", command=gui_funktionen.Startseite)
    file_menu.add_command(label="Admin", command=gui_funktionen.Admin)
    file_menu.add_command(label="Prüfungs Modus", command=gui_funktionen.Prüfungsmodus)
    file_menu.add_separator()
    file_menu.add_command(label="Beenden", command=root.quit)
    menubar.add_cascade(label="Datei", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Hilfe", menu=help_menu)

    root.config(menu=menubar)

    # Startansicht
    gui_funktionen.Startseite()

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
        
        
        