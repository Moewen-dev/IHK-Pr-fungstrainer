import sqlite3
import sys
import tkinter as tk
from tkinter import ttk
import gui_funktionen

sql_statements = ["""CREATE TABLE IF NOT EXISTS fragen (
    id INTEGER PRIMARY KEY,
    frage TEXT NOT NULL,
    antwort TEXT NOT NULL);""",]

db_name = "fragen.db"


def add_frage(con, cur, frage, antwort):
    cur.execute("INSERT INTO fragen (frage, antwort) VALUES (?, ?)", (frage, antwort))
    con.commit()
    
    
def del_frage(con, cur, id):
    cur.execute("DELETE FROM fragen WHERE id=?", (id,))
    con.commit()
    
    
def get_fragen(con, cur):
    cur.execute("SELECT * FROM fragen")
    return cur.fetchall()


<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk
import gui_funktionen  # Unser Modul importieren

# Hauptfenster und Inhalt vorbereiten
root = tk.Tk()
root.title("Vollbild GUI Vorlage")
root.attributes("-fullscreen", True)

inhalt_frame = tk.Frame(root)
inhalt_frame.pack(fill="both", expand=True)

# Übergib root & inhalt_frame an das Modul
gui_funktionen.init(root, inhalt_frame)

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
help_menu.add_command(label="Über", command=lambda: tk.messagebox.showinfo("Info", "GUI Vorlage"))
menubar.add_cascade(label="Hilfe", menu=help_menu)

root.config(menu=menubar)

# Startansicht
gui_funktionen.Startseite()

root.mainloop()

def main(con, cur):
    add_frage(con, cur, "Test Frage", "Test Antwort")
    print(get_fragen(con, cur))


=======
>>>>>>> 229c9ff4c95222ec2692635fc5d2e814a3334ef5
class Frage:
    def __init__(self, id, frage, antwort):
        self.id = id
        self.frage = frage
        self.antwort = antwort
        

def main(con, cur):
    add_frage(con, cur, "Test Frage", "Test Antwort")
    print(get_fragen(con, cur))


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
        
        
        