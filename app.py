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
