from flask import Flask, render_template, request
from itertools import permutations
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = "baza.db"
HISTORY_PASSWORD = "napad123"

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE historia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    czas TEXT,
                    drzwi_wejscie TEXT,
                    nad_drzwiami TEXT,
                    bar_lewo TEXT,
                    bar_prawo TEXT,
                    parkiet_lewo TEXT,
                    parkiet_prawo TEXT,
                    poprawna TEXT,
                    trafione INTEGER
                )
            """)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    komunikat = ""
    poprawna = ""
    trafione = False
    miejsca = {
        "drzwi_wejscie": "",
        "nad_drzwiami": "",
        "bar_lewo": "",
        "bar_prawo": "",
        "parkiet_lewo": "",
        "parkiet_prawo": ""
    }

    if request.method == "POST":
        if "clear" in request.form:
            return render_template("index.html", wynik=[], liczba_perm=0, error=None,
                                   miejsca=miejsca, poprawna="", trafione=False,
                                   historia=fetch_history(), komunikat="")

        if "clearhistory" in request.form:
            podane_haslo = request.form.get("clearpassword", "")
            if podane_haslo == HISTORY_PASSWORD:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("DELETE FROM historia")
                komunikat = "Historia została wyczyszczona ✅"
            else:
                komunikat = "Błędne hasło do usunięcia historii ❌"

        elif "zatwierdz" in request.form:
            for key in miejsca:
                miejsca[key] = request.form.get(key, "")
            poprawna = request.form.get("poprawna", "")
            cyfry = ''.join(miejsca.values())
            if len(poprawna) != 6 or not poprawna.isdigit():
                error = "Poprawna permutacja musi mieć dokładnie 6 cyfr."
            else:
                perms = sorted(set(permutations(cyfry)))
                wynik = [''.join(p) for p in perms]
                liczba_perm = len(wynik)
                if poprawna in wynik:
                    trafione = True
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("""
                        INSERT INTO historia (czas, drzwi_wejscie, nad_drzwiami, bar_lewo, bar_prawo, parkiet_lewo, parkiet_prawo, poprawna, trafione)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          miejsca["drzwi_wejscie"], miejsca["nad_drzwiami"],
                          miejsca["bar_lewo"], miejsca["bar_prawo"],
                          miejsca["parkiet_lewo"], miejsca["parkiet_prawo"],
                          poprawna, int(trafione)))
                komunikat = "Permutacja została zapisana ✅"
        else:
            for key in miejsca:
                miejsca[key] = request.form.get(key, "")
            cyfry = ''.join(miejsca.values())
            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."
            else:
                perms = sorted(set(permutations(cyfry)))
                wynik = [''.join(p) for p in perms]
                liczba_perm = len(wynik)

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error,
                           miejsca=miejsca, poprawna=poprawna, trafione=trafione,
                           historia=fetch_history(), komunikat=komunikat)

def fetch_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT czas, drzwi_wejscie, nad_drzwiami, bar_lewo, bar_prawo, parkiet_lewo, parkiet_prawo, poprawna, trafione FROM historia ORDER BY id DESC LIMIT 10")
        return cursor.fetchall()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
