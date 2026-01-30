from flask import Flask, render_template, request, jsonify
from algorithms import greedy_scheduler, dynamic_programming_scheduler
import heapq

app = Flask(__name__)

# Catalogue des plats pour le jeu Kitchen Load Balancer
PLATS_CATALOGUE = {
    'A': {'nom': 'Salade César', 'prep': 15, 'cuisson': 0, 'dressage': 5, 'priorite': 'normale', 'deadline': 25},
    'B': {'nom': 'Pizza', 'prep': 10, 'cuisson': 17, 'dressage': 3, 'priorite': 'normale', 'deadline': 30},
    'C': {'nom': 'Steak grillé', 'prep': 8, 'cuisson': 12, 'dressage': 4, 'priorite': 'elevee', 'deadline': 25},
    'D': {'nom': 'Plat gastronomique', 'prep': 20, 'cuisson': 25, 'dressage': 10, 'priorite': 'vip', 'deadline': 45},
    'E': {'nom': 'Burger', 'prep': 7, 'cuisson': 10, 'dressage': 3, 'priorite': 'normale', 'deadline': 20},
    'F': {'nom': 'Soupe', 'prep': 12, 'cuisson': 18, 'dressage': 4, 'priorite': 'basse', 'deadline': 35}
}

@app.route('/')
def index():
    return render_template('index.html')

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
    elif algorithm == 'dp':
        workers, makespan = dynamic_programming_scheduler(tasks, num_workers)
    else:
        return jsonify({'error': 'Algorithme non valide.'}), 400

    return jsonify({
        'workers': workers,
        'makespan': makespan
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

