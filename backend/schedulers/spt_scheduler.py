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
            key=lambda p: p.temps_prep + p.temps_cuisson
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
            'est_optimal': False,
            'details': {
                'nb_plats': len(plats_tries),
                'nb_commis': nb_commis,
                'nb_fours': nb_fours,
            }
        }