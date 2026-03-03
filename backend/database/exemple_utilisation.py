# backend/database/exemple_utilisation.py
"""
Exemples d'utilisation de la base de données
"""

from database.db_manager import DatabaseManager
from models.plat import Plat
from schedulers.johnson_scheduler import JohnsonScheduler
from schedulers.neh_scheduler import NEHScheduler
import time


def exemple_1_sauvegarder_instance():
    """Exemple 1: Sauvegarder une instance"""
    print("\n" + "="*60)
    print("EXEMPLE 1: Sauvegarder une instance")
    print("="*60)

    with DatabaseManager() as db:
        # Créer des plats
        plats_data = [
            {"id": 1, "nom": "Plat 1", "temps_prep": 15*60, "temps_cuisson": 17*60},
            {"id": 2, "nom": "Plat 2", "temps_prep": 11*60, "temps_cuisson": 16*60},
            {"id": 3, "nom": "Plat 3", "temps_prep": 0, "temps_cuisson": 12*60}
        ]

        # Sauvegarder l'instance
        instance_id = db.sauvegarder_instance(
            nom="test_exemple_1",
            plats=plats_data,
            nb_commis=1,
            nb_fours=1,
            description="Instance de test - 3 plats",
            difficulte="facile",
            created_by="utilisateur_test"
        )

        print(f"✅ Instance sauvegardée avec ID: {instance_id}")


def exemple_2_executer_et_sauvegarder():
    """Exemple 2: Exécuter des algorithmes et sauvegarder les résultats"""
    print("\n" + "="*60)
    print("EXEMPLE 2: Exécuter et sauvegarder les résultats")
    print("="*60)

    with DatabaseManager() as db:
        # Charger une instance
        instance = db.charger_instance_par_nom("test_exemple_1")

        if not instance:
            print("❌ Instance non trouvée. Exécutez d'abord exemple_1")
            return

        print(f"Instance chargée: {instance['nom']}")

        # Convertir en objets Plat
        plats = [
            Plat(p['id'], p['nom'], p['temps_prep'], p['temps_cuisson'])
            for p in instance['plats']
        ]

        stations = {'commis': instance['nb_commis'], 'fours': instance['nb_fours']}

        # Tester Johnson
        print("\nExécution de Johnson...")
        johnson = JohnsonScheduler()
        debut = time.time()
        resultat_j = johnson.schedule(plats, stations)
        temps_j = time.time() - debut

        execution_j_id = db.sauvegarder_execution(
            instance_id=instance['id'],
            algorithme="Johnson",
            makespan=resultat_j['makespan'],
            temps_execution=temps_j,
            ordre_plats=[p.id for p in resultat_j['ordre']]
        )
        print(f"  ✅ Makespan: {resultat_j['makespan']}, temps: {temps_j*1000:.2f}ms")
        print(f"  💾 Sauvegardé avec ID: {execution_j_id}")

        # Tester NEH
        print("\nExécution de NEH...")
        neh = NEHScheduler()
        debut = time.time()
        resultat_n = neh.schedule(plats, stations)
        temps_n = time.time() - debut

        execution_n_id = db.sauvegarder_execution(
            instance_id=instance['id'],
            algorithme="NEH",
            makespan=resultat_n['makespan'],
            temps_execution=temps_n,
            ordre_plats=[p.id for p in resultat_n['ordre']]
        )
        print(f"  ✅ Makespan: {resultat_n['makespan']}, temps: {temps_n*1000:.2f}ms")
        print(f"  💾 Sauvegardé avec ID: {execution_n_id}")


