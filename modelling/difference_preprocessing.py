import copy
import random
import math
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

def collect_data():
    INPUT_DAYS = 120
    INPUT_DAYS += 1 # Doing this as the first day is the one we compare to (not actually used)

    tickersdf = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",)[0]
    tickers = tickersdf.values.tolist()
    tickers = [i[0] for i in tickers]

    data = []
    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="200d", interval="1d")

        if ((history.empty) != True):
            # Adds if not delisted
            list = history.values.tolist()

            ## This line is selecting necessary information for each stock
            list = [i[:5] for i in list]

            data.append(list)
        
        else:
            tickers.remove(symbol)

    chosenSet = []
    ############################################################
    # ADD RANDOMNESS TO TIME, CURRENTLY JUST LOOKING AT END??? #
    ############################################################
    # NEVERMIND, THIS IS FOR THE RECENT DATA #
    ##########################################
    for stock in data:
        recordedDays = len(stock)
        if (recordedDays > INPUT_DAYS):
            startDay = (recordedDays - 1) - INPUT_DAYS

            dataRange = copy.deepcopy(stock[(startDay) :])

            chosenSet.append(dataRange)

    ###### Altering Input Relating To Start Close ######
    for stock in range(len(chosenSet)):
        comparePrice = chosenSet[stock][0][-2]
        compareTraded = chosenSet[stock][0][-1]
        for day in range(len(chosenSet[stock])):
            if (day != 0):
                for value in range(len(chosenSet[stock][day]) - 1): # -1 ignores the trading volume
                    chosenSet[stock][day][value] = chosenSet[stock][day][value] - comparePrice
                chosenSet[stock][day][-1] = chosenSet[stock][day][-1] - compareTraded
        chosenSet[stock].pop(0)
    ###### Altering Input Relating To Start Close ######         

    # Turning into list of inputs
    ###############################################
    # Unsure if the tickers here will be correct #
    ##############################################
    dataSet = []
    for i, stock in enumerate(chosenSet):
        stockTemp = []
        stockTemp.append(tickers[i])
        for day in stock[:-1]:
            for data in day:
                stockTemp.append(data) # Data for every day
        stockTemp.append(0)
        dataSet.append(stockTemp)

    ## Stock order goes open, high, low, close, traded
    colNames = []
    colNames.append("ticker")
    for day in range (0, int((len(dataSet[0]) - 1)/5)):
        colNames.append("open_day"+str(day))
        colNames.append("high_day"+str(day))
        colNames.append("low_day"+str(day))
        colNames.append("close_day"+str(day))
        colNames.append("traded_day"+str(day))
    colNames.append("close_end")

    npArray = np.array(dataSet)

    df = pd.DataFrame(npArray, columns = colNames)

    x = datetime.datetime.now()
    pathName = "modelling\\" + str(x)[:10] + "_data.csv"

    df.to_csv(pathName, index=False)

if __name__ == "__main__":
    collect_data()