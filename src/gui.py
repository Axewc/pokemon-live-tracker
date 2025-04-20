import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap

class TeamWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pokémon Live Tracker")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.slots = []
        for _ in range(6):
            vbox = QVBoxLayout()
            img_label = QLabel()
            nick_label = QLabel("—")
            vbox.addWidget(img_label)
            vbox.addWidget(nick_label)
            self.layout.addLayout(vbox)
            self.slots.append((img_label, nick_label))

    def update_team(self, team):
        for idx, (img_label, nick_label) in enumerate(self.slots):
            if idx < len(team):
                pokemon = team[idx]
                pixmap = QPixmap(f"sprites/sprites/{pokemon.image_index}.png")
                img_label.setPixmap(pixmap)
                nick_label.setText(pokemon.nickname.decode('utf-8').strip('\x00'))
            else:
                img_label.clear()
                nick_label.setText("—")