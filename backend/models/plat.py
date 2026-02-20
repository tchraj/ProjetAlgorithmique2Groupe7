# backend/models/plat.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Plat:
    """
    Représente un plat avec temps de préparation et cuisson
    """
    id: int
    nom: str
    temps_epluchage: int  # en secondes (cohérent avec les instances)
    temps_cuisson: int     # en secondes (cohérent avec les instances)
    priorite: Optional[int] = 0  # Pour extensions futures

    @property
    def temps_total(self) -> int:
        return self.temps_epluchage + self.temps_cuisson

    def __repr__(self):
        return f"Plat({self.nom}, epluchage={self.temps_epluchage}s, cuisson={self.temps_cuisson}s)"
