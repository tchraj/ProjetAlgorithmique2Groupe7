# backend/schedulers/lpt_scheduler.py
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq


class LPTScheduler(BaseScheduler):
    """
    Algorithme LPT (Longest Processing Time First)
    Heuristique gloutonne : ordonnance les plats par temps total décroissant

    Garanties théoriques :
    - Ratio d'approximation : 4/3 - 1/(3m) pour m machines
    - Très performant en pratique
    """

    def get_name(self) -> str:
        return "LPT (Longest Processing Time First)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Ordonnance les plats par temps total décroissant

        Principe :
        1. Calculer temps total (préparation + cuisson) pour chaque plat
        2. Trier par temps total décroissant
        3. Assigner séquentiellement aux stations disponibles
        """
        if not plats:
            return self._empty_schedule(stations)

        # Étape 1 : Trier par temps total décroissant
        plats_tries = sorted(
            plats,
            key=lambda p: p.temps_epluchage + p.temps_cuisson,
            reverse=True
        )

        # Étape 2 : Construire le schedule
        nb_commis = stations['commis']
        nb_fours = stations['fours']

        schedule_result = self._build_schedule(
            plats_tries, nb_commis, nb_fours
        )

        return {
            'ordre': plats_tries,
            'makespan': schedule_result['makespan'],
            'schedule_commis': schedule_result['schedule_commis'],
            'schedule_fours': schedule_result['schedule_fours'],
            'nom_algorithme': self.get_name(),
            'details': schedule_result['details']
        }

    def _build_schedule(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> Dict:
        """
        Construit le planning détaillé avec la stratégie LPT
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
                'strategie': 'LPT - Temps total décroissant'
            }
        }

