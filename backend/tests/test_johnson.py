# backend/tests/test_johnson.py
import pytest
from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler


def test_exemple_1():
    """Exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    plats = [
        Plat(1, "Plat 1", temps_prep=15, temps_cuisson=17),
        Plat(2, "Plat 2", temps_prep=11, temps_cuisson=16),
        Plat(3, "Plat 3", temps_prep=0, temps_cuisson=12)
    ]

    scheduler = JohnsonScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifier l'ordre optimal
    ordre = [p.id for p in resultat['ordre']]
    assert ordre == [3, 2, 1], f"Ordre incorrect : {ordre}"

    # Vérifier le makespan
    makespan_attendu = 45  # À calculer manuellement
    assert resultat['makespan'] == makespan_attendu, \
        f"Makespan incorrect : {resultat['makespan']} (attendu : {makespan_attendu})"


def test_exemple_2_sujet():
    """Test avec l'Exemple 2 du sujet (ppage 3)"""
    plats = [
        Plat(1, "Plat 1", temps_prep=16, temps_cuisson=10),
        Plat(2, "Plat 2", temps_prep=14, temps_cuisson=14),
        Plat(3, "Plat 3", temps_prep=11, temps_cuisson=8)
    ]

    scheduler = JohnsonScheduler()
    resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})

    # Vérifier l'ordre optimal
    ordre_optimal = [2, 1, 3]  # Plat 2 → Plat 1 → Plat 3
    assert [p.id for p in resultat['ordre']] == ordre_optimal

    # Vérifier le makespan    # Calcul: Plat2[0-14,14-28], Plat1[14-30,30-40], Plat3[30-41,41-49]
    assert resultat['makespan'] == 49

def test_multi_stations():
    """Test avec 2 commis et 2 fours"""
    plats = [
        Plat(1, "Plat 1", temps_prep=10, temps_cuisson=15),
        Plat(2, "Plat 2", temps_prep=8, temps_cuisson=12),
        Plat(3, "Plat 3", temps_prep=12, temps_cuisson=10),
        Plat(4, "Plat 4", temps_prep=5, temps_cuisson=8)
    ]

    scheduler = JohnsonScheduler()
    resultat = scheduler.schedule(plats, {'commis': 2, 'fours': 2})

    # Vérifier que chaque commis a des tâches
    assert all(len(c) > 0 for c in resultat['schedule_commis'])

    # Vérifier que chaque four a des tâches
    assert all(len(f) > 0 for f in resultat['schedule_fours'])

    # Vérifier qu'il n'y a pas de chevauchement
    for commis in resultat['schedule_commis']:
        for i in range(len(commis) - 1):
            assert commis[i]['fin'] <= commis[i + 1]['debut']


