import argparse
from typing import NoReturn
from chronobio.network.client import Client
from ferme.strategie import FarmStrategy
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

class PlayerGameClient(Client):
    def __init__(
        self: "PlayerGameClient", server_addr: str, port: int, username: str
    ) -> None:
        super().__init__(server_addr, port, username, spectator=False)
        self._commands: list[str] = []

        self.strategie = FarmStrategy(username)


    def run(self: "PlayerGameClient") -> NoReturn:
        while True:
            game_data = self.read_json()
            
            # --- GESTION DE L'AFFICHAGE ---
            for farm in game_data["farms"]:
                if farm["name"] == self.username:
                    print(farm)
                    break
            else:
                print(f"En attente de la ferme {self.username}...")
                continue 

            # --- PRISE DE DÉCISION ---
            if game_data["day"] == 0:
                self.add_command("0 EMPRUNTER 100000")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_CHAMP")
                self.add_command("0 ACHETER_TRACTEUR")
                self.add_command("0 ACHETER_TRACTEUR")
                self.add_command("0 EMPLOYER")
                self.add_command("0 EMPLOYER")
                self.add_command("1 SEMER PATATE 3")
            else:
                # === LOGIQUE JOURS SUIVANTS ===
                commandes_du_cerveau = self.strategie.jouer_tour(game_data)
                for cmd in commandes_du_cerveau:
                    self.add_command(cmd)

            self.send_commands()

    def add_command(self: "PlayerGameClient", command: str) -> None:
        self._commands.append(command)

    def send_commands(self: "PlayerGameClient") -> None:
        data = {"commands": self._commands.copy()}
        print("sending", data)
        self.send_json(data)
        self._commands.clear()

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Game client.")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="name of server on the network",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",   
        type=int,
        help="location where server listens",
        default=16210,
    )
    args = parser.parse_args()
    client = PlayerGameClient(args.address, args.port, "La_grande_folie") 
    client.run()