# backend/schedulers/johnson_scheduler.py  [VERSION REFACTORISÉE]
"""
Algorithme de Johnson (1954) — Flow Shop 2 machines

GARANTIE D'OPTIMALITÉ :
  - OPTIMAL uniquement pour 1 commis + 1 four (cas classique de l'énoncé)
  - Pour m commis + k fours : heuristique (ordre Johnson + affectation greedy)
    → bon en pratique mais sans garantie théorique d'optimalité

Référence :
  Johnson, S.M. (1954). "Optimal two- and three-stage production schedules
  with setup times included". Naval Research Logistics Quarterly, 1(1):61–68.
"""

from typing import List, Dict, Any

from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler


class JohnsonScheduler(BaseScheduler):

    def get_name(self) -> str:
        return "Johnson's Algorithm"

    # ──────────────────────────────────────────────────────────
    # Point d'entrée principal
    # ──────────────────────────────────────────────────────────

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Applique l'algorithme de Johnson.

        Étape 1 — Partitionner :
            Set1 : plats où temps_prep <= temps_cuisson  → début de séquence
            Set2 : plats où temps_prep >  temps_cuisson  → fin de séquence

        Étape 2 — Trier :
            Set1 par temps_prep  CROISSANT
            Set2 par temps_cuisson DÉCROISSANT

        Étape 3 — Ordre optimal = Set1 + Set2

        Étape 4 — Construire le planning en respectant la contrainte prep → cuisson
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)

        # ── Étape 1 & 2 : partitionner et trier ──────────────
        set1 = sorted(
            [p for p in plats if p.temps_prep <= p.temps_cuisson],
            key=lambda p: p.temps_prep
        )
        set2 = sorted(
            [p for p in plats if p.temps_prep > p.temps_cuisson],
            key=lambda p: p.temps_cuisson,
            reverse=True
        )
        ordre_johnson = set1 + set2

        # ── Étape 3 : construire le planning ─────────────────
        planning = self._build_schedule(ordre_johnson, nb_commis, nb_fours)

        # ── Étape 4 : déterminer si l'optimal est garanti ────
        est_optimal = (nb_commis == 1 and nb_fours == 1)

        return {
            "ordre":            ordre_johnson,
            "makespan":         planning["makespan"],
            "schedule_commis":  planning["schedule_commis"],
            "schedule_fours":   planning["schedule_fours"],
            "nom_algorithme":   self.get_name(),
            "est_optimal":      est_optimal,
            "details": {
                "nb_plats":   len(plats),
                "nb_commis":  nb_commis,
                "nb_fours":   nb_fours,
                "taille_set1": len(set1),
                "taille_set2": len(set2),
                "optimalite": (
                    "OPTIMAL garanti (1 commis + 1 four)"
                    if est_optimal
                    else "Heuristique : ordre Johnson + affectation greedy "
                         "(non garanti optimal pour m>1 ou k>1)"
                ),
            },
        }

