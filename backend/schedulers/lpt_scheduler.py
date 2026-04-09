# backend/schedulers/lpt_scheduler.py
"""
Algorithme LPT (Longest Processing Time First)
Heuristique gloutonne — garantie d'approximation 4/3 - 1/(3m)

Référence :
  Graham, R.L. (1969). SIAM Journal on Applied Mathematics, 17(2):416–429.
"""

from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class LPTScheduler(BaseScheduler):

    def get_name(self) -> str:
        return "LPT (Longest Processing Time First)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Trie les plats par temps TOTAL (prep + cuisson) DÉCROISSANT,
        puis construit le planning via _build_schedule.

        Garantie théorique : makespan_LPT ≤ (4/3 - 1/(3m)) × makespan_optimal
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)

        ordre = sorted(plats, key=lambda p: p.temps_total, reverse=True)

        planning = self._build_schedule(ordre, nb_commis, nb_fours)

        return {
            "ordre":           ordre,
            "makespan":        planning["makespan"],
            "schedule_commis": planning["schedule_commis"],
            "schedule_fours":  planning["schedule_fours"],
            "nom_algorithme":  self.get_name(),
            "est_optimal":     False,
            "details": {
                "nb_plats":  len(plats),
                "nb_commis": nb_commis,
                "nb_fours":  nb_fours,
                "optimalite": f"Heuristique — ratio ≤ 4/3 - 1/{3*nb_commis}",
            },
        }