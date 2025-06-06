import tkinter as tk
from tkinter.filedialog import askopenfilename
from main import import_fragen
# Diese Variablen werden später vom Hauptprogramm übergeben
root = None
inhalt_frame = None
con = None
cur = None

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
    Tk().withdraw() 
    filename = askopenfilename() 
    return filename

def Admin():
    clear_inhalt()
    admin_frame = tk.Frame(inhalt_frame, bg="lightgray")
    admin_frame.pack(fill="both", expand=True)
    label = tk.Label(admin_frame, text="Adminbereich", font=("Arial", 30), bg="lightgray")
    label.pack(pady=100)

def Prüfungsmodus():
    clear_inhalt()
    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)
    label = tk.Label(prüfungs_frame, text="Prüfungsmodus aktiv", font=("Arial", 30), bg="lightblue")
    label.pack(pady=100)
    fragen_import = tk.Button(text="Zur Prüfungssimulation", font=("Arial", 14), command=import_fragen(openfile))
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