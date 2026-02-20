"""
Validateur d'instances pour le problème d'ordonnancement de cuisine
Vérifie que les instances respectent les contraintes du problème
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResultatValidation:
    """Résultat de la validation d'une instance"""
    valide: bool
    erreurs: List[str]
    avertissements: List[str]
    statistiques: Dict
    
    def afficher(self):
        """Affiche le résultat de la validation de manière formatée"""
        if self.valide:
            print(" Instance VALIDE")
        else:
            print(" Instance INVALIDE")
        
        if self.erreurs:
            print("\n Erreurs:")
            for erreur in self.erreurs:
                print(f"   • {erreur}")
        
        if self.avertissements:
            print("\n  Avertissements:")
            for avert in self.avertissements:
                print(f"   • {avert}")
        
        if self.statistiques:
            print("\n Statistiques:")
            for key, value in self.statistiques.items():
                print(f"   • {key}: {value}")


class InstanceValidator:
    """Validateur pour les instances du problème"""
    
    # Contraintes du problème
    MIN_PLATS = 1
    MAX_PLATS = 1000  # Pour éviter des instances trop grandes
    MIN_COMMIS = 1
    MAX_COMMIS = 100
    MIN_TEMPS = 0
    MAX_TEMPS = 24 * 3600  # 24 heures max par tâche
    
    def __init__(self):
        """Initialise le validateur"""
        pass
    
    def valider_instance(self, instance: Dict) -> ResultatValidation:
        """
        Valide une instance complète
        
        Args:
            instance: Dictionnaire représentant l'instance
        
        Returns:
            ResultatValidation avec les résultats de la validation
        """
        erreurs = []
        avertissements = []
        statistiques = {}
        
        # Vérifier la structure de base
        champs_requis = ["nom", "plats", "nombre_commis"]
        for champ in champs_requis:
            if champ not in instance:
                erreurs.append(f"Champ obligatoire manquant: '{champ}'")
        
        if erreurs:
            return ResultatValidation(False, erreurs, avertissements, statistiques)
        
        # Valider le nom
        if not isinstance(instance["nom"], str) or not instance["nom"].strip():
            erreurs.append("Le nom de l'instance doit être une chaîne non vide")
        
        # Valider les plats
        plats = instance["plats"]
        if not isinstance(plats, list):
            erreurs.append("'plats' doit être une liste")
        elif len(plats) < self.MIN_PLATS:
            erreurs.append(f"Il doit y avoir au moins {self.MIN_PLATS} plat(s)")
        elif len(plats) > self.MAX_PLATS:
            avertissements.append(f"Instance très grande: {len(plats)} plats (max recommandé: {self.MAX_PLATS})")
        else:
            # Valider chaque plat
            for i, plat in enumerate(plats):
                erreurs_plat = self._valider_plat(plat, i)
                erreurs.extend(erreurs_plat)
        
        # Valider le nombre de commis
        nombre_commis = instance["nombre_commis"]
        if not isinstance(nombre_commis, int):
            erreurs.append("'nombre_commis' doit être un entier")
        elif nombre_commis < self.MIN_COMMIS:
            erreurs.append(f"Il doit y avoir au moins {self.MIN_COMMIS} commis")
        elif nombre_commis > self.MAX_COMMIS:
            avertissements.append(f"Nombre très élevé de commis: {nombre_commis}")
        
        # Vérifier la cohérence globale
        if not erreurs and isinstance(plats, list) and isinstance(nombre_commis, int):
            coherence_warnings = self._verifier_coherence(plats, nombre_commis)
            avertissements.extend(coherence_warnings)
            
            # Calculer les statistiques
            statistiques = self._calculer_statistiques(plats, nombre_commis)
        
        valide = len(erreurs) == 0
        
        return ResultatValidation(valide, erreurs, avertissements, statistiques)
    
    def _valider_plat(self, plat: Dict, index: int) -> List[str]:
        """
        Valide un plat individuel
        
        Args:
            plat: Dictionnaire représentant le plat
            index: Index du plat dans la liste
        
        Returns:
            Liste des erreurs trouvées
        """
        erreurs = []
        
        # Vérifier les champs requis
        if "nom" not in plat:
            erreurs.append(f"Plat {index + 1}: champ 'nom' manquant")
        elif not isinstance(plat["nom"], str) or not plat["nom"].strip():
            erreurs.append(f"Plat {index + 1}: le nom doit être une chaîne non vide")
        
        if "temps_epluchage" not in plat:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): champ 'temps_epluchage' manquant")
        elif not isinstance(plat["temps_epluchage"], (int, float)):
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): 'temps_epluchage' doit être un nombre")
        elif plat["temps_epluchage"] < self.MIN_TEMPS:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): temps_epluchage ne peut pas être négatif")
        elif plat["temps_epluchage"] > self.MAX_TEMPS:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): temps_epluchage trop élevé ({plat['temps_epluchage']}s > {self.MAX_TEMPS}s)")
        
        if "temps_cuisson" not in plat:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): champ 'temps_cuisson' manquant")
        elif not isinstance(plat["temps_cuisson"], (int, float)):
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): 'temps_cuisson' doit être un nombre")
        elif plat["temps_cuisson"] < self.MIN_TEMPS:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): temps_cuisson ne peut pas être négatif")
        elif plat["temps_cuisson"] > self.MAX_TEMPS:
            erreurs.append(f"Plat {index + 1} ({plat.get('nom', '?')}): temps_cuisson trop élevé ({plat['temps_cuisson']}s > {self.MAX_TEMPS}s)")
        
        return erreurs
    
    def _verifier_coherence(self, plats: List[Dict], nombre_commis: int) -> List[str]:
        """
        Vérifie la cohérence globale de l'instance
        
        Args:
            plats: Liste des plats
            nombre_commis: Nombre de commis
        
        Returns:
            Liste des avertissements
        """
        avertissements = []
        
        # Vérifier si tous les plats ont des temps nuls
        tous_nuls = all(
            plat.get("temps_epluchage", 0) == 0 and plat.get("temps_cuisson", 0) == 0
            for plat in plats
        )
        if tous_nuls:
            avertissements.append("Tous les plats ont des temps nuls - instance triviale")
        
        # Vérifier l'équilibre charge/commis
        temps_totaux = [
            plat.get("temps_epluchage", 0) + plat.get("temps_cuisson", 0)
            for plat in plats
        ]
        temps_total = sum(temps_totaux)
        
        if temps_total > 0:
            charge_moyenne = temps_total / nombre_commis
            temps_max = max(temps_totaux)
            
            if temps_max > charge_moyenne * 2:
                avertissements.append(
                    f"Déséquilibre potentiel: le plat le plus long ({temps_max}s) "
                    f"est plus de 2x la charge moyenne par commis ({charge_moyenne:.0f}s)"
                )
            
            if nombre_commis > len(plats):
                avertissements.append(
                    f"Plus de commis ({nombre_commis}) que de plats ({len(plats)}) - "
                    f"certains commis seront inactifs"
                )
        
        # Vérifier les noms de plats dupliqués
        noms = [plat.get("nom", "") for plat in plats]
        noms_uniques = set(noms)
        if len(noms_uniques) < len(noms):
            duplicats = [nom for nom in noms_uniques if noms.count(nom) > 1]
            avertissements.append(f"Noms de plats dupliqués: {', '.join(duplicats)}")
        
        return avertissements
    
    def _calculer_statistiques(self, plats: List[Dict], nombre_commis: int) -> Dict:
        """
        Calcule des statistiques sur l'instance
        
        Args:
            plats: Liste des plats
            nombre_commis: Nombre de commis
        
        Returns:
            Dictionnaire de statistiques
        """
        temps_epluchage = [plat.get("temps_epluchage", 0) for plat in plats]
        temps_cuisson = [plat.get("temps_cuisson", 0) for plat in plats]
        temps_totaux = [e + c for e, c in zip(temps_epluchage, temps_cuisson)]
        
        temps_total = sum(temps_totaux)
        
        stats = {
            "nombre_plats": len(plats),
            "nombre_commis": nombre_commis,
            "temps_total_travail": temps_total,
            "temps_total_epluchage": sum(temps_epluchage),
            "temps_total_cuisson": sum(temps_cuisson),
            "temps_moyen_par_plat": temps_total / len(plats) if plats else 0,
            "temps_max_plat": max(temps_totaux) if temps_totaux else 0,
            "temps_min_plat": min(temps_totaux) if temps_totaux else 0,
            "charge_theorique_par_commis": temps_total / nombre_commis if nombre_commis > 0 else 0,
            "ratio_plats_commis": len(plats) / nombre_commis if nombre_commis > 0 else 0
        }
        
        # Formater les temps en minutes pour lisibilité
        stats["temps_total_travail_minutes"] = f"{temps_total / 60:.1f} min"
        stats["charge_theorique_par_commis_minutes"] = f"{stats['charge_theorique_par_commis'] / 60:.1f} min"
        
        return stats
    
    def valider_fichier_instances(self, fichier: str) -> Dict[str, ResultatValidation]:
        """
        Valide toutes les instances d'un fichier JSON
        
        Args:
            fichier: Chemin du fichier JSON
        
        Returns:
            Dictionnaire {nom_instance: resultat_validation}
        """
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f" Fichier non trouvé: {fichier}")
            return {}
        except json.JSONDecodeError as e:
            print(f" Erreur de parsing JSON: {e}")
            return {}
        
        instances = data.get("instances", [])
        if not instances:
            print("  Aucune instance trouvée dans le fichier")
            return {}
        
        resultats = {}
        for instance in instances:
            nom = instance.get("nom", "instance_sans_nom")
            resultat = self.valider_instance(instance)
            resultats[nom] = resultat
        
        return resultats


