# Algorithmes d'Ordonnancement - Documentation

## 📋 Vue d'ensemble

Ce projet implémente plusieurs algorithmes d'ordonnancement pour le problème de **Flow Shop à 2 machines** (préparation → cuisson) avec plusieurs stations de chaque type.

### Problème

- **n plats** à préparer et cuire
- **m commis** pour la préparation (épluchage)
- **k fours** pour la cuisson
- **Objectif** : Minimiser le **makespan** (temps total de complétion)

---

## 🔧 Algorithmes Implémentés

### 1. **Johnson's Algorithm**  (OPTIMAL)

**Fichier** : `schedulers/johnson_scheduler.py`

**Type** : Algorithme exact

**Complexité** : O(n log n)

**Principe** :
```
1. Partitionner les plats :
   - Set1 : plats où temps_epluchage < temps_cuisson
   - Set2 : plats où temps_epluchage >= temps_cuisson

2. Trier :
   - Set1 par temps_epluchage croissant
   - Set2 par temps_cuisson décroissant

3. Ordre optimal = Set1 + Set2
```

**Garanties** :
- ✅ **OPTIMAL** pour Flow Shop à 2 machines avec 1 station de chaque type
- ✅ Très performant même avec plusieurs stations
- ✅ Complexité faible

**Utilisation** :
```python
from schedulers.johnson_scheduler import JohnsonScheduler

scheduler = JohnsonScheduler()
resultat = scheduler.schedule(plats, {'commis': 1, 'fours': 1})
print(f"Makespan optimal: {resultat['makespan']}")
```

---

### 2. **NEH (Nawaz-Enscore-Ham)** 🏅

**Fichier** : `schedulers/neh_scheduler.py`

**Type** : Heuristique constructive

**Complexité** : O(n³m)

**Principe** :
```
1. Trier les plats par temps total décroissant
2. Initialiser avec le premier plat
3. Pour chaque plat suivant :
   - Tester toutes les positions d'insertion
   - Garder celle qui minimise le makespan
```

**Performances** :
- 🥇 **Meilleure heuristique** en général
- ✅ Souvent à moins de 5% de l'optimal
- ⚠️ Plus lent que les autres heuristiques

**Quand l'utiliser** :
- Instances de taille moyenne (< 50 plats)
- Besoin d'une solution proche de l'optimal
- Temps de calcul acceptable

---

### 3. **LPT (Longest Processing Time First)** 📊

**Fichier** : `schedulers/lpt_scheduler.py`

**Type** : Heuristique gloutonne

**Complexité** : O(n log n)

**Principe** :
```
1. Trier par temps total (epluchage + cuisson) DÉCROISSANT
2. Assigner séquentiellement aux stations disponibles
```

**Performances** :
- ✅ Ratio d'approximation théorique : 4/3 - 1/(3m)
- ✅ Très rapide
- ⚠️ Peut être à 10-33% de l'optimal

**Garanties théoriques** :
- Pour m machines : makespan_LPT ≤ (4/3 - 1/(3m)) × makespan_optimal

---

### 4. **SPT (Shortest Processing Time First)** ⚡

**Fichier** : `schedulers/spt_scheduler.py`

**Type** : Heuristique gloutonne

**Complexité** : O(n log n)

**Principe** :
```
1. Trier par temps total (epluchage + cuisson) CROISSANT
2. Assigner séquentiellement aux stations disponibles
```

**Performances** :
- ✅ Très rapide
- ✅ Minimise le temps d'attente moyen
- ⚠️ Pas optimal pour le makespan
- ⚠️ Utile comme baseline

**Quand l'utiliser** :
- Besoin d'une solution rapide
- Benchmark / baseline
- Instances avec plats de tailles similaires

---

### 5. **Palmer's Algorithm** 📐

**Fichier** : `schedulers/palmer_scheduler.py`

**Type** : Heuristique spécifique au Flow Shop

**Complexité** : O(n log n)

**Principe** :
```
1. Calculer le "slope index" pour chaque plat :
   slope_i = temps_epluchage - temps_cuisson

2. Trier par slope décroissant

3. L'idée : privilégier les plats avec préparation longue
   et cuisson courte pour éviter les temps d'attente
```

**Performances** :
- ✅ Très rapide
- ⚠️ Peut être sous-optimal (jusqu'à 50% au-dessus de l'optimal)
- ⚠️ Historiquement important mais dépassé par NEH

---

## 📊 Comparaison des Performances

