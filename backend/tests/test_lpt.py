# backend/tests/test_lpt.py
"""
Tests unitaires pour l'algorithme LPT (Longest Processing Time First)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.lpt_scheduler import LPTScheduler


def test_lpt_ordre_decroissant():
    """Vérifie que LPT trie bien par temps total décroissant"""
    plats = [
        Plat(1, "Court", temps_epluchage=5*60, temps_cuisson=5*60),      # Total: 10min
        Plat(2, "Moyen", temps_epluchage=10*60, temps_cuisson=15*60),    # Total: 25min
        Plat(3, "Long", temps_epluchage=20*60, temps_cuisson=20*60)      # Total: 40min
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre devrait être : Long (40min), Moyen (25min), Court (10min)
    ordre = resultat['ordre']
    assert ordre[0].id == 3  # Long
    assert ordre[1].id == 2  # Moyen
    assert ordre[2].id == 1  # Court


def test_lpt_exemple_1():
    """Test LPT sur l'exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),  # Total: 32min
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),  # Total: 27min
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)       # Total: 12min
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3
    assert resultat['nom_algorithme'] == "LPT (Longest Processing Time First)"

    # L'ordre devrait être : Plat1 (32), Plat2 (27), Plat3 (12)
    ordre_ids = [p.id for p in resultat['ordre']]
    assert ordre_ids == [1, 2, 3]


def test_lpt_multi_stations():
    """Test LPT avec plusieurs commis et fours"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60),
        Plat(3, "Plat C", temps_epluchage=12*60, temps_cuisson=10*60),
        Plat(4, "Plat D", temps_epluchage=5*60, temps_cuisson=18*60),
        Plat(5, "Plat E", temps_epluchage=15*60, temps_cuisson=12*60)
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 5
    assert len(resultat['schedule_commis']) == 2
    assert len(resultat['schedule_fours']) == 2

    # Le makespan devrait être inférieur au cas avec 1 seule station
    resultat_1station = scheduler.schedule(plats, {'commis': 1, 'fours': 1})
    assert resultat['makespan'] <= resultat_1station['makespan']


def test_lpt_equilibrage_charge():
    """Vérifie que LPT équilibre bien la charge entre les stations"""
    plats = [
        Plat(i, f"Plat {i}", temps_epluchage=10*60, temps_cuisson=10*60)
        for i in range(1, 7)  # 6 plats identiques
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 3, 'fours': 2})

    # Avec 3 commis, chacun devrait avoir 2 plats
    charge_commis = [len(schedule) for schedule in resultat['schedule_commis']]
    assert sum(charge_commis) == 6  # Total de 6 plats
    # La différence de charge ne devrait pas être trop grande
    assert max(charge_commis) - min(charge_commis) <= 1


def test_lpt_cas_limite_1_plat():
    """Test avec un seul plat"""
    plats = [
        Plat(1, "Unique", temps_epluchage=10*60, temps_cuisson=15*60)
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == (10 + 15) * 60
    assert len(resultat['ordre']) == 1


def test_lpt_cas_limite_liste_vide():
    """Test avec liste vide"""
    plats = []

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == 0
    assert len(resultat['ordre']) == 0


def test_lpt_coherence_temps():
    """Vérifie que les temps sont cohérents dans le planning"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60)
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifier que chaque plat cuit après avoir été préparé
    for plat in resultat['ordre']:
        # Trouver quand il a été préparé
        fin_prep = None
        for commis_schedule in resultat['schedule_commis']:
            for tache in commis_schedule:
                if tache['plat'].id == plat.id:
                    fin_prep = tache['fin']
                    break
            if fin_prep:
                break

        # Trouver quand il a été cuit
        debut_cuisson = None
        for four_schedule in resultat['schedule_fours']:
            for tache in four_schedule:
                if tache['plat'].id == plat.id:
                    debut_cuisson = tache['debut']
                    break
            if debut_cuisson:
                break

        # La cuisson doit commencer après (ou au moment de) la fin de préparation
        assert debut_cuisson >= fin_prep, \
            f"Plat {plat.id}: cuisson commence à {debut_cuisson} mais préparation finit à {fin_prep}"


def test_lpt_temps_egaux():
    """Test avec des plats ayant le même temps total"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=15*60, temps_cuisson=5*60),   # Total: 20min
        Plat(2, "Plat B", temps_epluchage=10*60, temps_cuisson=10*60),  # Total: 20min
        Plat(3, "Plat C", temps_epluchage=5*60, temps_cuisson=15*60)    # Total: 20min
    ]

    scheduler = LPTScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Doit traiter tous les plats sans erreur
    assert len(resultat['ordre']) == 3
    assert resultat['makespan'] > 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

