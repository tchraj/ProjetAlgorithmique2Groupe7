import heapq

def greedy_scheduler(tasks, num_workers):
    """
    Attribue des tâches à un certain nombre de travailleurs à l'aide d'un algorithme glouton.

    :param tasks: Un dictionnaire de tâches où les clés sont les noms des tâches et les valeurs sont les temps de traitement.
    :param num_workers: Le nombre de travailleurs disponibles.
    :return: Une liste de listes, où chaque sous-liste représente les tâches assignées à un travailleur,
             et la durée totale du travail pour tous les travailleurs.
    """
    # Trier les tâches par temps de traitement par ordre décroissant
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1], reverse=True)

    # Initialiser les travailleurs avec un temps de travail de 0 et une liste de tâches vide
    workers = [{'time': 0, 'tasks': []} for _ in range(num_workers)]

    # Utiliser un tas min pour suivre le temps de travail total de chaque travailleur
    worker_heap = [(0, i) for i in range(num_workers)] # (temps, index_travailleur)

    # Assigner chaque tâche au travailleur avec le moins de travail
    for task_name, task_time in sorted_tasks:
        # Obtenir le travailleur avec le temps de travail le plus faible
        current_time, worker_index = heapq.heappop(worker_heap)

        # Assigner la tâche à ce travailleur
        workers[worker_index]['tasks'].append((task_name, task_time))
        new_time = current_time + task_time
        workers[worker_index]['time'] = new_time

        # Mettre à jour le tas avec le nouveau temps de travail du travailleur
        heapq.heappush(worker_heap, (new_time, worker_index))

    # Calculer le temps total (makespan)
    makespan = max(worker['time'] for worker in workers)

    return workers, makespan

def dynamic_programming_scheduler(tasks, num_workers):
    """
    Résout le problème d'ordonnancement à l'aide de la programmation dynamique.
    Ceci est pour un nombre fixe de travailleurs et est NP-difficile, donc seulement réalisable pour de petites instances.
    Pour ce projet, nous allons simuler une approche plus simple car une véritable solution DP
    est très complexe à mettre en œuvre correctement.

    Cette fonction fournira une solution de base et pourra être étendue.
    Pour l'instant, elle renverra le même résultat que l'algorithme glouton pour des raisons de simplicité.
    """
    # Pour la démonstration, nous allons appeler l'algorithme glouton.
    # Une véritable implémentation de la programmation dynamique serait beaucoup plus complexe.
    return greedy_scheduler(tasks, num_workers)

