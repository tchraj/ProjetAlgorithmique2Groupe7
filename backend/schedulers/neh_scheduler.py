# backend/schedulers/neh_scheduler.py
"""
Algorithme NEH (Nawaz-Enscore-Ham, 1983)
Heuristique constructive par insertion — très proche de l'optimal en pratique.

Complexité : O(n³) pour 2 machines
Référence  : Nawaz et al. (1983). Omega, 11(1):91–95.
"""

import heapq
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class NEHScheduler(BaseScheduler):

    def get_name(self) -> str:
        return "NEH (Nawaz-Enscore-Ham)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Principe NEH :
          1. Trier par temps total DÉCROISSANT
          2. Insérer les plats un à un à la position qui minimise le makespan courant
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)

        # Étape 1 : tri initial
        tries = sorted(plats, key=lambda p: p.temps_total, reverse=True)

        # Étape 2 : insertion constructive
        sequence = [tries[0]]
        for plat in tries[1:]:
            meilleur_makespan = float("inf")
            meilleure_pos     = 0

            for pos in range(len(sequence) + 1):
                seq_test = sequence[:pos] + [plat] + sequence[pos:]
                ms = self._makespan_rapide(seq_test, nb_commis, nb_fours)
                if ms < meilleur_makespan:
                    meilleur_makespan = ms
                    meilleure_pos     = pos

            sequence.insert(meilleure_pos, plat)

        planning = self._build_schedule(sequence, nb_commis, nb_fours)

        return {
            "ordre":           sequence,
            "makespan":        planning["makespan"],
            "schedule_commis": planning["schedule_commis"],
            "schedule_fours":  planning["schedule_fours"],
            "nom_algorithme":  self.get_name(),
            "est_optimal":     False,
            "details": {
                "nb_plats":   len(plats),
                "nb_commis":  nb_commis,
                "nb_fours":   nb_fours,
                "optimalite": "Heuristique constructive — souvent < 5% de l'optimal",
            },
        }

    def _makespan_rapide(
        self, plats: List[Plat], nb_commis: int, nb_fours: int
    ) -> int:
        """
        Calcule le makespan d'une séquence sans stocker le planning complet.
        Appelé O(n²) fois par NEH, doit être rapide.
        """
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)
        fin_prep = {}

        for plat in plats:
            dispo, _ = heapq.heappop(commis_heap)
            fin = dispo + plat.temps_prep
            fin_prep[plat.id] = fin
            heapq.heappush(commis_heap, (fin, _))

        fours_heap = [(0, i) for i in range(nb_fours)]
        heapq.heapify(fours_heap)

        for plat in plats:
            dispo, _ = heapq.heappop(fours_heap)
            fin = max(dispo, fin_prep[plat.id]) + plat.temps_cuisson
            heapq.heappush(fours_heap, (fin, _))

        return max(t for t, _ in fours_heap)