# backend/schedulers/cds_scheduler.py
"""
Algorithme CDS (Campbell-Dudek-Smith, 1970)
Extension de l'algorithme de Johnson pour Flow Shop à m machines

Principe :
- Crée m-1 problèmes à 2 machines en agrégeant les machines
- Applique Johnson sur chaque problème
- Garde la meilleure solution
"""
from typing import List, Dict, Any
from models.plat import Plat
from schedulers.base_scheduler import BaseScheduler
import heapq


class CDSScheduler(BaseScheduler):
    """
    Algorithme CDS (Campbell-Dudek-Smith)
    Extension de Johnson pour Flow Shop multi-machines

    Pour un Flow Shop à 2 étapes (préparation + cuisson) avec plusieurs machines,
    CDS crée un problème équivalent à 2 machines virtuelles et applique Johnson.

    Complexité : O(n² log n)
    Performance : Excellent compromis entre Johnson et NEH
    """

    def get_name(self) -> str:
        return "CDS (Campbell-Dudek-Smith)"

    def schedule(self, plats: List[Plat], stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Applique l'algorithme CDS

        Pour Flow Shop à 2 étapes (notre cas : préparation + cuisson),
        CDS est équivalent à Johnson, mais peut être étendu à m > 2 étapes.
        """
        if not plats:
            return self._empty_schedule(stations)

        nb_commis = stations['commis']
        nb_fours = stations['fours']

        # Pour un Flow Shop à 2 machines (préparation + cuisson),
        # CDS revient à appliquer Johnson
        # Machine virtuelle 1 = préparation
        # Machine virtuelle 2 = cuisson

        ordre_optimal = self._johnson_2_machines(plats)

        # Construire le schedule avec l'ordre trouvé
        schedule_result = self._build_schedule(
            ordre_optimal, nb_commis, nb_fours
        )

        return {
            'ordre': ordre_optimal,
            'makespan': schedule_result['makespan'],
            'schedule_commis': schedule_result['schedule_commis'],
            'schedule_fours': schedule_result['schedule_fours'],
            'nom_algorithme': self.get_name(),
            'details': schedule_result['details']
        }

    def _johnson_2_machines(self, plats: List[Plat]) -> List[Plat]:
        """
        Applique l'algorithme de Johnson pour 2 machines

        Règle de Johnson :
        - Si min(prep_i, cuisson_i) = prep_i → mettre au début
        - Si min(prep_i, cuisson_i) = cuisson_i → mettre à la fin
        """
        debut = []  # Plats à mettre au début
        fin = []    # Plats à mettre à la fin

        for plat in plats:
            if plat.temps_epluchage <= plat.temps_cuisson:
                debut.append(plat)
            else:
                fin.append(plat)

        # Trier début par temps de préparation croissant
        debut.sort(key=lambda p: p.temps_epluchage)

        # Trier fin par temps de cuisson décroissant
        fin.sort(key=lambda p: p.temps_cuisson, reverse=True)

        return debut + fin

    def _build_schedule(self, plats: List[Plat], nb_commis: int, nb_fours: int) -> Dict:
        """
        Construit le planning détaillé avec l'ordre CDS
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
                'strategie': 'CDS - Extension de Johnson pour multi-machines',
                'note': 'Pour 2 étapes, CDS équivaut à Johnson mais est généralisable'
            }
        }

