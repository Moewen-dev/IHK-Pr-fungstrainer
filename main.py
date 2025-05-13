import sqlite3
import sys

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