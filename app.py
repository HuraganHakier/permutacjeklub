from flask import Flask, render_template, request
from itertools import permutations
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DB_FILE = "baza.db"
HISTORY_PASSWORD = "napad123"

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historia (
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
    potwierdzenie = False
    miejsca = {k: "" for k in [
        "drzwi_wejscie", "nad_drzwiami", "bar_lewo", "bar_prawo", "parkiet_lewo", "parkiet_prawo"
    ]}

    if request.method == "POST":
        for key in miejsca:
            miejsca[key] = request.form.get(key, "")

        cyfry = ''.join(miejsca.values())
        poprawna = request.form.get("poprawna", "")
        brak_poprawnej = request.form.get("brakpoprawnej") == "on"
        zatwierdz = request.form.get("zatwierdz") == "1"

        if zatwierdz:

            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."
            elif not brak_poprawnej and (len(poprawna) != 6 or not poprawna.isdigit()):
                error = "Poprawna permutacja musi mieć dokładnie 6 cyfr."
    
        elif "clear" in request.form:
            return render_template("index.html", wynik=[], liczba_perm=0, error=None,
                                   miejsca={k:"" for k in miejsca}, poprawna="", trafione=False,
                                   historia=fetch_history(), komunikat="", potwierdzenie=False, licznik=policz_napady())

        if "clearhistory" in request.form:
            podane_haslo = request.form.get("clearpassword", "")
            if podane_haslo == HISTORY_PASSWORD:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("DELETE FROM historia")
                komunikat = "Historia została wyczyszczona ✅"
            else:
                komunikat = "Błędne hasło do usunięcia historii ❌"

        elif zatwierdz:
            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."
            elif not brak_poprawnej and (len(poprawna) != 6 or not poprawna.isdigit()):
                error = "Poprawna permutacja musi mieć dokładnie 6 cyfr."
            else:
                if not brak_poprawnej:
                    perms = sorted(set(permutations(cyfry)))
                    wynik = [''.join(p) for p in perms]
                    liczba_perm = len(wynik)
                    trafione = poprawna in wynik
                else:
                    poprawna = None
                    trafione = False

                if not is_duplicate(cyfry):
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("""
                            INSERT INTO historia (czas, drzwi_wejscie, nad_drzwiami, bar_lewo, bar_prawo, parkiet_lewo, parkiet_prawo, poprawna, trafione)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              miejsca["drzwi_wejscie"], miejsca["nad_drzwiami"],
                              miejsca["bar_lewo"], miejsca["bar_prawo"],
                              miejsca["parkiet_lewo"], miejsca["parkiet_prawo"],
                              poprawna, int(trafione)))
                        potwierdzenie = True
                else:
                    komunikat = "❗ Ten napad już został zapisany w ciągu ostatnich kilku minut."

        else:
            if len(cyfry) == 6 and cyfry.isdigit():
                perms = sorted(set(permutations(cyfry)))
                wynik = [''.join(p) for p in perms]
                liczba_perm = len(wynik)
            else:
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error,
                           miejsca=miejsca, poprawna=poprawna,
                           trafione=trafione, komunikat=komunikat,
                           historia=fetch_history(), potwierdzenie=potwierdzenie, licznik=policz_napady())

def fetch_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT czas, drzwi_wejscie || nad_drzwiami || bar_lewo || bar_prawo || parkiet_lewo || parkiet_prawo AS cyfry, poprawna, trafione, id FROM historia ORDER BY id DESC LIMIT 10")
        return cursor.fetchall()

def is_duplicate(cyfry):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT czas FROM historia
            WHERE drzwi_wejscie || nad_drzwiami || bar_lewo || bar_prawo || parkiet_lewo || parkiet_prawo = ?
            ORDER BY id DESC LIMIT 1
        """, (cyfry,))
        row = cursor.fetchone()
        if row:
            ostatni_czas = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            return datetime.now() - ostatni_czas < timedelta(minutes=3)
    return False

def policz_napady():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM historia")
        return cursor.fetchone()[0]

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
