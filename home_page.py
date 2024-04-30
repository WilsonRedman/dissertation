from PyQt5 import  QtWidgets, uic
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout)
from PyQt5.QtCore import Qt

import sqlite3

class Home(QWidget):
    def __init__(self):
        super(Home, self).__init__()
        uic.loadUi("ui/Home Page.ui", self)
        self.loadStocks()

    def loadStocks(self):
        conn = sqlite3.connect("db/trades.db")
        cursor = conn.cursor()

        # Queries the stocks the user owns
        query = cursor.execute("SELECT own.ticker, stocks.name, own.quantity FROM own INNER JOIN stocks on own.ticker = stocks.ticker")
        data = query.fetchall()

        # Clears the display of information (otherwise it stacks when loading the page)
        while self.scrollLayout.count():
            child = self.scrollLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Displays the users owned stocks
        if(data is not None):
            for owned in data:
                layout = QHBoxLayout()

                ticker = QLabel(owned[0])
                ticker.setAlignment(Qt.AlignCenter)

                name = QLabel(owned[1])
                name.setMinimumHeight(50)
                name.setAlignment(Qt.AlignCenter)
                name.setWordWrap(True)

                quantity = QLabel(str(owned[2]))
                quantity.setAlignment(Qt.AlignCenter)

                layout.addWidget(ticker)
                layout.addWidget(name)
                layout.addWidget(quantity)

                self.scrollLayout.addLayout(layout)