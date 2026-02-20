# backend/algorithms/comparaison_algorithmes.py
"""
Script de comparaison des performances des différents algorithmes d'ordonnancement
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
import time
from typing import List, Dict, Any


class ComparateurAlgorithmes:
    """Compare les performances de différents algorithmes d'ordonnancement"""

    def __init__(self):
        self.algorithmes = [
            JohnsonScheduler(),
            LPTScheduler(),
            SPTScheduler(),
            PalmerScheduler(),
            NEHScheduler()
        ]

    def comparer(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Compare tous les algorithmes sur une instance donnée

        Returns:
            Dictionnaire avec les résultats de chaque algorithme
        """
        resultats = {}

        for algo in self.algorithmes:
            nom = algo.get_name()

            # Mesurer le temps d'exécution
            debut = time.time()
            resultat = algo.schedule(plats, stations)
            temps_exec = time.time() - debut

            resultats[nom] = {
                'makespan': resultat['makespan'],
                'temps_execution': temps_exec,
                'ordre': [p.id for p in resultat['ordre']],
                'details': resultat.get('details', {})
            }

        # Trouver le meilleur makespan parmi les algorithmes testés
        # Note: C'est la meilleure solution TROUVÉE, pas forcément l'optimal théorique
        # Pour 1 commis + 1 four : Johnson est garanti optimal
        # Pour m commis + k fours : le meilleur est une borne supérieure de l'optimal
        meilleur_makespan = min(r['makespan'] for r in resultats.values())
        meilleur_algo_nom = min(resultats.keys(), key=lambda k: resultats[k]['makespan'])

        # Déterminer si on a probablement l'optimal
        est_probablement_optimal = (meilleur_algo_nom == "Johnson's Algorithm" and
                                     stations.get('commis', 0) == 1 and
                                     stations.get('fours', 0) == 1)

        # Calculer les ratios par rapport au meilleur trouvé
        for nom in resultats:
            resultats[nom]['ratio_optimal'] = resultats[nom]['makespan'] / meilleur_makespan
            resultats[nom]['ecart_percent'] = ((resultats[nom]['makespan'] - meilleur_makespan)
                                                / meilleur_makespan * 100)

        return {
            'resultats': resultats,
            'meilleur_algo': min(resultats.keys(), key=lambda k: resultats[k]['makespan']),
            'meilleur_makespan': meilleur_makespan,
            'est_probablement_optimal': est_probablement_optimal,
            'statistiques': self._calculer_statistiques(resultats)
        }

    def _calculer_statistiques(self, resultats: Dict) -> Dict:
        """Calcule des statistiques sur les résultats"""
        makespans = [r['makespan'] for r in resultats.values()]
        temps_exec = [r['temps_execution'] for r in resultats.values()]

        return {
            'makespan_moyen': sum(makespans) / len(makespans),
            'makespan_min': min(makespans),
            'makespan_max': max(makespans),
            'temps_exec_moyen': sum(temps_exec) / len(temps_exec),
            'temps_exec_total': sum(temps_exec)
        }

    def afficher_resultats(self, comparaison: Dict):
        """Affiche les résultats de manière lisible"""
        print("\n" + "="*80)
        print("COMPARAISON DES ALGORITHMES D'ORDONNANCEMENT")
        print("="*80)

        resultats = comparaison['resultats']

        # Tableau des résultats
        print(f"\n{'Algorithme':<40} {'Makespan':<12} {'Temps (ms)':<12} {'Ratio':<10} {'Écart %':<10}")
        print("-"*80)

        # Trier par makespan
        algos_tries = sorted(resultats.keys(), key=lambda k: resultats[k]['makespan'])

        for nom in algos_tries:
            r = resultats[nom]
            temps_ms = r['temps_execution'] * 1000
            print(f"{nom:<40} {r['makespan']:<12} {temps_ms:<12.3f} {r['ratio_optimal']:<10.4f} {r['ecart_percent']:<10.2f}")

        print("\n" + "="*80)
        print(f"🏆 MEILLEUR ALGORITHME : {comparaison['meilleur_algo']}")

        if comparaison.get('est_probablement_optimal', False):
            print(f"📊 MAKESPAN OPTIMAL (garanti par Johnson) : {comparaison['meilleur_makespan']}")
            print("   ✅ Johnson garantit l'optimal pour 1 commis + 1 four")
        else:
            print(f"📊 MEILLEUR MAKESPAN TROUVÉ : {comparaison['meilleur_makespan']}")
            print("   ⚠️  Pas forcément l'optimal théorique (référence = meilleur parmi les algos testés)")

        print("="*80)

        # Statistiques
        stats = comparaison['statistiques']
        print(f"\nStatistiques:")
        print(f"  - Makespan moyen: {stats['makespan_moyen']:.2f}")
        print(f"  - Makespan min: {stats['makespan_min']}")
        print(f"  - Makespan max: {stats['makespan_max']}")
        print(f"  - Temps d'exécution total: {stats['temps_exec_total']*1000:.3f} ms")


def exemple_comparaison_1():
    """Exemple 1 : Instance simple de l'énoncé"""
    print("\n" + "="*80)
    print("EXEMPLE 1 : Instance de l'énoncé (3 plats, 1 commis, 1 four)")
    print("="*80)

    plats = [
        Plat(1, "Plat 1", temps_epluchage=15, temps_cuisson=17),
        Plat(2, "Plat 2", temps_epluchage=11, temps_cuisson=16),
        Plat(3, "Plat 3", temps_epluchage=0, temps_cuisson=12)
    ]

    stations = {'commis': 1, 'fours': 1}

    comparateur = ComparateurAlgorithmes()
    resultats = comparateur.comparer(plats, stations)
    comparateur.afficher_resultats(resultats)


def exemple_comparaison_2():
    """Exemple 2 : Instance plus grande"""
    print("\n" + "="*80)
    print("EXEMPLE 2 : Instance moyenne (10 plats, 3 commis, 2 fours)")
    print("="*80)

    plats = [
        Plat(1, "Plat 1", temps_epluchage=20, temps_cuisson=15),
        Plat(2, "Plat 2", temps_epluchage=15, temps_cuisson=20),
        Plat(3, "Plat 3", temps_epluchage=10, temps_cuisson=25),
        Plat(4, "Plat 4", temps_epluchage=25, temps_cuisson=10),
        Plat(5, "Plat 5", temps_epluchage=12, temps_cuisson=18),
        Plat(6, "Plat 6", temps_epluchage=18, temps_cuisson=12),
        Plat(7, "Plat 7", temps_epluchage=8, temps_cuisson=22),
        Plat(8, "Plat 8", temps_epluchage=22, temps_cuisson=8),
        Plat(9, "Plat 9", temps_epluchage=14, temps_cuisson=16),
        Plat(10, "Plat 10", temps_epluchage=16, temps_cuisson=14)
    ]

    stations = {'commis': 3, 'fours': 2}

    comparateur = ComparateurAlgorithmes()
    resultats = comparateur.comparer(plats, stations)
    comparateur.afficher_resultats(resultats)


def exemple_comparaison_3():
    """Exemple 3 : Cas difficile pour tester les heuristiques"""
    print("\n" + "="*80)
    print("EXEMPLE 3 : Cas difficile (15 plats, 4 commis, 3 fours)")
    print("="*80)

    plats = [
        Plat(i, f"Plat {i}",
             temps_epluchage=10 + (i * 3) % 20,
             temps_cuisson=15 + (i * 5) % 25)
        for i in range(1, 16)
    ]

    stations = {'commis': 4, 'fours': 3}

    comparateur = ComparateurAlgorithmes()
    resultats = comparateur.comparer(plats, stations)
    comparateur.afficher_resultats(resultats)


if __name__ == "__main__":
    # Exécuter tous les exemples
    exemple_comparaison_1()
    exemple_comparaison_2()
    exemple_comparaison_3()

    print("\n" + "="*80)
    print("✅ COMPARAISON TERMINÉE")
    print("="*80)

