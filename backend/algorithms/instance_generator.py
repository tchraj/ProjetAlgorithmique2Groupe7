import random
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from models.plat import Plat

@dataclass
class Instance:
    """Représente une instance complète du problème"""
    nom: str
    description: str
    plats: List[Dict]
    nombre_commis: int
    difficulte: str  # "facile", "moyen", "difficile"
    
    def to_dict(self):
        """Convertit l'instance en dictionnaire"""
        return {
            "nom": self.nom,
            "description": self.description,
            "plats": self.plats,
            "nombre_commis": self.nombre_commis,
            "difficulte": self.difficulte,
            "statistiques": self.calculer_statistiques()
        }
    
    def calculer_statistiques(self) -> Dict:
        """Calcule les statistiques de l'instance"""
        temps_prep = [p["temps_prep"] for p in self.plats]
        temps_cuisson = [p["temps_cuisson"] for p in self.plats]
        temps_totaux = [p["temps_prep"] + p["temps_cuisson"] for p in self.plats]
        
        return {
            "nombre_plats": len(self.plats),
            "temps_total_travail": sum(temps_totaux),
            "temps_moyen_par_plat": sum(temps_totaux) // len(self.plats) if self.plats else 0,
            "temps_max_plat": max(temps_totaux) if temps_totaux else 0,
            "temps_min_plat": min(temps_totaux) if temps_totaux else 0,
            "charge_theorique_par_commis": sum(temps_totaux) // self.nombre_commis if self.nombre_commis > 0 else 0
        }


