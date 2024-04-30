from PyQt5 import  QtWidgets, uic
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import pathlib
import subprocess
import sqlite3
from transformers import TapexTokenizer, BartForConditionalGeneration
import pandas as pd
import documents.PDF_creation
import chatbot.chat

class Documentation(QWidget):
        def __init__(self):
            super(Documentation, self).__init__()
            uic.loadUi("ui/Documentation Page.ui", self)

            # Creates instances of downloaded tokenizer and our locally saved model
            # The model is not in the folder due to it's size
            self.tokenizer = TapexTokenizer.from_pretrained("chatbot/tokenizer")
            self.model = BartForConditionalGeneration.from_pretrained("chatbot/tapex")

            self.queryButton.clicked.connect(lambda: self.chatClick())

            # Calls the monthly report creation that will create reports if needed
            documents.PDF_creation.monthly_report()
            self.loadReceipts()
            self.loadReports()

        def loadReceipts(self):

            # Loads all of the saved receipt files
            path = sorted(pathlib.Path("documents/receipts").glob("**/*"), key=os.path.getmtime, reverse=True)
            self.receipts = [x for x in path if x.is_file()]

            # Clears any currently displayed receipts
            while self.receiptLayout.count():
                child = self.receiptLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Displays receipts
            for receipt in self.receipts:

                 button = QPushButton(str(receipt)[19:-4])
                 button.clicked.connect(lambda checked, receipt = receipt : self.onClick(receipt))

                 self.receiptLayout.addWidget(button)

        def loadReports(self):
            
            # Loads all of the report files
            path = sorted(pathlib.Path("documents/reports").glob("**/*"), key=os.path.getmtime, reverse=True)
            self.reports = [x for x in path if x.is_file()]

            # Clears any currently displayed reports
            while self.reportLayout.count():
                child = self.reportLayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Displays reports
            for report in self.reports:
                button = QPushButton(str(report)[18:-4])
                button.clicked.connect(lambda checked, report = report : self.onClick(report))

                self.reportLayout.addWidget(button)

        def onClick(self, file):
            # Opens pdf files when their respective button is clicked
            subprocess.Popen([file], shell=True)

        def chatClick(self):
            # When the user sends a message to the chatbot
            conn = sqlite3.connect("db/trades.db")
            cursor = conn.cursor()

            # Trade history is queried from the database
            query = cursor.execute("""SELECT stocks.name, transactions.quantity, transactions.price, transactions.created_at 
                                        FROM transactions JOIN stocks on transactions.ticker = stocks.ticker""")
            data = query.fetchall()


            dict = {"Stock": [], "Type": [], "Quantity": [], "Trade Price": [], "Transaction Date": []}

            # Data is formatted to make it easier for the chatbot to understand
            for trade in data:
                dict["Stock"].append(trade[0])
                if (trade[1] < 0):
                    dict["Type"].append("Sell")
                else:
                    dict["Type"].append("Buy")
                dict["Quantity"].append(str(trade[1]))
                dict["Trade Price"].append(str(trade[1] * trade[2]))
                dict["Transaction Date"].append(trade[3][:16])

            table = pd.DataFrame.from_dict(dict)
            
            # Query is retrieved
            query = self.queryInput.text()
            self.queryInput.clear()

            # Query is displayed in the message box
            message = QLabel(query)
            message.setFont(QFont("Lucidia Sans", 11))
            message.setAlignment(Qt.AlignRight)
            message.setWordWrap(True)

            self.messageLayout.addWidget(message)

            # Response is requested from the chatbot 
            output = chatbot.chat.query(query, table, self.tokenizer, self.model)

            # Response is displayed in the message box
            reply = QLabel(output[0])

            reply.setFont(QFont("Lucidia Sans", 11))
            reply.setAlignment(Qt.AlignLeft)
            reply.setWordWrap(True)

            self.messageLayout.addWidget(reply)