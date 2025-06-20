from flask import Flask, render_template, request
from itertools import permutations

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    cyfry = ""

    if request.method == "POST":
        cyfry = request.form.get("cyfry")
        if len(cyfry) != 6 or not cyfry.isdigit():
            error = "Wprowadź dokładnie 6 cyfr."
        else:
            perms = sorted(set(permutations(cyfry)))
            wynik = [''.join(p) for p in perms]
            liczba_perm = len(wynik)
            with open("historia.txt", "a") as f:
                f.write(f"{cyfry} → {liczba_perm} permutacji\n")

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error, cyfry=cyfry)

if __name__ == "__main__":
    app.run(debug=True)
