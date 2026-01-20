from typing import Dict, Any, List, Tuple

class FinanceManager:
    def __init__(self):
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 50_000
        self.SECURITY_BUFFER = 10_000 

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> Tuple[List[str], int]:
        commandes = []
        cout_action = 0
        
        cash = farm_data.get("cash", farm_data.get("money", 0))
        fields = farm_data.get("fields", [])
        tractors = farm_data.get("tractors", [])
        loans = farm_data.get("loans", [])
        employees = farm_data.get("employees", [])
        
        nb_fields_bought = sum(1 for f in fields if f.get("bought", False))
        nb_tractors = len(tractors)
        nb_loans = len(loans)

        print(f"💰 [FINANCE] Emprunts: {nb_loans}")
        # Urgence : Emprunt
        if cash < 5000 and nb_loans < self.MAX_LOANS:
             print(f"💰 [FINANCE] Cash faible ({cash}€). Emprunt de {self.LOAN_AMOUNT}€")
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             return commandes, cout_action 

        # Calcul du budget investissement
        masse_salariale = len(employees) * 1200 
        cash_investissable = cash - self.SECURITY_BUFFER - masse_salariale

        if cash_investissable <= 0:
            return [], 0

        # 1 Action par tour MAX
        if nb_tractors < nb_fields_bought and nb_tractors < self.MAX_TRACTORS_GLOBAL:
            if cash_investissable >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                cout_action = self.PRICE_TRACTOR 
                print(f"🚜 [FINANCE] Achat Tracteur (Coût: {cout_action})")
                return commandes, cout_action

        # Sinon achat de champ
        elif nb_fields_bought < self.MAX_FIELDS:
            if cash_investissable >= self.PRICE_FIELD:
                commandes.append("0 ACHETER_CHAMP")
                cout_action = self.PRICE_FIELD 
                print(f"⛳ [FINANCE] Achat Champ (Coût: {cout_action})")
                return commandes, cout_action
            
        return commandes, 0