# backend/schedulers/neh_scheduler.py
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq


class NEHScheduler(BaseScheduler):
    """
    Algorithme NEH (Nawaz-Enscore-Ham, 1983)
    Heuristique constructive très performante pour le Flow Shop

    Principe :
    1. Trier les jobs par temps total décroissant
    2. Prendre les 2 premiers, essayer les 2 ordres, garder le meilleur
    3. Pour chaque job restant, l'insérer à la meilleure position

    Complexité : O(n³m) où n = nombre de jobs, m = nombre de machines
    Très bon en pratique, souvent proche de l'optimal
    """

    def get_name(self) -> str:
        return "NEH (Nawaz-Enscore-Ham)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Applique l'algorithme NEH
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations['commis']
        nb_fours = stations['fours']

        # Étape 1 : Trier par temps total décroissant
        plats_tries = sorted(
            plats,
            key=lambda p: p.temps_epluchage + p.temps_cuisson,
            reverse=True
        )

        # Étape 2 : Initialiser avec le premier plat
        sequence_optimale = [plats_tries[0]]

        # Étape 3 : Insérer les plats un par un à la meilleure position
        for i in range(1, len(plats_tries)):
            plat_a_inserer = plats_tries[i]
            meilleur_makespan = float('inf')
            meilleure_position = 0

            # Essayer toutes les positions d'insertion
            for pos in range(len(sequence_optimale) + 1):
                # Créer une séquence test
                sequence_test = sequence_optimale[:pos] + [plat_a_inserer] + sequence_optimale[pos:]

                # Calculer le makespan de cette séquence
                makespan = self._calculate_makespan(sequence_test, nb_commis, nb_fours)

                # Garder la meilleure
                if makespan < meilleur_makespan:
                    meilleur_makespan = makespan
                    meilleure_position = pos

            # Insérer à la meilleure position
            sequence_optimale.insert(meilleure_position, plat_a_inserer)

        # Étape 4 : Construire le schedule final
        schedule_result = self._build_schedule(
            sequence_optimale, nb_commis, nb_fours
        )

        return {
            'ordre': sequence_optimale,
            'makespan': schedule_result['makespan'],
            'schedule_commis': schedule_result['schedule_commis'],
            'schedule_fours': schedule_result['schedule_fours'],
            'nom_algorithme': self.get_name(),
            'details': schedule_result['details']
        }

    def _calculate_makespan(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> int:
        """
        Calcule rapidement le makespan d'une séquence donnée
        (version optimisée pour NEH)
        """
        # Min-heap pour les commis
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)

        # Min-heap pour les fours
        fours_heap = [(0, i) for i in range(nb_fours)]
        heapq.heapify(fours_heap)

        fin_preparation = {}

        # Phase 1 : Préparations
        for plat in plats:
            temps_libre, id_commis = heapq.heappop(commis_heap)
            fin = temps_libre + plat.temps_epluchage
            fin_preparation[plat.id] = fin
            heapq.heappush(commis_heap, (fin, id_commis))

        # Phase 2 : Cuissons
        for plat in plats:
            temps_libre, id_four = heapq.heappop(fours_heap)
            debut = max(temps_libre, fin_preparation[plat.id])
            fin = debut + plat.temps_cuisson
            heapq.heappush(fours_heap, (fin, id_four))

        # Le makespan est le temps maximal sur tous les fours
        return max(temps for temps, _ in fours_heap)

    def _build_schedule(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> Dict:
        """
        Construit le planning détaillé
        """
        # Min-heap pour les commis (temps de disponibilité, id)
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)

        # Min-heap pour les fours
        fours_heap = [(0, i) for i in range(nb_fours)]
        heapq.heapify(fours_heap)

        schedule_commis = [[] for _ in range(nb_commis)]
        schedule_fours = [[] for _ in range(nb_fours)]

        fin_preparation = {}

        # Phase 1 : Assigner les préparations
        for plat in plats:
            temps_libre, id_commis = heapq.heappop(commis_heap)

            debut = temps_libre
            fin = debut + plat.temps_epluchage

            schedule_commis[id_commis].append({
                'plat': plat,
                'debut': debut,
                'fin': fin
            })

            fin_preparation[plat.id] = fin
            heapq.heappush(commis_heap, (fin, id_commis))

        # Phase 2 : Assigner les cuissons
        for plat in plats:
            temps_libre, id_four = heapq.heappop(fours_heap)

            # Le plat ne peut cuire qu'après avoir été préparé
            debut = max(temps_libre, fin_preparation[plat.id])
            fin = debut + plat.temps_cuisson

            schedule_fours[id_four].append({
                'plat': plat,
                'debut': debut,
                'fin': fin
            })

            heapq.heappush(fours_heap, (fin, id_four))

        # Calculer le makespan
        makespan = max(
            max((tache['fin'] for tache in four), default=0)
            for four in schedule_fours
        )

        return {
            'makespan': makespan,
            'schedule_commis': schedule_commis,
            'schedule_fours': schedule_fours,
            'details': {
                'nb_plats': len(plats),
                'nb_commis': nb_commis,
                'nb_fours': nb_fours,
                'strategie': 'NEH - Insertion constructive'
            }
        }

    def _empty_schedule(self, stations: Dict[str, int]) -> Dict[str, Any]:
        """Retourne un schedule vide"""
        nb_commis = stations['commis']
        nb_fours = stations['fours']

        return {
            'ordre': [],
            'makespan': 0,
            'schedule_commis': [[] for _ in range(nb_commis)],
            'schedule_fours': [[] for _ in range(nb_fours)],
            'nom_algorithme': self.get_name(),
            'details': {
                'nb_plats': 0,
                'nb_commis': nb_commis,
                'nb_fours': nb_fours,
                'strategie': 'NEH - Insertion constructive'
            }
        }