### Exemple 1 : 3 plats, 1 commis, 1 four

| Algorithme | Makespan | Ratio | Temps (ms) |
|-----------|----------|-------|------------|
| **Johnson** | **45** | 1.00 | 0.037 |
| **SPT** | **45** | 1.00 | 0.016 |
| **NEH** | **45** | 1.00 | 0.055 |
| LPT | 60 | 1.33 | 0.020 |
| Palmer | 60 | 1.33 | 0.016 |

### Exemple 2 : 10 plats, 3 commis, 2 fours

| Algorithme | Makespan | Ratio | Temps (ms) |
|-----------|----------|-------|------------|
| **Johnson** | **90** | 1.00 | 0.065 |
| **NEH** | **91** | 1.01 | 0.493 |
| SPT | 96 | 1.07 | 0.027 |
| LPT | 99 | 1.10 | 0.036 |
| Palmer | 112 | 1.24 | 0.038 |

### Exemple 3 : 15 plats, 4 commis, 3 fours

| Algorithme | Makespan | Ratio | Temps (ms) |
|-----------|----------|-------|------------|
| **NEH** | **138** | 1.00 | 1.678 |
| Johnson | 146 | 1.06 | 0.045 |
| SPT | 150 | 1.09 | 0.033 |
| LPT | 152 | 1.10 | 0.040 |
| Palmer | 156 | 1.13 | 0.036 |

---

## 🎯 Recommandations d'Usage

### Pour les petites instances (< 10 plats)
👉 **Johnson** - Optimal et ultra-rapide

### Pour les instances moyennes (10-50 plats)
👉 **NEH** - Meilleur compromis qualité/temps

### Pour les grandes instances (> 50 plats)
👉 **Johnson** ou **LPT** - Rapides avec bonnes performances

### Pour du benchmarking
👉 Utiliser **tous les algorithmes** pour comparer

---

## 🧪 Tests et Validation

### Lancer tous les tests
```bash
cd backend
python -m pytest tests/test_all_schedulers.py -v
```

### Comparer les algorithmes
```bash
python algorithms/comparaison_algorithmes.py
```

### Tests individuels
```bash
python -m pytest tests/test_johnson.py -v
```

---

## 📚 Références

1. **Johnson, S.M.** (1954). "Optimal two- and three-stage production schedules with setup times included". *Naval Research Logistics Quarterly*, 1(1):61–68.

2. **Nawaz, M., Enscore Jr, E.E., Ham, I.** (1983). "A heuristic algorithm for the m-machine, n-job flow-shop sequencing problem". *Omega*, 11(1):91–95.

3. **Palmer, D.S.** (1965). "Sequencing jobs through a multi-stage process in the minimum total time—a quick method of obtaining a near optimum". *Journal of the Operational Research Society*, 16(1):101–107.

4. **Graham, R.L.** (1969). "Bounds on multiprocessing timing anomalies". *SIAM Journal on Applied Mathematics*, 17(2):416–429. (LPT analysis)

---

## 🔍 Notes Techniques

### Attributs des plats
- `temps_epluchage` : temps de préparation (en secondes)
- `temps_cuisson` : temps de cuisson (en secondes)

### Structure des résultats
```python
{
    'ordre': List[Plat],           # Ordre d'exécution des plats
    'makespan': int,                # Temps total de complétion
    'schedule_commis': List[List],  # Planning détaillé des commis
    'schedule_fours': List[List],   # Planning détaillé des fours
    'nom_algorithme': str,          # Nom de l'algorithme utilisé
    'details': Dict                 # Statistiques additionnelles
}
```

### Architecture
```
backend/schedulers/
├── base_scheduler.py       # Interface commune
├── johnson_scheduler.py    # Johnson (OPTIMAL)
├── neh_scheduler.py        # NEH (meilleure heuristique)
├── lpt_scheduler.py        # LPT (glouton)
├── spt_scheduler.py        # SPT (glouton)
└── palmer_scheduler.py     # Palmer (historique)
```

---

## ✅ Checklist de Validation

- [x] Johnson implémenté et testé
- [x] NEH implémenté et testé
- [x] LPT implémenté et testé
- [x] SPT implémenté et testé
- [x] Palmer implémenté et testé
- [x] Tests unitaires pour tous les algorithmes
- [x] Script de comparaison fonctionnel
- [x] Documentation complète
- [ ] Intégration avec le frontend (à faire)
- [ ] API REST endpoints (à faire)
- [ ] Visualisation des résultats (à faire)

