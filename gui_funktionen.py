import tkinter as tk
from tkinter.filedialog import askopenfilename
from main import import_fragen
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from admin import check_admin_login

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
    tk().withdraw() 
    filename = askopenfilename() 
    return filename

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
    fragen_import = tk.Button(admin_frame, text="Zur Prüfungssimulation", font=("Arial", 14),
                              command=lambda: import_fragen(openfile()))
    fragen_import.pack(pady=50)


# Admin Bereich Ende

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
    
    Adminbtn = tk.Button(start_frame, text="Adminbereich (Login)", font=("Arial", 14), command=AdminLogin)
    Adminbtn.pack(pady=20)
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