from flask import Flask, render_template, request
from itertools import permutations
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = "baza.db"
HISTORY_PASSWORD = "napad123"  # hasło do czyszczenia historii

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE historia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    czas TEXT,
                    cyfry TEXT,
                    poprawna TEXT,
                    trafione INTEGER
                )
            """)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    poprawna = ""
    trafione = False
    komunikat = ""
    cyfry_input = ["", "", "", "", "", ""]

    if request.method == "POST":
        if "clearhistory" in request.form:
            podane_haslo = request.form.get("clearpassword", "")
            if podane_haslo == HISTORY_PASSWORD:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("DELETE FROM historia")
                komunikat = "Historia została wyczyszczona ✅"
            else:
                komunikat = "Błędne hasło do usunięcia historii ❌"

        elif "clear" in request.form:
            return render_template("index.html", wynik=[], liczba_perm=0, error=None,
                                   cyfry_input=[""]*6, poprawna="", trafione=False,
                                   historia=fetch_history(), komunikat="")

        else:
            cyfry_input = [request.form.get(f"cyfra{i}", "") for i in range(6)]
            poprawna = request.form.get("poprawna", "")
            cyfry = ''.join(cyfry_input)

            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr (po jednej w każdym polu)."
            elif poprawna and (not poprawna.isdigit() or len(poprawna) != 6):
                error = "Poprawna permutacja musi składać się z dokładnie 6 cyfr."
            else:
                perms = sorted(set(permutations(cyfry)))
                wynik = [''.join(p) for p in perms]

                liczba_perm = len(wynik)
                if poprawna in wynik:
                    trafione = True

                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT INTO historia (czas, cyfry, poprawna, trafione) VALUES (?, ?, ?, ?)",
                                 (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), cyfry, poprawna, int(trafione)))

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error,
                           cyfry_input=cyfry_input, poprawna=poprawna, trafione=trafione,
                           historia=fetch_history(), komunikat=komunikat)

def fetch_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT czas, cyfry, poprawna, trafione FROM historia ORDER BY id DESC LIMIT 10")
        return cursor.fetchall()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