def exemple_3_consulter_historique():
    """Exemple 3: Consulter l'historique des exécutions"""
    print("\n" + "="*60)
    print("EXEMPLE 3: Consulter l'historique")
    print("="*60)

    with DatabaseManager() as db:
        # Lister les instances
        print("\n📋 Instances disponibles:")
        instances = db.lister_instances()
        for inst in instances:
            print(f"  - {inst['nom']}: {inst['nb_plats']} plats, "
                  f"{inst['nb_commis']} commis (créée le {inst['date_creation']})")

        if not instances:
            print("  Aucune instance trouvée")
            return

        # Historique pour la première instance
        instance = instances[0]
        print(f"\n📊 Historique pour '{instance['nom']}':")
        executions = db.lister_executions_instance(instance['id'])

        for exec in executions:
            print(f"  - {exec['algorithme']}: makespan={exec['makespan']}, "
                  f"temps={exec['temps_execution']*1000:.2f}ms ({exec['date_execution']})")

        # Meilleure exécution
        meilleure = db.get_meilleure_execution(instance['id'])
        if meilleure:
            print(f"\n🏆 Meilleure exécution:")
            print(f"  Algorithme: {meilleure['algorithme']}")
            print(f"  Makespan: {meilleure['makespan']}")
            print(f"  Temps: {meilleure['temps_execution']*1000:.2f}ms")


def exemple_4_statistiques():
    """Exemple 4: Statistiques globales"""
    print("\n" + "="*60)
    print("EXEMPLE 4: Statistiques globales")
    print("="*60)

    with DatabaseManager() as db:
        # Statistiques par algorithme
        print("\n📊 Statistiques par algorithme:")

        for algo in ["Johnson", "NEH", "LPT", "SPT", "Palmer"]:
            stats = db.get_statistiques_algorithme(algo)
            if stats['nb_executions'] > 0:
                print(f"\n{algo}:")
                print(f"  Exécutions: {stats['nb_executions']}")
                print(f"  Makespan moyen: {stats['makespan_moyen']:.2f}")
                print(f"  Makespan min: {stats['makespan_min']}")
                print(f"  Makespan max: {stats['makespan_max']}")
                print(f"  Temps moyen: {stats['temps_execution_moyen']*1000:.2f}ms")

        # Classement
        print("\n🏆 Classement des algorithmes (makespan moyen):")
        classement = db.get_classement_algorithmes()
        for i, algo in enumerate(classement, 1):
            print(f"  {i}. {algo['algorithme']}: {algo['makespan_moyen']:.2f} "
                  f"({algo['nb_executions']} exécutions)")


def exemple_5_importer_json():
    """Exemple 5: Importer les instances JSON existantes"""
    print("\n" + "="*60)
    print("EXEMPLE 5: Importer instances JSON → Base de données")
    print("="*60)

    import json
    from pathlib import Path

    with DatabaseManager() as db:
        # Charger reference_instances.json
        json_path = Path("../instances/reference_instances.json")

        if not json_path.exists():
            print("❌ Fichier reference_instances.json non trouvé")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"Importation de {len(data['instances'])} instances...")

        for inst in data['instances']:
            instance_id = db.sauvegarder_instance(
                nom=inst['nom'],
                plats=inst['plats'],
                nb_commis=inst['nombre_commis'],
                nb_fours=1,  # Par défaut
                description=inst.get('description', ''),
                difficulte=inst.get('difficulte', 'moyen'),
                created_by='import_json'
            )
            print(f"  ✅ {inst['nom']} → ID {instance_id}")

        print(f"\n✅ {len(data['instances'])} instances importées avec succès!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DÉMONSTRATION DE LA BASE DE DONNÉES SQLite")
    print("="*70)

    # Exécuter tous les exemples
    exemple_1_sauvegarder_instance()
    exemple_2_executer_et_sauvegarder()
    exemple_3_consulter_historique()
    exemple_4_statistiques()
    # exemple_5_importer_json()  # Décommenter pour importer les JSON

    print("\n" + "="*70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("="*70)
    print("\n💾 Base de données créée dans: data/ordonnancement.db")
    print("📊 Vous pouvez l'ouvrir avec SQLite Browser pour l'explorer")

