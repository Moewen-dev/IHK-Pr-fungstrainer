import sqlite3
import sys

sql_statements = ["""CREATE TABLE IF NOT EXISTS fragen (
    id INTEGER PRIMARY KEY,
    frage TEXT NOT NULL,
    antwort TEXT NOT NULL);""",]

db_name = "fragen.db"


def main(con, cur):
    print("Hi")
    
    
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