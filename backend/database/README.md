# 💾 Base de Données SQLite - Documentation

## 🎯 Pourquoi une Base de Données ?

Votre projet utilise maintenant **SQLite** pour :

### ✅ Avantages

1. **📈 Historique des exécutions**
   - Comparer les résultats dans le temps
   - Voir quelle solution était la meilleure
   - Ne pas perdre le travail effectué

2. **👥 Partage et collaboration**
   - D'autres personnes peuvent consulter les résultats
   - Éviter de recalculer les mêmes instances
   - Base commune pour tous les utilisateurs

3. **📊 Statistiques et analyses**
   - Quel algorithme est le plus performant ?
   - Quelles instances sont les plus difficiles ?
   - Évolution des performances

4. **🎓 Professionnalisme**
   - Projet académique plus crédible
   - Prêt pour une utilisation réelle
   - Facilite les démonstrations

---

## 🏗️ Structure de la Base de Données

```
ordonnancement.db
├── instances         → Instances de problèmes (plats à ordonnancer)
├── executions        → Résultats d'exécutions d'algorithmes
├── comparaisons      → Groupes de comparaisons
└── comparaison_executions → Liaison comparaisons ↔ exécutions
```

### Table `instances`

Stocke les instances de problèmes

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | ID unique |
| nom | TEXT | Nom de l'instance (unique) |
| description | TEXT | Description |
| nb_plats | INTEGER | Nombre de plats |
| nb_commis | INTEGER | Nombre de commis |
| nb_fours | INTEGER | Nombre de fours |
| difficulte | TEXT | facile/moyen/difficile |
| plats_json | TEXT | JSON des plats |
| date_creation | TIMESTAMP | Date de création |
| created_by | TEXT | Créateur |

### Table `executions`

Stocke les résultats d'exécutions

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | ID unique |
| instance_id | INTEGER | Référence à l'instance |
| algorithme | TEXT | Nom de l'algorithme |
| makespan | INTEGER | Temps total |
| temps_execution | REAL | Temps CPU (secondes) |
| ordre_plats | TEXT | JSON de l'ordre |
| schedule_commis | TEXT | JSON du planning commis |
| schedule_fours | TEXT | JSON du planning fours |
| date_execution | TIMESTAMP | Date d'exécution |

---

## 🚀 Utilisation

### Installation (aucune !)

SQLite est **inclus avec Python**, aucune installation nécessaire ! ✅

### Exemple 1 : Sauvegarder une instance

```python
from database.db_manager import DatabaseManager

# Créer/ouvrir la base de données
db = DatabaseManager()

# Sauvegarder une instance
plats = [
    {"id": 1, "nom": "Plat 1", "temps_epluchage": 900, "temps_cuisson": 1020},
    {"id": 2, "nom": "Plat 2", "temps_epluchage": 660, "temps_cuisson": 960}
]

instance_id = db.sauvegarder_instance(
    nom="mon_test",
    plats=plats,
    nb_commis=2,
    nb_fours=1,
    description="Test avec 2 plats",
    difficulte="facile"
)

print(f"Instance sauvegardée avec ID: {instance_id}")
```

### Exemple 2 : Exécuter et sauvegarder

```python
from database.db_manager import DatabaseManager
from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
import time

db = DatabaseManager()

# Charger une instance
instance = db.charger_instance_par_nom("mon_test")

# Convertir en objets Plat
plats = [
    Plat(p['id'], p['nom'], p['temps_epluchage'], p['temps_cuisson'])
    for p in instance['plats']
]

# Exécuter Johnson
johnson = JohnsonScheduler()
stations = {'commis': instance['nb_commis'], 'fours': instance['nb_fours']}

debut = time.time()
resultat = johnson.schedule(plats, stations)
temps_exec = time.time() - debut

# Sauvegarder le résultat
execution_id = db.sauvegarder_execution(
    instance_id=instance['id'],
    algorithme="Johnson",
    makespan=resultat['makespan'],
    temps_execution=temps_exec,
    ordre_plats=[p.id for p in resultat['ordre']]
)

print(f"Exécution sauvegardée avec ID: {execution_id}")
print(f"Makespan: {resultat['makespan']}")
```

### Exemple 3 : Consulter l'historique

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Lister toutes les instances
print("📋 Instances disponibles:")
instances = db.lister_instances()
for inst in instances:
    print(f"  - {inst['nom']}: {inst['nb_plats']} plats")

# Historique pour une instance
instance_id = 1
print(f"\n📊 Historique des exécutions:")
executions = db.lister_executions_instance(instance_id)
for exec in executions:
    print(f"  {exec['algorithme']}: makespan={exec['makespan']}")

# Meilleure exécution
meilleure = db.get_meilleure_execution(instance_id)
print(f"\n🏆 Meilleure: {meilleure['algorithme']} avec {meilleure['makespan']}")
```

### Exemple 4 : Statistiques

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Statistiques pour un algorithme
stats = db.get_statistiques_algorithme("Johnson")
print(f"Johnson:")
print(f"  Exécutions: {stats['nb_executions']}")
print(f"  Makespan moyen: {stats['makespan_moyen']:.2f}")

# Classement des algorithmes
print("\n🏆 Classement:")
classement = db.get_classement_algorithmes()
for i, algo in enumerate(classement, 1):
    print(f"  {i}. {algo['algorithme']}: {algo['makespan_moyen']:.2f}")
```

