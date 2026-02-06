# 📋 Générateur d'Instances - Projet Ordonnancement Cuisine

**Projet:** Algorithmes et Médiation - Polytech Nice SI4  
**Groupe:** 7  
**Responsable de la tâche:** Imane  
**Période:** Janvier-Avril 2026

---

## 📖 Description

Ce module génère des instances pour le problème d'ordonnancement de cuisine, où l'objectif est de répartir des plats (nécessitant épluchage et cuisson) entre plusieurs commis afin de minimiser le temps total de traitement.

---

## 🎯 Objectifs

1. **Générer des instances variées** pour tester différents algorithmes d'ordonnancement
2. **Fournir des instances de référence** basées sur les exemples du sujet
3. **Permettre la validation** des instances générées
4. **Faciliter les tests** et benchmarks pour comparer les performances des algorithmes

---

## 📁 Structure des fichiers

```
.
├── instance_generator.py          # Générateur d'instances intelligent
├── create_reference_instances.py  # Script pour créer les instances du sujet
├── instance_validator.py          # Validateur d'instances
├── reference_instances.json       # Instances de référence (exemples du sujet)
├── instances_test.json           # Instances générées pour tests
└── README.md                     # Cette documentation
```

---

## 🚀 Utilisation

### 1. Générer des instances de test

```python
from instance_generator import InstanceGenerator

# Créer le générateur
generator = InstanceGenerator(seed=42)  # seed pour reproductibilité

# Générer une instance simple
instance_simple = generator.generer_instance_simple(
    nombre_plats=5,
    nombre_commis=3,
    nom="mon_instance"
)

# Générer une instance équilibrée (plus difficile)
instance_equilibree = generator.generer_instance_equilibree(
    nombre_plats=8,
    nombre_commis=3
)

# Générer une instance difficile
instance_difficile = generator.generer_instance_difficile(
    nombre_plats=10,
    nombre_commis=4
)

# Sauvegarder les instances
generator.sauvegarder_instances(
    [instance_simple, instance_equilibree, instance_difficile],
    "mes_instances.json"
)
```

### 2. Générer un lot d'instances

```python
# Générer 10 instances variées
instances = generator.generer_batch_instances(
    nombre_instances=10,
    types=["simple", "equilibree", "difficile"]
)

generator.sauvegarder_instances(instances, "batch_instances.json")
```

### 3. Valider des instances

```python
from instance_validator import InstanceValidator

validator = InstanceValidator()

# Valider une instance
resultat = validator.valider_instance(mon_instance)
resultat.afficher()

# Valider toutes les instances d'un fichier
resultats = validator.valider_fichier_instances("mes_instances.json")

for nom, resultat in resultats.items():
    print(f"\nInstance: {nom}")
    resultat.afficher()
```

---

## 📊 Types d'instances disponibles

### 1. **Instance Simple** (`generer_instance_simple`)
- Temps de traitement aléatoires mais raisonnables
- Bonne répartition entre épluchage et cuisson
- **Difficulté:** Facile
- **Usage:** Tests de base, validation d'algorithmes

### 2. **Instance Équilibrée** (`generer_instance_equilibree`)
- Tous les plats ont des temps similaires (±30%)
- Plus difficile à optimiser (moins de marge de manœuvre)
- **Difficulté:** Moyen
- **Usage:** Tester la robustesse des algorithmes

### 3. **Instance Difficile** (`generer_instance_difficile`)
- Quelques plats très longs, beaucoup de plats courts
- Déséquilibre intentionnel
- **Difficulté:** Difficile
- **Usage:** Benchmarking, comparaison d'algorithmes

### 4. **Instance Déséquilibrée** (`generer_instance_desequilibree`)
- Rapport plats/commis inadapté
- Peut avoir trop ou trop peu de commis
- **Difficulté:** Difficile
- **Usage:** Cas limites, tests de robustesse

---

## 📋 Instances de référence

Le fichier `reference_instances.json` contient **7 instances de référence** :

### Exemples du sujet
1. **exemple_1_sujet** : 3 plats, 2 commis (du document)
2. **exemple_2_sujet** : 3 plats, 2 commis (du document)
3. **exemple_3_sujet** : 4 plats, 2 commis (du document)

