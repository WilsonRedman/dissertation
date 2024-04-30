from PyQt5 import  QtWidgets, uic
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout)
from PyQt5.QtCore import Qt
import sys
import home_page
import predict_page
import trade_page
import documentation_page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home_window = home_page.Home()
    prediction_window = predict_page.Predictions()
    trade_window = trade_page.Trade()
    documentation_window = documentation_page.Documentation()

    win = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(win)

    win.setFixedSize(1000,600)

    # Stack for all of the pages
    stack = QtWidgets.QStackedWidget()

    # Each page is added to the stack
    stack.addWidget(home_window)
    stack.addWidget(prediction_window)
    stack.addWidget(trade_window)
    stack.addWidget(documentation_window)

    layout.addWidget(stack)

    # This connects the page buttons to their correct pages
    home_window.predictionButton.clicked.connect(lambda: stack.setCurrentIndex(1))
    home_window.tradeButton.clicked.connect(lambda: stack.setCurrentIndex(2))
    home_window.documentButton.clicked.connect(lambda: [stack.setCurrentIndex(3), documentation_window.loadReceipts(), documentation_window.loadReports()])

    prediction_window.homeButton.clicked.connect(lambda: [stack.setCurrentIndex(0), home_window.loadStocks()])
    prediction_window.tradeButton.clicked.connect(lambda: stack.setCurrentIndex(2))
    prediction_window.documentButton.clicked.connect(lambda: [stack.setCurrentIndex(3), documentation_window.loadReceipts(), documentation_window.loadReports()])

    trade_window.homeButton.clicked.connect(lambda: [stack.setCurrentIndex(0), home_window.loadStocks()])
    trade_window.predictionButton.clicked.connect(lambda: stack.setCurrentIndex(1))
    trade_window.documentButton.clicked.connect(lambda: [stack.setCurrentIndex(3), documentation_window.loadReceipts(), documentation_window.loadReports()])

    documentation_window.homeButton.clicked.connect(lambda: [stack.setCurrentIndex(0), home_window.loadStocks()])
    documentation_window.predictionButton.clicked.connect(lambda: stack.setCurrentIndex(1))
    documentation_window.tradeButton.clicked.connect(lambda: stack.setCurrentIndex(2))

    win.setLayout(layout)
    win.show()
    sys.exit(app.exec_())
