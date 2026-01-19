from ferme.cultiver import Cultiver
from ferme.employer import GestionnairePersonnel 

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        
        # On initialise nos experts
        self.cultivator = Cultiver()
        self.drh = GestionnairePersonnel(nom_ferme)

    def jouer_tour(self, game_data: dict) -> list[str]:
        """
        Orchestre les différents modules de la ferme.
        """
        commandes: list[str] = []
        
        # 1. Récupération de ma ferme
        ma_ferme = None
        for ferme in game_data["farms"]:
            if ferme["name"] == self.nom_ferme:
                ma_ferme = ferme
                break
        
        if not ma_ferme:
            return []
        
        # --- SÉCURITÉ GLOBALE ---
        if ma_ferme.get("blocked", False):
            print(f"🛑 [STRATÉGIE] Ferme bloquée au jour {game_data['day']}. Silence total.")
            return []

        # Données utiles
        day = game_data["day"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))

        # --- MODULE 1 : AGRICULTURE (Cultiver) ---
        # (Suppose que ta classe Cultiver a bien une méthode execute)
        commandes_agriculture = self.cultivator.execute(ma_ferme, day, cash)
        commandes.extend(commandes_agriculture)
        
        # --- MODULE 2 : Employés ---
        commandes_rh = self.drh.gerer_effectifs(ma_ferme)
        commandes.extend(commandes_rh)

        return commandes