### Exemples additionnels
4. **exemple_fruits_classique** : Problème initial avec pommes, mangues, tomates, litchis
5. **exemple_vacances_ludique** : Approche ludique "planification de vacances"
6. **exemple_mini_test** : Instance minimale pour tests rapides (2 plats, 2 commis)
7. **exemple_benchmark_complexe** : Instance complexe pour benchmarking (15 plats, 5 commis)

---

## 🔍 Format des instances

Structure JSON d'une instance :

```json
{
  "nom": "exemple_1_sujet",
  "description": "Description de l'instance",
  "plats": [
    {
      "nom": "plat_1",
      "temps_epluchage": 900,  // en secondes
      "temps_cuisson": 1200
    }
  ],
  "nombre_commis": 3,
  "difficulte": "moyen",
  "statistiques": {
    "nombre_plats": 5,
    "temps_total_travail": 15000,
    "charge_theorique_par_commis": 5000
  }
}
```

---

## ✅ Validation des instances

Le validateur vérifie :

### Erreurs bloquantes
- ❌ Champs obligatoires manquants
- ❌ Types de données incorrects
- ❌ Valeurs négatives
- ❌ Valeurs hors limites (>24h par tâche)

### Avertissements (non bloquants)
- ⚠️ Instances triviales (tous les temps à 0)
- ⚠️ Déséquilibre important (un plat > 2x la charge moyenne)
- ⚠️ Plus de commis que de plats
- ⚠️ Noms de plats dupliqués

---

## 🎨 Personnalisation

### Modifier les listes d'ingrédients

Dans `instance_generator.py`, modifier les listes :

```python
FRUITS = ["pomme", "poire", "mangue", ...]
LEGUMES = ["carotte", "tomate", ...]
```

### Ajuster les contraintes

Dans `instance_validator.py` :

```python
MIN_PLATS = 1
MAX_PLATS = 1000
MIN_COMMIS = 1
MAX_COMMIS = 100
MAX_TEMPS = 24 * 3600  # 24 heures
```

---

## 📈 Statistiques calculées

Pour chaque instance, les statistiques suivantes sont calculées :

- **nombre_plats** : Nombre total de plats
- **temps_total_travail** : Somme de tous les temps (épluchage + cuisson)
- **temps_moyen_par_plat** : Temps moyen pour un plat
- **temps_max_plat** : Plat le plus long
- **temps_min_plat** : Plat le plus court
- **charge_theorique_par_commis** : Charge si parfaitement équilibré
- **ratio_plats_commis** : Nombre de plats par commis

---

## 🧪 Exemples d'exécution

### Générer et tester rapidement

```bash
# Générer les instances de référence
python create_reference_instances.py

# Générer des instances de test
python instance_generator.py

# Valider toutes les instances
python instance_validator.py
```

### Sortie attendue

```
✅ 7 instance(s) sauvegardée(s) dans reference_instances.json
✅ Instance VALIDE
📊 Statistiques:
   • nombre_plats: 5
   • temps_total_travail: 8220
   • charge_theorique_par_commis: 2740.0
```

---

## 🔗 Intégration avec l'application

Les instances peuvent être :
1. **Chargées directement** dans l'application Flask
2. **Utilisées pour les tests** des algorithmes glouton et programmation dynamique
3. **Comparées** pour évaluer les performances
4. **Exportées** vers d'autres formats (CSV, etc.)

---

## 📝 Notes importantes

- Les temps sont en **secondes**
- L'épluchage doit **toujours précéder** la cuisson (contrainte du problème)
- Utiliser `seed` pour garantir la **reproductibilité** des tests
- Les instances de référence sont **figées** (ne pas les modifier)
- Créer de nouvelles instances pour vos propres tests

---

## 🎓 Contexte académique

Ce générateur fait partie du projet d'**Algorithmes et Médiation** pour :
- Étudier le **problème d'ordonnancement** (NP-complet)
- Comparer **algorithmes gloutons** vs **programmation dynamique**
- Analyser la **qualité des approximations**
- Réaliser des **benchmarks** sur différentes tailles d'instances

---

## 👥 Contribution

**Responsable:** Imane  
**Groupe:** 7  
**Encadrant:** Équipe pédagogique Polytech Nice SI4

Pour toute question ou amélioration, contacter l'équipe du projet.

---

## 📚 Références

- Document du projet : "Ordonnancement, Cuisine et approximations"
- Problème d'équilibrage de charge (Load Balancing)
- Algorithmes d'approximation pour problèmes NP-complets

---

**Dernière mise à jour:** Janvier 2026  
**Version:** 1.0