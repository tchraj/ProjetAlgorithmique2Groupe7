# backend/demo_comparison.py
"""
Script de démonstration du service de comparaison des algorithmes
Usage: python demo_comparison.py
"""
import sys
import os

from schedulers import CDSScheduler, FIFOScheduler

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.spt_scheduler import SPTScheduler
from schedulers.lpt_scheduler import LPTScheduler
from schedulers.neh_scheduler import NEHScheduler
from schedulers.palmer_scheduler import PalmerScheduler
from services.comparison_service import ComparisonService


def formater_temps(secondes: int) -> str:
    """Formate un temps en secondes en format lisible"""
    minutes = secondes // 60
    sec = secondes % 60
    return f"{minutes:02d}:{sec:02d}"


def afficher_resultats(resultats_comparaison: dict):
    """Affiche les résultats de façon formatée"""
    print("\n" + "=" * 80)
    print(" RÉSULTATS DE LA COMPARAISON DES ALGORITHMES")
    print("=" * 80)

    print(f"\n  Nombre de plats : {resultats_comparaison['nb_plats']}")
    print(f" Stations : {resultats_comparaison['stations']}")

    if resultats_comparaison.get('makespan_optimal'):
        print(f" Makespan optimal connu : {formater_temps(resultats_comparaison['makespan_optimal'])}")

    print(f"\n🏆 Meilleur algorithme : {resultats_comparaison['meilleur']['algorithme']}")
    print(f"   Makespan : {formater_temps(resultats_comparaison['meilleur_makespan'])}")

    print("\n" + "-" * 80)
    print("DÉTAILS PAR ALGORITHME")
    print("-" * 80)

    # En-tête du tableau
    print(f"{'Algorithme':<30} {'Makespan':<12} {'Ratio':<8} {'Écart':<12} {'Temps (ms)':<12}")
    print("-" * 80)

    # Trier par makespan
    resultats_tries = sorted(resultats_comparaison['resultats'], key=lambda r: r['makespan'])

    for res in resultats_tries:
        algo_nom = res['algorithme']
        makespan_str = formater_temps(res['makespan'])
        ratio_str = f"{res['ratio_vs_meilleur']:.3f}"
        ecart_str = f"+{formater_temps(res['ecart_absolu'])}" if res['ecart_absolu'] > 0 else "0"
        temps_ms = f"{res['temps_execution'] * 1000:.2f}"

        symbole = "🥇" if res['ratio_vs_meilleur'] == 1.0 else "  "

        print(f"{symbole} {algo_nom:<28} {makespan_str:<12} {ratio_str:<8} {ecart_str:<12} {temps_ms:<12}")

        # Si on a des infos vs optimal
        if 'ratio_vs_optimal' in res:
            print(f"   → vs optimal: ratio={res['ratio_vs_optimal']:.3f}, "
                  f"écart={res['ecart_vs_optimal_pct']:.1f}%")

    print("\n" + "-" * 80)
    print("STATISTIQUES GLOBALES")
    print("-" * 80)

    stats = resultats_comparaison['statistiques']
    print(f"Makespan min       : {formater_temps(stats['makespan_min'])}")
    print(f"Makespan max       : {formater_temps(stats['makespan_max'])}")
    print(f"Makespan moyen     : {formater_temps(int(stats['makespan_moyen']))}")
    print(f"Temps exec moyen   : {stats['temps_exec_moyen'] * 1000:.2f} ms")
    print(f"Temps exec total   : {stats['temps_exec_total'] * 1000:.2f} ms")

    if 'ecart_moyen_vs_optimal_pct' in stats:
        print(f"Écart moyen vs opt : {stats['ecart_moyen_vs_optimal_pct']:.1f}%")