class InstanceGenerator:
    """Générateur d'instances pour le problème d'ordonnancement"""
    
    # Listes de noms de fruits/légumes pour générer des instances réalistes
    FRUITS = [
        "pomme", "poire", "mangue", "ananas", "kiwi", "orange", "pêche", 
        "abricot", "prune", "cerise", "fraise", "framboise", "myrtille",
        "melon", "pastèque", "raisin", "litchi", "papaye", "goyave"
    ]
    
    LEGUMES = [
        "carotte", "pomme de terre", "courgette", "aubergine", "poivron",
        "tomate", "concombre", "radis", "navet", "céleri", "poireau",
        "champignon", "brocoli", "chou-fleur", "haricot vert"
    ]
    
    def __init__(self, seed: int = None):
        """
        Initialise le générateur
        
        Args:
            seed: Graine pour la génération aléatoire (pour reproductibilité)
        """
        if seed is not None:
            random.seed(seed)
    
    def generer_instance_simple(
        self, 
        nombre_plats: int = 5, 
        nombre_commis: int = 3,
        nom: str = None
    ) -> Instance:
        """
        Génère une instance simple avec des temps aléatoires
        
        Args:
            nombre_plats: Nombre de plats à générer
            nombre_commis: Nombre de commis disponibles
            nom: Nom de l'instance (généré automatiquement si None)
        
        Returns:
            Instance générée
        """
        plats = []
        ingredients = random.sample(self.FRUITS + self.LEGUMES, nombre_plats)
        
        for i, ingredient in enumerate(ingredients):
            # Temps d'épluchage entre 5 et 20 minutes
            temps_prep = random.randint(5, 20) * 60
            # Temps de cuisson entre 5 et 30 minutes
            temps_cuisson = random.randint(5, 30) * 60
            
            plats.append({
                "nom": ingredient,
                "temps_prep": temps_prep,
                "temps_cuisson": temps_cuisson
            })
        
        nom_instance = nom or f"instance_simple_{nombre_plats}plats_{nombre_commis}commis"
        
        return Instance(
            nom=nom_instance,
            description=f"Instance simple avec {nombre_plats} plats et {nombre_commis} commis",
            plats=plats,
            nombre_commis=nombre_commis,
            difficulte="facile"
        )
    
    def generer_instance_equilibree(
        self,
        nombre_plats: int = 8,
        nombre_commis: int = 3,
        nom: str = None
    ) -> Instance:
        """
        Génère une instance équilibrée où les temps sont similaires
        (plus difficile à optimiser)
        
        Args:
            nombre_plats: Nombre de plats à générer
            nombre_commis: Nombre de commis disponibles
            nom: Nom de l'instance
        
        Returns:
            Instance générée
        """
        plats = []
        ingredients = random.sample(self.FRUITS + self.LEGUMES, nombre_plats)
        
        # Temps moyens autour desquels on va générer
        temps_moyen_epluchage = 10 * 60  # 10 minutes
        temps_moyen_cuisson = 15 * 60     # 15 minutes
        variation = 0.3  # 30% de variation
        
        for ingredient in ingredients:
            temps_prep = int(random.gauss(
                temps_moyen_epluchage, 
                temps_moyen_epluchage * variation
            ))
            temps_cuisson = int(random.gauss(
                temps_moyen_cuisson,
                temps_moyen_cuisson * variation
            ))
            
            # S'assurer que les temps sont positifs et raisonnables
            temps_prep = max(60, min(temps_prep, 30 * 60))
            temps_cuisson = max(60, min(temps_cuisson, 40 * 60))
            
            plats.append({
                "nom": ingredient,
                "temps_prep": temps_prep,
                "temps_cuisson": temps_cuisson
            })
        
        nom_instance = nom or f"instance_equilibree_{nombre_plats}plats_{nombre_commis}commis"
        
        return Instance(
            nom=nom_instance,
            description=f"Instance équilibrée avec {nombre_plats} plats et {nombre_commis} commis (temps similaires)",
            plats=plats,
            nombre_commis=nombre_commis,
            difficulte="moyen"
        )
    
    def generer_instance_difficile(
        self,
        nombre_plats: int = 10,
        nombre_commis: int = 4,
        nom: str = None
    ) -> Instance:
        """
        Génère une instance difficile avec des temps très variés
        (un ou deux plats très longs, beaucoup de plats courts)
        
        Args:
            nombre_plats: Nombre de plats à générer
            nombre_commis: Nombre de commis disponibles
            nom: Nom de l'instance
        
        Returns:
            Instance générée
        """
        plats = []
        ingredients = random.sample(self.FRUITS + self.LEGUMES, nombre_plats)
        
        # Créer quelques plats très longs
        nombre_plats_longs = max(2, nombre_plats // 4)
        
        for i, ingredient in enumerate(ingredients):
            if i < nombre_plats_longs:
                # Plats longs
                temps_prep = random.randint(20, 40) * 60
                temps_cuisson = random.randint(30, 60) * 60
            else:
                # Plats courts
                temps_prep = random.randint(2, 8) * 60
                temps_cuisson = random.randint(5, 15) * 60
            
            plats.append({
                "nom": ingredient,
                "temps_prep": temps_prep,
                "temps_cuisson": temps_cuisson
            })
        
        # Mélanger pour ne pas avoir tous les plats longs au début
        random.shuffle(plats)
        
        nom_instance = nom or f"instance_difficile_{nombre_plats}plats_{nombre_commis}commis"
        
        return Instance(
            nom=nom_instance,
            description=f"Instance difficile avec {nombre_plats} plats et {nombre_commis} commis (temps très variés)",
            plats=plats,
            nombre_commis=nombre_commis,
            difficulte="difficile"
        )
    
    def generer_instance_desequilibree(
        self,
        nombre_plats: int = 12,
        nombre_commis: int = 5,
        nom: str = None
    ) -> Instance:
        """
        Génère une instance déséquilibrée où le nombre de commis
        n'est pas adapté à la charge de travail
        
        Args:
            nombre_plats: Nombre de plats à générer
            nombre_commis: Nombre de commis disponibles
            nom: Nom de l'instance
        
        Returns:
            Instance générée
        """
        plats = []
        ingredients = random.sample(self.FRUITS + self.LEGUMES, nombre_plats)
        
        for ingredient in ingredients:
            temps_prep = random.randint(8, 25) * 60
            temps_cuisson = random.randint(10, 35) * 60
            
            plats.append({
                "nom": ingredient,
                "temps_prep": temps_prep,
                "temps_cuisson": temps_cuisson
            })
        
        nom_instance = nom or f"instance_desequilibree_{nombre_plats}plats_{nombre_commis}commis"
        
        return Instance(
            nom=nom_instance,
            description=f"Instance déséquilibrée avec {nombre_plats} plats et {nombre_commis} commis",
            plats=plats,
            nombre_commis=nombre_commis,
            difficulte="difficile"
        )
    
    def generer_batch_instances(
        self,
        nombre_instances: int = 5,
        types: List[str] = None
    ) -> List[Instance]:
        """
        Génère un lot d'instances de différents types
        
        Args:
            nombre_instances: Nombre d'instances à générer
            types: Liste des types d'instances ("simple", "equilibree", "difficile", "desequilibree")
        
        Returns:
            Liste d'instances générées
        """
        if types is None:
            types = ["simple", "equilibree", "difficile", "desequilibree"]
        
        instances = []
        
        for i in range(nombre_instances):
            type_instance = random.choice(types)
            nombre_plats = random.randint(5, 15)
            nombre_commis = random.randint(2, 6)
            
            if type_instance == "simple":
                instance = self.generer_instance_simple(nombre_plats, nombre_commis, f"batch_{i+1}_simple")
            elif type_instance == "equilibree":
                instance = self.generer_instance_equilibree(nombre_plats, nombre_commis, f"batch_{i+1}_equilibree")
            elif type_instance == "difficile":
                instance = self.generer_instance_difficile(nombre_plats, nombre_commis, f"batch_{i+1}_difficile")
            else:  # desequilibree
                instance = self.generer_instance_desequilibree(nombre_plats, nombre_commis, f"batch_{i+1}_desequilibree")
            
            instances.append(instance)
        
        return instances
    
    def sauvegarder_instances(self, instances: List[Instance], fichier: str):
        """
        Sauvegarde les instances dans un fichier JSON
        
        Args:
            instances: Liste d'instances à sauvegarder
            fichier: Chemin du fichier de sortie
        """
        data = {
            "metadata": {
                "nombre_instances": len(instances),
                "generateur": "InstanceGenerator v1.0",
                "projet": "Ordonnancement Cuisine - Polytech Nice SI4"
            },
            "instances": [instance.to_dict() for instance in instances]
        }
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f" {len(instances)} instance(s) sauvegardée(s) dans {fichier}")


