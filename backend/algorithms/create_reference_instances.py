import json
from pathlib import Path

# ─────────────────────────────────────────────
# Exemple 1
# Plat 1 : prep=15min, cuisson=17min
# Plat 2 : prep=11min, cuisson=16min
# Plat 3 : prep=0min,  cuisson=12min
# Solution optimale connue : 45 min (ordre C→B→A, règle de Johnson)
# ─────────────────────────────────────────────
EXEMPLE_1 = {
    "nom": "exemple_1_sujet",
    "description": "3 plats issus de l'énoncé — 1 commis, 1 four. Solution optimale = 45 min.",
    "plats": [
        {"nom": "plat_A", "temps_prep": 15 * 60, "temps_cuisson": 17 * 60},
        {"nom": "plat_B", "temps_prep": 11 * 60, "temps_cuisson": 16 * 60},
        {"nom": "plat_C", "temps_prep":  0 * 60, "temps_cuisson": 12 * 60},
    ],
    "nombre_commis": 1,
    "nombre_fours": 1,
    "difficulte": "facile",
    "solution_optimale_connue": 45 * 60,
    "ordre_optimal": ["plat_C", "plat_B", "plat_A"],
    "source": "Énoncé projet — Exemple 1"
}

# ─────────────────────────────────────────────
# Exemple 2
# Plat 1 : prep=16min, cuisson=10min
# Plat 2 : prep=14min, cuisson=14min
# Plat 3 : prep=11min, cuisson=8min
# Tous dans Set2 (prep >= cuisson) → ordre par cuisson décroissante
# ─────────────────────────────────────────────
EXEMPLE_2 = {
    "nom": "exemple_2_sujet",
    "description": "3 plats issus de l'énoncé — 1 commis, 1 four. Tous dans Set2 (prep ≥ cuisson).",
    "plats": [
        {"nom": "plat_1", "temps_prep": 16 * 60, "temps_cuisson": 10 * 60},
        {"nom": "plat_2", "temps_prep": 14 * 60, "temps_cuisson": 14 * 60},
        {"nom": "plat_3", "temps_prep": 11 * 60, "temps_cuisson":  8 * 60},
    ],
    "nombre_commis": 1,
    "nombre_fours": 1,
    "difficulte": "facile",
    "solution_optimale_connue": None,  # À calculer
    "ordre_optimal": ["plat_2", "plat_1", "plat_3"],  # Johnson : cuisson décrois. → 14,10,8
    "source": "Énoncé projet — Exemple 2"
}

# ─────────────────────────────────────────────
# Exemple 3
# 6 plats, 1 commis, 1 four
# "Le dernier exemple semble beaucoup plus difficile à résoudre à la main"
# ─────────────────────────────────────────────
EXEMPLE_3 = {
    "nom": "exemple_3_sujet",
    "description": "6 plats issus de l'énoncé — 1 commis, 1 four. Instance 'difficile à résoudre à la main'.",
    "plats": [
        {"nom": "plat_1", "temps_prep":  8 * 60, "temps_cuisson": 12 * 60},
        {"nom": "plat_2", "temps_prep": 12 * 60, "temps_cuisson":  8 * 60},
        {"nom": "plat_3", "temps_prep": 17 * 60, "temps_cuisson": 20 * 60},
        {"nom": "plat_4", "temps_prep": 19 * 60, "temps_cuisson": 17 * 60},
        {"nom": "plat_5", "temps_prep": 19 * 60, "temps_cuisson": 20 * 60},
        {"nom": "plat_6", "temps_prep": 19 * 60, "temps_cuisson": 12 * 60},
    ],
    "nombre_commis": 1,
    "nombre_fours": 1,
    "difficulte": "difficile",
    "solution_optimale_connue": None,  # À calculer par l'algorithme
    "ordre_optimal": None,
    "source": "Énoncé projet — Exemple 3"
}

# ─────────────────────────────────────────────
# Exemple fruits
# Problème d'équilibrage de charge (load balancing)
# Pas de contrainte prep→cuisson ici, c'est le problème de base
# ─────────────────────────────────────────────
EXEMPLE_FRUITS = {
    "nom": "exemple_fruits_load_balancing",
    "description": "Équilibrage de charge : 4 types de fruits, 3 commis. Problème de base sans contrainte de précédence.",
    "plats": [
        {"nom": "pommes (43)",  "temps_prep": 43 * 30,  "temps_cuisson": 0},
        {"nom": "mangues (57)", "temps_prep": 57 * 600, "temps_cuisson": 0},
        {"nom": "tomates (107)","temps_prep": 107 * 10, "temps_cuisson": 0},
        {"nom": "litchis (13)", "temps_prep": 13 * 5,   "temps_cuisson": 0},
    ],
    "nombre_commis": 3,
    "nombre_fours": 0,  # Pas de cuisson dans ce problème
    "difficulte": "moyen",
    "note": "Problème d'équilibrage pur (Load Balancing). LPT s'applique ici, pas Johnson.",
    "source": "Énoncé projet — Problème initial fruits"
}

