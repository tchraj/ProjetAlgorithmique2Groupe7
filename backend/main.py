# backend/main.py ou test.py
from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler

# Exemple 1 de l'énoncé
plats = [
    Plat(1, "Plat 1", temps_preparation=15, temps_cuisson=17),
    Plat(2, "Plat 2", temps_preparation=11, temps_cuisson=16),
    Plat(3, "Plat 3", temps_preparation=0, temps_cuisson=12)
]

scheduler = JohnsonScheduler()
resultat = scheduler.schedule(
    plats=plats,
    stations={'commis': 1, 'fours': 1}
)

print(f"Ordre optimal: {[p.nom for p in resultat['ordre']]}")
print(f"Makespan: {resultat['makespan']} minutes")

# Afficher le planning
print("\n=== Planning Commis ===")
for i, taches in enumerate(resultat['schedule_commis']):
    print(f"Commis {i+1}:")
    for tache in taches:
        print(f"  {tache['plat'].nom}: {tache['debut']}-{tache['fin']}min")

print("\n=== Planning Fours ===")
for i, taches in enumerate(resultat['schedule_fours']):
    print(f"Four {i+1}:")
    for tache in taches:
        print(f"  {tache['plat'].nom}: {tache['debut']}-{tache['fin']}min")