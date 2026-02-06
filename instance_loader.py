"""
Module d'intégration des instances dans l'application Flask
Permet de charger et utiliser les instances générées dans l'interface web

"""

import json
import os
from typing import List, Dict, Optional


class InstanceManager:
    """Gestionnaire des instances pour l'application"""
    
    def __init__(self, instances_dir: str = "instances"):
        """
        Initialise le gestionnaire d'instances
        
        Args:
            instances_dir: Répertoire contenant les fichiers d'instances
        """
        self.instances_dir = instances_dir
        self.instances_cache = {}
    
    def charger_fichier_instances(self, fichier: str) -> Dict:
        """
        Charge un fichier d'instances JSON
        
        Args:
            fichier: Nom du fichier (ex: "reference_instances.json")
        
        Returns:
            Dictionnaire contenant les instances
        """
        chemin = os.path.join(self.instances_dir, fichier)
        
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️  Fichier non trouvé: {chemin}")
            return {"instances": []}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing JSON: {e}")
            return {"instances": []}
    
    def lister_instances_disponibles(self) -> List[Dict]:
        """
        Liste toutes les instances disponibles
        
        Returns:
            Liste des instances avec leurs informations de base
        """
        instances = []
        
        # Charger les instances de référence
        ref_data = self.charger_fichier_instances("reference_instances.json")
        for instance in ref_data.get("instances", []):
            instances.append({
                "nom": instance["nom"],
                "description": instance["description"],
                "nombre_plats": len(instance["plats"]),
                "nombre_commis": instance["nombre_commis"],
                "difficulte": instance.get("difficulte", "non définie"),
                "source": "reference"
            })
        
        # Charger les instances de test
        test_data = self.charger_fichier_instances("instances_test.json")
        for instance in test_data.get("instances", []):
            instances.append({
                "nom": instance["nom"],
                "description": instance["description"],
                "nombre_plats": len(instance["plats"]),
                "nombre_commis": instance["nombre_commis"],
                "difficulte": instance.get("difficulte", "non définie"),
                "source": "test"
            })
        
        return instances
    
    def obtenir_instance_par_nom(self, nom: str) -> Optional[Dict]:
        """
        Récupère une instance spécifique par son nom
        
        Args:
            nom: Nom de l'instance
        
        Returns:
            L'instance ou None si non trouvée
        """
        # Vérifier dans le cache
        if nom in self.instances_cache:
            return self.instances_cache[nom]
        
        # Chercher dans les fichiers
        for fichier in ["reference_instances.json", "instances_test.json"]:
            data = self.charger_fichier_instances(fichier)
            for instance in data.get("instances", []):
                if instance["nom"] == nom:
                    self.instances_cache[nom] = instance
                    return instance
        
        return None
    
    def convertir_instance_pour_algorithme(self, instance: Dict) -> tuple:
        """
        Convertit une instance au format attendu par les algorithmes
        
        Args:
            instance: Instance à convertir
        
        Returns:
            Tuple (tasks_dict, num_workers) pour les algorithmes
        """
        tasks = {}
        
        for plat in instance["plats"]:
            nom = plat["nom"]
            # Pour l'instant, on additionne épluchage et cuisson
            # Dans une version avancée, on gérera la contrainte de précédence
            temps_total = plat["temps_epluchage"] + plat["temps_cuisson"]
            tasks[nom] = temps_total
        
        num_workers = instance["nombre_commis"]
        
        return tasks, num_workers
    
    def convertir_instance_pour_affichage(self, instance: Dict) -> str:
        """
        Convertit une instance au format texte pour l'interface web
        
        Args:
            instance: Instance à convertir
        
        Returns:
            Chaîne de caractères au format "nom, temps"
        """
        lignes = []
        for plat in instance["plats"]:
            nom = plat["nom"]
            temps_total = plat["temps_epluchage"] + plat["temps_cuisson"]
            lignes.append(f"{nom}, {temps_total}")
        
        return "\n".join(lignes)
    
    def generer_instance_aleatoire(
        self,
        nombre_plats: int = 5,
        nombre_commis: int = 3,
        difficulte: str = "moyen"
    ) -> Dict:
        """
        Génère une nouvelle instance aléatoire
        
        Args:
            nombre_plats: Nombre de plats
            nombre_commis: Nombre de commis
            difficulte: Niveau de difficulté ("facile", "moyen", "difficile")
        
        Returns:
            Nouvelle instance générée
        """
        from instance_generator import InstanceGenerator
        
        generator = InstanceGenerator()
        
        if difficulte == "facile":
            instance = generator.generer_instance_simple(nombre_plats, nombre_commis)
        elif difficulte == "difficile":
            instance = generator.generer_instance_difficile(nombre_plats, nombre_commis)
        else:  # moyen
            instance = generator.generer_instance_equilibree(nombre_plats, nombre_commis)
        
        return instance.to_dict()


