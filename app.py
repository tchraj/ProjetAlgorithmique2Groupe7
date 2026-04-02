import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from flask import Flask, render_template, request, jsonify
# Import des algorithmes et du gestionnaire d'instances depuis le package backend.algorithms
from algorithms.load_balancing_algorithms import greedy_scheduler
from algorithms.instance_loader import InstanceManager
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.lpt_scheduler     import LPTScheduler
from schedulers.neh_scheduler     import NEHScheduler
from schedulers.fifo_scheduler    import FIFOScheduler
from schedulers.brute_force_scheduler import BruteForceScheduler
from models.plat                  import Plat
import time as time_module
import heapq
import math

app = Flask(__name__)

# Gestionnaire d'instances
instance_manager = InstanceManager()

# Catalogue des plats pour le jeu Kitchen Load Balancer
PLATS_CATALOGUE = {
    'A': {'nom': 'Salade César', 'prep': 15, 'cuisson': 0, 'dressage': 5, 'priorite': 'normale', 'deadline': 25},
    'B': {'nom': 'Pizza', 'prep': 10, 'cuisson': 17, 'dressage': 3, 'priorite': 'normale', 'deadline': 30},
    'C': {'nom': 'Steak grillé', 'prep': 8, 'cuisson': 12, 'dressage': 4, 'priorite': 'elevee', 'deadline': 25},
    'D': {'nom': 'Plat gastronomique', 'prep': 20, 'cuisson': 25, 'dressage': 10, 'priorite': 'vip', 'deadline': 45},
    'E': {'nom': 'Burger', 'prep': 7, 'cuisson': 10, 'dressage': 3, 'priorite': 'normale', 'deadline': 20},
    'F': {'nom': 'Soupe', 'prep': 12, 'cuisson': 18, 'dressage': 4, 'priorite': 'basse', 'deadline': 35}
}

