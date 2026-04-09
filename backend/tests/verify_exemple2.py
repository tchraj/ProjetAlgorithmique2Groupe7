# Script de vérification pour le test_exemple_2
import sys
sys.path.insert(0, '..')

from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler

plats = [
    Plat(1, "Plat 1", temps_prep=16, temps_cuisson=10),
    Plat(2, "Plat 2", temps_prep=14, temps_cuisson=14),
    Plat(3, "Plat 3", temps_prep=11, temps_cuisson=8)
]

print("Analyse Johnson:")
print("-" * 60)
for p in plats:
    categorie = "Set1 (epl<cuis)" if p.temps_prep < p.temps_cuisson else "Set2 (epl>=cuis)"
    print(f"Plat {p.id}: epl={p.temps_prep}, cuis={p.temps_cuisson} → {categorie}")

scheduler = JohnsonScheduler()
resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

print(f"\nOrdre optimal Johnson: {[p.id for p in resultat['ordre']]}")
print(f"Makespan: {resultat['makespan']}")

# Calcul manuel détaillé
print("\n" + "="*60)
print("CALCUL DÉTAILLÉ DU MAKESPAN")
print("="*60)

ordre = resultat['ordre']
temps_prep = 0
temps_four = 0

for i, plat in enumerate(ordre, 1):
    debut_prep = temps_prep
    fin_prep = debut_prep + plat.temps_prep

    debut_cuisson = max(fin_prep, temps_four)
    fin_cuisson = debut_cuisson + plat.temps_cuisson

    print(f"\nPlat {plat.id}:")
    print(f"  Préparation: [{debut_prep:2d} → {fin_prep:2d}] (durée: {plat.temps_prep})")
    print(f"  Cuisson:     [{debut_cuisson:2d} → {fin_cuisson:2d}] (durée: {plat.temps_cuisson})")

    temps_prep = fin_prep
    temps_four = fin_cuisson

print(f"\n{'='*60}")
print(f"MAKESPAN FINAL: {temps_four}")
print(f"{'='*60}")

