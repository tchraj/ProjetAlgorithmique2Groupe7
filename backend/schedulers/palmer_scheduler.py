# backend/schedulers/palmer_scheduler.py
"""
Algorithme de Palmer (1965) — Heuristique Flow Shop

Principe : calculer un "slope index" pour chaque plat et trier par ordre
décroissant. Les plats avec une préparation longue et une cuisson courte
passent en premier pour réduire les temps d'attente au four.

Pour un Flow Shop à 2 machines (prep → cuisson) :
    slope_i = temps_prep_i - temps_cuisson_i

Trier par slope décroissant → les plats où prep > cuisson passent d'abord.

Référence :
  Palmer, D.S. (1965). "Sequencing jobs through a multi-stage process in the
  minimum total time — a quick method of obtaining a near optimum".
  Journal of the Operational Research Society, 16(1):101–107.
"""

from typing import List, Dict, Any

from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class PalmerScheduler(BaseScheduler):

    def get_name(self) -> str:
        return "Palmer's Heuristic"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Applique l'heuristique de Palmer.

        Étape 1 — Calculer le slope index de chaque plat :
            slope_i = temps_prep_i - temps_cuisson_i

        Étape 2 — Trier par slope DÉCROISSANT :
            Les plats avec prep > cuisson passent en premier.

        Étape 3 — Construire le planning via BaseScheduler.
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)

        ordre = sorted(
            plats,
            key=lambda p: p.temps_prep - p.temps_cuisson,
            reverse=True
        )

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
                "optimalite": "Heuristique Palmer — slope index décroissant",
            },
        }