def exemple_1():
    """Exemple 1 de l'énoncé : 3 plats, 1 commis, 1 four"""
    print("\n" + "=" * 80)
    print("EXEMPLE 1 : Instance de l'énoncé (3 plats)")
    print("=" * 80)

    plats = [
        Plat(1, "Plat 1 (Ratatouille)", temps_epluchage=15*60, temps_cuisson=17*60),
        Plat(2, "Plat 2 (Gratin)", temps_epluchage=11*60, temps_cuisson=16*60),
        Plat(3, "Plat 3 (Salade)", temps_epluchage=0, temps_cuisson=12*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        SPTScheduler(),
        LPTScheduler(),
        NEHScheduler(),
        PalmerScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(
        plats,
        {'commis': 1, 'fours': 1},
        makespan_optimal=45*60  # Johnson devrait trouver l'optimal
    )

    afficher_resultats(resultat)

    # Afficher l'ordre du meilleur
    print("\n📋 Ordre optimal trouvé (meilleur algorithme) :")
    for i, nom_plat in enumerate(resultat['meilleur']['ordre'], 1):
        print(f"   {i}. {nom_plat}")


def exemple_2():
    """Exemple avec plusieurs stations"""
    print("\n" + "=" * 80)
    print("EXEMPLE 2 : Instance plus grande (5 plats, 2 commis, 2 fours)")
    print("=" * 80)

    plats = [
        Plat(1, "Soupe à l'oignon", temps_epluchage=10*60, temps_cuisson=25*60),
        Plat(2, "Poulet rôti", temps_epluchage=15*60, temps_cuisson=45*60),
        Plat(3, "Tarte aux pommes", temps_epluchage=20*60, temps_cuisson=30*60),
        Plat(4, "Gratin dauphinois", temps_epluchage=18*60, temps_cuisson=35*60),
        Plat(5, "Salade César", temps_epluchage=8*60, temps_cuisson=5*60)
    ]

    schedulers = [
        JohnsonScheduler(),
        NEHScheduler(),
        PalmerScheduler(),
        CDSScheduler(),
        FIFOScheduler()
    ]

    schedulers = [
        JohnsonScheduler(),
        SPTScheduler(),
        LPTScheduler(),
        NEHScheduler(),
        PalmerScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare(plats, {'commis': 2, 'fours': 2})

    afficher_resultats(resultat)


def exemple_3():
    """Comparaison sur un batch d'instances"""
    print("\n" + "=" * 80)
    print("EXEMPLE 3 : Comparaison sur plusieurs instances")
    print("=" * 80)

    instances = [
        {
            'nom': 'Petite instance (2 plats)',
            'plats': [
                Plat(1, "Entrée", temps_epluchage=5*60, temps_cuisson=10*60),
                Plat(2, "Plat principal", temps_epluchage=15*60, temps_cuisson=20*60)
            ],
            'stations': {'commis': 1, 'fours': 1}
        },
        {
            'nom': 'Instance moyenne (4 plats)',
            'plats': [
                Plat(1, "Soupe", temps_epluchage=8*60, temps_cuisson=15*60),
                Plat(2, "Poisson", temps_epluchage=12*60, temps_cuisson=18*60),
                Plat(3, "Légumes", temps_epluchage=10*60, temps_cuisson=12*60),
                Plat(4, "Dessert", temps_epluchage=15*60, temps_cuisson=25*60)
            ],
            'stations': {'commis': 2, 'fours': 1}
        },
        {
            'nom': 'Grande instance (6 plats)',
            'plats': [
                Plat(i, f"Plat {i}", temps_epluchage=(5 + i*2)*60, temps_cuisson=(10 + i*3)*60)
                for i in range(1, 7)
            ],
            'stations': {'commis': 2, 'fours': 2}
        }
    ]

    schedulers = [
        JohnsonScheduler(),
        NEHScheduler(),
        PalmerScheduler(),
        CDSScheduler()
    ]

    service = ComparisonService(schedulers)
    resultat = service.compare_batch(instances)

    print(f"\n🎯 Nombre d'instances testées : {resultat['nb_instances']}")
    print("\n" + "-" * 80)
    print("STATISTIQUES AGRÉGÉES PAR ALGORITHME")
    print("-" * 80)

    print(f"{'Algorithme':<30} {'Makespan moy':<15} {'Ratio moy':<12} {'Temps (ms)':<12} {'% Meilleur':<12}")
    print("-" * 80)

    stats_agregees = resultat['statistiques_agregees']
    for algo_nom, stats in sorted(stats_agregees.items(), key=lambda x: x[1]['makespan_moyen']):
        makespan_moy = formater_temps(int(stats['makespan_moyen']))
        ratio_moy = f"{stats['ratio_moyen_vs_meilleur']:.3f}"
        temps_ms = f"{stats['temps_exec_moyen'] * 1000:.2f}"
        pct_meilleur = f"{stats['pct_meilleur']:.1f}%"

        print(f"{algo_nom:<30} {makespan_moy:<15} {ratio_moy:<12} {temps_ms:<12} {pct_meilleur:<12}")

    print("\n")
    for instance_result in resultat['instances']:
        print(f"Instance '{instance_result['nom_instance']}' → Meilleur: {instance_result['meilleur']['algorithme']} "
              f"({formater_temps(instance_result['meilleur_makespan'])})")


def main():
    """Point d'entrée principal"""
    print("\n" + "🍳" * 40)
    print("     COMPARAISON DES ALGORITHMES D'ORDONNANCEMENT")
    print("     Projet : Ordonnancement, Cuisine et approximations")
    print("🍳" * 40)

    try:
        exemple_1()
        input("\n[Appuyez sur Entrée pour continuer...]")

        exemple_2()
        input("\n[Appuyez sur Entrée pour continuer...]")

        exemple_3()

    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du programme.")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Démonstration terminée !")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

