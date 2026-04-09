# backend/tests/test_fifo.py
"""
Tests unitaires pour l'algorithme FIFO (First In First Out)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.fifo_scheduler import FIFOScheduler


def test_fifo_ordre_preserved():
    """Vérifie que FIFO préserve l'ordre d'arrivée"""
    plats = [
        Plat(1, "Premier", temps_prep=10*60, temps_cuisson=15*60),
        Plat(2, "Deuxième", temps_prep=5*60, temps_cuisson=20*60),
        Plat(3, "Troisième", temps_prep=15*60, temps_cuisson=10*60)
    ]

    scheduler = FIFOScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre doit être exactement celui d'entrée
    ordre = resultat['ordre']
    assert ordre[0].id == 1  # Premier
    assert ordre[1].id == 2  # Deuxième
    assert ordre[2].id == 3  # Troisième


def test_fifo_exemple_1():
    """Test FIFO sur l'exemple 1 de l'énoncé"""
    plats = [
        Plat(1, "Plat 1", temps_prep=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_prep=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_prep=0, temps_cuisson=12*60)
    ]

    scheduler = FIFOScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3
    assert resultat['nom_algorithme'] == "FIFO (First In First Out)"

    # L'ordre doit être 1, 2, 3
    ordre_ids = [p.id for p in resultat['ordre']]
    assert ordre_ids == [1, 2, 3]


def test_fifo_vs_optimal():
    """Vérifie que FIFO donne généralement un résultat sous-optimal"""
    # Exemple où FIFO n'est pas optimal
    plats = [
        Plat(1, "Long", temps_prep=20*60, temps_cuisson=20*60),    # Long
        Plat(2, "Court", temps_prep=5*60, temps_cuisson=5*60)      # Court
    ]

    from schedulers.johnson_scheduler import JohnsonScheduler

    fifo = FIFOScheduler()
    johnson = JohnsonScheduler()

    resultat_fifo = fifo.schedule(plats, {'commis': 1, 'fours': 1})
    resultat_johnson = johnson.schedule(plats, {'commis': 1, 'fours': 1})

    # Johnson devrait être au moins aussi bon que FIFO
    assert resultat_johnson['makespan'] <= resultat_fifo['makespan']


def test_fifo_multi_stations():
    """Test FIFO avec plusieurs commis et fours"""
    plats = [
        Plat(1, "Plat A", temps_prep=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_prep=8*60, temps_cuisson=20*60),
        Plat(3, "Plat C", temps_prep=12*60, temps_cuisson=10*60),
        Plat(4, "Plat D", temps_prep=5*60, temps_cuisson=18*60)
    ]

    scheduler = FIFOScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 4
    assert len(resultat['schedule_commis']) == 2
    assert len(resultat['schedule_fours']) == 2

    # L'ordre doit être préservé
    ordre_ids = [p.id for p in resultat['ordre']]
    assert ordre_ids == [1, 2, 3, 4]


def test_fifo_cas_limite_1_plat():
    """Test avec un seul plat"""
    plats = [
        Plat(1, "Unique", temps_prep=10*60, temps_cuisson=15*60)
    ]

    scheduler = FIFOScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == (10 + 15) * 60
    assert len(resultat['ordre']) == 1


def test_fifo_cas_limite_liste_vide():
    """Test avec liste vide"""
    plats = []

    scheduler = FIFOScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == 0
    assert len(resultat['ordre']) == 0


def test_fifo_coherence_temps():
    """Vérifie que les temps sont cohérents dans le planning"""
    plats = [
        Plat(1, "Plat A", temps_prep=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_prep=8*60, temps_cuisson=20*60)
    ]

    scheduler = FIFOScheduler()
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


def test_fifo_baseline():
    """FIFO doit servir de baseline : généralement le moins performant"""
    plats = [
        Plat(3, "C", temps_prep=15*60, temps_cuisson=10*60),
        Plat(1, "A", temps_prep=5*60, temps_cuisson=20*60),
        Plat(2, "B", temps_prep=10*60, temps_cuisson=15*60)
    ]

    # FIFO garde l'ordre 3, 1, 2
    fifo = FIFOScheduler()
    resultat_fifo = fifo.schedule(plats, {'commis': 1, 'fours': 1})

    # L'ordre FIFO doit être celui d'entrée
    assert [p.id for p in resultat_fifo['ordre']] == [3, 1, 2]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

