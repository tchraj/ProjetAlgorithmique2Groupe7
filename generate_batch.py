"""
Script de génération en batch d'instances
Crée rapidement plusieurs instances de différents types

Usage:
    python generate_batch.py --nombre 20 --output mes_instances.json

"""

import argparse
from instance_generator import InstanceGenerator


def generer_instances_batch(
    nombre: int = 10,
    output: str = "batch_instances.json",
    seed: int = 42
):
    """
    Génère un lot d'instances variées
    
    Args:
        nombre: Nombre d'instances à générer
        output: Nom du fichier de sortie
        seed: Graine pour reproductibilité
    """
    print(f"🍳 Génération de {nombre} instances...")
    print(f"📝 Sortie: {output}")
    print(f"🎲 Seed: {seed}\n")
    
    generator = InstanceGenerator(seed=seed)
    
    # Générer un mix d'instances
    instances = []
    
    # Distribuer les types uniformément
    types = ["simple", "equilibree", "difficile", "desequilibree"]
    
    for i in range(nombre):
        type_instance = types[i % len(types)]
        
        # Varier la taille
        if i < nombre // 3:
            # Petites instances
            nb_plats = 3 + (i % 5)
            nb_commis = 2 + (i % 3)
        elif i < 2 * nombre // 3:
            # Instances moyennes
            nb_plats = 8 + (i % 7)
            nb_commis = 3 + (i % 4)
        else:
            # Grandes instances
            nb_plats = 15 + (i % 10)
            nb_commis = 5 + (i % 5)
        
        nom = f"batch_{i+1:03d}_{type_instance}_{nb_plats}p_{nb_commis}c"
        
        # Générer selon le type
        if type_instance == "simple":
            instance = generator.generer_instance_simple(nb_plats, nb_commis, nom)
        elif type_instance == "equilibree":
            instance = generator.generer_instance_equilibree(nb_plats, nb_commis, nom)
        elif type_instance == "difficile":
            instance = generator.generer_instance_difficile(nb_plats, nb_commis, nom)
        else:  # desequilibree
            instance = generator.generer_instance_desequilibree(nb_plats, nb_commis, nom)
        
        instances.append(instance)
        print(f"✓ {i+1:2d}/{nombre} - {nom}")
    
    # Sauvegarder
    generator.sauvegarder_instances(instances, output)
    
    print(f"\n✅ {len(instances)} instances générées avec succès!")
    print(f"📁 Fichier: {output}")
    
    # Statistiques
    print("\n📊 Résumé:")
    types_count = {}
    for inst in instances:
        t = inst.difficulte
        types_count[t] = types_count.get(t, 0) + 1
    
    for type_diff, count in sorted(types_count.items()):
        print(f"   - {type_diff}: {count} instances")
    
    total_plats = sum(len(inst.plats) for inst in instances)
    print(f"\n   Total plats générés: {total_plats}")
    print(f"   Moyenne plats/instance: {total_plats/len(instances):.1f}")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Générateur d'instances en batch pour ordonnancement cuisine"
    )
    
    parser.add_argument(
        "--nombre",
        type=int,
        default=10,
        help="Nombre d'instances à générer (défaut: 10)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="batch_instances.json",
        help="Nom du fichier de sortie (défaut: batch_instances.json)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine pour génération aléatoire (défaut: 42)"
    )
    
    args = parser.parse_args()
    
    generer_instances_batch(
        nombre=args.nombre,
        output=args.output,
        seed=args.seed
    )


if __name__ == "__main__":
    main()