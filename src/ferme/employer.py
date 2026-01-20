import math

class GestionnairePersonnel:
    def __init__(self, nom_ferme: str):
        self.nom_ferme = nom_ferme
        self.MAX_EMPLOYES = 300
        self.SALAIRE_BASE = 1000

    def estimer_cout_licenciement(self, salaire_actuel: int) -> int:
        salaire_prochain_mois = math.ceil(salaire_actuel * 1.01)
        return salaire_prochain_mois

    def gerer_effectifs(self, ma_ferme: dict) -> list[str]:
        if ma_ferme.get("blocked", False):
            return []
            
        commandes = []
        employes = ma_ferme["employees"]
        champs = ma_ferme["fields"]
        cash = ma_ferme.get("cash", ma_ferme.get("money", 0))
        nb_employes = len(employes)
        nb_champs_actifs = sum(1 for f in champs if f["bought"])

        # --- NOUVELLE STRATÉGIE RH : L'ARMÉE ---
        if nb_champs_actifs > 0:
            cible = (nb_champs_actifs * 3) + 6
        else:
            cible = 2

        cible = min(cible, self.MAX_EMPLOYES)
        masse_salariale_totale = sum(e.get("salary", self.SALAIRE_BASE) for e in employes)

        # EMBAUCHE
        if nb_employes < cible:
            cout_premier_mois = self.SALAIRE_BASE

            if cash > (masse_salariale_totale + cout_premier_mois + 10_000): 
                commandes.append("0 EMPLOYER")
                print(f"🤝 RH: Recrutement (Effectif: {nb_employes} / Cible: {cible})")
            else:   
                print(f"💸 RH: Cash insuffisant pour recruter ({cash}€)")

        # LICENCIEMENT
        elif nb_employes >= cible:
            employes_tries = sorted(employes, key=lambda x: x.get("salary", 0), reverse=True)
            candidat = employes_tries[0]
            cout_indemnite = self.estimer_cout_licenciement(candidat.get("salary", self.SALAIRE_BASE))

            if cash > cout_indemnite:
                commandes.append(f"0 LICENCIER {candidat['id']}")
                print(f"👋 RH: Licenciement économique de {candidat['id']}")

        return commandes