def main():
    """Fonction principale pour tester le générateur"""
    print("🍳 Générateur d'instances - Problème d'ordonnancement de cuisine")
    print("=" * 70)
    
    generator = InstanceGenerator(seed=42)  # Pour reproductibilité
    
    # Générer différents types d'instances
    print("\n Génération d'instances de test...\n")
    
    instance_simple = generator.generer_instance_simple(5, 3, "test_simple")
    print(f"✓ Instance simple générée: {instance_simple.nom}")
    print(f"  - {len(instance_simple.plats)} plats, {instance_simple.nombre_commis} commis")
    
    instance_equilibree = generator.generer_instance_equilibree(8, 3, "test_equilibree")
    print(f"✓ Instance équilibrée générée: {instance_equilibree.nom}")
    print(f"  - {len(instance_equilibree.plats)} plats, {instance_equilibree.nombre_commis} commis")
    
    instance_difficile = generator.generer_instance_difficile(10, 4, "test_difficile")
    print(f"✓ Instance difficile générée: {instance_difficile.nom}")
    print(f"  - {len(instance_difficile.plats)} plats, {instance_difficile.nombre_commis} commis")
    
    # Sauvegarder les instances
    instances = [instance_simple, instance_equilibree, instance_difficile]
    generator.sauvegarder_instances(instances, "instances/test_instances.json")
    
    print("\n📈 Statistiques de l'instance difficile:")
    stats = instance_difficile.calculer_statistiques()
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    print("\n✨ Génération terminée avec succès!")


if __name__ == "__main__":
    main()