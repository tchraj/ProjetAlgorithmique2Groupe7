# backend/schedulers/spt_scheduler.py
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq


class SPTScheduler(BaseScheduler):
    """
    Algorithme SPT (Shortest Processing Time First)
    Heuristique gloutonne : ordonnance les plats par temps total croissant

    Propriétés :
    - Minimise le temps d'attente moyen
    - Pas optimal pour makespan mais utile comme baseline
    - Très simple et rapide
    """

    def get_name(self) -> str:
        return "SPT (Shortest Processing Time First)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Ordonnance les plats par temps total croissant

        Principe :
        1. Calculer temps total (préparation + cuisson) pour chaque plat
        2. Trier par temps total croissant
        3. Assigner séquentiellement aux stations disponibles
        """
        # Étape 1 : Trier par temps total croissant
        plats_tries = sorted(
            plats,
            key=lambda p: p.temps_epluchage + p.temps_cuisson
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
        Construit le planning détaillé avec la stratégie SPT
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
                'strategie': 'SPT - Temps total croissant'
            }
        }

