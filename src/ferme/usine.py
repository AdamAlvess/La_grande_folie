class Usine:
    _MEMOIRE_OCCUPATION: dict[int, int] = {} 
    _EST_SUR_PLACE: set[int] = set()
    _DERNIER_JOUR_VU = -1

    def __init__(self):
        pass

    @property
    def employee_busy_until(self):
        return Usine._MEMOIRE_OCCUPATION

    def _nettoyage_nouvelle_partie(self, day: int):
        if day < Usine._DERNIER_JOUR_VU:
            Usine._MEMOIRE_OCCUPATION.clear()
            Usine._EST_SUR_PLACE.clear()
        Usine._DERNIER_JOUR_VU = day

    def _est_bloquee(self, farm: dict) -> bool:
        return farm.get("blocked", False)

    def _calculer_stock_total(self, farm: dict) -> int:
        factory = farm.get("soup_factory", {})
        stock = factory.get("stock", {})
        return sum(stock.values())

    def _employe_est_disponible(self, emp: dict, day: int, ids_autorises: list[int]) -> bool:
        e_id = int(emp["id"])
        if e_id not in ids_autorises: 
            return False
        if day <= self.employee_busy_until.get(e_id, -1): 
            return False
        if emp.get("action", "IDLE") != "IDLE": 
            return False
        return True

    def _assigner_cuisine(self, emp_id: int, day: int):
        if emp_id in Usine._EST_SUR_PLACE:
            duree = 1
            log_msg = "Cuisine (Sur place)"
        else:
            duree = 7
            Usine._EST_SUR_PLACE.add(emp_id)
            log_msg = "Marche vers Usine + Cuisine"
        duree += 1
        self.employee_busy_until[emp_id] = day + duree
        return f"{emp_id} CUISINER", log_msg, duree

    def execute(self, farm: dict, day: int, ids_autorises: list[int]) -> list[str]:
        self._nettoyage_nouvelle_partie(day)
        if self._est_bloquee(farm): 
            return []
        stock_restant = self._calculer_stock_total(farm)
        if stock_restant <= 0: 
            return []
        commandes = []
        employees = farm.get("employees", [])
        for emp in employees:
            if self._employe_est_disponible(emp, day, ids_autorises):
                e_id = int(emp["id"])
                cmd_str, log_msg, duree = self._assigner_cuisine(e_id, day)
                commandes.append(cmd_str)
                stock_restant -= 100
                if stock_restant <= 0: 
                    break
        return commandes