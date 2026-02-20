# backend/tests/test_cds.py
"""
Tests unitaires pour l'algorithme CDS (Campbell-Dudek-Smith)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.cds_scheduler import CDSScheduler


def test_cds_exemple_1():
    """Test CDS sur l'exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)
    ]

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # CDS devrait donner le même résultat que Johnson pour 2 machines
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3
    assert resultat['nom_algorithme'] == "CDS (Campbell-Dudek-Smith)"

    # Vérifier que tous les plats sont dans l'ordre
    ordre_ids = [p.id for p in resultat['ordre']]
    assert len(set(ordre_ids)) == 3  # Pas de doublons


def test_cds_multi_stations():
    """Test CDS avec plusieurs commis et fours"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60),
        Plat(3, "Plat C", temps_epluchage=12*60, temps_cuisson=10*60),
        Plat(4, "Plat D", temps_epluchage=5*60, temps_cuisson=18*60),
        Plat(5, "Plat E", temps_epluchage=15*60, temps_cuisson=12*60)
    ]

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 5
    assert len(resultat['schedule_commis']) == 2
    assert len(resultat['schedule_fours']) == 2

    # Le makespan devrait être inférieur au cas avec 1 seule station
    resultat_1station = scheduler.schedule(plats, {'commis': 1, 'fours': 1})
    assert resultat['makespan'] <= resultat_1station['makespan']


def test_cds_ordre_johnson():
    """Vérifie que CDS applique bien la règle de Johnson pour 2 machines"""
    plats = [
        # Plats avec prep < cuisson → doivent aller au début
        Plat(1, "Prep courte", temps_epluchage=5*60, temps_cuisson=20*60),
        # Plats avec prep > cuisson → doivent aller à la fin
        Plat(2, "Prep longue", temps_epluchage=25*60, temps_cuisson=10*60),
        Plat(3, "Équilibré", temps_epluchage=15*60, temps_cuisson=15*60)
    ]

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # CDS devrait appliquer Johnson : prep courte au début
    ordre = resultat['ordre']
    # Premier plat devrait avoir prep <= cuisson
    assert ordre[0].temps_epluchage <= ordre[0].temps_cuisson


def test_cds_cas_limite_1_plat():
    """Test avec un seul plat"""
    plats = [
        Plat(1, "Unique", temps_epluchage=10*60, temps_cuisson=15*60)
    ]

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == (10 + 15) * 60
    assert len(resultat['ordre']) == 1


def test_cds_cas_limite_liste_vide():
    """Test avec liste vide"""
    plats = []

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == 0
    assert len(resultat['ordre']) == 0


def test_cds_coherence_temps():
    """Vérifie que les temps sont cohérents dans le planning"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60)
    ]

    scheduler = CDSScheduler()
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


def test_cds_exemple_2():
    """Test CDS sur l'exemple 2 de l'énoncé"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=16*60, temps_cuisson=10*60),
        Plat(2, "Plat 2", temps_epluchage=2*60, temps_cuisson=14*60),
        Plat(3, "Plat 3", temps_epluchage=11*60, temps_cuisson=8*60)
    ]

    scheduler = CDSScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifier que le makespan est raisonnable
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