# ─────────────────────────────────────────────
# Instance mini — pour tests rapides
# ─────────────────────────────────────────────
EXEMPLE_MINI = {
    "nom": "exemple_mini_test",
    "description": "2 plats — instance minimale pour tests unitaires rapides.",
    "plats": [
        {"nom": "salade", "temps_prep":  5 * 60, "temps_cuisson":  0 * 60},
        {"nom": "soupe",  "temps_prep": 10 * 60, "temps_cuisson": 20 * 60},
    ],
    "nombre_commis": 1,
    "nombre_fours": 1,
    "difficulte": "facile",
    "solution_optimale_connue": None,
    "source": "Instance de test minimale"
}

# ─────────────────────────────────────────────
# Instance benchmark — pour comparer les algos
# ─────────────────────────────────────────────
EXEMPLE_BENCHMARK = {
    "nom": "exemple_benchmark_complexe",
    "description": "15 plats, 1 commis, 1 four — pour comparer les algorithmes sur une instance de taille réelle.",
    "plats": [
        {"nom": f"plat_{i+1}",
         "temps_prep":  (5 + i * 2) * 60,
         "temps_cuisson": (10 + i * 3) * 60}
        for i in range(15)
    ],
    "nombre_commis": 1,
    "nombre_fours": 1,
    "difficulte": "difficile",
    "source": "Instance de benchmark"
}


def _ajouter_statistiques(instance: dict) -> dict:
    """Calcule et ajoute les statistiques à une instance."""
    plats = instance["plats"]
    temps_prep   = [p["temps_prep"]    for p in plats]
    temps_cuis   = [p["temps_cuisson"] for p in plats]
    temps_totaux = [a + b for a, b in zip(temps_prep, temps_cuis)]

    nb_commis = instance.get("nombre_commis", 1)

    instance["statistiques"] = {
        "nombre_plats": len(plats),
        "temps_total_prep_secondes":    sum(temps_prep),
        "temps_total_cuisson_secondes": sum(temps_cuis),
        "temps_total_travail_secondes": sum(temps_totaux),
        "temps_moyen_par_plat_secondes": sum(temps_totaux) // len(plats) if plats else 0,
        "temps_max_plat_secondes": max(temps_totaux) if temps_totaux else 0,
        "temps_min_plat_secondes": min(temps_totaux) if temps_totaux else 0,
        "charge_theorique_par_commis_secondes": (
            sum(temps_totaux) // nb_commis if nb_commis > 0 else 0
        ),
    }
    return instance


def generer_fichier_instances_reference() -> dict:
    """Assemble toutes les instances et calcule leurs statistiques."""
    instances = [
        EXEMPLE_1,
        EXEMPLE_2,
        EXEMPLE_3,
        EXEMPLE_FRUITS,
        EXEMPLE_MINI,
        EXEMPLE_BENCHMARK,
    ]

    instances = [_ajouter_statistiques(inst) for inst in instances]

    return {
        "metadata": {
            "titre":       "Instances de référence — Projet Ordonnancement Cuisine",
            "projet":      "Polytech Nice SI4 — Algorithmes et Médiation 2026",
            "groupe":      "Groupe 7",
            "description": "Instances exactement tirées de l'énoncé du projet.",
            "nombre_instances": len(instances),
            "important": (
                "Les instances exemple_1/2/3 ont 1 commis + 1 four : "
                "Johnson y est OPTIMAL. "
                "L'instance fruits est un Load Balancing pur (LPT, pas Johnson)."
            ),
        },
        "instances": instances,
    }


if __name__ == "__main__":
    print("📋 Génération des instances de référence...")

    data = generer_fichier_instances_reference()

    # Créer le dossier instances/ à la racine du projet
    project_root = Path(__file__).parent.parent.parent
    instances_dir = project_root / "instances"
    instances_dir.mkdir(exist_ok=True)

    fichier_sortie = instances_dir / "reference_instances.json"
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f" {len(data['instances'])} instances générées dans '{fichier_sortie}'")
    print()
    for inst in data["instances"]:
        nb_p = inst["statistiques"]["nombre_plats"]
        nc   = inst.get("nombre_commis", "?")
        nf   = inst.get("nombre_fours", "?")
        opt  = inst.get("solution_optimale_connue")
        opt_str = f" | optimal={opt//60}min" if opt else ""
        print(f"  • {inst['nom']:<40} {nb_p} plats  {nc} commis  {nf} fours{opt_str}")