# Test simple de la base de données
import sys
sys.path.insert(0, '..')

try:
    from database.db_manager import DatabaseManager

    print("Test de la base de données SQLite")
    print("="*50)

    # Créer la base
    db = DatabaseManager()
    print("✅ Base de données créée")

    # Sauvegarder une instance
    plats = [
        {"id": 1, "nom": "Test 1", "temps_epluchage": 600, "temps_cuisson": 900}
    ]

    instance_id = db.sauvegarder_instance(
        nom="test_simple",
        plats=plats,
        nb_commis=1,
        nb_fours=1,
        description="Test simple"
    )

    print(f"✅ Instance sauvegardée: ID={instance_id}")

    # Charger l'instance
    instance = db.charger_instance(instance_id)
    print(f"✅ Instance chargée: {instance['nom']}")

    # Lister les instances
    instances = db.lister_instances()
    print(f"✅ Nombre d'instances: {len(instances)}")

    db.close()
    print("\n✅ Tous les tests ont réussi!")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

