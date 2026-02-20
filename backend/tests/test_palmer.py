# backend/tests/test_palmer.py
"""
Tests unitaires pour l'algorithme de Palmer
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.palmer_scheduler import PalmerScheduler


def test_palmer_slope_index():
    """Vérifie que Palmer trie bien par slope index (prep - cuisson) décroissant"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=20*60, temps_cuisson=5*60),   # Slope: +15min
        Plat(2, "Plat B", temps_epluchage=10*60, temps_cuisson=10*60),  # Slope: 0
        Plat(3, "Plat C", temps_epluchage=5*60, temps_cuisson=20*60)    # Slope: -15min
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre devrait être : A (slope +15), B (slope 0), C (slope -15)
    ordre = resultat['ordre']
    assert ordre[0].id == 1  # Plat A
    assert ordre[1].id == 2  # Plat B
    assert ordre[2].id == 3  # Plat C


def test_palmer_exemple_1():
    """Test Palmer sur l'exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),  # Slope: -2min
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),  # Slope: -5min
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)       # Slope: -12min
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3
    assert resultat['nom_algorithme'] == "Palmer's Algorithm"

    # L'ordre par slope décroissant: Plat1 (-2), Plat2 (-5), Plat3 (-12)
    ordre_ids = [p.id for p in resultat['ordre']]
    assert ordre_ids == [1, 2, 3]


def test_palmer_multi_stations():
    """Test Palmer avec plusieurs commis et fours"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60),
        Plat(3, "Plat C", temps_epluchage=12*60, temps_cuisson=10*60),
        Plat(4, "Plat D", temps_epluchage=5*60, temps_cuisson=18*60),
        Plat(5, "Plat E", temps_epluchage=15*60, temps_cuisson=12*60)
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 5
    assert len(resultat['schedule_commis']) == 2
    assert len(resultat['schedule_fours']) == 2

    # Le makespan devrait être inférieur au cas avec 1 seule station
    resultat_1station = scheduler.schedule(plats, {'commis': 1, 'fours': 1})
    assert resultat['makespan'] <= resultat_1station['makespan']


def test_palmer_principe_slope():
    """
    Test le principe de Palmer : privilégier les plats avec préparation longue
    et cuisson courte au début (pour éviter idle time au four)
    """
    plats = [
        Plat(1, "Prep longue, cuisson courte", temps_epluchage=30*60, temps_cuisson=5*60),  # Slope: +25
        Plat(2, "Prep courte, cuisson longue", temps_epluchage=5*60, temps_cuisson=30*60)   # Slope: -25
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Palmer devrait mettre le plat 1 en premier (slope positif élevé)
    ordre = resultat['ordre']
    assert ordre[0].id == 1
    assert ordre[1].id == 2


def test_palmer_cas_limite_1_plat():
    """Test avec un seul plat"""
    plats = [
        Plat(1, "Unique", temps_epluchage=10*60, temps_cuisson=15*60)
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == (10 + 15) * 60
    assert len(resultat['ordre']) == 1


def test_palmer_cas_limite_liste_vide():
    """Test avec liste vide"""
    plats = []

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == 0
    assert len(resultat['ordre']) == 0


def test_palmer_coherence_temps():
    """Vérifie que les temps sont cohérents dans le planning"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60)
    ]

    scheduler = PalmerScheduler()
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


def test_palmer_slopes_negatifs():
    """Test avec tous les slopes négatifs (cuisson > préparation)"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=5*60, temps_cuisson=20*60),   # Slope: -15
        Plat(2, "Plat B", temps_epluchage=3*60, temps_cuisson=25*60),   # Slope: -22
        Plat(3, "Plat C", temps_epluchage=7*60, temps_cuisson=18*60)    # Slope: -11
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre devrait être : C (-11), A (-15), B (-22)
    ordre = resultat['ordre']
    assert ordre[0].id == 3  # C, slope le moins négatif
    assert ordre[1].id == 1  # A
    assert ordre[2].id == 2  # B, slope le plus négatif


def test_palmer_slopes_positifs():
    """Test avec tous les slopes positifs (préparation > cuisson)"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=20*60, temps_cuisson=5*60),   # Slope: +15
        Plat(2, "Plat B", temps_epluchage=25*60, temps_cuisson=3*60),   # Slope: +22
        Plat(3, "Plat C", temps_epluchage=18*60, temps_cuisson=7*60)    # Slope: +11
    ]

    scheduler = PalmerScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre devrait être : B (+22), A (+15), C (+11)
    ordre = resultat['ordre']
    assert ordre[0].id == 2  # B, slope le plus élevé
    assert ordre[1].id == 1  # A
    assert ordre[2].id == 3  # C


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

