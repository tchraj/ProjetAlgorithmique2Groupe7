# backend/models/plat.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Plat:
    id: int
    nom: str
    temps_prep: int
    temps_cuisson: int
    priorite: Optional[int] = 0

    @property
    def temps_total(self) -> int:
        return self.temps_prep + self.temps_cuisson

    def __repr__(self):
        return f"Plat({self.nom}, epluchage={self.temps_prep}s, cuisson={self.temps_cuisson}s)"
