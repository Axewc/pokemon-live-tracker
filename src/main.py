import sys
import os
import time
import yaml
from threading import Thread
from PyQt5.QtWidgets import QApplication
from src.memory_client import MemoryClient
from src.parser import get_team
from src.gui import TeamWindow

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_config():
    with open("config/offsets.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    memory_client = MemoryClient(config['host'], config['port'])
    memory_client.connect()

    app = QApplication(sys.argv)
    window = TeamWindow()
    window.show()

    def refresh():
        while True:
            team = get_team(memory_client, config['team_base_offset'], config['pokemon_struct_size'])
            window.update_team(team)
            time.sleep(1)

    Thread(target=refresh, daemon=True).start()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()