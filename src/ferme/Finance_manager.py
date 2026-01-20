from typing import Dict, Any, List, Tuple
import math

class FinanceManager:
    def __init__(self):
        self.PRICE_FIELD = 10_000
        self.PRICE_TRACTOR = 30_000
        self.MAX_FIELDS = 5
        self.MAX_TRACTORS_GLOBAL = 50
        self.MAX_LOANS = 10
        self.LOAN_AMOUNT = 50_000 

    def calculer_charges_mensuelles(self, farm_data: Dict[str, Any]) -> int:
        employees = farm_data.get("employees", [])
        loans = farm_data.get("loans", [])
        
        # Salaires (+5% marge)
        masse_salariale = sum(e.get("salary", 1000) for e in employees)
        cout_salaires = math.ceil(masse_salariale * 1.05)
        
        # Remboursements
        cout_emprunts = len(loans) * 5000 
        
        return cout_salaires + cout_emprunts

    def get_manager_action(self, farm_data: Dict[str, Any], day: int) -> Tuple[List[str], int]:
        commandes = []
        cout_action = 0
        
        cash = farm_data.get("money", 0)
        fields = farm_data.get("fields", [])
        tractors = farm_data.get("tractors", [])
        loans = farm_data.get("loans", [])
        
        nb_fields_bought = sum(1 for f in fields if f.get("bought", False))
        nb_tractors = len(tractors)
        nb_loans = len(loans)
        
        charges = self.calculer_charges_mensuelles(farm_data)
        security_buffer = (charges * 2) + 5000

        print(f"💰 [FINANCE] Cash: {cash} | Buffer Requis: {security_buffer} | Tracteurs: {nb_tractors}")

        # 1. URGENCE : Emprunt
        if cash < charges and nb_loans < self.MAX_LOANS:
             # CORRECTION : Suppression du 'f' car pas de variable {}
             print("🚨 [FINANCE] Emprunt de secours !")
             commandes.append(f"0 EMPRUNTER {self.LOAN_AMOUNT}")
             return commandes, 0

        # 2. INVESTISSEMENT
        cash_investissable = cash - security_buffer

        if cash_investissable <= 0:
            return [], 0

        # A. Achat Tracteur
        if nb_tractors <= nb_fields_bought and nb_tractors < self.MAX_TRACTORS_GLOBAL:
            if cash_investissable >= self.PRICE_TRACTOR:
                commandes.append("0 ACHETER_TRACTEUR")
                cout_action = self.PRICE_TRACTOR 
                print(f"🚜 [FINANCE] Achat Tracteur (Total: {nb_tractors + 1})")
                return commandes, cout_action

        # B. Achat Champ
        elif nb_fields_bought < self.MAX_FIELDS:
            if cash_investissable >= self.PRICE_FIELD:
                commandes.append("0 ACHETER_CHAMP")
                cout_action = self.PRICE_FIELD 
                print(f"⛳ [FINANCE] Achat Champ (Total: {nb_fields_bought + 1})")
                return commandes, cout_action
            
        return commandes, 0