# Fonction d'aide pour l'intégration dans Flask
def preparer_instances_pour_select() -> List[Dict]:
    """
    Prépare les instances pour un menu déroulant HTML
    
    Returns:
        Liste de dictionnaires {value, label, description}
    """
    manager = InstanceManager()
    instances = manager.lister_instances_disponibles()
    
    options = []
    for instance in instances:
        label = f"{instance['nom']} ({instance['nombre_plats']} plats, {instance['nombre_commis']} commis)"
        options.append({
            "value": instance["nom"],
            "label": label,
            "description": instance["description"],
            "difficulte": instance["difficulte"]
        })
    
    return options


def charger_instance_pour_interface(nom_instance: str) -> tuple:
    """
    Charge une instance et la prépare pour l'interface web
    
    Args:
        nom_instance: Nom de l'instance à charger
    
    Returns:
        Tuple (texte_taches, nombre_commis, info_instance)
    """
    manager = InstanceManager()
    instance = manager.obtenir_instance_par_nom(nom_instance)
    
    if not instance:
        return "", 3, {}
    
    texte = manager.convertir_instance_pour_affichage(instance)
    nombre_commis = instance["nombre_commis"]
    
    info = {
        "nom": instance["nom"],
        "description": instance.get("description", ""),
        "difficulte": instance.get("difficulte", ""),
        "statistiques": instance.get("statistiques", {})
    }
    
    return texte, nombre_commis, info


# Point d'entrée pour tester le module
if __name__ == "__main__":
    print("🔧 Test du module d'intégration des instances")
    print("=" * 70)
    
    manager = InstanceManager()
    
    # Lister toutes les instances
    print("\n📋 Instances disponibles:")
    instances = manager.lister_instances_disponibles()
    for i, inst in enumerate(instances, 1):
        print(f"{i}. {inst['nom']}")
        print(f"   - {inst['description'][:60]}...")
        print(f"   - Plats: {inst['nombre_plats']}, Commis: {inst['nombre_commis']}, Difficulté: {inst['difficulte']}")
    
    # Charger une instance spécifique
    print("\n\n🔍 Test de chargement de l'exemple 1:")
    instance = manager.obtenir_instance_par_nom("exemple_1_sujet")
    if instance:
        print(f"✅ Instance chargée: {instance['nom']}")
        print(f"   Description: {instance['description']}")
        
        # Convertir pour l'algorithme
        tasks, workers = manager.convertir_instance_pour_algorithme(instance)
        print(f"\n   Format pour algorithme:")
        print(f"   - Tâches: {tasks}")
        print(f"   - Commis: {workers}")
        
        # Convertir pour l'affichage
        texte = manager.convertir_instance_pour_affichage(instance)
        print(f"\n   Format pour interface web:")
        print(texte)
    
    # Préparer pour menu déroulant
    print("\n\n📋 Options pour menu déroulant:")
    options = preparer_instances_pour_select()
    for opt in options[:3]:  # Afficher les 3 premières
        print(f"   - {opt['label']}")
    
    print("\n✨ Test terminé!")