# backend/database/db_manager.py
"""
Gestionnaire de base de données SQLite pour le projet d'ordonnancement
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class DatabaseManager:
    """Gestion de la base de données SQLite"""

    def __init__(self, db_path: str = "data/ordonnancement.db"):
        """
        Initialise la connexion à la base de données

        Args:
            db_path: Chemin vers le fichier SQLite
        """
        # Créer le dossier data si nécessaire
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Établit la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom

    def _create_tables(self):
        """Crée les tables si elles n'existent pas"""
        cursor = self.conn.cursor()

        # Table des instances
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                description TEXT,
                nb_plats INTEGER NOT NULL,
                nb_commis INTEGER NOT NULL,
                nb_fours INTEGER NOT NULL,
                difficulte TEXT,
                plats_json TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system'
            )
        """)

        # Table des exécutions d'algorithmes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance_id INTEGER NOT NULL,
                algorithme TEXT NOT NULL,
                makespan INTEGER NOT NULL,
                temps_execution REAL NOT NULL,
                ordre_plats TEXT NOT NULL,
                schedule_commis TEXT,
                schedule_fours TEXT,
                date_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instance_id) REFERENCES instances(id)
            )
        """)

        # Table des comparaisons (plusieurs algos sur une même instance)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparaisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                instance_id INTEGER NOT NULL,
                date_comparaison TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instance_id) REFERENCES instances(id)
            )
        """)

        # Table de liaison comparaisons-executions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparaison_executions (
                comparaison_id INTEGER NOT NULL,
                execution_id INTEGER NOT NULL,
                FOREIGN KEY (comparaison_id) REFERENCES comparaisons(id),
                FOREIGN KEY (execution_id) REFERENCES executions(id),
                PRIMARY KEY (comparaison_id, execution_id)
            )
        """)

        # Index pour améliorer les performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_instance 
            ON executions(instance_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_algorithme 
            ON executions(algorithme)
        """)

        self.conn.commit()

    # ========== GESTION DES INSTANCES ==========

    def sauvegarder_instance(
        self,
        nom: str,
        plats: List[Dict],
        nb_commis: int,
        nb_fours: int = 1,
        description: str = "",
        difficulte: str = "moyen",
        created_by: str = "user"
    ) -> int:
        """
        Sauvegarde une instance dans la base

        Returns:
            ID de l'instance créée
        """
        cursor = self.conn.cursor()

        plats_json = json.dumps(plats, ensure_ascii=False)

        try:
            cursor.execute("""
                INSERT INTO instances 
                (nom, description, nb_plats, nb_commis, nb_fours, difficulte, plats_json, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nom, description, len(plats), nb_commis, nb_fours, difficulte, plats_json, created_by))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Instance existe déjà, retourner son ID
            cursor.execute("SELECT id FROM instances WHERE nom = ?", (nom,))
            return cursor.fetchone()[0]

    def charger_instance(self, instance_id: int) -> Optional[Dict]:
        """Charge une instance par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM instances WHERE id = ?", (instance_id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row['id'],
                'nom': row['nom'],
                'description': row['description'],
                'nb_plats': row['nb_plats'],
                'nb_commis': row['nb_commis'],
                'nb_fours': row['nb_fours'],
                'difficulte': row['difficulte'],
                'plats': json.loads(row['plats_json']),
                'date_creation': row['date_creation'],
                'created_by': row['created_by']
            }
        return None

    def charger_instance_par_nom(self, nom: str) -> Optional[Dict]:
        """Charge une instance par son nom"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM instances WHERE nom = ?", (nom,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row['id'],
                'nom': row['nom'],
                'description': row['description'],
                'nb_plats': row['nb_plats'],
                'nb_commis': row['nb_commis'],
                'nb_fours': row['nb_fours'],
                'difficulte': row['difficulte'],
                'plats': json.loads(row['plats_json']),
                'date_creation': row['date_creation'],
                'created_by': row['created_by']
            }
        return None

    def lister_instances(self, limit: int = 100) -> List[Dict]:
        """Liste toutes les instances (sans les détails des plats)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nom, description, nb_plats, nb_commis, nb_fours, 
                   difficulte, date_creation, created_by
            FROM instances
            ORDER BY date_creation DESC
            LIMIT ?
        """, (limit,))

        instances = []
        for row in cursor.fetchall():
            instances.append({
                'id': row['id'],
                'nom': row['nom'],
                'description': row['description'],
                'nb_plats': row['nb_plats'],
                'nb_commis': row['nb_commis'],
                'nb_fours': row['nb_fours'],
                'difficulte': row['difficulte'],
                'date_creation': row['date_creation'],
                'created_by': row['created_by']
            })

        return instances

    # ========== GESTION DES EXÉCUTIONS ==========

    def sauvegarder_execution(
        self,
        instance_id: int,
        algorithme: str,
        makespan: int,
        temps_execution: float,
        ordre_plats: List[int],
        schedule_commis: List = None,
        schedule_fours: List = None
    ) -> int:
        """
        Sauvegarde le résultat d'une exécution d'algorithme

        Returns:
            ID de l'exécution créée
        """
        cursor = self.conn.cursor()

        ordre_json = json.dumps(ordre_plats)
        schedule_commis_json = json.dumps(schedule_commis) if schedule_commis else None
        schedule_fours_json = json.dumps(schedule_fours) if schedule_fours else None

        cursor.execute("""
            INSERT INTO executions
            (instance_id, algorithme, makespan, temps_execution, 
             ordre_plats, schedule_commis, schedule_fours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (instance_id, algorithme, makespan, temps_execution,
              ordre_json, schedule_commis_json, schedule_fours_json))

        self.conn.commit()
        return cursor.lastrowid

    def charger_execution(self, execution_id: int) -> Optional[Dict]:
        """Charge une exécution par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM executions WHERE id = ?", (execution_id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row['id'],
                'instance_id': row['instance_id'],
                'algorithme': row['algorithme'],
                'makespan': row['makespan'],
                'temps_execution': row['temps_execution'],
                'ordre_plats': json.loads(row['ordre_plats']),
                'schedule_commis': json.loads(row['schedule_commis']) if row['schedule_commis'] else None,
                'schedule_fours': json.loads(row['schedule_fours']) if row['schedule_fours'] else None,
                'date_execution': row['date_execution']
            }
        return None

    def lister_executions_instance(self, instance_id: int) -> List[Dict]:
        """Liste toutes les exécutions pour une instance"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, algorithme, makespan, temps_execution, date_execution
            FROM executions
            WHERE instance_id = ?
            ORDER BY date_execution DESC
        """, (instance_id,))

        executions = []
        for row in cursor.fetchall():
            executions.append({
                'id': row['id'],
                'algorithme': row['algorithme'],
                'makespan': row['makespan'],
                'temps_execution': row['temps_execution'],
                'date_execution': row['date_execution']
            })

        return executions

    # ========== STATISTIQUES ==========

    def get_statistiques_algorithme(self, algorithme: str) -> Dict:
        """Statistiques pour un algorithme"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
                COUNT(*) as nb_executions,
                AVG(makespan) as makespan_moyen,
                MIN(makespan) as makespan_min,
                MAX(makespan) as makespan_max,
                AVG(temps_execution) as temps_moyen
            FROM executions
            WHERE algorithme = ?
        """, (algorithme,))

        row = cursor.fetchone()
        return {
            'algorithme': algorithme,
            'nb_executions': row['nb_executions'],
            'makespan_moyen': row['makespan_moyen'],
            'makespan_min': row['makespan_min'],
            'makespan_max': row['makespan_max'],
            'temps_execution_moyen': row['temps_moyen']
        }

    def get_meilleure_execution(self, instance_id: int) -> Optional[Dict]:
        """Trouve la meilleure exécution pour une instance"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM executions
            WHERE instance_id = ?
            ORDER BY makespan ASC, temps_execution ASC
            LIMIT 1
        """, (instance_id,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'algorithme': row['algorithme'],
                'makespan': row['makespan'],
                'temps_execution': row['temps_execution'],
                'date_execution': row['date_execution']
            }
        return None

    def get_classement_algorithmes(self) -> List[Dict]:
        """Classement des algorithmes par performance moyenne"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                algorithme,
                COUNT(*) as nb_executions,
                AVG(makespan) as makespan_moyen,
                AVG(temps_execution) as temps_moyen
            FROM executions
            GROUP BY algorithme
            ORDER BY makespan_moyen ASC
        """)

        classement = []
        for row in cursor.fetchall():
            classement.append({
                'algorithme': row['algorithme'],
                'nb_executions': row['nb_executions'],
                'makespan_moyen': row['makespan_moyen'],
                'temps_execution_moyen': row['temps_moyen']
            })

        return classement

    # ========== UTILITAIRES ==========

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fermeture automatique avec context manager"""
        self.close()