def main():
    """Fonction principale pour tester le validateur"""
    print("🔍 Validateur d'instances - Problème d'ordonnancement de cuisine")
    print("=" * 70)
    
    validator = InstanceValidator()
    
    # Obtenir le chemin du dossier instances
    project_root = Path(__file__).parent.parent.parent
    instances_dir = project_root / "instances"

    # Tester les instances de référence
    print("\n📋 Validation des instances de référence...")
    fichier_reference = instances_dir / "reference_instances.json"

    if not fichier_reference.exists():
        print(f"⚠️  Fichier non trouvé: {fichier_reference}")
        print("   Veuillez d'abord exécuter create_reference_instances.py")
        return

    resultats = validator.valider_fichier_instances(str(fichier_reference))

    print(f"\n✅ {len(resultats)} instance(s) validée(s)\n")

    instances_valides = sum(1 for r in resultats.values() if r.valide)
    instances_invalides = len(resultats) - instances_valides
    
    print(f"Résumé: {instances_valides} valides, {instances_invalides} invalides")
    print("-" * 70)
    
    for nom, resultat in resultats.items():
        print(f"\n📌 Instance: {nom}")
        resultat.afficher()
        print()
    
    # Tester les instances générées
    print("\n" + "=" * 70)
    print("📋 Validation des instances de test...")
    fichier_test = instances_dir / "test_instances.json"

    if fichier_test.exists():
        resultats_test = validator.valider_fichier_instances(str(fichier_test))

        print(f"\n✅ {len(resultats_test)} instance(s) de test validée(s)\n")

        for nom, resultat in resultats_test.items():
            print(f"\n📌 Instance: {nom}")
            resultat.afficher()
            print()
    else:
        print(f"ℹ️  Aucun fichier de test trouvé à {fichier_test}")

    print("\n✨ Validation terminée!")


if __name__ == "__main__":
    main()