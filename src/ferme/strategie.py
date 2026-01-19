from ferme.cultiver import Cultiver
from ferme.employer import GestionnairePersonnel 
from ferme.usine import Usine

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        
        # On initialise nos experts
        self.cultivator = Cultiver()
        self.drh = GestionnairePersonnel(nom_ferme)
        self.chef_cuisine = Usine()

    def _extraire_ids_occupes(self, commandes: list[str]) -> list[int]:
        """
        Petite fonction pour lire les commandes d'agriculture (ex: '10 SEMER...')
        et savoir quels employés sont déjà pris.
        """
        ids = []
        for cmd in commandes:
            parts = cmd.split()
            # Si la commande commence par un ID d'employé (pas 0 qui est la ferme)
            if parts[0].isdigit() and parts[0] != "0":
                ids.append(int(parts[0]))
        return ids

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
        
        # # --- MODULE 2 : USINE (Cuisiner) ---         

        # ids_aux_champs = self._extraire_ids_occupes(commandes_agriculture)
        # commandes_usine = self.chef_cuisine.execute(ma_ferme, day, excluded_ids=ids_aux_champs)
        # commandes.extend(commandes_usine)

        # --- MODULE 3 : Employés ---
        commandes_rh = self.drh.gerer_effectifs(ma_ferme)
        commandes.extend(commandes_rh)

        
        return commandes