# backend/schedulers/fifo_scheduler.py
"""
Algorithme FIFO (First In First Out) — Baseline
Aucune optimisation : les plats sont traités dans l'ordre où ils arrivent.
Sert de référence pour mesurer le gain des autres algorithmes.
"""

from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class FIFOScheduler(BaseScheduler):

    def get_name(self) -> str:
        return "FIFO (First In First Out)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Aucun tri — ordre d'arrivée conservé.
        Utile comme baseline : montre ce qui se passe sans optimisation.
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)

        ordre    = list(plats)  # pas de tri
        planning = self._build_schedule(ordre, nb_commis, nb_fours)

        return {
            "ordre":           ordre,
            "makespan":        planning["makespan"],
            "schedule_commis": planning["schedule_commis"],
            "schedule_fours":  planning["schedule_fours"],
            "nom_algorithme":  self.get_name(),
            "est_optimal":     False,
            "details": {
                "nb_plats":   len(plats),
                "nb_commis":  nb_commis,
                "nb_fours":   nb_fours,
                "optimalite": "Baseline — aucune optimisation",
            },
        }