"""
Instances de référence du sujet
VERSION WINDOWS
"""

import json
import os
from pathlib import Path

# Instance basée sur l'Exemple 1 du sujet
EXEMPLE_1 = {
    "nom": "exemple_1_sujet",
    "description": "3 plats: plat 1 (15min prep, 0min cuisson), plat 2 (11min prep, 16min cuisson), plat 3 (0min prep, 8min cuisson)",
    "plats": [
        {"nom": "plat_1", "temps_epluchage": 15 * 60, "temps_cuisson": 0},
        {"nom": "plat_2", "temps_epluchage": 11 * 60, "temps_cuisson": 16 * 60},
        {"nom": "plat_3", "temps_epluchage": 0, "temps_cuisson": 8 * 60}
    ],
    "nombre_commis": 2,
    "difficulte": "facile",
    "source": "Document projet - Exemple 1"
}

EXEMPLE_2 = {
    "nom": "exemple_2_sujet",
    "description": "3 plats: plat 1 (16min prep, 10min cuisson), plat 2 (11min prep, 14min cuisson), plat 3 (0min prep, 8min cuisson)",
    "plats": [
        {"nom": "plat_1", "temps_epluchage": 16 * 60, "temps_cuisson": 10 * 60},
        {"nom": "plat_2", "temps_epluchage": 11 * 60, "temps_cuisson": 14 * 60},
        {"nom": "plat_3", "temps_epluchage": 0, "temps_cuisson": 8 * 60}
    ],
    "nombre_commis": 2,
    "difficulte": "facile",
    "source": "Document projet - Exemple 2"
}

EXEMPLE_3 = {
    "nom": "exemple_3_sujet",
    "description": "6 plats: plat 1 (8min prep, 12min cuisson), plat 2 (12min prep, 8min cuisson), plat 3 (17min prep, 20min cuisson), plat 4 (19min prep, 17min cuisson), plat 5 (19min prep, 20min cuisson), plat 6 (19min prep, 12min cuisson)",
    "plats": [
        {"nom": "plat_1", "temps_epluchage": 8 * 60, "temps_cuisson": 12 * 60},
        {"nom": "plat_2", "temps_epluchage": 12 * 60, "temps_cuisson": 8 * 60},
        {"nom": "plat_3", "temps_epluchage": 17 * 60, "temps_cuisson": 20 * 60},
        {"nom": "plat_4", "temps_epluchage": 19 * 60, "temps_cuisson": 17 * 60},
        {"nom": "plat_5", "temps_epluchage": 19 * 60, "temps_cuisson": 20 * 60},
        {"nom": "plat_6", "temps_epluchage": 19 * 60, "temps_cuisson": 12 * 60}
    ],
    "nombre_commis": 2,
    "difficulte": "difficile",  # Changé de "moyen" à "difficile"
    "source": "Document projet - Exemple 3"
}

EXEMPLE_FRUITS = {
    "nom": "exemple_fruits_classique",
    "description": "Problème d'origine: 43 pommes, 57 mangues, 107 tomates, 13 litchis",
    "plats": [
        {"nom": "pommes", "temps_epluchage": 43 * 30, "temps_cuisson": 43 * 200},
        {"nom": "mangues", "temps_epluchage": 57 * 600, "temps_cuisson": 57 * 100},
        {"nom": "tomates", "temps_epluchage": 107 * 10, "temps_cuisson": 107 * 150},
        {"nom": "litchis", "temps_epluchage": 13 * 5, "temps_cuisson": 13 * 50}
    ],
    "nombre_commis": 3,
    "difficulte": "moyen",
    "source": "Document projet - Problème initial avec fruits"
}

EXEMPLE_VACANCES = {
    "nom": "exemple_vacances_ludique",
    "description": "Planifier des vacances avec activités et horaires contraints",
    "plats": [
        {"nom": "musee", "temps_epluchage": 10 * 3600, "temps_cuisson": 0},
        {"nom": "parc_attraction", "temps_epluchage": 15 * 3600, "temps_cuisson": 0},
        {"nom": "restaurant", "temps_epluchage": 70 * 60, "temps_cuisson": 0},
        {"nom": "plage_matin", "temps_epluchage": 3 * 3600, "temps_cuisson": 0},
        {"nom": "plage_apresmidi", "temps_epluchage": 4 * 3600, "temps_cuisson": 0}
    ],
    "nombre_commis": 5,
    "difficulte": "moyen",
    "source": "Document projet - Approche ludique vacances"
}

EXEMPLE_MINI = {
    "nom": "exemple_mini_test",
    "description": "Instance minimale pour tests rapides (2 plats, 2 commis)",
    "plats": [
        {"nom": "salade", "temps_epluchage": 5 * 60, "temps_cuisson": 0},
        {"nom": "soupe", "temps_epluchage": 10 * 60, "temps_cuisson": 20 * 60}
    ],
    "nombre_commis": 2,
    "difficulte": "facile",
    "source": "Instance de test minimale"
}

EXEMPLE_BENCHMARK = {
    "nom": "exemple_benchmark_complexe",
    "description": "Instance complexe pour tester les performances (15 plats, 5 commis)",
    "plats": [
        {"nom": f"plat_{i+1}", 
         "temps_epluchage": (5 + i * 2) * 60, 
         "temps_cuisson": (10 + i * 3) * 60}
        for i in range(15)
    ],
    "nombre_commis": 5,
    "difficulte": "difficile",
    "source": "Instance de benchmark"
}

def generer_fichier_instances_reference():
    instances = [
        EXEMPLE_1, EXEMPLE_2, EXEMPLE_3, EXEMPLE_FRUITS,
        EXEMPLE_VACANCES, EXEMPLE_MINI, EXEMPLE_BENCHMARK
    ]
    
    for instance in instances:
        plats = instance["plats"]
        temps_totaux = [p["temps_epluchage"] + p["temps_cuisson"] for p in plats]
        
        instance["statistiques"] = {
            "nombre_plats": len(plats),
            "temps_total_travail": sum(temps_totaux),
            "temps_moyen_par_plat": sum(temps_totaux) // len(plats) if plats else 0,
            "temps_max_plat": max(temps_totaux) if temps_totaux else 0,
            "temps_min_plat": min(temps_totaux) if temps_totaux else 0,
            "charge_theorique_par_commis": sum(temps_totaux) // instance["nombre_commis"] if instance["nombre_commis"] > 0 else 0
        }
    
    data = {
        "metadata": {
            "titre": "Instances de référence - Projet Ordonnancement Cuisine",
            "projet": "Polytech Nice SI4 - Algorithmes et Médiation",
            "groupe": "Groupe 7",
            "auteur": "Imane",
            "description": "Instances basées sur les exemples du document projet",
            "nombre_instances": len(instances),
            "date_creation": "janvier-avril 2026"
        },
        "instances": instances
    }
    
    return data

if __name__ == "__main__":
    print("📋 Génération des instances de référence...")
    
    data = generer_fichier_instances_reference()
    
    # Créer le dossier instances/ à la racine du projet
    project_root = Path(__file__).parent.parent.parent
    instances_dir = project_root / "instances"
    instances_dir.mkdir(exist_ok=True)

    # Sauvegarder dans le dossier instances/
    fichier_sortie = instances_dir / "reference_instances.json"

    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(data['instances'])} instances de référence générées!")
    print("\nInstances créées:")
    for instance in data['instances']:
        print(f"  • {instance['nom']}")
    
    print(f"\n✨ Fichier '{fichier_sortie}' créé avec succès!")