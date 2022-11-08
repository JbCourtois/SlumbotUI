import itertools
import json
import re

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtWidgets import QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap

from .client import Session
from .cards import CARDS


STACK_SIZE = 20000

BUTTON_POS = [
    (1000, 450),
    (510, 450),
]

RE_ACTION = re.compile(r'^b\d+|c|k|f$')


class CardLabel(QLabel):
    SIZE = (72, 112)

    def __init__(self, parent, pos):
        super().__init__(parent)
        self.reset()
        self.move(*pos)

    def update(self, card):
        img_path = f'img/cards/{CARDS[card]}.png'
        pixmap = QPixmap(img_path).scaled(*self.SIZE)
        self.setPixmap(pixmap)

    def reset(self):
        img_path = f'img/cards/back.png'
        pixmap = QPixmap(img_path).scaled(*self.SIZE)
        self.setPixmap(pixmap)


class App(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()
        self.session = Session()
        self.is_hand_over = True

    def initUI(self):
        self.setWindowTitle('Slumbot UI')
        self.setGeometry(0, -100, 1600, 1000)
        main_font = "Arial"
        self.setStyleSheet(f"""
            QPushButton{{font: bold 14pt "{main_font}";}}
            QLabel{{font: bold 18pt "{main_font}"; color: white;}}
            QLineEdit{{font: 14pt "{main_font}";}}
        """)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap('img/table.jpg')
        label.setPixmap(pixmap)

        # Display backs
        self.hero_cards = [
            CardLabel(self, (350, 450)),
            CardLabel(self, (425, 450)),
        ]
        self.board_cards = [
            CardLabel(self, (600, 450)),
            CardLabel(self, (675, 450)),
            CardLabel(self, (750, 450)),
            CardLabel(self, (825, 450)),
            CardLabel(self, (900, 450)),
        ]
        self.bot_cards = [
            CardLabel(self, (1100, 450)),
            CardLabel(self, (1175, 450)),
        ]

        # Player labels
        QLabel('Hero', self).move(390, 400)
        QLabel('Slumbot', self).move(1110, 400)

        self.hero_stack = QLabel(str(STACK_SIZE), self)
        self.hero_stack.resize(500, 50)
        self.hero_stack.move(375, 560)

        self.bot_stack = QLabel(str(STACK_SIZE), self)
        self.bot_stack.resize(500, 50)
        self.bot_stack.move(1125, 560)

        self.dealer_button = self.initDealer()
        self.dealer_button.move(765, 475)

        self.top_label = QLabel(self)
        self.top_label.resize(1000, 50)
        self.top_label.move(590, 305)

        self.pot_label = QLabel('Pot: 0', self)
        self.pot_label.resize(1000, 50)
        self.pot_label.move(720, 560)

        self.action = QLabel(self)
        self.action.resize(1000, 50)
        self.action.move(500, 640)

        self.newHandButton = QPushButton('New hand', self)
        self.newHandButton.setGeometry(QtCore.QRect(300, 850, 150, 50))
        self.newHandButton.clicked.connect(self.new_hand)

        self.actText = QLineEdit(self)
        self.actText.setGeometry(QtCore.QRect(850, 850, 150, 40))
        self.actText.returnPressed.connect(self.act)

        self.actButton = QPushButton('Act', self)
        self.actButton.setGeometry(QtCore.QRect(650, 850, 150, 50))
        self.actButton.clicked.connect(self.act)

        self.show()

    def initDealer(self):
        label = QLabel(self)
        pixmap = QPixmap('img/dealer.png').scaled(50, 50)
        label.setPixmap(pixmap)

        return label

    def new_hand(self):
        for label in itertools.chain(self.hero_cards, self.board_cards, self.bot_cards):
            label.reset()
        self.top_label.clear()

        response = self.session.new_hand()
        self.update_from_response(response)

    def act(self):
        if self.is_hand_over:
            return self.new_hand()

        action = self.actText.text()
        if not RE_ACTION.match(action):
            self.top_label.setText(f'Invalid action: {action}')
            self.actText.clear()
            self.actText.setFocus()
            return

        self.top_label.clear()

        try:
            response = self.session.act(action)
        except ValueError as exc:
            self.top_label.setText(str(exc))
            return

        self.update_from_response(response)

    def update_from_response(self, response):
        for label, card in zip(self.hero_cards, response.get('hole_cards', [])):
            label.update(card)
        for label, card in zip(self.board_cards, response.get('board', [])):
            label.update(card)
        for label, card in zip(self.bot_cards, response.get('bot_hole_cards', [])):
            label.update(card)

        self.is_hand_over = 'bot_hole_cards' in response
        if self.is_hand_over:
            self.end(response)

        action = response.get('action') or '-'
        self.action.setText(action)

        pot_size = self.get_pot(action)
        self.pot_label.setText(f'Pot: {2 * pot_size}')
        stack = str(STACK_SIZE - pot_size)
        self.hero_stack.setText(stack)
        self.bot_stack.setText(stack)

        dealer_position = BUTTON_POS[response['client_pos']]
        self.dealer_button.move(*dealer_position)

        self.actText.clear()
        self.actText.setFocus()

    def end(self, response):
        response.pop('old_action', None)
        with open('logs/hands.json', 'a') as file:
            json.dump(response, file, separators=(',', ':'))
            print(file=file)

        self.top_label.setText(
            f'Won: {response["winnings"]}   '
            f'Baseline: {response["baseline_winnings"]}'
        )

    def get_pot(self, action):
        bets = re.findall(r'b(\d+)[a-z]*/', action)
        return sum(map(int, bets))
