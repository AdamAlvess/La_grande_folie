import argparse
import sys
import os
from typing import NoReturn
from chronobio.network.client import Client

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# =============================================================================

from cultiver import Cultiver

class PlayerGameClient(Client):
    def __init__(
        self: "PlayerGameClient", server_addr: str, port: int, username: str
    ) -> None:
        super().__init__(server_addr, port, username, spectator=False)
        self._commands: list[str] = []

        # On initialise ton cerveau
        self.strategy = Cultiver()

    def run(self: "PlayerGameClient") -> NoReturn:
        while True:
            game_data = self.read_json()
            my_farm = None
            
            for farm in game_data["farms"]:
                if farm["name"] == self.username:
                    my_farm = farm
                    break
            else:
                print(f"En attente de la ferme {self.username}...")
                continue 

            day = game_data["day"]
            current_cash = my_farm.get("cash", my_farm.get("money", 0))
                
            print(f"--- JOUR {day} --- Cash: {current_cash}")

            if day == 0:
                # TA STRAT DU JOUR 0 (MANUELLE)
                print("🔧 Exécution du Jour 0 manuel")
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
                # JOUR 1+ : L'INTELLIGENCE ARTIFICIELLE PREND LE RELAIS
                self.strategy.execute(self, my_farm, day, current_cash)

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