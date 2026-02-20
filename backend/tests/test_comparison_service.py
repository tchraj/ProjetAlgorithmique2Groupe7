# backend/tests/test_comparison_service.py
"""
Tests pour le service de comparaison des algorithmes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.spt_scheduler import SPTScheduler
from schedulers.lpt_scheduler import LPTScheduler
from schedulers.neh_scheduler import NEHScheduler
from schedulers.palmer_scheduler import PalmerScheduler
from services.comparison_service import ComparisonService


def test_comparison_basic():
    """Test basique de comparaison entre plusieurs algorithmes"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        SPTScheduler(),
        LPTScheduler(),
        NEHScheduler(),
        PalmerScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1})

    # Vérifications
    assert len(resultat['resultats']) == 5
    assert resultat['nb_plats'] == 3
    assert resultat['meilleur'] is not None
    assert resultat['meilleur_makespan'] > 0

    # Vérifier que tous les résultats ont les champs nécessaires
    for res in resultat['resultats']:
        assert 'algorithme' in res
        assert 'makespan' in res
        assert 'temps_execution' in res
        assert 'ratio_vs_meilleur' in res
        assert 'ecart_absolu' in res
        assert 'ecart_relatif_pct' in res


def test_comparison_avec_optimal():
    """Test de comparaison avec makespan optimal fourni"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        SPTScheduler(),
        LPTScheduler()
    ]

    service = ComparisonService(schedulers)
    makespan_optimal = 45 * 60  # Par exemple, 45 minutes

    resultat = service.compare(plats, {'commis': 1, 'fours': 1}, makespan_optimal)

    # Vérifier que les ratios et écarts vs optimal sont calculés
    assert resultat['makespan_optimal'] == makespan_optimal

    for res in resultat['resultats']:
        assert 'ratio_vs_optimal' in res
        assert 'ecart_vs_optimal' in res
        assert 'ecart_vs_optimal_pct' in res
        assert res['ratio_vs_optimal'] >= 1.0  # Toujours >= optimal


def test_comparison_meilleur_algorithme():
    """Vérifie que le meilleur algorithme est correctement identifié"""
    plats = [
        Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=20*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        LPTScheduler(),
        NEHScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1})

    # Le meilleur doit avoir ratio_vs_meilleur = 1.0
    meilleur = resultat['meilleur']
    meilleur_makespan = resultat['meilleur_makespan']

    # Trouver ce résultat dans la liste
    meilleur_dans_liste = next(
        r for r in resultat['resultats']
        if r['algorithme'] == meilleur['algorithme']
    )

    assert meilleur_dans_liste['ratio_vs_meilleur'] == 1.0
    assert meilleur_dans_liste['ecart_absolu'] == 0
    assert meilleur_dans_liste['makespan'] == meilleur_makespan


def test_comparison_statistiques():
    """Test des statistiques calculées"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=10*60, temps_cuisson=10*60),
        Plat(2, "Plat 2", temps_epluchage=10*60, temps_cuisson=10*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        SPTScheduler(),
        LPTScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1})

    stats = resultat['statistiques']

    # Vérifier les statistiques
    assert stats['nb_algorithmes'] == 3
    assert stats['makespan_min'] > 0
    assert stats['makespan_max'] >= stats['makespan_min']
    assert stats['makespan_moyen'] > 0
    assert stats['temps_exec_moyen'] >= 0
    assert stats['temps_exec_total'] >= 0


