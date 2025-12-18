from ferme.cultiver import Cultiver  # N'oublie pas l'import !

class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        # On initialise le cerveau "Cultiver" ici pour qu'il garde sa mémoire
        self.cultivator = Cultiver()

    def jouer_tour(self, game_data: dict) -> list[str]:
        """
        Calcul les commandes pour les jours > 0.
        """
        commandes: list[str] = []
        
        # Récupération de ma ferme
        ma_ferme = None
        for ferme in game_data["farms"]:
            if ferme["name"] == self.nom_ferme:
                ma_ferme = ferme
                break
        
        if not ma_ferme:
            return []

        day = game_data["day"]
        # Récupération du cash (supporte 'cash' ou 'money' selon version serveur)
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))

        # --- LOGIQUE DU JEU ---
        
        # On demande à Cultiver ses ordres
        commandes_agriculture = self.cultivator.execute(ma_ferme, day, cash)
        
        # On ajoute ces ordres à la liste globale
        commandes.extend(commandes_agriculture)

        # Si tes potes font d'autres modules (ex: Vente), tu feras pareil :
        # commandes.extend(self.vendeur.execute(...))

        return commandes