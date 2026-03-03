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

import heapq
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

    # ──────────────────────────────────────────────────────────
    # Construction du planning
    # ──────────────────────────────────────────────────────────

    def _build_schedule(
        self,
        plats: List[Plat],
        nb_commis: int,
        nb_fours: int,
    ) -> Dict:
        """
        Construit le planning détaillé en respectant la contrainte prep → cuisson.

        Phase 1 — Préparations :
            Chaque commis est libre dès que sa tâche précédente est finie.
            On assigne chaque plat (dans l'ordre Johnson) au commis
            le plus tôt disponible (min-heap).

        Phase 2 — Cuissons :
            Un plat ne peut entrer au four qu'APRÈS la fin de sa préparation.
            On parcourt les plats dans le même ordre Johnson,
            et on assigne chacun au four le plus tôt disponible,
            en respectant la contrainte de précédence.
        """
        # ── Phase 1 : préparations ────────────────────────────
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)

        schedule_commis = [[] for _ in range(nb_commis)]
        fin_prep: Dict[int, int] = {}  # plat.id → temps de fin de préparation

        for plat in plats:
            dispo, id_commis = heapq.heappop(commis_heap)
            debut = dispo
            fin   = debut + plat.temps_prep

            schedule_commis[id_commis].append({
                "plat":  plat,
                "debut": debut,
                "fin":   fin,
            })
            fin_prep[plat.id] = fin
            heapq.heappush(commis_heap, (fin, id_commis))

        # ── Phase 2 : cuissons ────────────────────────────────
        fours_heap = [(0, i) for i in range(nb_fours)]
        heapq.heapify(fours_heap)

        schedule_fours = [[] for _ in range(nb_fours)]

        for plat in plats:
            dispo, id_four = heapq.heappop(fours_heap)

            # Contrainte : le plat doit être prêt avant d'entrer au four
            debut = max(dispo, fin_prep[plat.id])
            fin   = debut + plat.temps_cuisson

            schedule_fours[id_four].append({
                "plat":  plat,
                "debut": debut,
                "fin":   fin,
            })
            heapq.heappush(fours_heap, (fin, id_four))

        # ── Makespan = fin de la dernière tâche de cuisson ────
        makespan = max(
            tache["fin"]
            for four in schedule_fours
            for tache in four
        ) if any(schedule_fours) else 0

        return {
            "makespan":        makespan,
            "schedule_commis": schedule_commis,
            "schedule_fours":  schedule_fours,
        }

    # ──────────────────────────────────────────────────────────
    # Utilitaire : affichage Gantt ASCII
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def afficher_gantt(resultat: Dict, unite: str = "min") -> None:
        """
        Affiche un diagramme de Gantt simplifié dans le terminal.

        Args:
            resultat : dictionnaire retourné par schedule()
            unite    : "min" (divise par 60) ou "sec"
        """
        div = 60 if unite == "min" else 1
        symbole = "min" if unite == "min" else "sec"

        print("\n" + "═" * 60)
        print(f"  PLANNING — {resultat['nom_algorithme']}")
        print(f"  {'✅ OPTIMAL' if resultat.get('est_optimal') else '⚠️  Heuristique'}")
        print("═" * 60)

        for i, commis in enumerate(resultat["schedule_commis"]):
            ligne = f"  Commis {i+1} : "
            for tache in commis:
                p = tache["plat"]
                d = tache["debut"] // div
                f = tache["fin"]   // div
                ligne += f"[{p.nom} {d}→{f}{symbole}]"
            print(ligne)

        print()
        for i, four in enumerate(resultat["schedule_fours"]):
            ligne = f"  Four   {i+1} : "
            for tache in four:
                p = tache["plat"]
                d = tache["debut"] // div
                f = tache["fin"]   // div
                ligne += f"[{p.nom} {d}→{f}{symbole}]"
            print(ligne)

        print()
        makespan = resultat["makespan"] // div
        print(f"  Makespan : {makespan} {symbole}")
        print(f"  {resultat['details']['optimalite']}")
        print("═" * 60 + "\n")