SCHEDULERS = {
    'johnson': JohnsonScheduler(),
    'neh':     NEHScheduler(),
    'lpt':     LPTScheduler(),
    'fifo':    FIFOScheduler(),
    'brute':   BruteForceScheduler(),
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activite-debranchee')
def activite_debranchee():
    """Page de l'activité débranchée : simulation animée + cartes imprimables."""
    return render_template('activite_debranchee.html')

@app.route('/api/plats', methods=['GET'])
def get_plats():
    """Retourne le catalogue des plats disponibles."""
    return jsonify(PLATS_CATALOGUE)

@app.route('/api/assign', methods=['POST'])
def assign_plat():
    """
    Assigne un plat à une station en utilisant l'algorithme spécifié.
    Retourne la station recommandée pour l'étape suivante du plat.
    """
    data = request.json
    plat_id = data.get('plat_id')
    current_etape = data.get('current_etape')
    algorithm = data.get('algorithm', 'least-loaded')
    stations_load = data.get('stations_load', {})

    if plat_id not in PLATS_CATALOGUE:
        return jsonify({'error': 'Plat inconnu'}), 400

    plat = PLATS_CATALOGUE[plat_id]

    # Déterminer l'étape suivante
    etapes = ['preparation', 'cuisson', 'dressage']
    if current_etape is None:
        next_etape = 'preparation'
    else:
        try:
            current_index = etapes.index(current_etape)
            if current_index < len(etapes) - 1:
                next_etape = etapes[current_index + 1]
                # Sauter la cuisson si temps = 0
                if next_etape == 'cuisson' and plat['cuisson'] == 0:
                    next_etape = 'dressage'
            else:
                return jsonify({'next_etape': None, 'message': 'Plat terminé'})
        except ValueError:
            return jsonify({'error': 'Étape invalide'}), 400

    # Appliquer l'algorithme de load balancing
    result = {
        'next_etape': next_etape,
        'algorithm_used': algorithm,
        'plat_info': plat
    }

    if algorithm == 'least-loaded':
        # Retourner la charge de la station cible
        load = stations_load.get(next_etape, 0)
        result['station_load'] = load
    elif algorithm == 'round-robin':
        result['message'] = 'Round Robin: assignation cyclique'
    elif algorithm == 'shortest-job':
        # Priorité aux plats les plus courts
        total_time = plat['prep'] + plat['cuisson'] + plat['dressage']
        result['total_time'] = total_time
    elif algorithm == 'priority-first':
        # Priorité VIP > elevee > normale > basse
        priority_order = {'vip': 0, 'elevee': 1, 'normale': 2, 'basse': 3}
        result['priority_rank'] = priority_order.get(plat['priorite'], 2)

    return jsonify(result)

@app.route('/api/simulate', methods=['POST'])
def simulate_schedule():
    """
    Simule l'ordonnancement complet d'une liste de plats.
    Utilise l'algorithme spécifié pour optimiser le makespan.
    """
    data = request.json
    plats_ids = data.get('plats', [])
    algorithm = data.get('algorithm', 'least-loaded')

    if not plats_ids:
        return jsonify({'error': 'Aucun plat fourni'}), 400

    # Construire les tâches pour chaque station
    prep_tasks = {}
    cuisson_tasks = {}
    dressage_tasks = {}

    for i, plat_id in enumerate(plats_ids):
        if plat_id in PLATS_CATALOGUE:
            plat = PLATS_CATALOGUE[plat_id]
            task_name = f"{plat['nom']}_{i}"
            prep_tasks[task_name] = plat['prep']
            if plat['cuisson'] > 0:
                cuisson_tasks[task_name] = plat['cuisson']
            dressage_tasks[task_name] = plat['dressage']

    # Simuler avec l'algorithme glouton (Least Loaded)
    results = {
        'preparation': greedy_scheduler(prep_tasks, 2)[1] if prep_tasks else 0,
        'cuisson': greedy_scheduler(cuisson_tasks, 1)[1] if cuisson_tasks else 0,
        'dressage': greedy_scheduler(dressage_tasks, 1)[1] if dressage_tasks else 0
    }

    # Le makespan total est approximatif car les étapes sont séquentielles
    total_makespan = results['preparation'] + results['cuisson'] + results['dressage']

    return jsonify({
        'algorithm': algorithm,
        'station_makespans': results,
        'estimated_total': total_makespan,
        'plats_count': len(plats_ids)
    })

@app.route('/schedule', methods=['POST'])
def schedule():
    """Endpoint legacy pour l'ancien formulaire de planification."""
    data = request.json
    tasks_str = data.get('tasks')
    num_workers = int(data.get('num_workers'))
    algorithm = data.get('algorithm')

    # Analyser les tâches à partir de la chaîne de caractères
    tasks = {}
    for line in tasks_str.strip().split('\n'):
        try:
            name, time = line.split(',')
            tasks[name.strip()] = int(time.strip())
        except ValueError:
            return jsonify({'error': f"Ligne mal formatée : {line}"}), 400

    if not tasks:
        return jsonify({'error': 'Aucune tâche fournie.'}), 400

    if algorithm == 'greedy':
        workers, makespan = greedy_scheduler(tasks, num_workers)
    else:
        return jsonify({'error': 'Algorithme non valide.'}), 400

    return jsonify({
        'workers': workers,
        'makespan': makespan
    })


@app.route('/compare')
def compare():
    """Page de comparaison des algorithmes."""
    return render_template('compare.html')


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """
    Compare plusieurs algorithmes sur une même instance.

    Body JSON attendu :
    {
        "plats": [
            {"nom": "Plat A", "prep": 15, "cuisson": 17},
            ...
        ],
        "nb_commis": 1,
        "nb_fours":  1,
        "algos": ["johnson", "neh", "lpt", "fifo"]
    }

    Retourne :
    {
        "resultats": {
            "johnson": {
                "makespan": 2700,
                "temps_execution": 0.00012,
                "est_optimal": true,
                "ordre": ["Plat C", "Plat B", "Plat A"],
                "schedule_commis": [...],
                "schedule_fours":  [...]
            },
            ...
        },
        "meilleur_algo":       "johnson",
        "meilleur_makespan":   2700,
        "est_optimal_garanti": true,
        "nb_commis": 1,
        "nb_fours":  1
    }
    """
    data       = request.get_json(force=True)
    plats_raw  = data.get('plats', [])
    nb_commis  = max(1, int(data.get('nb_commis', 1)))
    nb_fours   = max(1, int(data.get('nb_fours',  1)))
    algos_req  = data.get('algos', list(SCHEDULERS.keys()))

    # ── Validation ───────────────────────────────────────
    if not plats_raw:
        return jsonify({'error': 'Aucun plat fourni.'}), 400

    if len(plats_raw) > 30:
        return jsonify({'error': 'Maximum 30 plats par comparaison.'}), 400

    # ── Construire les objets Plat ────────────────────────
    plats = []
    for i, p in enumerate(plats_raw):
        try:
            nom     = str(p.get('nom', f'Plat {i+1}')).strip() or f'Plat {i+1}'
            prep    = max(0, int(p.get('prep',    0))) * 60  # minutes → secondes
            cuisson = max(0, int(p.get('cuisson', 0))) * 60
            plats.append(Plat(id=i, nom=nom, temps_prep=prep, temps_cuisson=cuisson))
        except (ValueError, TypeError):
            return jsonify({'error': f'Plat {i+1} : données invalides.'}), 400

    stations = {'commis': nb_commis, 'fours': nb_fours}

    # ── Lancer chaque algorithme ──────────────────────────
    resultats = {}

    for nom_algo in algos_req:
        scheduler = SCHEDULERS.get(nom_algo)
        if not scheduler:
            continue  # algo inconnu → on ignore silencieusement

        t0      = time_module.perf_counter()
        resultat = scheduler.schedule(plats, stations)
        elapsed  = time_module.perf_counter() - t0

        # Sérialiser le planning pour le JSON
        resultats[nom_algo] = {
            'makespan':        resultat['makespan'],
            'temps_execution': elapsed,
            'est_optimal':     resultat.get('est_optimal', False),
            'ordre':           [p.nom for p in resultat['ordre']],
            'schedule_commis': _serialiser_schedule(resultat['schedule_commis']),
            'schedule_fours':  _serialiser_schedule(resultat['schedule_fours']),
        }

    if not resultats:
        return jsonify({'error': 'Aucun algorithme valide sélectionné.'}), 400

    # ── Trouver le meilleur ───────────────────────────────
    meilleur_algo     = min(resultats, key=lambda k: resultats[k]['makespan'])
    meilleur_makespan = resultats[meilleur_algo]['makespan']

    # L'optimal est garanti seulement si Johnson est le meilleur ET 1+1
    est_optimal_garanti = (
        'johnson' in resultats
        and nb_commis == 1
        and nb_fours  == 1
    )

    # Ajouter le ratio par rapport au meilleur pour chaque algo
    for r in resultats.values():
        r['ratio'] = round(r['makespan'] / meilleur_makespan, 4) if meilleur_makespan > 0 else 1.0

    return jsonify({
        'resultats':           resultats,
        'meilleur_algo':       meilleur_algo,
        'meilleur_makespan':   meilleur_makespan,
        'est_optimal_garanti': est_optimal_garanti,
        'nb_commis':           nb_commis,
        'nb_fours':            nb_fours,
    })


def _serialiser_schedule(schedule_liste):
    """
    Convertit les objets Plat dans le planning en dicts JSON-sérialisables.
    schedule_liste : List[List[{'plat': Plat, 'debut': int, 'fin': int}]]
    """
    resultat = []
    for station in schedule_liste:
        taches = []
        for tache in station:
            p = tache['plat']
            taches.append({
                'plat':  {'nom': p.nom, 'id': p.id},
                'debut': tache['debut'],
                'fin':   tache['fin'],
            })
        resultat.append(taches)
    return resultat

# ================================================
# API Instances - Rendre les instances générées utilisables par le front
# ================================================

# Icônes associées aux ingrédients pour l'affichage frontend
ICONS_INGREDIENTS = {
    "pomme": "\U0001F34E", "poire": "\U0001F350", "mangue": "\U0001F96D",
    "ananas": "\U0001F34D", "kiwi": "\U0001F95D", "orange": "\U0001F34A",
    "pêche": "\U0001F351", "abricot": "\U0001F351", "prune": "\U0001F351",
    "cerise": "\U0001F352", "fraise": "\U0001F353", "framboise": "\U0001F353",
    "myrtille": "\U0001FAD0", "melon": "\U0001F348", "pastèque": "\U0001F349",
    "raisin": "\U0001F347", "litchi": "\U0001F352", "papaye": "\U0001F96D",
    "goyave": "\U0001F96D", "carotte": "\U0001F955", "pomme de terre": "\U0001F954",
    "courgette": "\U0001F96C", "aubergine": "\U0001F346", "poivron": "\U0001FAD1",
    "tomate": "\U0001F345", "concombre": "\U0001F96C", "radis": "\U0001F96C",
    "navet": "\U0001F96C", "céleri": "\U0001F96C", "poireau": "\U0001F96C",
    "champignon": "\U0001F344", "brocoli": "\U0001F966", "chou-fleur": "\U0001F966",
    "haricot vert": "\U0001FAD8", "salade": "\U0001F957", "soupe": "\U0001F372",
}
ICON_PAR_DEFAUT = "\U0001F37D\uFE0F"


def convertir_plat_pour_frontend(plat_backend, index):
    """
    Convertit un plat du format instance (temps_prep/temps_cuisson en secondes)
    vers le format attendu par le frontend (prep/cuisson/dressage en secondes de jeu).

    Règle de conversion : temps réels (secondes) / 60 → secondes de jeu
    Cela rend les instances jouables (900s réelles = 15s de jeu).
    """
    prep = max(1, round(plat_backend["temps_prep"] / 60))
    cuisson = round(plat_backend["temps_cuisson"] / 60)

    # Dressage : ~25% du temps de préparation, entre 2 et 10 secondes de jeu
    dressage = max(2, min(10, round(prep * 0.25))) if prep > 0 else 3

    temps_total = prep + cuisson + dressage

    # Priorité basée sur le temps total
    if temps_total > 45:
        priorite = "vip"
    elif temps_total > 30:
        priorite = "elevee"
    elif temps_total < 12:
        priorite = "basse"
    else:
        priorite = "normale"

    # Deadline : temps total * 1.6, arrondi, minimum 15s
    deadline = max(15, round(temps_total * 1.6))

    # Icône basée sur le nom de l'ingrédient
    nom_lower = plat_backend["nom"].lower()
    icon = ICONS_INGREDIENTS.get(nom_lower, ICON_PAR_DEFAUT)

    # ID unique basé sur l'index
    plat_id = chr(65 + (index % 26))  # A, B, C, ...
    if index >= 26:
        plat_id = f"{plat_id}{index // 26}"

    return {
        "id": plat_id,
        "nom": plat_backend["nom"].capitalize(),
        "icon": icon,
        "prep": prep,
        "cuisson": cuisson,
        "dressage": dressage,
        "priorite": priorite,
        "deadline": deadline,
        # Garder les temps originaux pour référence
        "temps_prep_original": plat_backend["temps_prep"],
        "temps_cuisson_original": plat_backend["temps_cuisson"]
    }


def convertir_instance_pour_frontend(instance):
    """Convertit une instance complète au format frontend."""
    plats_convertis = [
        convertir_plat_pour_frontend(plat, i)
        for i, plat in enumerate(instance["plats"])
    ]
    return {
        "nom": instance["nom"],
        "description": instance.get("description", ""),
        "difficulte": instance.get("difficulte", "moyen"),
        "nombre_commis": instance.get("nombre_commis", 3),
        "statistiques": instance.get("statistiques", {}),
        "plats": plats_convertis
    }


@app.route('/api/instances', methods=['GET'])
def list_instances():
    """Liste toutes les instances disponibles (référence + test)."""
    instances = instance_manager.lister_instances_disponibles()
    return jsonify({"instances": instances})


@app.route('/api/instances/<nom>', methods=['GET'])
def get_instance(nom):
    """
    Retourne une instance spécifique convertie au format frontend.
    Le paramètre ?raw=true retourne le format brut (temps_prep/temps_cuisson).
    """
    instance = instance_manager.obtenir_instance_par_nom(nom)
    if not instance:
        return jsonify({"error": f"Instance '{nom}' non trouvée"}), 404

    raw = request.args.get('raw', 'false').lower() == 'true'
    if raw:
        return jsonify(instance)

    return jsonify(convertir_instance_pour_frontend(instance))


@app.route('/api/instances/generate', methods=['POST'])
def generate_instance():
    """
    Génère une nouvelle instance aléatoire et la retourne au format frontend.

    Body JSON attendu :
    {
        "nombre_plats": 5,       (optionnel, défaut: 5)
        "nombre_commis": 3,      (optionnel, défaut: 3)
        "difficulte": "moyen"    (optionnel: "facile", "moyen", "difficile")
    }
    """
    data = request.json or {}
    nombre_plats = data.get("nombre_plats", 5)
    nombre_commis = data.get("nombre_commis", 3)
    difficulte = data.get("difficulte", "moyen")

    # Validation
    nombre_plats = max(2, min(20, int(nombre_plats)))
    nombre_commis = max(1, min(10, int(nombre_commis)))
    if difficulte not in ("facile", "moyen", "difficile"):
        difficulte = "moyen"

    instance = instance_manager.generer_instance_aleatoire(
        nombre_plats=nombre_plats,
        nombre_commis=nombre_commis,
        difficulte=difficulte
    )

    raw = request.args.get('raw', 'false').lower() == 'true'
    if raw:
        return jsonify(instance)

    return jsonify(convertir_instance_pour_frontend(instance))

@app.route('/jouer')
def jouer():
    """Page mode humain — tester sa propre solution."""
    return render_template('jouer.html')


@app.route('/api/jouer', methods=['POST'])
def api_jouer():
    """
    Calcule le makespan de l'ordre humain ET de Johnson pour comparaison.

    Body JSON :
    {
        "plats":       [{"nom": "Plat A", "prep": 15, "cuisson": 17}, ...],
        "ordre_human": [2, 1, 0],   ← indices dans l'ordre choisi par l'utilisateur
        "nb_commis":   1,
        "nb_fours":    1
    }
    """
    data       = request.get_json(force=True)
    plats_raw  = data.get('plats', [])
    ordre_idx  = data.get('ordre_human', [])
    nb_commis  = max(1, int(data.get('nb_commis', 1)))
    nb_fours   = max(1, int(data.get('nb_fours',  1)))

    if not plats_raw:
        return jsonify({'error': 'Aucun plat fourni.'}), 400

    # Construire les objets Plat
    plats = []
    for i, p in enumerate(plats_raw):
        nom     = str(p.get('nom', f'Plat {i+1}')).strip()
        prep    = max(0, int(p.get('prep',    0))) * 60
        cuisson = max(0, int(p.get('cuisson', 0))) * 60
        plats.append(Plat(id=i, nom=nom, temps_prep=prep, temps_cuisson=cuisson))

    stations = {'commis': nb_commis, 'fours': nb_fours}

    # ── Ordre humain ──────────────────────────────────────
    try:
        plats_human = [plats[i] for i in ordre_idx]
    except IndexError:
        return jsonify({'error': 'Indices d\'ordre invalides.'}), 400

    scheduler_johnson = SCHEDULERS['johnson']

    # Calculer avec l'ordre humain via FIFO (respecte l'ordre donné)
    fifo = SCHEDULERS['fifo']
    res_human = fifo.schedule(plats_human, stations)

    # Calculer avec Johnson
    res_johnson = SCHEDULERS['johnson'].schedule(plats, stations)

    return jsonify({
        'makespan_human':   res_human['makespan'],
        'makespan_johnson': res_johnson['makespan'],
        'ordre_human':      [p.nom for p in plats_human],
        'ordre_johnson':    [p.nom for p in res_johnson['ordre']],
        'schedule_human': {
            'makespan':        res_human['makespan'],
            'schedule_commis': _serialiser_schedule(res_human['schedule_commis']),
            'schedule_fours':  _serialiser_schedule(res_human['schedule_fours']),
        },
        'schedule_johnson': {
            'makespan':        res_johnson['makespan'],
            'schedule_commis': _serialiser_schedule(res_johnson['schedule_commis']),
            'schedule_fours':  _serialiser_schedule(res_johnson['schedule_fours']),
        },
    })

@app.route('/complexite')
def complexite():
    return render_template('complexite.html')

@app.route('/pedagogie')
def pedagogie():
    """Page pédagogique — Algorithme de Johnson expliqué aux lycéens."""
    return render_template('pedagogie_johnson.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

