# Objectifs SMART - Kitchen Load Balancer

## Introduction

Ce document définit les objectifs SMART du projet **Kitchen Load Balancer**, un jeu éducatif 2D qui enseigne les concepts de load balancing à travers la gestion d'une cuisine.

**SMART** = **S**pécifique, **M**esurable, **A**tteignable, **R**éaliste, **T**emporel

---

## Objectif 1 : Pédagogique

> Enseigner les algorithmes de load balancing de manière interactive

| Critère | Description |
|---------|-------------|
| **Spécifique** | Permettre aux étudiants de comprendre les 4 algorithmes de load balancing : Round Robin, Least Loaded, Shortest Job First, Priority First |
| **Mesurable** | L'étudiant peut expliquer la différence entre les algorithmes après 3 parties jouées |
| **Atteignable** | Utilisation de l'analogie cuisine/informatique pour simplifier les concepts abstraits |
| **Réaliste** | Adapté au niveau d'étudiants en cours d'algorithmique |
| **Temporel** | Compréhension de base acquise en 15-20 minutes de jeu |

### Correspondance Cuisine / Informatique

| Cuisine | Informatique |
|---------|--------------|
| Plat | Job / Tâche |
| Station | Serveur / Worker |
| File d'attente | Queue |
| Load balancer | Scheduler |
| Plat brûlé | Timeout |
| Client VIP | Requête prioritaire |

---

## Objectif 2 : Gameplay

> Créer une expérience de jeu engageante et équilibrée

| Critère | Description |
|---------|-------------|
| **Spécifique** | Servir des plats en respectant les deadlines tout en gérant les files d'attente des stations |
| **Mesurable** | Maintenir une satisfaction client > 80% et servir au moins 20 plats par session |
| **Atteignable** | Difficulté progressive avec des niveaux débloquables et des algorithmes accessibles |
| **Réaliste** | Mécanique simple en 3 étapes : sélectionner un plat, assigner à une station, observer le résultat |
| **Temporel** | Session de jeu de 5-10 minutes par niveau |

### Conditions de victoire/défaite

- **Victoire** : Satisfaction > 80%, aucun goulot critique
- **Défaite** : Satisfaction = 0% ou client VIP perdu

---

## Objectif 3 : Technique

> Développer une application web robuste et maintenable

| Critère | Description |
|---------|-------------|
| **Spécifique** | Développer une application web fonctionnelle avec Flask (backend) + JavaScript (frontend) |
| **Mesurable** | Implémenter 6 types de plats, 3 stations, 4 algorithmes, et 2 modes de jeu (manuel/auto) |
| **Atteignable** | Stack technique accessible : Python, HTML, CSS, JavaScript vanilla |
| **Réaliste** | Code modulaire, maintenable et extensible pour ajouts futurs |
| **Temporel** | MVP fonctionnel livré dans le cadre du projet algorithmique |

### Architecture technique

```
Frontend (JavaScript)
├── GameEngine      → Boucle de jeu principale
├── Station         → Gestion des stations de travail
├── Plat            → Représentation des plats/tâches
├── LoadBalancer    → Implémentation des algorithmes
├── SoundManager    → Effets sonores
└── ParticleEffects → Animations visuelles

Backend (Flask/Python)
├── app.py          → Routes API et serveur
└── algorithms.py   → Algorithmes d'ordonnancement
```

---

## Objectif 4 : Évaluation et Feedback

> Fournir des métriques de performance pour l'apprentissage

| Critère | Description |
|---------|-------------|
| **Spécifique** | Afficher des statistiques de performance à la fin de chaque session de jeu |
| **Mesurable** | 4 indicateurs clés : temps moyen de service, taux d'occupation, plats ratés, satisfaction client |
| **Atteignable** | Calculs simples basés sur les données collectées pendant le jeu |
| **Réaliste** | Feedback immédiat permettant à l'étudiant de comprendre ses erreurs |
| **Temporel** | Résultats affichés en temps réel (HUD) et récapitulés en fin de partie |

### Indicateurs affichés

| Indicateur | Description | Affichage |
|------------|-------------|-----------|
| Satisfaction | Jauge de bonheur client | Barre de progression |
| Temps écoulé | Durée de la session | Timer MM:SS |
| Plats servis | Nombre de succès | Compteur vert |
| Plats ratés | Nombre d'échecs | Compteur rouge |

---

## Objectif 5 : UX/UI (Expérience Utilisateur)

> Créer une interface intuitive et agréable

| Critère | Description |
|---------|-------------|
| **Spécifique** | Interface intuitive avec feedback visuel (animations, couleurs) et sonore (effets audio) |
| **Mesurable** | Temps de prise en main < 2 minutes pour les contrôles de base |
| **Atteignable** | Design cartoon coloré, animations fluides, sons contextuels |
| **Réaliste** | Accessible sur navigateur sans installation, responsive design |
| **Temporel** | Tutoriel intégré consultable à tout moment depuis le menu |

### Éléments UX implémentés

- **Page d'accueil** : Menu principal animé avec options
- **Tutoriel** : Guide interactif en 4 étapes
- **Effets sonores** : Clic, succès, échec, alerte
- **Animations** : Confettis (VIP servi), fumée (plat critique), flammes (plat brûlé)
- **Feedback visuel** : Couleurs (vert/orange/rouge), tremblements, pulsations

---

## Tableau récapitulatif

| # | Objectif | Indicateur clé de succès |
|---|----------|-------------------------|
| 1 | Pédagogique | Compréhension des 4 algorithmes de load balancing |
| 2 | Gameplay | Satisfaction > 80%, 20+ plats servis par session |
| 3 | Technique | 4 algorithmes, 3 stations, 6 plats, 2 modes |
| 4 | Évaluation | 4 statistiques affichées en temps réel |
| 5 | UX/UI | Prise en main < 2 minutes |

---

## Conclusion

Ces objectifs SMART permettent de guider le développement du projet Kitchen Load Balancer en assurant :

1. **Clarté** : Chaque objectif est bien défini
2. **Mesurabilité** : Des critères concrets pour évaluer le succès
3. **Faisabilité** : Objectifs réalistes dans le cadre du projet
4. **Pertinence** : Alignement avec les objectifs pédagogiques du cours d'algorithmique
5. **Délais** : Échéances claires pour chaque fonctionnalité

---

*Document généré pour le Projet Algorithmique - Groupe 7*
