# backend/schedulers/base_scheduler.py
"""
Classe de base pour tous les algorithmes d'ordonnancement.

Contient la logique commune :
  - _build_schedule : construction du planning (prep → cuisson) avec heapq
  - _empty_schedule : retourne un résultat vide
  - afficher_gantt  : diagramme de Gantt ASCII dans le terminal

Chaque scheduler héritant de BaseScheduler n'a plus qu'à :
  1. Implémenter get_name()
  2. Implémenter schedule() qui détermine l'ORDRE des plats
  3. Appeler self._build_schedule(ordre, nb_commis, nb_fours)
"""

import heapq
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from models.plat import Plat


class BaseScheduler(ABC):

    # ──────────────────────────────────────────────────────────
    # Interface obligatoire (à implémenter dans chaque sous-classe)
    # ──────────────────────────────────────────────────────────

    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom lisible de l'algorithme."""
        pass

    @abstractmethod
    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Ordonnance les plats sur les stations.

        Args:
            plats    : liste des plats à ordonnancer
            stations : {'commis': m, 'fours': k}

        Returns:
            {
                'ordre'           : List[Plat],   ordre d'exécution
                'makespan'        : int,           temps total (secondes)
                'schedule_commis' : List[List],    planning détaillé commis
                'schedule_fours'  : List[List],    planning détaillé fours
                'nom_algorithme'  : str,
                'est_optimal'     : bool,          True seulement si garanti
                'details'         : Dict           infos supplémentaires
            }
        """
        pass

    # ──────────────────────────────────────────────────────────
    # Logique partagée — construction du planning
    # ──────────────────────────────────────────────────────────

    def _build_schedule(
        self,
        plats: List[Plat],
        nb_commis: int,
        nb_fours: int,
    ) -> Dict:
        """
        Construit le planning détaillé à partir d'un ordre de plats donné.

        La SEULE chose qui change entre les algorithmes c'est l'ORDRE des plats.
        Une fois l'ordre décidé, la construction du planning est identique partout :

        Phase 1 — Préparations :
            On assigne chaque plat (dans l'ordre donné) au commis
            le plus tôt disponible (min-heap sur le temps de fin).

        Phase 2 — Cuissons :
            On assigne chaque plat (dans le même ordre) au four
            le plus tôt disponible, EN RESPECTANT la contrainte :
                debut_cuisson >= fin_preparation

        Args:
            plats     : plats dans l'ordre décidé par l'algorithme
            nb_commis : nombre de commis disponibles
            nb_fours  : nombre de fours disponibles

        Returns:
            {
                'makespan'        : int,
                'schedule_commis' : List[List[dict]],
                'schedule_fours'  : List[List[dict]],
            }
            Chaque tâche est un dict {'plat': Plat, 'debut': int, 'fin': int}.
        """
        # ── Phase 1 : préparations ────────────────────────────
        commis_heap = [(0, i) for i in range(nb_commis)]
        heapq.heapify(commis_heap)

        schedule_commis: List[List[Dict]] = [[] for _ in range(nb_commis)]
        fin_prep: Dict[int, int] = {}  # plat.id → instant de fin de préparation

        for plat in plats:
            dispo, id_commis = heapq.heappop(commis_heap)
            debut = dispo
            fin   = debut + plat.temps_prep

            schedule_commis[id_commis].append({
                "plat": plat, "debut": debut, "fin": fin
            })
            fin_prep[plat.id] = fin
            heapq.heappush(commis_heap, (fin, id_commis))

        # ── Phase 2 : cuissons ────────────────────────────────
        fours_heap = [(0, i) for i in range(nb_fours)]
        heapq.heapify(fours_heap)

        schedule_fours: List[List[Dict]] = [[] for _ in range(nb_fours)]

        for plat in plats:
            dispo, id_four = heapq.heappop(fours_heap)

            # Contrainte fondamentale : prep doit être terminée avant cuisson
            debut = max(dispo, fin_prep[plat.id])
            fin   = debut + plat.temps_cuisson

            schedule_fours[id_four].append({
                "plat": plat, "debut": debut, "fin": fin
            })
            heapq.heappush(fours_heap, (fin, id_four))

        # ── Makespan ──────────────────────────────────────────
        toutes_fins = [
            tache["fin"]
            for four in schedule_fours
            for tache in four
        ]
        makespan = max(toutes_fins) if toutes_fins else 0

        return {
            "makespan":        makespan,
            "schedule_commis": schedule_commis,
            "schedule_fours":  schedule_fours,
        }

    # ──────────────────────────────────────────────────────────
    # Utilitaires partagés
    # ──────────────────────────────────────────────────────────

    def _empty_schedule(self, stations: Dict[str, int]) -> Dict[str, Any]:
        """Retourne un résultat vide (liste de plats vide)."""
        nb_commis = stations.get("commis", 1)
        nb_fours  = stations.get("fours",  1)
        return {
            "ordre":            [],
            "makespan":         0,
            "schedule_commis":  [[] for _ in range(nb_commis)],
            "schedule_fours":   [[] for _ in range(nb_fours)],
            "nom_algorithme":   self.get_name(),
            "est_optimal":      False,
            "details": {
                "nb_plats":  0,
                "nb_commis": nb_commis,
                "nb_fours":  nb_fours,
            },
        }

    def afficher_gantt(self, resultat: Dict, unite: str = "min") -> None:
        """
        Affiche un diagramme de Gantt ASCII dans le terminal.

        Args:
            resultat : dictionnaire retourné par schedule()
            unite    : "min" pour afficher en minutes, "sec" pour secondes
        """
        div    = 60 if unite == "min" else 1
        symbole = "min" if unite == "min" else "sec"
        label_optimal = "OPTIMAL" if resultat.get("est_optimal") else "  Heuristique"

        print("\n" + "═" * 65)
        print(f"  PLANNING — {resultat['nom_algorithme']}")
        print(f"  {label_optimal}")
        print("═" * 65)

        for i, commis in enumerate(resultat["schedule_commis"]):
            taches = "".join(
                f"[{t['plat'].nom} {t['debut']//div}→{t['fin']//div}{symbole}]"
                for t in commis
            )
            print(f"  Commis {i+1} : {taches}")

        print()

        for i, four in enumerate(resultat["schedule_fours"]):
            taches = "".join(
                f"[{t['plat'].nom} {t['debut']//div}→{t['fin']//div}{symbole}]"
                for t in four
            )
            print(f"  Four   {i+1} : {taches}")

        print()
        print(f"  Makespan : {resultat['makespan'] // div} {symbole}")
        if "details" in resultat and "optimalite" in resultat["details"]:
            print(f"  {resultat['details']['optimalite']}")
        print("═" * 65 + "\n")