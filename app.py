from flask import Flask, render_template, request
from itertools import permutations

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    wynik = []
    liczba_perm = 0
    error = None
    poprawna = ""
    trafione = False
    cyfry_input = ["", "", "", "", "", ""]

    if request.method == "POST":
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

            pierwsza_cyfra = cyfry_input[0]
            if pierwsza_cyfra:
                wynik.sort(key=lambda x: (x[0] != pierwsza_cyfra, x))

            liczba_perm = len(wynik)
            if poprawna in wynik:
                trafione = True

    return render_template("index.html", wynik=wynik, liczba_perm=liczba_perm, error=error,
                           cyfry_input=cyfry_input, poprawna=poprawna, trafione=trafione)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