---

## 🎯 Utilisation avec Context Manager

Meilleure pratique pour fermer automatiquement la connexion :

```python
from database.db_manager import DatabaseManager

with DatabaseManager() as db:
    # Utiliser la base de données
    instances = db.lister_instances()
    # ...
# La connexion est fermée automatiquement
```

---

## 📊 Visualiser la Base de Données

### Option 1 : DB Browser for SQLite (Recommandé)

1. **Télécharger** : https://sqlitebrowser.org/
2. **Installer** (gratuit et open-source)
3. **Ouvrir** : `data/ordonnancement.db`
4. **Explorer** : Tables, données, requêtes SQL

### Option 2 : En ligne de commande

```bash
# Windows
sqlite3 data/ordonnancement.db

# Commandes utiles
.tables                    # Lister les tables
SELECT * FROM instances;   # Voir les instances
SELECT * FROM executions;  # Voir les exécutions
.quit                      # Quitter
```

### Option 3 : Python

```python
import sqlite3

conn = sqlite3.connect('data/ordonnancement.db')
cursor = conn.cursor()

# Compter les instances
cursor.execute("SELECT COUNT(*) FROM instances")
print(f"Nombre d'instances: {cursor.fetchone()[0]}")

# Compter les exécutions
cursor.execute("SELECT COUNT(*) FROM executions")
print(f"Nombre d'exécutions: {cursor.fetchone()[0]}")

conn.close()
```

---

## 🧪 Tester la Base de Données

```bash
cd backend
python database/exemple_utilisation.py
```

Ce script va :
1. ✅ Créer la base de données
2. ✅ Sauvegarder une instance
3. ✅ Exécuter Johnson et NEH
4. ✅ Afficher l'historique
5. ✅ Afficher les statistiques

---

## 🔧 Intégration avec l'API

### Endpoint pour lister les instances

```python
# backend/api/routes.py

from flask import Flask, jsonify
from database.db_manager import DatabaseManager

app = Flask(__name__)
db = DatabaseManager()

@app.route('/api/instances', methods=['GET'])
def get_instances():
    """Liste toutes les instances"""
    instances = db.lister_instances()
    return jsonify(instances)

@app.route('/api/instances/<int:instance_id>/executions', methods=['GET'])
def get_executions(instance_id):
    """Historique des exécutions pour une instance"""
    executions = db.lister_executions_instance(instance_id)
    return jsonify(executions)

@app.route('/api/instances/<int:instance_id>/best', methods=['GET'])
def get_best_execution(instance_id):
    """Meilleure exécution pour une instance"""
    best = db.get_meilleure_execution(instance_id)
    return jsonify(best)
```

---

## 📁 Localisation de la Base

Par défaut : `data/ordonnancement.db`

Pour changer :
```python
db = DatabaseManager(db_path="mon_chemin/ma_base.db")
```

---

## 🎓 Pour le Rapport

Vous pouvez écrire :

> **Persistance des données**
> 
> Notre application utilise **SQLite** pour stocker :
> - Les instances de problèmes (configurations de plats à ordonnancer)
> - Les résultats d'exécutions des algorithmes
> - Les statistiques de performance
> 
> SQLite a été choisi pour :
> - Sa simplicité (aucune installation requise)
> - Sa portabilité (fichier unique)
> - Sa fiabilité (standard industriel)
> - Son intégration native avec Python
> 
> Cette architecture permet aux utilisateurs de :
> - Conserver un historique des exécutions
> - Comparer les performances dans le temps
> - Partager facilement les résultats (fichier .db)
> - Analyser les tendances statistiques

---

## ⚠️ Important

### Migrations / Évolution du Schéma

Si vous ajoutez des colonnes plus tard :

```python
# backend/database/migrations.py

def migrate_v1_to_v2(db_path):
    """Ajoute une colonne user_notes"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            ALTER TABLE instances 
            ADD COLUMN user_notes TEXT
        """)
        conn.commit()
        print("✅ Migration v1→v2 réussie")
    except sqlite3.OperationalError:
        print("⚠️  Colonne déjà existante")
    
    conn.close()
```

### Backup

```python
import shutil
from datetime import datetime

# Créer un backup
backup_name = f"data/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
shutil.copy2("data/ordonnancement.db", backup_name)
print(f"✅ Backup créé: {backup_name}")
```

---

## ✅ Checklist d'Intégration

- [x] Base de données SQLite créée
- [x] Tables définies (instances, executions, ...)
- [x] DatabaseManager implémenté
- [x] Exemples d'utilisation fournis
- [ ] Intégration avec l'API Flask (à faire)
- [ ] Intégration avec le frontend (à faire)
- [ ] Migration des JSON existants (optionnel)

---

## 🚀 Prochaines Étapes

1. **Tester la base de données**
   ```bash
   python backend/database/exemple_utilisation.py
   ```

2. **Intégrer avec l'API**
   - Créer les endpoints REST
   - Connecter au frontend

3. **Migrer les données existantes**
   - Importer les JSON dans la base
   - Conserver les deux formats (compatibilité)

4. **Ajouter des fonctionnalités**
   - Favoris d'instances
   - Notes utilisateur
   - Export de rapports

---

**La base de données est prête à l'emploi ! 🎉**

SQLite offre tout ce dont vous avez besoin pour un projet académique professionnel, sans la complexité d'un serveur de base de données externe.

