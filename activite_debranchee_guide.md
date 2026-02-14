# Activite Debranchee : Chef d'Orchestre en Cuisine
## Guide Complet de A a Z

**Projet :** Ordonnancement, Cuisine et Approximations
**Groupe 7 :** AMDYOUN Boubaker, AMRAOUI Imane, TCHANI Rajaa
**Public cible :** Lyceens (Seconde/Premiere/Terminale)
**Duree :** 45 a 60 minutes
**Nombre de participants :** 15 a 30 eleves

---

## A. OBJECTIF DE L'ACTIVITE

Faire comprendre aux lyceens, sans aucun ordinateur, comment fonctionne un algorithme d'ordonnancement (repartir des taches entre des travailleurs pour finir le plus vite possible). A la fin, ils doivent :

- Comprendre ce qu'est un **makespan** (temps total pour tout finir)
- Savoir appliquer l'**algorithme glouton** a la main
- Comprendre pourquoi certains problemes sont **tres difficiles** meme pour un ordinateur (NP-complet)
- Avoir manipule, touche, deplace des objets physiques pour experimenter

---

## B. MATERIEL A PREPARER

### B.1 Les Cartes-Plats (le coeur de l'activite)

Ce sont des cartes que les eleves prennent en main, trient, deplacent et posent sur les plateaux.

**Comment les fabriquer :**

