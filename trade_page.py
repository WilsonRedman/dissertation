from PyQt5 import  QtWidgets, uic
from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import documents.PDF_creation
import datetime
import sqlite3

class Trade(QWidget):
        def __init__(self):
            super(Trade, self).__init__()
            uic.loadUi("ui/Trade Page.ui", self)

            self.sellTicker.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            self.sellTicker.currentTextChanged.connect(self.combobox_change)

            conn = sqlite3.connect("db/trades.db")
            cursor = conn.cursor()

            # Queries for owned stocks
            query = cursor.execute("SELECT ticker, quantity FROM own")
            # Stores owned stocks in the class
            self.owned = query.fetchall()

            conn.close()

            self.fill_info()

            self.buySubmit.clicked.connect(self.purchase)
            self.sellSubmit.clicked.connect(self.sell)
        
        def fill_info(self):
            # Adds the owned stock tickers to the drop down
            self.sellTicker.clear()
            if(self.owned is not None):
                 for item in self.owned:
                    self.sellTicker.addItem(item[0])

        def combobox_change(self, value):
            # When a new ticker is selected to sell, the maximum for the quantity is changed with it
            maxQuantity = 0
            for i in self.owned:
                 if i[0] == value:
                      maxQuantity = i[1]
            self.sellQuantity.setMaximum(maxQuantity)
        
        def purchase(self):
            # Called when stock is entered to purchase
            # Gets all of the information
            ticker = self.buyTicker.text()
            name = self.buyName.text()
            quantity = int(self.buyQuantity.text())
            price = self.buyPrice.text()

            # Validation checks
            if ticker != "":
                validTicker = True
            else:
                validTicker = False

            if name != "":
                validName = True
            else:
                validName = False 
            
            if quantity > 0:
                validQuantity = True
            else:
                validQuantity = False

            try:
                price = float(price)
                validPrice = True
            except:
                validPrice = False

            # Checks if valid
            if (validTicker & validName & validQuantity & validPrice):
                date = datetime.datetime.now()

                # Clears the inputs
                self.buyTicker.clear() 
                self.buyName.clear() 
                self.buyQuantity.setValue(0)
                self.buyPrice.clear()

                conn = sqlite3.connect("db/trades.db")
                cursor = conn.cursor()

                stored = True
                # Checks if ticker and stock name are stored
                query = cursor.execute("SELECT * FROM stocks WHERE ticker='"+ticker+"'")
                if(query.fetchone() is None):
                    stored = False
                
                # Stores ticker and stock name if they aren't stored
                if (stored == False):
                    cursor.execute("INSERT INTO stocks VALUES (?, ?)", (ticker, name))
                # Enters transaction into database
                cursor.execute("INSERT INTO transactions(ticker, quantity, price, created_at) VALUES (?, ?, ?, ?)", (ticker, quantity, price, date))     

                # Checks if the stock is owned
                query = cursor.execute("SELECT * FROM own WHERE ticker='"+ticker+"'")
                data = query.fetchone()
                if(data is None):
                    # If not owned, the stock is added to owned
                    cursor.execute("INSERT INTO own VALUES (?, ?)", (ticker, quantity))    
                else:
                    # If it is owned, the quantity is added to owned
                    oldQuantity = data[1]
                    quantity += oldQuantity
                    cursor.execute("UPDATE own SET quantity="+str(quantity)+" WHERE ticker='"+ticker+"'")
                conn.commit()
                conn.close()
                documents.PDF_creation.receipt(ticker, name, quantity, price, date)

                # Updates the sell stocks part
                self.fill_info()
            else:
                # Displays error message if not valid
                error = QtWidgets.QErrorMessage()
                error.showMessage("Invalid information Provided")
                error.exec_()

        def sell(self):
            # Called when stock is entered to sell
            # Gets all of the information
            ticker = self.sellTicker.currentText()
            quantity = int(self.sellQuantity.text())
            price = self.sellPrice.text()

            # Validation checks
            validTicker = False
            for i in self.owned:
                if i[0] == ticker:
                    validTicker = True
            
            if quantity > 0:
                validQuantity = True
            else:
                validQuantity = False

            try:
                price = float(price)
                validPrice = True
            except:
                validPrice = False

            # Checks if valid
            if (validTicker & validQuantity & validPrice):
                date = datetime.datetime.now()

                # Clears the inputs
                self.sellTicker.setCurrentIndex(0) 
                self.sellQuantity.setValue(0)
                self.sellPrice.clear()

                for stock in self.owned:
                    if ticker == stock[0]:
                        oldQuantity = stock[1]
                
                newQuantity = oldQuantity - quantity

                conn = sqlite3.connect("db/trades.db")
                cursor = conn.cursor()

                query = cursor.execute("SELECT name FROM stocks where ticker='"+ticker+"'")
                data = query.fetchone()
                name = data[0]

                # Enters transaction into database
                cursor.execute("INSERT INTO transactions(ticker, quantity, price, created_at) VALUES (?, ?, ?, ?)", (ticker, -quantity, price, date))
                if newQuantity == 0:
                    # Removes from owned if quantity is 0
                    cursor.execute("DELETE FROM own WHERE ticker='"+ticker+"'")
                else:
                    # Otherwise updates to new quantity
                    cursor.execute("UPDATE own SET quantity="+str(newQuantity)+" WHERE ticker='"+ticker+"'")
                conn.commit()
                conn.close()
                documents.PDF_creation.receipt(ticker, name, -quantity, price, date)

                # Updates the sell stocks part 
                self.fill_info()
            else:
                # Displays error message if not valid
                error = QtWidgets.QErrorMessage()
                error.showMessage("Invalid information Provided")
                error.exec_()