# Test rapide de la configuration finale
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.neh_scheduler import NEHScheduler
from schedulers.palmer_scheduler import PalmerScheduler
from schedulers.cds_scheduler import CDSScheduler
from schedulers.fifo_scheduler import FIFOScheduler
from services.comparison_service import ComparisonService

def test_configuration_finale():
    """Test rapide de la configuration finale sur l'Exemple 1 de l'énoncé"""
    print("=" * 80)
    print("TEST DE LA CONFIGURATION FINALE")
    print("Exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four")
    print("=" * 80)

    # Exemple 1 de l'énoncé
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)
    ]

    # Configuration finale des algorithmes
    schedulers = [
        JohnsonScheduler(),
        NEHScheduler(),
        PalmerScheduler(),
        CDSScheduler(),
        FIFOScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1}, makespan_optimal=45*60)

    print("\nRÉSULTATS:")
    print("-" * 80)
    print(f"{'Algorithme':<30} {'Makespan':<15} {'Ratio vs opt':<15} {'Optimal?':<10}")
    print("-" * 80)

    for res in sorted(resultat['resultats'], key=lambda r: r['makespan']):
        algo = res['algorithme']
        makespan_min = res['makespan'] // 60
        ratio = res.get('ratio_vs_optimal', 0)
        optimal = "✅ OUI" if ratio == 1.0 else "❌ NON"

        print(f"{algo:<30} {makespan_min:>3} min {'':<8} {ratio:<15.3f} {optimal:<10}")

    print("-" * 80)
    print(f"\nMeilleur algorithme: {resultat['meilleur']['algorithme']}")
    print(f"Makespan optimal: {resultat['makespan_optimal'] // 60} min")

    # Vérifications
    print("\n" + "=" * 80)
    print("VÉRIFICATIONS:")
    print("=" * 80)

    # Johnson et CDS devraient trouver l'optimal
    johnson_res = next(r for r in resultat['resultats'] if 'Johnson' in r['algorithme'])
    cds_res = next(r for r in resultat['resultats'] if 'CDS' in r['algorithme'])

    checks = [
        ("Johnson trouve l'optimal", johnson_res['makespan'] == 45*60),
        ("CDS trouve l'optimal", cds_res['makespan'] == 45*60),
        ("Tous les algorithmes testés", len(resultat['resultats']) == 5),
        ("Ratio vs optimal calculé", 'ratio_vs_optimal' in johnson_res),
        ("Ordre optimal trouvé", len(resultat['meilleur']['ordre']) == 3)
    ]

    for check, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check}")

    all_ok = all(result for _, result in checks)
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ CONFIGURATION FINALE VALIDÉE - TOUS LES TESTS PASSENT")
    else:
        print("❌ PROBLÈME DÉTECTÉ")
    print("=" * 80)

    return all_ok

if __name__ == "__main__":
    success = test_configuration_finale()
    sys.exit(0 if success else 1)