1. Prendre du **papier cartonne de couleur** (160g minimum pour que ce soit rigide)
2. Decouper des rectangles de **8 cm x 12 cm** (taille d'une carte a jouer en plus grand)
3. Sur chaque carte, ecrire au feutre :
   - En haut : le **nom du plat** en gros (ex: "Pomme", "Mangue", "Steak")
   - Au milieu : un **dessin simple** du plat (ou coller une image imprimee)
   - En bas a gauche : **Epluchage : XX min** (en vert)
   - En bas a droite : **Cuisson : XX min** (en orange)
   - Tout en bas, entoure : **TOTAL : XX min** (en rouge, bien visible)

**Option amelioree :**
- Plastifier les cartes pour les reutiliser plusieurs fois
- Utiliser des couleurs de fond differentes selon la difficulte :
  - Vert clair = plat rapide (total < 15 min)
  - Jaune = plat moyen (total 15-30 min)
  - Rouge clair = plat long (total > 30 min)

**Quantite :** Preparer 5 a 6 jeux identiques de cartes (un jeu par groupe de 5 eleves)

**Exemple d'instance a utiliser (exemple_3_sujet) :**

| Carte | Nom | Epluchage | Cuisson | Total |
|-------|-----|-----------|---------|-------|
| 1 | Plat 1 | 8 min | 12 min | 20 min |
| 2 | Plat 2 | 12 min | 8 min | 20 min |
| 3 | Plat 3 | 17 min | 20 min | 37 min |
| 4 | Plat 4 | 19 min | 12 min | 31 min |

Nombre de commis pour cette instance : **2**

**Autre instance plus grande (test_simple) :**

| Carte | Nom | Epluchage | Cuisson | Total |
|-------|-----|-----------|---------|-------|
| 1 | Abricot | 9 min | 28 min | 37 min |
| 2 | Poire | 8 min | 26 min | 34 min |
| 3 | Papaye | 7 min | 23 min | 30 min |
| 4 | Raisin | 18 min | 6 min | 24 min |
| 5 | Pasteque | 5 min | 7 min | 12 min |

Nombre de commis pour cette instance : **3**

---

### B.2 Les Plateaux Commis

Ce sont les zones sur la table ou les eleves posent les cartes pour chaque commis.

**Comment les fabriquer :**

1. Prendre des **feuilles A3** (ou 2 feuilles A4 scotchees)
2. Ecrire en haut en gros : **COMMIS 1** (ou 2, 3...)
3. Dessiner 4 a 5 rectangles en pointilles (emplacements pour poser les cartes)
4. En bas, ecrire : **Charge totale : _______ min**
5. Sur le cote gauche, tracer une **echelle graduee** de 0 a 60 min (pour visualiser la charge comme une barre)

**Option amelioree :**
- Utiliser des **napperons de couleurs differentes** (un par commis)
- Ou des **sets de table** IKEA/Action avec le nom du commis ecrit dessus
- Coller une bande de ruban adhesif de couleur sur le bord pour identifier chaque commis

**Quantite :** 2 a 3 plateaux par groupe (selon le nombre de commis de l'instance choisie)

---

### B.3 La Timeline (Ligne du Temps)

Pour visualiser physiquement le makespan, c'est l'element le plus parlant.

**Comment la fabriquer :**

1. Tendre une **ficelle** ou un **ruban** de 1 metre sur la table (ou coller du scotch de couleur)
2. Marquer des graduations tous les 2 cm avec un feutre (chaque graduation = 5 minutes)
3. Ecrire les valeurs : 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60
4. Chaque commis a sa propre ligne parallele

**Utilisation :** Quand un eleve assigne un plat a un commis, il avance un **pion** (bouchon, gomme, piece de monnaie) le long de la timeline du nombre de minutes du plat. Le pion qui est le plus loin = le makespan.

**Alternative simple :** Pas de timeline, juste additionner les temps et comparer les totaux.

---

### B.4 La Fiche Score

Une feuille par groupe pour noter les resultats.

**Contenu :**

```
FICHE RESULTATS
Groupe : ________________    Date : ________________

Instance : ________________  Nombre de commis : ____

+------------------------------+----------+----------+-----------+
|                              | Commis 1 | Commis 2 | MAKESPAN  |
+------------------------------+----------+----------+-----------+
| Tour 1 (strategie libre)     |          |          |           |
+------------------------------+----------+----------+-----------+
| Tour 2 (algorithme glouton)  |          |          |           |
+------------------------------+----------+----------+-----------+

Quelle strategie avez-vous utilisee au Tour 1 ?
_____________________________________________________________

Le glouton a-t-il fait mieux ? Pourquoi ?
_____________________________________________________________
```

**Quantite :** Une fiche par groupe (5-6 fiches)

---

### B.5 Affiche "Regles du Jeu"

Une grande affiche (A2 ou A1) a poser sur le mur ou le tableau, visible de tous.

**Contenu :**

```
REGLES DU JEU - CHEF D'ORCHESTRE EN CUISINE

VOUS ETES CHEF CUISINIER !
Vous avez des plats a preparer et des commis pour vous aider.
Chaque plat a un temps d'epluchage + un temps de cuisson.

VOTRE MISSION :
Repartir les plats entre les commis pour finir LE PLUS VITE POSSIBLE !

LE MAKESPAN = le temps du commis qui finit EN DERNIER
(c'est ce nombre qu'il faut minimiser)

TOUR 1 : Faites comme vous voulez !
TOUR 2 : Suivez l'algorithme glouton (l'animateur explique)
```

---

### B.6 Materiel Divers

| Materiel | Usage | Quantite |
|----------|-------|----------|
| Ciseaux | Decouper les cartes (si pas deja fait) | 5-6 paires |
| Feutres de couleur | Ecrire sur les cartes et plateaux | 1 boite |
| Scotch / Patafix | Fixer les plateaux sur la table | 1 rouleau |
| Chronometre | Timer pour les tours (telephone suffit) | 1 |
| Calculatrice simple | Additionner les temps (optionnel) | 1 par groupe |
| Stylos | Remplir les fiches score | 1 par eleve |
| Tableau blanc ou paperboard | Ecrire les resultats de tous les groupes | 1 |

---

## C. LISTE DE COURSES

| Article | Prix estime | Ou acheter |
|---------|-------------|------------|
| Papier cartonne couleur A4 (50 feuilles) | 5 euros | Action / Cultura |
| Feutres gros pointe (boite de 12) | 3 euros | Action |
| Feuilles A3 blanches (10 feuilles) | 2 euros | Papeterie |
| Ficelle ou ruban (10m) | 2 euros | Brico / Action |
| Pochettes de plastification (optionnel) | 5 euros | Amazon / Cultura |
| Post-its grands format (optionnel) | 4 euros | Cultura |
| **TOTAL** | **15-20 euros** | |

La plupart du materiel existe deja au lycee ou a l'universite (ciseaux, feutres, scotch, papier).

---

## D. PREPARATION LA VEILLE

### D.1 Fabriquer les cartes (1 heure)

1. Choisir l'instance (on recommande **exemple_3_sujet** : 4 plats, 2 commis, simple et efficace)
2. Decouper les rectangles de papier cartonne (8x12 cm)
3. Ecrire les informations sur chaque carte (nom, epluchage, cuisson, total)
4. Faire **6 jeux identiques** (6 groupes x 4 cartes = 24 cartes a fabriquer)
5. Optionnel : plastifier

### D.2 Fabriquer les plateaux (30 min)

1. Sur chaque feuille A3, ecrire "COMMIS 1", "COMMIS 2"
2. Tracer les emplacements pour les cartes
3. Ecrire "Charge totale : ___ min" en bas
4. Faire 6 x 2 = 12 plateaux

### D.3 Imprimer les fiches (10 min)

1. Imprimer 6 fiches score
2. Imprimer 1 affiche regles du jeu (ou l'ecrire au tableau)
3. Preparer une feuille au tableau pour noter les resultats de tous les groupes

### D.4 Calculer la solution glouton a l'avance

Pour l'instance exemple_3_sujet (4 plats, 2 commis) :

**Etape 1 - Tri :** Plat 3 (37) >= Plat 4 (31) >= Plat 1 (20) >= Plat 2 (20)

**Etape 2 - Assignation :**
- Plat 3 (37 min) → Commis 1 (charge 0, le moins charge) → C1 = 37
- Plat 4 (31 min) → Commis 2 (charge 0, le moins charge) → C2 = 31
- Plat 1 (20 min) → Commis 2 (charge 31 < 37) → C2 = 51
- Plat 2 (20 min) → Commis 1 (charge 37 < 51) → C1 = 57

**Resultat :** Commis 1 = 57 min, Commis 2 = 51 min, **Makespan = 57 min**

---

## E. LE JOUR J - DEROULEMENT MINUTE PAR MINUTE

### E.1 Installation de la salle (10 min avant)

1. Disposer les tables en **ilots** de 5 places (5-6 ilots)
2. Sur chaque ilot, poser :
   - 1 jeu de cartes-plats (face cachee pour le suspense)
   - 2 plateaux commis
   - 1 fiche score
   - Des stylos
3. Au tableau, ecrire le titre : "Chef d'Orchestre en Cuisine"
4. Afficher les regles du jeu

---

### E.2 Accueil et Accroche (5 min)

**Ce que dit l'animateur :**

> "Bonjour a tous ! Aujourd'hui vous allez devenir chefs cuisinier. Imaginez : vous travaillez dans un grand restaurant. C'est le coup de feu du samedi soir. Vous avez plusieurs plats a preparer, mais seulement 2 commis pour vous aider."

> "Chaque plat doit etre epluche puis cuit. Votre probleme : comment repartir les plats entre vos commis pour que tout soit pret le plus vite possible ?"

> "Retournez vos cartes et decouvrez vos plats !"

Les eleves retournent les cartes et decouvrent les plats avec leurs temps.

---

### E.3 Tour 1 - Strategie Libre (7 min)

**Ce que dit l'animateur :**

> "Vous avez 5 minutes pour repartir vos plats entre les 2 commis. Posez les cartes sur les plateaux. Il n'y a pas de mauvaise reponse, faites comme vous le sentez !"

> "Quand c'est fait, additionnez les temps totaux de chaque commis. Le makespan, c'est le temps du commis le plus charge. Notez-le sur votre fiche."

**Ce que font les eleves :**
- Ils prennent les cartes en main
- Ils discutent entre eux ("mets celui-la chez commis 2, il a moins")
- Ils posent les cartes sur les plateaux
- Ils calculent les totaux
- Ils ecrivent le makespan sur la fiche

**Ce que fait l'animateur :**
- Circuler entre les groupes
- Observer les strategies (certains font au hasard, d'autres essaient d'equilibrer)
- Ne pas donner de conseil, les laisser faire
- Au bout de 5 min : "Stop ! Notez votre makespan."

---

### E.4 Tour 2 - Algorithme Glouton (10 min)

**Ce que dit l'animateur :**

> "Maintenant, on va essayer une methode systematique. Ca s'appelle l'algorithme glouton. Suivez bien les etapes :"

> "Etape 1 : Prenez toutes vos cartes et triez-les du temps total le plus grand au plus petit. Mettez-les en ligne sur la table."

Les eleves trient physiquement les cartes. L'animateur verifie.

> "Etape 2 : Prenez la premiere carte (la plus longue). Posez-la sur le commis qui a le MOINS de travail. Si c'est egal, choisissez n'importe lequel."

> "Etape 3 : Prenez la carte suivante. Regardez quel commis a le moins de charge. Posez-la dessus."

> "Continuez jusqu'a ce que toutes les cartes soient placees."

**Ce que font les eleves :**
- Ils retirent toutes les cartes des plateaux
- Ils les trient en ligne (du plus long au plus court)
- Carte par carte, ils les posent sur le commis le moins charge
- Ils calculent le nouveau makespan
- Ils notent sur la fiche

**Ce que fait l'animateur :**
- Passer dans les groupes pour verifier le tri
- S'assurer qu'ils assignent bien au commis le MOINS charge
- Aider si besoin avec les additions

---

### E.5 Comparaison et Resultats (5 min)

**Ce que dit l'animateur :**

> "C'est l'heure des resultats ! Chaque groupe, donnez-moi vos deux makespans."

L'animateur note au tableau :

```
| Groupe | Tour 1 (libre) | Tour 2 (glouton) | Difference |
|--------|----------------|------------------|------------|
| G1     | 68 min         | 57 min           | -11 min    |
| G2     | 57 min         | 57 min           | 0          |
| G3     | 62 min         | 57 min           | -5 min     |
| ...    |                |                  |            |
```

> "Qui a reussi a faire MIEUX que l'algorithme glouton au Tour 1 ?"

(En general, peu de groupes y arrivent. Si un groupe y arrive, les feliciter !)

> "Qui a obtenu le MEME resultat que le glouton ?"

> "Remarquez : tout le monde obtient le meme resultat au Tour 2. Normal, c'est un ALGORITHME : il donne toujours le meme resultat pour les memes donnees."

---

### E.6 La Revelation - Pourquoi c'est Important (8 min)

**Ce que dit l'animateur :**

> "Question : est-ce que l'algorithme glouton donne toujours LA meilleure solution possible ?"

Laisser les eleves repondre.

> "La reponse est NON. Mais il donne une TRES bonne solution, et surtout, il est RAPIDE."

> "Maintenant, imaginons qu'on a 20 plats et 5 commis. Combien de facons differentes de repartir existe-t-il ?"

Laisser les eleves reflechir.

> "Pour chaque plat, on a 5 choix (quel commis). Donc 5 x 5 x 5 x ... (20 fois) = 5 puissance 20 = environ 95 000 milliards de combinaisons !"

Ecrire le nombre au tableau : **95 000 000 000 000**

> "Meme un ordinateur tres rapide ne peut pas toutes les tester. Ce type de probleme s'appelle NP-complet. C'est un des grands mysteres de l'informatique."

> "L'algorithme glouton, lui, ne teste qu'UNE seule combinaison, mais il la choisit intelligemment. Et il garantit un resultat au pire 2 fois l'optimal."

**Analogie pour les eleves :**

> "C'est comme si vous cherchiez un mot dans le dictionnaire. Vous pourriez lire toutes les pages (methode exhaustive = tres lent). Ou vous ouvrez au milieu et vous vous rapprochez (methode intelligente = rapide). L'algo glouton, c'est la methode intelligente."

---

### E.7 Mini-Quiz Oral (5 min)

Poser ces questions a la classe, lever la main pour repondre :

**Q1 :** "L'algorithme glouton donne-t-il toujours la solution parfaite ?"
→ Non, mais une bonne approximation

**Q2 :** "Pourquoi on trie les plats du plus grand au plus petit ?"
→ Pour placer les gros d'abord et equilibrer avec les petits ensuite

**Q3 :** "Donnez un exemple de la vie quotidienne ou on retrouve ce probleme"
→ Caisses de supermarche, emploi du temps, GPS, serveurs internet, chaine de montage

**Q4 :** "Si on a 100 plats et 10 commis, combien de combinaisons ?"
→ 10 puissance 100 = un googol (plus que d'atomes dans l'univers)

---

### E.8 Cloture (2 min)

> "Ce qu'on a vu aujourd'hui, c'est exactement ce que font les ingenieurs en informatique au quotidien. Votre GPS, Netflix, Amazon... tous utilisent des algorithmes comme celui-ci pour optimiser."

> "Et la grande question P = NP, c'est-a-dire 'existe-t-il un algorithme rapide pour ces problemes difficiles ?', c'est un des 7 problemes du millenaire. Il y a 1 million de dollars de recompense pour celui qui le resout !"

Ramasser les fiches score, les cartes et les plateaux.

---

## F. VARIANTES ET ADAPTATIONS

### F.1 Version plus facile (college, seconde)
- Utiliser une instance a 3 plats et 2 commis (exemple_1_sujet)
- Ne pas parler de NP-completude
- Se concentrer sur le tri et l'equilibrage

### F.2 Version plus difficile (terminale NSI)
- Utiliser une instance a 10+ plats (test_difficile)
- Ajouter un Tour 3 ou les eleves doivent trouver la solution OPTIMALE (en testant toutes les combinaisons pour une petite instance)
- Comparer le temps qu'ils mettent vs le temps du glouton
- Introduire le ratio d'approximation 2 - 1/m

### F.3 Version competition
- Chaque groupe essaie de trouver le MEILLEUR makespan possible au Tour 1
- Le groupe gagnant est celui qui a le plus petit makespan
- Puis on compare avec le glouton : "L'algorithme a-t-il battu les humains ?"

### F.4 Version avec contraintes supplementaires
- Ajouter une contrainte : "Commis 1 ne peut pas faire plus de 3 plats" (contrainte de capacite)
- Ou : "Le Plat 3 doit etre fini avant le Plat 4" (contrainte de precedence)
- Ca montre que les problemes reels sont encore plus complexes

---

## G. ERREURS COURANTES A EVITER

1. **Ne pas laisser assez de temps pour manipuler** : le but c'est que les eleves touchent les cartes, pas qu'ils regardent l'animateur
2. **Donner la reponse trop vite** : laisser les eleves galerrer au Tour 1, c'est pedagogique
3. **Instance trop grande** : avec 15 plats et 5 commis, les eleves se perdent dans les calculs. Commencer simple (4 plats, 2 commis)
4. **Oublier de comparer** : tout l'interet est dans la comparaison Tour 1 vs Tour 2. Ne pas la sauter
5. **Trop de theorie** : les lyceens decrochent apres 5 min de theorie. Alterner manipulation et explication
6. **Pas de conclusion concrete** : toujours finir par "a quoi ca sert dans la vraie vie"

---

## H. LIENS AVEC LE PROGRAMME SCOLAIRE

| Niveau | Matiere | Notion |
|--------|---------|--------|
| Seconde | SNT | Algorithmes, donnees structurees |
| Premiere NSI | NSI | Algorithmes de tri, complexite |
| Terminale NSI | NSI | Programmation dynamique, graphes, NP-completude |
| Terminale | Maths | Optimisation, denombrement, combinatoire |

---

## I. CHECKLIST JOUR J

- [ ] 6 jeux de cartes-plats prets
- [ ] 12 plateaux commis (2 par groupe)
- [ ] 6 fiches score imprimees
- [ ] Affiche regles du jeu
- [ ] Feutres et stylos
- [ ] Chronometre pret
- [ ] Tableau blanc disponible
- [ ] Solution glouton calculee a l'avance
- [ ] Salle avec tables en ilots
- [ ] Avoir repete le discours une fois avant
