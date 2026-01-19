from typing import Dict, Any, List

class FinanceManager:
    def __init__(self):
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000
        self.SECURITY_BUFFER = 10_000 

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> List[str]:
        commandes = []
        
        cash = farm_data.get("cash", 0)
        fields = farm_data.get("fields", [])
        tractors = farm_data.get("tractors", [])
        loans = farm_data.get("loans", [])
        employees = farm_data.get("employees", [])
        
        # 1. COMPTER CE QU'ON A VRAIMENT (Correction du bug)
        # On ne compte que les champs qui ont "bought" = True
        nb_fields_bought = sum(1 for f in fields if f["bought"])
        nb_tractors = len(tractors)
        nb_loans = len(loans)
        
        # On garde une copie locale du cash pour simuler les achats successifs
        current_cash = cash 

        # --- 2. GESTION DES EMPRUNTS ---
        # On emprunte SEULEMENT si on est pauvre (< 5000) ET qu'on a de la marge de prêt
        # Si on a 100 000 de cash, on n'emprunte pas !
        if current_cash < 5000 and nb_loans < self.MAX_LOANS:
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             current_cash += self.LOAN_AMOUNT

        # Sécurité : on garde de quoi payer les salaires avant d'investir
        masse_salariale = len(employees) * 1200 # Marge large
        cash_investissable = current_cash - self.SECURITY_BUFFER - masse_salariale

        # --- 3. ACHAT DE CHAMPS (Boucle) ---
        # Tant qu'on a moins de 5 champs et assez d'argent, on achète
        while nb_fields_bought < self.MAX_FIELDS and cash_investissable >= self.PRICE_FIELD:
            commandes.append("0 ACHETER_CHAMP")
            cash_investissable -= self.PRICE_FIELD
            nb_fields_bought += 1 # On simule l'achat pour la suite de la boucle

        # --- 4. ACHAT DE TRACTEURS (Boucle) ---
        # Règle d'or : On veut AUTANT de tracteurs que de champs achetés
        while nb_tractors < nb_fields_bought and nb_tractors < self.MAX_TRACTORS_GLOBAL:
            if cash_investissable >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                cash_investissable -= self.PRICE_TRACTOR
                nb_tractors += 1
            else:
                break # Plus d'argent

        return commandes