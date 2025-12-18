class FarmStrategy:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme

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

        # --- LOGIQUE DU JEU (Jours 1, 2, 3...) ---

        return commandes