def test_comparison_batch():
    """Test de comparaison sur un lot d'instances"""
    instances = [
        {
            'nom': 'instance_1',
            'plats': [
                Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=15*60),
                Plat(2, "Plat B", temps_epluchage=8*60, temps_cuisson=12*60)
            ],
            'stations': {'commis': 1, 'fours': 1}
        },
        {
            'nom': 'instance_2',
            'plats': [
                Plat(1, "Plat C", temps_epluchage=5*60, temps_cuisson=10*60),
                Plat(2, "Plat D", temps_epluchage=12*60, temps_cuisson=8*60),
                Plat(3, "Plat E", temps_epluchage=7*60, temps_cuisson=14*60)
            ],
            'stations': {'commis': 2, 'fours': 1}
        }
    ]

    schedulers = [
        JohnsonScheduler(),
        LPTScheduler(),
        NEHScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare_batch(instances)

    # Vérifications
    assert resultat['nb_instances'] == 2
    assert len(resultat['instances']) == 2

    # Vérifier les statistiques agrégées
    stats_agregees = resultat['statistiques_agregees']
    assert len(stats_agregees) == 3  # 3 algorithmes

    for algo_nom, stats in stats_agregees.items():
        assert 'makespan_moyen' in stats
        assert 'ratio_moyen_vs_meilleur' in stats
        assert 'temps_exec_moyen' in stats
        assert 'nb_fois_meilleur' in stats
        assert 'pct_meilleur' in stats


def test_comparison_batch_avec_optimaux():
    """Test de comparaison batch avec makespans optimaux"""
    instances = [
        {
            'nom': 'instance_facile',
            'plats': [
                Plat(1, "Plat A", temps_epluchage=10*60, temps_cuisson=10*60)
            ],
            'stations': {'commis': 1, 'fours': 1}
        },
        {
            'nom': 'instance_moyenne',
            'plats': [
                Plat(1, "Plat B", temps_epluchage=15*60, temps_cuisson=20*60),
                Plat(2, "Plat C", temps_epluchage=10*60, temps_cuisson=15*60)
            ],
            'stations': {'commis': 1, 'fours': 1}
        }
    ]

    makespan_optimaux = {
        'instance_facile': 20 * 60,
        'instance_moyenne': 60 * 60
    }

    schedulers = [
        JohnsonScheduler(),
        NEHScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare_batch(instances, makespan_optimaux)

    # Vérifier que les ratios vs optimal sont calculés
    for instance_result in resultat['instances']:
        assert instance_result['makespan_optimal'] is not None
        for res in instance_result['resultats']:
            assert 'ratio_vs_optimal' in res


def test_comparison_liste_vide():
    """Test avec liste de plats vide"""
    plats = []

    schedulers = [JohnsonScheduler(), LPTScheduler()]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1})

    # Doit retourner une comparaison vide sans erreur
    assert resultat['nb_plats'] == 0
    assert resultat['meilleur_makespan'] == 0


def test_comparison_temps_execution():
    """Vérifie que les temps d'exécution sont mesurés"""
    plats = [
        Plat(i, f"Plat {i}", temps_epluchage=10*60, temps_cuisson=10*60)
        for i in range(1, 11)  # 10 plats
    ]

    schedulers = [
        JohnsonScheduler(),
        NEHScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 2, 'fours': 2})

    # Tous les résultats doivent avoir un temps d'exécution > 0
    for res in resultat['resultats']:
        assert res['temps_execution'] >= 0


def test_comparison_coherence_ratios():
    """Vérifie la cohérence des ratios calculés"""
    plats = [
        Plat(1, "Plat 1", temps_epluchage=15*60, temps_cuisson=20*60),
        Plat(2, "Plat 2", temps_epluchage=10*60, temps_cuisson=15*60),
        Plat(3, "Plat 3", temps_epluchage=12*60, temps_cuisson=18*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        LPTScheduler(),
        NEHScheduler(),
        PalmerScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 1, 'fours': 1})

    meilleur_makespan = resultat['meilleur_makespan']

    for res in resultat['resultats']:
        # ratio = makespan / meilleur_makespan
        ratio_attendu = res['makespan'] / meilleur_makespan
        assert abs(res['ratio_vs_meilleur'] - ratio_attendu) < 0.001  # Tolérance numérique

        # écart_absolu = makespan - meilleur_makespan
        ecart_attendu = res['makespan'] - meilleur_makespan
        assert res['ecart_absolu'] == ecart_attendu

        # écart_relatif = (makespan - meilleur) / meilleur * 100
        ecart_rel_attendu = (res['makespan'] - meilleur_makespan) / meilleur_makespan * 100
        assert abs(res['ecart_relatif_pct'] - ecart_rel_attendu) < 0.001


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

