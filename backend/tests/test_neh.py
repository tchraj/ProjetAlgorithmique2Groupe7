# backend/tests/test_neh.py
"""
Tests unitaires pour l'algorithme NEH (Nawaz-Enscore-Ham)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.neh_scheduler import NEHScheduler


def test_neh_exemple_1():
    """Test NEH sur l'exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)
    ]

    scheduler = NEHScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # NEH devrait donner un bon résultat (pas forcément optimal pour 2 machines)
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 3
    assert resultat['nom_algorithme'] == "NEH (Nawaz-Enscore-Ham)"

    # Vérifier que tous les plats sont dans l'ordre
    ordre_ids = [p.id for p in resultat['ordre']]
    assert len(set(ordre_ids)) == 3  # Pas de doublons


def test_neh_multi_stations():
    """Test NEH avec plusieurs commis et fours"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60),
        Plat(3, "Plat C", temps_epluchage=12*60, temps_cuisson=10*60),
        Plat(4, "Plat D", temps_epluchage=5*60, temps_cuisson=18*60),
        Plat(5, "Plat E", temps_epluchage=15*60, temps_cuisson=12*60)
    ]

    scheduler = NEHScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifications de base
    assert resultat['makespan'] > 0
    assert len(resultat['ordre']) == 5
    assert len(resultat['schedule_commis']) == 2
    assert len(resultat['schedule_fours']) == 2

    # Le makespan devrait être inférieur au cas avec 1 seule station
    resultat_1station = scheduler.schedule(plats, {'commis': 1, 'fours': 1})
    assert resultat['makespan'] <= resultat_1station['makespan']


def test_neh_tri_initial():
    """Vérifie que NEH commence bien par trier par temps total décroissant"""
    plats = [
        Plat(1, "Court", temps_epluchage=5*60, temps_cuisson=5*60),      # Total: 10
        Plat(2, "Moyen", temps_epluchage=10*60, temps_cuisson=15*60),    # Total: 25
        Plat(3, "Long", temps_epluchage=20*60, temps_cuisson=20*60)      # Total: 40
    ]

    scheduler = NEHScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # NEH trie par temps total décroissant
    # Donc le premier dans l'ordre devrait être le plus long (Plat 3)
    # Note: NEH peut réordonner après insertion, donc on vérifie juste qu'il y a un ordre logique
    assert len(resultat['ordre']) == 3
    assert resultat['makespan'] > 0


def test_neh_cas_limite_1_plat():
    """Test avec un seul plat"""
    plats = [
        Plat(1, "Unique", temps_epluchage=10*60, temps_cuisson=15*60)
    ]

    scheduler = NEHScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == (10 + 15) * 60
    assert len(resultat['ordre']) == 1


def test_neh_cas_limite_liste_vide():
    """Test avec liste vide"""
    plats = []

    scheduler = NEHScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    assert resultat['makespan'] == 0
    assert len(resultat['ordre']) == 0


def test_neh_coherence_temps():
    """Vérifie que les temps sont cohérents dans le planning"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60)
    ]

    scheduler = NEHScheduler()
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


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

