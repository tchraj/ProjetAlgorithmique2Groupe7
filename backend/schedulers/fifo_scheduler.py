# backend/schedulers/fifo_scheduler.py
"""
Algorithme FIFO (First In First Out)
Baseline la plus simple : traiter les plats dans l'ordre d'arrivée

Principe :
- Aucune réorganisation
- Les plats sont traités dans l'ordre donné
- Sert de référence pour montrer l'amélioration des autres algorithmes
"""
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq


class FIFOScheduler(BaseScheduler):
    """
    Algorithme FIFO (First In First Out)
    Baseline simple : pas d'optimisation, ordre d'arrivée

    Complexité : O(n)
    Performance : Généralement la pire, mais sert de référence
    """

    def get_name(self) -> str:
        return "FIFO (First In First Out)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Ordonnance les plats dans leur ordre d'arrivée (FIFO)

        Aucune optimisation : on prend les plats tels quels
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations['commis']
        nb_fours = stations['fours']

        # Pas de réorganisation : on garde l'ordre d'arrivée
        ordre = plats.copy()

        # Construire le schedule
        schedule_result = self._build_schedule(
            ordre, nb_commis, nb_fours
        )

        return {
            'ordre': ordre,
            'makespan': schedule_result['makespan'],
            'schedule_commis': schedule_result['schedule_commis'],
            'schedule_fours': schedule_result['schedule_fours'],
            'nom_algorithme': self.get_name(),
            'details': schedule_result['details']
        }

    def _build_schedule(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> Dict:
        """
        Construit le planning sans optimisation (ordre FIFO)
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

        # Phase 1 : Assigner les préparations (dans l'ordre FIFO)
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

        # Phase 2 : Assigner les cuissons (dans l'ordre FIFO)
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
                'strategie': 'FIFO - Aucune optimisation (baseline)',
                'note': 'Sert de référence pour mesurer l\'amélioration des autres algorithmes'
            }
        }

