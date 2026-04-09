# backend/database/__init__.py
"""
Module de gestion de la base de données SQLite
"""

from database.db_manager import DatabaseManager
from database.models import (
    Instance,
    Execution,
    Resultat,
    Comparaison
)

__all__ = [
    'DatabaseManager',
    'Instance',
    'Execution',
    'Resultat',
    'Comparaison'
]

