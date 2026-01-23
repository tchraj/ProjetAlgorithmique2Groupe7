from flask import Flask, render_template, request, jsonify
from algorithms import greedy_scheduler, dynamic_programming_scheduler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
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

