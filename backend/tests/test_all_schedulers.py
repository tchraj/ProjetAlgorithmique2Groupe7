# backend/tests/test_all_schedulers.py
"""
Tests pour tous les algorithmes d'ordonnancement
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.lpt_scheduler import LPTScheduler
from schedulers.spt_scheduler import SPTScheduler
from schedulers.palmer_scheduler import PalmerScheduler
from schedulers.neh_scheduler import NEHScheduler


def test_exemple_simple_tous_algos():
    """Test que tous les algorithmes produisent un résultat valide"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=10, temps_cuisson=15),
        Plat(2, "Plat 2", temps_epluchage=8, temps_cuisson=12),
        Plat(3, "Plat 3", temps_epluchage=5, temps_cuisson=10)
    ]

    stations = {'commis': 2, 'fours': 2}

    # Tester tous les algorithmes
    algorithmes = [
        JohnsonScheduler(),
        LPTScheduler(),
        SPTScheduler(),
        PalmerScheduler(),
        NEHScheduler()
    ]

    resultats = {}

    for algo in algorithmes:
        resultat = algo.schedule(plats, stations)
        nom = algo.get_name()

        # Vérifications de base
        assert 'ordre' in resultat, f"{nom}: 'ordre' manquant"
        assert 'makespan' in resultat, f"{nom}: 'makespan' manquant"
        assert 'schedule_commis' in resultat, f"{nom}: 'schedule_commis' manquant"
        assert 'schedule_fours' in resultat, f"{nom}: 'schedule_fours' manquant"

        assert len(resultat['ordre']) == len(plats), f"{nom}: nombre de plats incorrect"
        assert resultat['makespan'] > 0, f"{nom}: makespan doit être positif"

        resultats[nom] = resultat['makespan']
        print(f"{nom}: makespan = {resultat['makespan']}")

    # Johnson doit être optimal (ou parmi les meilleurs)
    makespan_johnson = resultats["Johnson's Algorithm"]
    print(f"\nComparaison des makespans:")
    for nom, makespan in resultats.items():
        ratio = makespan / makespan_johnson
        print(f"  {nom}: {makespan} (ratio: {ratio:.3f})")


def test_cas_trivial():
    """Test avec un seul plat"""
    plats = [Plat(1, "Plat unique", temps_epluchage=10, temps_cuisson=20)]
    stations = {'commis': 1, 'fours': 1}

    algorithmes = [
        JohnsonScheduler(),
        LPTScheduler(),
        SPTScheduler(),
        PalmerScheduler(),
        NEHScheduler()
    ]

    for algo in algorithmes:
        resultat = algo.schedule(plats, stations)
        # Tous doivent donner le même résultat pour un seul plat
        assert resultat['makespan'] == 30, f"{algo.get_name()}: makespan incorrect pour 1 plat"
        assert len(resultat['ordre']) == 1


def test_multi_stations():
    """Test avec plusieurs stations"""
    plats = [
        Plat(i, f"Plat {i}", temps_epluchage=10+i, temps_cuisson=15+i)
        for i in range(1, 6)
    ]

    stations = {'commis': 3, 'fours': 2}

    algorithmes = [
        JohnsonScheduler(),
        LPTScheduler(),
        SPTScheduler(),
        PalmerScheduler(),
        NEHScheduler()
    ]

    for algo in algorithmes:
        resultat = algo.schedule(plats, stations)
        assert len(resultat['ordre']) == 5
        assert resultat['makespan'] > 0
        assert len(resultat['schedule_commis']) == 3
        assert len(resultat['schedule_fours']) == 2


def test_neh_qualite():
    """Test que NEH donne de bons résultats (souvent proche de Johnson)"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15, temps_cuisson=17),
        Plat(2, "Plat 2", temps_epluchage=11, temps_cuisson=16),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12),
        Plat(4, "Plat 4", temps_epluchage=8, temps_cuisson=14),
        Plat(5, "Plat 5", temps_epluchage=12, temps_cuisson=10)
    ]

    stations = {'commis': 1, 'fours': 1}

    johnson = JohnsonScheduler()
    neh = NEHScheduler()

    resultat_johnson = johnson.schedule(plats, stations)
    resultat_neh = neh.schedule(plats, stations)

    # NEH devrait être proche de Johnson (max 10% de différence en général)
    ratio = resultat_neh['makespan'] / resultat_johnson['makespan']
    print(f"\nJohnson: {resultat_johnson['makespan']}")
    print(f"NEH: {resultat_neh['makespan']}")
    print(f"Ratio NEH/Johnson: {ratio:.3f}")

    assert ratio <= 1.15, f"NEH trop éloigné de l'optimal: ratio = {ratio}"


def test_palmer_vs_johnson():
    """Test que Palmer donne des résultats raisonnables"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=20, temps_cuisson=5),
        Plat(2, "Plat 2", temps_epluchage=5, temps_cuisson=20),
        Plat(3, "Plat 3", temps_epluchage=10, temps_cuisson=10)
    ]

    stations = {'commis': 1, 'fours': 1}

    johnson = JohnsonScheduler()
    palmer = PalmerScheduler()

    resultat_johnson = johnson.schedule(plats, stations)
    resultat_palmer = palmer.schedule(plats, stations)

    print(f"\nJohnson: {resultat_johnson['makespan']}")
    print(f"Palmer: {resultat_palmer['makespan']}")

    # Palmer devrait être raisonnable (pas plus de 60% au-dessus de l'optimal)
    # Note: Palmer est une heuristique simple, peut être sous-optimale sur certains cas
    ratio = resultat_palmer['makespan'] / resultat_johnson['makespan']
    assert ratio <= 1.6, f"Palmer trop éloigné de l'optimal: ratio = {ratio}"


if __name__ == "__main__":
    print("=== Test exemple simple ===")
    test_exemple_simple_tous_algos()

    print("\n=== Test cas trivial ===")
    test_cas_trivial()

    print("\n=== Test multi-stations ===")
    test_multi_stations()

    print("\n=== Test qualité NEH ===")
    test_neh_qualite()

    print("\n=== Test Palmer vs Johnson ===")
    test_palmer_vs_johnson()

    print("\n✅ Tous les tests sont passés!")

