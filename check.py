import pickle

with open("models/simulation_results.pkl", "rb") as f:
    d = pickle.load(f)

print("Keys:", list(d.keys()))
print()
print("Quarterfinals:")
for row in d["quarterfinals"]:
    print(" ", row)
print()
print("Results:")
for row in d["results"]:
    print(" ", row)
print()
print("n_sims:", d.get("n_sims"))