# backend/services/comparison_service.py
from typing import List, Dict, Optional
from schedulers.base_scheduler import BaseScheduler
from models.plat import Plat
import time


class ComparisonService:
    """
    Compare plusieurs algorithmes sur les mêmes instances
    Calcule des métriques : makespan, ratio, écart, temps d'exécution
    """

    def __init__(self, schedulers: List[BaseScheduler]):
        self.schedulers = schedulers

    def compare(
        self,
        plats: List[Plat],
        stations: Dict[str, int],
        makespan_optimal: Optional[int] = None
    ) -> Dict:
        """
        Exécute tous les algorithmes et compare les résultats

        Args:
            plats: Liste des plats à ordonnancer
            stations: {'commis': m, 'fours': x}
            makespan_optimal: Makespan optimal connu (si disponible)

        Returns:
            Dictionnaire avec résultats détaillés et statistiques
        """
        if not plats:
            return self._empty_comparison(stations)

        resultats = []

        for scheduler in self.schedulers:
            start_time = time.perf_counter()
            solution = scheduler.schedule(plats, stations)
            execution_time = time.perf_counter() - start_time

            resultats.append({
                'algorithme': scheduler.get_name(),
                'makespan': solution['makespan'],
                'temps_execution': execution_time,
                'ordre': [p.nom for p in solution['ordre']],
                'ordre_ids': [p.id for p in solution['ordre']],
                'solution_complete': solution
            })

        # Trouver le meilleur makespan parmi les résultats
        meilleur_makespan = min(r['makespan'] for r in resultats)
        meilleur = min(resultats, key=lambda r: r['makespan'])

        # Calculer ratio et écart pour chaque algo
        for resultat in resultats:
            makespan = resultat['makespan']

            # Ratio par rapport au meilleur trouvé
            resultat['ratio_vs_meilleur'] = makespan / meilleur_makespan if meilleur_makespan > 0 else 1.0

            # Écart absolu par rapport au meilleur
            resultat['ecart_absolu'] = makespan - meilleur_makespan

            # Écart relatif (en %)
            resultat['ecart_relatif_pct'] = (
                (makespan - meilleur_makespan) / meilleur_makespan * 100
                if meilleur_makespan > 0 else 0.0
            )

            # Si makespan optimal fourni, calculer ratio et écart vs optimal
            if makespan_optimal:
                resultat['ratio_vs_optimal'] = makespan / makespan_optimal if makespan_optimal > 0 else 1.0
                resultat['ecart_vs_optimal'] = makespan - makespan_optimal
                resultat['ecart_vs_optimal_pct'] = (
                    (makespan - makespan_optimal) / makespan_optimal * 100
                    if makespan_optimal > 0 else 0.0
                )

        # Statistiques globales
        statistiques = self._calculer_statistiques(resultats, makespan_optimal)

        return {
            'resultats': resultats,
            'meilleur': meilleur,
            'meilleur_makespan': meilleur_makespan,
            'makespan_optimal': makespan_optimal,
            'nb_plats': len(plats),
            'stations': stations,
            'statistiques': statistiques
        }

    def compare_batch(
        self,
        instances: List[Dict],
        makespan_optimaux: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Compare les algorithmes sur un lot d'instances

        Args:
            instances: Liste de dict {'nom': str, 'plats': List[Plat], 'stations': Dict}
            makespan_optimaux: Dict {nom_instance: makespan_optimal}

        Returns:
            Résultats agrégés sur toutes les instances
        """
        tous_resultats = []

        for instance in instances:
            nom = instance['nom']
            plats = instance['plats']
            stations = instance['stations']
            optimal = makespan_optimaux.get(nom) if makespan_optimaux else None

            resultat_instance = self.compare(plats, stations, optimal)
            resultat_instance['nom_instance'] = nom
            tous_resultats.append(resultat_instance)

        # Agréger les statistiques
        stats_agregees = self._agreger_statistiques(tous_resultats)

        return {
            'instances': tous_resultats,
            'nb_instances': len(instances),
            'statistiques_agregees': stats_agregees
        }

    def _calculer_statistiques(
        self,
        resultats: List[Dict],
        makespan_optimal: Optional[int]
    ) -> Dict:
        """Calcule des statistiques sur les résultats"""
        makespans = [r['makespan'] for r in resultats]
        temps_exec = [r['temps_execution'] for r in resultats]

        stats = {
            'nb_algorithmes': len(resultats),
            'makespan_min': min(makespans),
            'makespan_max': max(makespans),
            'makespan_moyen': sum(makespans) / len(makespans),
            'temps_exec_moyen': sum(temps_exec) / len(temps_exec),
            'temps_exec_total': sum(temps_exec)
        }

        if makespan_optimal:
            stats['ecart_moyen_vs_optimal_pct'] = sum(
                r.get('ecart_vs_optimal_pct', 0) for r in resultats
            ) / len(resultats)

        return stats

    def _agreger_statistiques(self, tous_resultats: List[Dict]) -> Dict:
        """Agrège les statistiques sur plusieurs instances"""
        stats_par_algo = {}

        # Collecter les résultats par algorithme
        for resultat_instance in tous_resultats:
            for res in resultat_instance['resultats']:
                algo_nom = res['algorithme']
                if algo_nom not in stats_par_algo:
                    stats_par_algo[algo_nom] = {
                        'makespans': [],
                        'ratios_vs_meilleur': [],
                        'ratios_vs_optimal': [],
                        'temps_exec': [],
                        'nb_meilleur': 0
                    }

                stats_par_algo[algo_nom]['makespans'].append(res['makespan'])
                stats_par_algo[algo_nom]['ratios_vs_meilleur'].append(res['ratio_vs_meilleur'])
                stats_par_algo[algo_nom]['temps_exec'].append(res['temps_execution'])

                if 'ratio_vs_optimal' in res:
                    stats_par_algo[algo_nom]['ratios_vs_optimal'].append(res['ratio_vs_optimal'])

                # Compter combien de fois cet algo est le meilleur
                if res['algorithme'] == resultat_instance['meilleur']['algorithme']:
                    stats_par_algo[algo_nom]['nb_meilleur'] += 1

        # Calculer moyennes et stats finales
        stats_finales = {}
        for algo_nom, stats in stats_par_algo.items():
            nb_instances = len(stats['makespans'])

            stats_finales[algo_nom] = {
                'makespan_moyen': sum(stats['makespans']) / nb_instances,
                'ratio_moyen_vs_meilleur': sum(stats['ratios_vs_meilleur']) / nb_instances,
                'temps_exec_moyen': sum(stats['temps_exec']) / nb_instances,
                'nb_fois_meilleur': stats['nb_meilleur'],
                'pct_meilleur': (stats['nb_meilleur'] / nb_instances * 100) if nb_instances > 0 else 0
            }

            if stats['ratios_vs_optimal']:
                stats_finales[algo_nom]['ratio_moyen_vs_optimal'] = (
                    sum(stats['ratios_vs_optimal']) / len(stats['ratios_vs_optimal'])
                )

        return stats_finales

    def _empty_comparison(self, stations: Dict[str, int]) -> Dict:
        """Retourne une comparaison vide"""
        return {
            'resultats': [],
            'meilleur': None,
            'meilleur_makespan': 0,
            'makespan_optimal': None,
            'nb_plats': 0,
            'stations': stations,
            'statistiques': {
                'nb_algorithmes': 0,
                'makespan_min': 0,
                'makespan_max': 0,
                'makespan_moyen': 0,
                'temps_exec_moyen': 0,
                'temps_exec_total': 0
            }
        }