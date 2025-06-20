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
                    trafione INTEGER
                )
            """)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    komunikat = ""
    trafione = False
    potwierdzenie = False
    miejsca = {k: "" for k in [
        "drzwi_wejscie", "nad_drzwiami", "bar_lewo", "bar_prawo", "parkiet_lewo", "parkiet_prawo"
    ]}

    if request.method == "POST":
        for key in miejsca:
            miejsca[key] = request.form.get(key, "")

        cyfry = ''.join(miejsca.values())
        brak_poprawnej = request.form.get("brakpoprawnej") == "on"


            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."
                error = "Poprawna permutacja musi mieć dokładnie 6 cyfr."
    
        elif "clear" in request.form:
            return render_template("index.html", wynik=[], liczba_perm=0, error=None,
                                   historia=fetch_history(), komunikat="", potwierdzenie=False, licznik=policz_napady())

        if "clearhistory" in request.form:
            podane_haslo = request.form.get("clearpassword", "")
            if podane_haslo == HISTORY_PASSWORD:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("DELETE FROM historia")
                komunikat = "Historia została wyczyszczona ✅"
            else:
                komunikat = "Błędne hasło do usunięcia historii ❌"

            if len(cyfry) != 6 or not cyfry.isdigit():
                error = "Wprowadź dokładnie 6 cyfr – po jednej w każdym miejscu."
                error = "Poprawna permutacja musi mieć dokładnie 6 cyfr."
            else:
                if not brak_poprawnej:
                    perms = sorted(set(permutations(cyfry)))
                    wynik = [''.join(p) for p in perms]
                    liczba_perm = len(wynik)
                else:
                    trafione = False

                if not is_duplicate(cyfry):
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("""
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              miejsca["drzwi_wejscie"], miejsca["nad_drzwiami"],
                              miejsca["bar_lewo"], miejsca["bar_prawo"],
                              miejsca["parkiet_lewo"], miejsca["parkiet_prawo"],
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
                           trafione=trafione, komunikat=komunikat,
                           historia=fetch_history(), potwierdzenie=potwierdzenie, licznik=policz_napady())

def fetch_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
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


@app.route("/eksportuj")
def eksportuj():
    from flask import Response, request
    from itertools import permutations
    miejsca = ["drzwi_wejscie", "nad_drzwiami", "bar_lewo", "bar_prawo", "parkiet_lewo", "parkiet_prawo"]
    params = [request.args.get(m, "") for m in miejsca]
    if not all(len(x) == 1 and x.isdigit() for x in params):
        return "Błędne dane wejściowe", 400
    wejscie = ''.join(params)
    perms = sorted(set([''.join(p) for p in permutations(wejscie)]))
    txt = "\n".join(perms)
    return Response(txt, mimetype="text/plain",
                    headers={"Content-Disposition":f"attachment;filename=permutacje_{wejscie}.txt"})
