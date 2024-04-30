from PyQt5 import  QtWidgets, uic
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from transformers import TapexTokenizer, BartForConditionalGeneration
import pandas as pd
import modelling.predict
import chatbot.chat

class Predictions(QWidget):
        def __init__(self):
            super(Predictions, self).__init__()
            uic.loadUi("ui/Prediction Page.ui", self)

            # Creates instances of downloaded tokenizer and our locally saved model
            # The model is not in the folder due to it's size
            self.tokenizer = TapexTokenizer.from_pretrained("chatbot/tokenizer")
            self.model = BartForConditionalGeneration.from_pretrained("chatbot/tapex")

            self.queryButton.clicked.connect(lambda: self.chatClick())

            self.loadPredictions()

        def loadPredictions(self):

            # Loads the predictions to be displayed
            self.predictions = modelling.predict.predictions()
            # Stores predictions in the class
            self.tickers = [x[0] for x in self.predictions]
            self.values = [str(x[1]) for x in self.predictions]

            # Displays each of the predictions
            for stock in self.predictions:
                layout = QHBoxLayout()

                ticker = QLabel(stock[0])
                ticker.setAlignment(Qt.AlignCenter)

                if stock[1] > 0:
                    # Colour formatting
                    prediction = QLabel("+ $"+"{:.2f}".format(stock[1]))
                    prediction.setStyleSheet("color: green")
                else:
                    # Colour formatting
                    prediction = QLabel("- $"+("{:.2f}".format(stock[1]))[1:])
                    prediction.setStyleSheet("color: red")
                prediction.setFont(QFont("Lucidia Sans", 12))
                prediction.setMinimumHeight(50)
                prediction.setAlignment(Qt.AlignCenter)
                prediction.setWordWrap(True)

                layout.addWidget(ticker)
                layout.addWidget(prediction)

                self.scrollLayout.addLayout(layout)

        def chatClick(self):
            # When the user sends a message to the chatbot

            # Query is retrieved
            query = self.queryInput.text()
            self.queryInput.clear()

            # Query is displayed in the message box
            message = QLabel(query)
            message.setFont(QFont("Lucidia Sans", 11))
            message.setAlignment(Qt.AlignRight)
            message.setWordWrap(True)

            self.messageLayout.addWidget(message)

            # Data is formatted so it's easier for the chatbot to understand
            data = {"Stock Tickers": self.tickers[:60], "Predicted Price Change": self.values[:60]}
            table = pd.DataFrame.from_dict(data)

            # Response is requested from the chatbot 
            output = chatbot.chat.query(query, table, self.tokenizer, self.model)

            # Response is displayed in the message box
            reply = QLabel(output[0])

            reply.setFont(QFont("Lucidia Sans", 11))
            reply.setAlignment(Qt.AlignLeft)
            reply.setWordWrap(True)

            self.messageLayout.addWidget(reply)

