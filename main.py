import sqlite3, sys, json, random, hashlib
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

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
    fragen_total INTEGER,
    fragen_richtig INTEGER,
    fragen_falsch TEXT);"""]

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
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")

def get_fragen(cur):
    cur.execute("SELECT * FROM fragen")
    db_data = cur.fetchall()
    fragen = []
    for data in db_data:
        frage = Frage(data[0], data[1], data[2], data[3], data[4], data[5])
        fragen.append(frage)
    return fragen

def Fragen_nach_ID(cur, id_liste):
    placeholder = ",".join(["?"] * len(id_liste))  
    query = f"SELECT * FROM fragen WHERE id IN ({placeholder})"
    cur.execute(query, id_liste)
    db_data = cur.fetchall()
    
    fragen = []
    for data in db_data:
        frage = Frage(data[0], data[1], data[2], data[3], data[4], data[5])
        fragen.append(frage)
    return fragen

def import_fragen(con, cur, filename):
    try:
        with open(filename, "r") as f:
            fragen = json.load(f)
        for item in fragen["fragen"]:
            frage = item["frage"]
            A = item["A"]
            B = item["B"]
            C = item["C"]
            antwort = item["richtigeAntwort"]
            add_frage(con, cur, frage, A, B, C, antwort)
    except TypeError as e:
        print(f"Error: {e}")

def add_user(con, cur, is_admin, username, pw_hash):
    print(f"Admin: {is_admin}\nUsername: {username}\npw hash: {pw_hash}")
    cur.execute("INSERT INTO userdata (is_admin, username, pw_hash) VALUES (?, ?, ?)", (is_admin, username, pw_hash))
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

# Verbessert
def Prüfungsmodus():
    if user.user_id == 0:
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich an, um den Prüfungsmodus zu nutzen.")
        Guilogin()
        return

    clear_inhalt()
    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)
    label = tk.Label(prüfungs_frame, text="Prüfungsmodus aktiv", font=("Arial", 30), bg="lightblue")
    label.pack(pady=100)

    
#Startet den Lernmodus mit den Fragen. Initalisiert Variabel und leitet weiter nach "zeige Fragen"
def Lernmodus():
    clear_inhalt()

    # Auswahl anzeigen
    wahl_var = tk.BooleanVar(value=True)

    gesamtfragen_btn = tk.Radiobutton(inhalt_frame, text="Willst du alle Fragen lernen?", variable=wahl_var, value=True)
    gesamtfragen_btn.pack(pady=10)

    falsche_fragen_btn = tk.Radiobutton(inhalt_frame, text="Nur die Falschen wiederholen?", variable=wahl_var, value=False)
    falsche_fragen_btn.pack(pady=10)

    weiter_btn = tk.Button(inhalt_frame, text="Weiter mit der Auswahl", command=lambda: starte_fragen(wahl_var.get()))
    weiter_btn.pack(pady=20)


def starte_fragen(wahl):
    clear_inhalt()

    prüfungs_frame = tk.Frame(inhalt_frame, bg="lightblue")
    prüfungs_frame.pack(fill="both", expand=True)

    if wahl:
        fragen = get_fragen(cur)
    else:
        fragen = Fragen_nach_ID(cur)

    random.shuffle(fragen)

    zeige_frage(fragen, prüfungs_frame)


#Hier werden die Fragen angezeigt und überprüft ob alle Fragen schonmal dran waren
def zeige_frage(fragen, auswahl, prüfungs_frame): # Funktioniert nicht, wenn "auswahl" übergeben wird
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()

    auswahl = tk.StringVar(value="X")

    frage_index = 0
    alle_fragen = len(fragen)

    if frage_index < alle_fragen:

        aktuelle_frage = fragen[frage_index]

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

        submit_btn = tk.Button(prüfungs_frame,text="Antwort absenden",command=lambda: frage_überprüfen(auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame, alle_fragen))
        submit_btn.pack(pady=30)
    else:
        Fertig_label = tk.Label(prüfungs_frame, text="Herzlichen Glückwunsch!\nDu hast alle Fragen beantwortet!")
        Fertig_label.pack(pady=50)

        statbtn = tk.Button(prüfungs_frame, text="Zurück zur Startseite", command=Menu)
        statbtn.pack(padx=25)

        wiederholenbtn = tk.Button(prüfungs_frame, text="Nochmal alle Fragen durch gehen", command=lambda:Lernmodus())
        wiederholenbtn.pack(pady=25)

#Hier wird die abgegebene Antwort überprüft und jenachdem auch das angezeigt
def frage_überprüfen(auswahl, aktuelle_frage, fragen, frage_index, prüfungs_frame, alle_fragen):
    for widget in prüfungs_frame.winfo_children():
        widget.destroy()
        
    if aktuelle_frage.antwort == auswahl.get():

        r_label = tk.Label(prüfungs_frame, text="Das war Richtig!", bg="Green")
        r_label.pack(pady=50)
        user.fragen_richtig += 1
        user.fragen_total += 1

        print("Die Frage wurde richtig beantwortet!")

        if aktuelle_frage.id in user.falsche_fragen: # AttributeError: 'User' object has no attribute 'falsche_fragen'
            user.falsche_fragen.remove(aktuelle_frage.id)
            print(f"Die Frage mit der ID {aktuelle_frage.id} wurde herraus genommen")
    else:
        f_antwort = tk.Label(prüfungs_frame, text="Die Antwort war nicht richtig! Die Richtige Antwort ist:", bg="Red")
        f_antwort.pack(pady=50)

        print("Die Frage wurde nicht richtig brantwortet!")

        richtige_antwort_text = getattr(aktuelle_frage, aktuelle_frage.antwort)
        l_antwort = tk.Label(prüfungs_frame, text=richtige_antwort_text)
        l_antwort.pack(pady=10)
        user.fragen_total += 1
        user.fragen_falsch.append(aktuelle_frage.id)

        user.falsche_fragen.append(aktuelle_frage.id)

    frage_index += 1
    
    user.save()
    
    weiter_btn = tk.Button(prüfungs_frame, text="Weiter", command=lambda: zeige_frage(fragen, frage_index, auswahl, prüfungs_frame, alle_fragen))
    weiter_btn.pack(pady=20)

def Startseite():
    if user.user_id == 0:
        clear_inhalt()
        start_frame = tk.Frame(inhalt_frame, bg="white")
        start_frame.pack(fill="both", expand=True)
        label = tk.Label(start_frame, text="Willkommen!", font=("Arial", 30), bg="white")
        label.pack(pady=100)
        
        Loginbtn = tk.Button(start_frame, text="Login", font=("Arial", 14), command=Guilogin)
        Loginbtn.pack(pady=100)
        
        Registerbtn = tk.Button(start_frame, text="Registrieren", font=("Arial", 14), command=Guiregister)
        Registerbtn.pack(pady=0)
    else:
        Menu()

def Menu():
    clear_inhalt()
    menu_frame = tk.Frame(inhalt_frame, bg="white")
    menu_frame.pack(fill="both", expand=True)
    label = tk.Label(menu_frame, text="Willkommen!", font=("Arial", 30), bg="white")
    label.pack(pady=100)
    
    Lernbtn = tk.Button(menu_frame, text="Weiter", font=("Arial", 14), command=Lernmodus)
    Lernbtn.pack(pady=100)

    Prüfungsbtn = tk.Button(menu_frame, text="Zur Prüfungssimulation", font=("Arial", 14), command=Prüfungsmodus)
    Prüfungsbtn.pack(pady=50)
    
    if user.is_admin == 1:
        Adminbtn = tk.Button(menu_frame, text="Adminbereich", font=("Arial", 14), command=Admin)
        Adminbtn.pack(pady=20)

# Login
def Guilogin():
    clear_inhalt()
    login_frame = tk.Frame(inhalt_frame, bg="white")
    login_frame.pack(fill="both", expand=True)
    label = tk.Label(login_frame, text="Loginbereich", font=("Arial", 20), bg="white")
    label.pack(pady=100)
    
    tk.Label(login_frame, text="Benutzername:", bg="white").pack(pady=(10, 0))
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)
    
    tk.Label(login_frame, text="Passwort:", bg="white").pack(pady=(10, 0))
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)
    
    def handle_login():
        username = username_entry.get()
        pw_hash = hashlib.sha256(password_entry.get().encode()).hexdigest()
        if login(cur, username, pw_hash):
            Menu()
            return
    
    loginbtn = tk.Button(login_frame, text="Login", command=handle_login)
    loginbtn.pack(pady=20)

# Registrierungsbereich
def Guiregister():
    clear_inhalt()
    register_frame = tk.Frame(inhalt_frame, bg="white")
    register_frame.pack(fill="both", expand=True)
    label = tk.Label(register_frame, text="Registrierbereich", font=("Arial", 20), bg="white")
    label.pack(pady=100)
    
    tk.Label(register_frame, text="Benutzername:", bg="white").pack(pady=(10, 0))
    username_entry = tk.Entry(register_frame)
    username_entry.pack(pady=5)
    
    tk.Label(register_frame, text="Passwort:", bg="white").pack(pady=(10, 0))
    password_entry = tk.Entry(register_frame, show="*")
    password_entry.pack(pady=5)
    
    is_admin = tk.IntVar()
    tk.Label(register_frame, text="Admin: ", bg="white").pack(pady=(10, 0))
    is_admin_entry = tk.Checkbutton(register_frame, text="Admin", variable=is_admin)
    is_admin_entry.pack(pady=5)
    
    def handle_register():
        username = username_entry.get()
        pw_hash = hashlib.sha256(password_entry.get().encode()).hexdigest()
        add_user(con, cur, is_admin.get(), username, pw_hash)
        Guilogin()
        
    registerbtn = tk.Button(register_frame, text="Register", command=handle_register)
    registerbtn.pack(pady=20)
    

# Admin Bereich
def Admin():
    if user.user_id == 0:
        Guilogin()
        messagebox.showerror("Nicht angemeldet", "Bitte melden Sie sich als Admin an, um den Adminbereich zu nutzen.")
        return
    elif user.is_admin != 1:
        messagebox.showerror("Keine Admin-Berechtigung", "Bitte melden Sie sich mit einem Admin-Konto an, um den Adminbereich zu nutzen.")
        return
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

# Login Funktion
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
            else:
                user.fragen_falsch = []
            return True
    return False

# Zum Abmelden einfach Benutzer Objekt nullen
def abmelden():
    global user
    if user.user_id != 0:
        user = User(0, 0, 0, 0, 0, 0)
        Startseite()
        messagebox.showinfo("Abmeldung", "Sie wurden erfolgreich abgemeldet.")
    else:
        messagebox.showwarning("Abmeldung nicht möglich", "Sie sind nicht angemeldet.")

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
        self.fragen_falsch = []
    
    def save(self):
        save_statement = "UPDATE userdata SET fragen_total = ?, fragen_richtig = ?, fragen_falsch = ? WHERE user_id = ?"
        cur.execute(save_statement, (self.fragen_total, self.fragen_richtig, json.dumps(self.fragen_falsch, indent=None), self.user_id))
        con.commit()
        
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
         