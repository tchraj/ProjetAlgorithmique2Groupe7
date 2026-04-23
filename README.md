# ProjetAlgorithmique2Groupe7 — Guide de déploiement

Application Flask de simulation d'ordonnancement en cuisine (Algorithme de Johnson, NEH, LPT, FIFO, Brute Force).

---

## Prérequis

Assurez-vous d'avoir sur la machine de build :

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et **lancé**
- `make` installé (`choco install make` sur Windows, déjà présent sur Linux/macOS)
- Accès au registry Docker de Terra Numerica
- Accès SSH au serveur de déploiement Terra Numerica

---

## ⚙️ Configuration initiale (à faire une seule fois)

Avant toute chose, remplacez les placeholders dans **deux fichiers** par les vraies valeurs Terra Numerica :

### 1. Dans `Makefile` (ligne 2)

```makefile
REGISTRY=<adresse-registry-terra-numerica>
```

### 2. Dans `deploy/docker-compose.yaml` (ligne 3)

```yaml
image: <adresse-registry-terra-numerica>/projetalgorithmique2groupe7:latest
```

> ⚠️ L'adresse doit être **identique** dans les deux fichiers.

---

## 🚀 Étapes de déploiement

### Étape 1 — Cloner le projet

```bash
git clone <url-du-repo>
cd ProjetAlgorithmique2Groupe7
```

### Étape 2 — Build de l'image Docker

```bash
make build
```

En cas de succès, vous devriez voir en fin de sortie :

```
=> naming to docker.io/library/projetalgorithmique2groupe7:latest
```

> **Sans `make`** : `docker build -t projetalgorithmique2groupe7:latest .`

### Étape 3 — Push de l'image sur le registry Terra Numerica

```bash
make push
```

Cette commande tague l'image et l'envoie sur le registry. Le serveur pourra ensuite la télécharger automatiquement.

> **Sans `make`** :
> ```bash
> docker tag projetalgorithmique2groupe7:latest <adresse-registry-terra-numerica>/projetalgorithmique2groupe7:latest
> docker push <adresse-registry-terra-numerica>/projetalgorithmique2groupe7:latest
> ```

### Étape 4 — Copier les fichiers sur le serveur Terra Numerica

Depuis votre machine locale, exécutez les commandes suivantes en remplaçant `<user>` et `<serveur>` par vos identifiants Terra Numerica :

```bash
# Créer le répertoire dédié sur le serveur
ssh <user>@<serveur> "mkdir -p /home/<user>/projetalgorithmique2groupe7"

# Copier le docker-compose de production
scp deploy/docker-compose.yaml <user>@<serveur>:/home/<user>/projetalgorithmique2groupe7/

# Copier le dossier instances (requis par le bind mount — données JSON lues au runtime)
scp -r instances/ <user>@<serveur>:/home/<user>/projetalgorithmique2groupe7/
```

> Le dossier `instances/` contient les fichiers JSON utilisés par l'application. Il doit être présent sur le serveur **au même niveau** que le `docker-compose.yaml`, conformément au bind mount défini dans `deploy/docker-compose.yaml` :
> ```yaml
> volumes:
>   - ./instances:/app/instances
> ```

### Étape 5 — Lancer le stack sur le serveur

Connectez-vous en SSH au serveur, puis lancez l'application :

```bash
ssh <user>@<serveur>
cd /home/<user>/projetalgorithmique2groupe7/
docker compose up -d
```

Le flag `-d` lance le container en arrière-plan.

### Étape 6 — Vérifier le démarrage via les logs

Toujours sur le serveur :

```bash
docker compose logs -f
```

Vous devriez voir :

```
web-1  | [INFO] Starting gunicorn 22.0.0
web-1  | [INFO] Listening at: http://0.0.0.0:5000
web-1  | [INFO] Booting worker with pid: 7
web-1  | [INFO] Page d'accueil chargée
web-1  | [INFO] Algorithmes disponibles : johnson, neh, lpt, fifo, brute
```

> Appuyez sur `Ctrl+C` pour quitter l'affichage des logs. Le container continue de tourner.

### Étape 7 — Vérifier le fonctionnement depuis un navigateur

Ouvrez un navigateur sur n'importe quelle machine et accédez à :

```
http://<adresse-serveur>:5000
```

Vous devriez voir la page d'accueil de l'application **Kitchen Scheduler**.

---

## 📁 Structure des fichiers de déploiement

```
ProjetAlgorithmique2Groupe7/
├── app.py                    # Point d'entrée Flask
├── Dockerfile                # Image Docker
├── docker-compose.yml        # Compose pour le développement LOCAL uniquement
├── Makefile                  # Commandes build / push / run
├── requirements.txt          # Dépendances Python (flask, gunicorn)
├── .dockerignore             # Fichiers exclus du build
│
├── deploy/                   # ← Contenu à copier sur le serveur (étape 4)
│   └── docker-compose.yaml   # Compose de PRODUCTION (tire l'image depuis le registry)
│
├── instances/                # ← À copier sur le serveur (étape 4) — bind mount
│   ├── reference_instances.json
│   └── test_instances.json
│
├── backend/
│   ├── algorithms/           # Algorithmes de load balancing
│   ├── schedulers/           # Johnson, NEH, LPT, FIFO, Brute Force
│   ├── models/               # Modèle Plat
│   └── services/             # Services de comparaison
├── static/                   # CSS, JS, images
└── templates/                # Templates HTML Flask
```

---

## 🛠️ Commandes utiles

| Commande | Description |
|----------|-------------|
| `make build` | Construire l'image Docker |
| `make push` | Pousser l'image sur le registry |
| `make run` | Lancer le stack en local |
| `make logs` | Afficher les logs en local |
| `make stop` | Arrêter le stack local |
| `docker compose logs -f` | Logs en temps réel (sur le serveur) |
| `docker compose down` | Arrêter et supprimer le stack |
| `docker compose ps` | Voir l'état des containers |

---

## ❗ En cas de problème

**Docker ne répond pas**
→ Vérifiez que Docker Desktop est lancé (icône baleine 🐳 dans la barre des tâches).

**`make` non reconnu sur Windows**
→ Ouvrez PowerShell en administrateur et exécutez `choco install make`.
→ Ou utilisez directement les commandes `docker` équivalentes indiquées à chaque étape.

**Erreur lors du `make push` : `No such file or directory`**
→ Vous n'avez pas remplacé `<adresse-registry-terra-numerica>` dans le `Makefile`. Voir la section Configuration initiale.

**Port 5000 déjà utilisé sur le serveur**
→ Modifiez `deploy/docker-compose.yaml` : remplacez `"5000:5000"` par `"5001:5000"` et accédez à `:5001`.

**Le container démarre mais l'application est inaccessible**
→ Vérifiez que `app.py` se termine bien par `app.run(host='0.0.0.0', port=5000, debug=False)`.
→ Vérifiez que le port 5000 est ouvert dans le pare-feu du serveur Terra Numerica.

**Les instances ne se chargent pas**
→ Vérifiez que le dossier `instances/` a bien été copié sur le serveur (étape 4) au même niveau que `docker-compose.yaml`.
