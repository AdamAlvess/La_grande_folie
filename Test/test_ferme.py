from unittest.mock import MagicMock, patch
import sys
from minimal_logiciel import PlayerGameClient
sys.modules["chronobio.network.client"] = MagicMock()

def test_borrow_money_at_start():
    fake_data = {
        "day": 0,
        "farms": [{"name": "La_grande_folie", "cash": 1000}]
    }

    with patch('minal_logiciel.Client'):
        bot = PlayerGameClient("localhost", 1234, "La_grande_folie")
        bot.read_json = MagicMock(side_effect=[fake_data, StopIteration])
        bot.send_json = MagicMock()
        try:
            bot.run()
        except StopIteration:
            pass
        args = bot.send_json.call_args[0][0]
        commands = args["commands"]
        assert "0 EMPRUNTER 100000" in commands