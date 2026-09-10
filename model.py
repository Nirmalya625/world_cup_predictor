
import csv
import pickle
import random

K_BASE = 28           # base K-factor for World Cup matches
K_KNOCKOUT_BOOST = 6   # extra weight for knockout matches
N_SIMS = 100_000

# Confirmed quarterfinal matchups (bracket structure as of July 9, 2026)
QUARTERFINALS = [
    ("France", "Morocco"),
    ("Spain", "Belgium"),
    ("Argentina", "Switzerland"),
    ("Norway", "England"),
]
# QF1 winner plays QF2 winner in SF1; QF3 winner plays QF4 winner in SF2
SF_PAIRING = [(0, 1), (2, 3)]


def load_teams(path="data/teams.csv"):
    ratings = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ratings[row["team"]] = float(row["pre_tournament_elo"])
    return ratings


def load_matches(path="data/matches.csv"):
    matches = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            matches.append((
                row["home_team"],
                row["away_team"],
                int(row["home_goals"]),
                int(row["away_goals"]),
                row["is_knockout"] == "True",
                row["penalties_winner"] or None,
            ))
    return matches


def expected_score(r_a, r_b):
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400))


def goal_diff_multiplier(gd):
    if gd <= 1:
        return 1.0
    elif gd == 2:
        return 1.5
    return (11 + gd) / 8


def update_elo(ratings, home, away, home_goals, away_goals, knockout=False, penalties_winner=None):
    r_home, r_away = ratings[home], ratings[away]
    exp_home = expected_score(r_home, r_away)
    exp_away = 1 - exp_home

    if home_goals > away_goals:
        actual_home, actual_away, gd = 1.0, 0.0, home_goals - away_goals
    elif away_goals > home_goals:
        actual_home, actual_away, gd = 0.0, 1.0, away_goals - home_goals
    else:
        if penalties_winner == home:
            actual_home, actual_away = 0.6, 0.4
        elif penalties_winner == away:
            actual_home, actual_away = 0.4, 0.6
        else:
            actual_home, actual_away = 0.5, 0.5
        gd = 0

    k = K_BASE + (K_KNOCKOUT_BOOST if knockout else 0)
    mult = goal_diff_multiplier(gd)

    ratings[home] = r_home + k * mult * (actual_home - exp_home)
    ratings[away] = r_away + k * mult * (actual_away - exp_away)


def build_current_elo():
    ratings = load_teams()
    for home, away, hg, ag, ko, pens in load_matches():
        update_elo(ratings, home, away, hg, ag, knockout=ko, penalties_winner=pens)
    return ratings


def simulate_match(team_a, team_b, ratings, rng):
    p_a = expected_score(ratings[team_a], ratings[team_b])
    return team_a if rng.random() < p_a else team_b


def simulate_tournament(ratings, rng):
    qf_winners = [simulate_match(a, b, ratings, rng) for a, b in QUARTERFINALS]
    sf_winners = [simulate_match(qf_winners[i], qf_winners[j], ratings, rng) for i, j in SF_PAIRING]
    champion = simulate_match(sf_winners[0], sf_winners[1], ratings, rng)
    return qf_winners, sf_winners, champion


def run_simulation(ratings, n_sims=N_SIMS, seed=42):
    rng = random.Random(seed)
    teams = sorted({t for pair in QUARTERFINALS for t in pair})
    reach_sf = {t: 0 for t in teams}
    reach_final = {t: 0 for t in teams}
    win_title = {t: 0 for t in teams}

    for _ in range(n_sims):
        qf_w, sf_w, champ = simulate_tournament(ratings, rng)
        for t in qf_w:
            reach_sf[t] += 1
        for t in sf_w:
            reach_final[t] += 1
        win_title[champ] += 1

    results = [
        {
            "team": t,
            "elo": round(ratings[t], 1),
            "reach_semis_pct": round(100 * reach_sf[t] / n_sims, 1),
            "reach_final_pct": round(100 * reach_final[t] / n_sims, 1),
            "win_title_pct": round(100 * win_title[t] / n_sims, 1),
        }
        for t in teams
    ]
    results.sort(key=lambda r: -r["win_title_pct"])
    return results


def main():
    ratings = build_current_elo()
    results = run_simulation(ratings)

    with open("models/elo_ratings.pkl", "wb") as f:
        pickle.dump(ratings, f)

    with open("models/simulation_results.pkl", "wb") as f:
        pickle.dump({
            "quarterfinals": QUARTERFINALS,
            "sf_pairing": SF_PAIRING,
            "results": results,
            "n_sims": N_SIMS,
        }, f)

    print(f"Simulated {N_SIMS:,} tournaments.")
    print("Saved models/elo_ratings.pkl and models/simulation_results.pkl")
    for r in results:
        print(f"  {r['team']:<12} win title: {r['win_title_pct']}%")


if __name__ == "__main__":
    main()
