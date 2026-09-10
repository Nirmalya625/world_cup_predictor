import pickle

from flask import Flask, render_template

app = Flask(__name__)

with open("models/elo_ratings.pkl", "rb") as f:
    ELO_RATINGS = pickle.load(f)

with open("models/simulation_results.pkl", "rb") as f:
    SIM = pickle.load(f)


def win_prob(elo_a, elo_b):
    return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400))


@app.route("/")
def predict():
    quarterfinals = []
    for a, b in SIM["quarterfinals"]:
        p_a = win_prob(ELO_RATINGS[a], ELO_RATINGS[b])
        quarterfinals.append({
            "team_a": a, "team_b": b,
            "prob_a": round(p_a * 100, 1),
            "prob_b": round((1 - p_a) * 100, 1),
        })

    return render_template(
        "predict.html",
        quarterfinals=quarterfinals,
        results=SIM["results"],
        n_sims=f"{SIM['n_sims']:,}",
    )


if __name__ == "__main__":
    app.run(debug=True)
