from typing import Dict, Any, List

class FinanceManager:
    def __init__(self):
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 100_000
        self.SECURITY_BUFFER = 15_000

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> List[str]:
        commandes = []
        
        # 1. RECUPERATION DE L'ARGENT RÉEL
        cash = farm_data.get("cash", farm_data.get("money", 0))
        
        fields = farm_data.get("fields", [])
        tractors = farm_data.get("tractors", [])
        loans = farm_data.get("loans", [])
        employees = farm_data.get("employees", [])
        
        nb_fields_bought = sum(1 for f in fields if f["bought"])
        nb_tractors = len(tractors)
        nb_loans = len(loans)
        
        # --- 2. GESTION DES EMPRUNTS (Urgence Uniquement) ---
        if cash < 2000 and nb_loans < self.MAX_LOANS:
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             print(f"💸 [FINANCE] Compte à sec ({cash}€). Emprunt demandé. On attend l'argent.")
             return commandes # <--- ON STOPPE TOUT ICI

        # --- 3. CALCUL DU BUDGET RÉEL ---
        masse_salariale = len(employees) * 1200 
        cash_investissable = cash - self.SECURITY_BUFFER - masse_salariale
        if cash_investissable <= 0:
            return []

        # --- 4. INVESTISSEMENT (Uniquement si on a le cash en main) ---
        while True:
            action_faite = False
            if nb_tractors < nb_fields_bought and nb_tractors < self.MAX_TRACTORS_GLOBAL:
                if cash_investissable >= self.PRICE_TRACTOR:
                    commandes.append("0 ACHETER_TRACTEUR")
                    print(f"🚜 [FINANCE] Achat Tracteur cash (Reste: {cash_investissable - self.PRICE_TRACTOR})")
                    cash_investissable -= self.PRICE_TRACTOR
                    nb_tractors += 1
                    action_faite = True
                else:
                    break 

            elif nb_fields_bought < self.MAX_FIELDS:
                if cash_investissable >= self.PRICE_FIELD:
                    commandes.append("0 ACHETER_CHAMP")
                    print(f"⛳ [FINANCE] Achat Champ cash (Reste: {cash_investissable - self.PRICE_FIELD})")
                    cash_investissable -= self.PRICE_FIELD
                    nb_fields_bought += 1
                    action_faite = True
                else:
                    break
            
            if not action_faite:
                break

        return commandes