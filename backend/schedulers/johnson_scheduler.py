# backend/schedulers/johnson_scheduler.py
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq

class JohnsonScheduler(BaseScheduler):
    """
    Algorithme de Johnson (1954) pour Flow Shop à 2 machines
    OPTIMAL pour minimiser le makespan dans Préparation → Cuisson
    """

    def get_name(self) -> str:
        return "Johnson's Algorithm"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Applique l'algorithme de Johnson

        Principe:
        1. Set1 = plats où prep < cuisson → trier par prep croissant
        2. Set2 = plats où prep >= cuisson → trier par cuisson décroissant
        3. Ordre optimal = Set1 + Set2
        """
        # Étape 1 : Partitionner les plats
        set_1 = []  # prep < cuisson
        set_2 = []  # prep >= cuisson

        for plat in plats:
            if plat.temps_epluchage < plat.temps_cuisson:
                set_1.append(plat)
            else:
                set_2.append(plat)

        # Étape 2 : Trier
        set_1.sort(key=lambda p: p.temps_epluchage)
        set_2.sort(key=lambda p: p.temps_cuisson, reverse=True)

        # Étape 3 : Ordre optimal
        ordre_optimal = set_1 + set_2

        # Étape 4 : Construire le schedule détaillé
        nb_commis = stations['commis']
        nb_fours = stations['fours']

        schedule_result = self._build_schedule(
            ordre_optimal, nb_commis, nb_fours
        )

        return {
            'ordre': ordre_optimal,
            'makespan': schedule_result['makespan'],
            'schedule_commis': schedule_result['schedule_commis'],
            'schedule_fours': schedule_result['schedule_fours'],
            'nom_algorithme': self.get_name(),
            'details': schedule_result['details']
        }

    def _build_schedule(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> Dict:
        """
        Construit le planning détaillé en respectant l'ordre de Johnson
        """
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)

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

            debut = max(temps_libre, fin_preparation[plat.id])
            fin = debut + plat.temps_cuisson

            schedule_fours[id_four].append({
                'plat': plat,
                'debut': debut,
                'fin': fin
            })

            heapq.heappush(fours_heap, (fin, id_four))

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
                'nb_fours': nb_fours
            }
        }
