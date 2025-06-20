from flask import Flask, render_template, request
from itertools import permutations

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    cyfry_input = ["", "", "", "", "", ""]

    if request.method == "POST":
        cyfry_input = [request.form.get(f"cyfra{i}", "") for i in range(6)]
        cyfry = ''.join(cyfry_input)
        if len(cyfry) != 6 or not cyfry.isdigit():
            error = "Wprowadź dokładnie 6 cyfr (po jednej w każdym polu)."
        else:
            perms = sorted(set(permutations(cyfry)))
            wynik = [''.join(p) for p in perms]

            pierwsza_cyfra = cyfry_input[0]
            if pierwsza_cyfra:
                wynik.sort(key=lambda x: (x[0] != pierwsza_cyfra, x))

            liczba_perm = len(wynik)

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error, cyfry_input=cyfry_input)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
