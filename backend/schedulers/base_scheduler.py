# backend/schedulers/base_scheduler.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseScheduler(ABC):
    """
    Interface pour tous les algorithmes d'ordonnancement
    """

    @abstractmethod
    def schedule(self, plats: List, stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Ordonnance les plats sur les stations

        Args:
            plats: Liste des plats à ordonnancer
            stations: {'commis': m, 'fours': x}

        Returns:
            {
                'ordre': List[Plat],
                'makespan': int,
                'schedule_commis': List[List[Plat]],
                'schedule_fours': List[List[Plat]],
                'nom_algorithme': str
            }
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom de l'algorithme"""
        pass

    def _empty_schedule(self, stations: Dict[str, int]) -> Dict[str, Any]:
        """
        Retourne un schedule vide (utilitaire)

        Args:
            stations: {'commis': m, 'fours': x}

        Returns:
            Schedule vide
        """
        nb_commis = stations.get('commis', 1)
        nb_fours = stations.get('fours', 1)

        return {
            'ordre': [],
            'makespan': 0,
            'schedule_commis': [[] for _ in range(nb_commis)],
            'schedule_fours': [[] for _ in range(nb_fours)],
            'nom_algorithme': self.get_name(),
            'details': {
                'nb_plats': 0,
                'nb_commis': nb_commis,
                'nb_fours': nb_fours
            }
        }

