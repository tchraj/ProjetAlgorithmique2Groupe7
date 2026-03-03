# backend/schedulers/brute_force_scheduler.py
"""
Algorithme par force brute — Recherche exhaustive de l'ordre optimal

Principe : teste TOUTES les permutations possibles des plats et garde
la meilleure. Garanti optimal mais coût factoriel O(n!).

Utilisations dans ce projet :
  1. Vérifier que Johnson est bien optimal sur 1 commis + 1 four
  2. Montrer pourquoi les heuristiques sont indispensables :
       3 plats →       6 permutations  (instantané)
       6 plats →     720 permutations  (rapide)
      10 plats →  3 628 800 permutations  (quelques secondes)
      15 plats → 1 307 674 368 000 permutations  (impossible)

LIMITE : n <= 10 recommandé, n > 12 déconseillé.
"""

import heapq
from itertools import permutations
from typing import List, Dict, Any

from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class BruteForceScheduler(BaseScheduler):

    MAX_PLATS = 10  # Au-delà, on refuse pour éviter un blocage

    def get_name(self) -> str:
        return "Force Brute (Optimal exact)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Teste toutes les permutations et retourne la meilleure.
        Garanti OPTIMAL pour toute configuration (m commis, k fours).
        """
        if not plats:
            return self._empty_schedule(stations)

        if len(plats) > self.MAX_PLATS:
            return {
                **self._empty_schedule(stations),
                'erreur': (
                    f"Force brute limitée à {self.MAX_PLATS} plats "
                    f"({len(plats)} fournis → {_factoriel(len(plats)):,} permutations)."
                )
            }

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)
        nb_perms  = _factoriel(len(plats))

        meilleur_makespan = float("inf")
        meilleur_ordre    = None
        perms_testees     = 0

        for perm in permutations(plats):
            makespan = self._makespan_rapide(list(perm), nb_commis, nb_fours)
            perms_testees += 1
            if makespan < meilleur_makespan:
                meilleur_makespan = makespan
                meilleur_ordre    = list(perm)

        # Construire le planning complet avec l'ordre optimal trouvé
        planning = self._build_schedule(meilleur_ordre, nb_commis, nb_fours)

        return {
            "ordre":           meilleur_ordre,
            "makespan":        planning["makespan"],
            "schedule_commis": planning["schedule_commis"],
            "schedule_fours":  planning["schedule_fours"],
            "nom_algorithme":  self.get_name(),
            "est_optimal":     True,  # toujours vrai par définition
            "details": {
                "nb_plats":       len(plats),
                "nb_commis":      nb_commis,
                "nb_fours":       nb_fours,
                "nb_permutations": nb_perms,
                "optimalite":     f"OPTIMAL garanti — {nb_perms:,} permutations testées",
            },
        }

    def _makespan_rapide(
        self, plats: List[Plat], nb_commis: int, nb_fours: int
    ) -> int:
        """
        Calcule le makespan d'une séquence sans stocker le planning.
        Appelé n! fois — doit être le plus rapide possible.
        """
        commis_heap = [0] * nb_commis
        heapq.heapify(commis_heap)
        fin_prep = {}

        for plat in plats:
            dispo = heapq.heappop(commis_heap)
            fin   = dispo + plat.temps_prep
            fin_prep[plat.id] = fin
            heapq.heappush(commis_heap, fin)

        fours_heap = [0] * nb_fours
        heapq.heapify(fours_heap)

        for plat in plats:
            dispo = heapq.heappop(fours_heap)
            fin   = max(dispo, fin_prep[plat.id]) + plat.temps_cuisson
            heapq.heappush(fours_heap, fin)

        return max(fours_heap)


# ── Utilitaire ────────────────────────────────────────────
def _factoriel(n: int) -> int:
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r