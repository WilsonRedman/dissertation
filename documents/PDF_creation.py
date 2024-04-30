from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import sqlite3
import pathlib
import os
from dateutil.relativedelta import relativedelta

pdfmetrics.registerFont(TTFont("Cambria", "Cambria.ttf"))
pdfmetrics.registerFont(TTFont("CambriaBd", "Cambria-bold.ttf"))

def monthly_report():
    path = sorted(pathlib.Path("documents/reports").glob("**/*"), key=os.path.getmtime, reverse=True)
    reports = [x for x in path if x.is_file()]

    if not not reports: 
        newest = reports[0]
        oldDate = str(newest)[18:-11]
        oldDate = datetime.strptime(oldDate, "%Y-%m-%d")
        date = oldDate + relativedelta(months = 1)

        while date < datetime.now():
            conn = sqlite3.connect("db/trades.db")
            cursor = conn.cursor()
            query = cursor.execute("""SELECT stocks.name, transactions.quantity, transactions.price, transactions.created_at 
                                        FROM transactions JOIN stocks on transactions.ticker = stocks.ticker
                                        WHERE transactions.created_at between '"""+str(oldDate)[:10]+
                                        """' and '"""+str(date)[:10]+
                                        """' ORDER BY stocks.name ASC, transactions.created_at ASC""")
            data = query.fetchall()
            data = [list(trade) for trade in data]

            lastName=""
            for trade in data:
                trade[3] = trade[3][:16]
                if (trade[0] == lastName):
                    trade[0] = ""
                else:
                    lastName = trade[0]

            profits = {}

            formatted = []
            count = 0
            stockTrack = 0
            nameTrack = ""
            for trade in data:
                ## Add total for each stock traded
                if (trade[0] != ""):
                    if (nameTrack ==""):
                        nameTrack = trade[0]
                    else:
                        if (stockTrack < 0):
                            stockStr = "-£"+format(abs(stockTrack),".2f")
                        else:
                            stockStr = "+£"+format(stockTrack,".2f")
                        formatted.insert(count,["","","","Total:",stockStr])
                        formatted.insert(count,["","","","",""])

                        profits[nameTrack] = round(stockTrack, 2)
                        nameTrack = trade[0]
                        count += 1
                        stockTrack = 0

                cost = (-1)*(trade[1])*(trade[2])
                stockTrack += cost
                if (cost < 0):
                    costStr = "-£"+format(abs(cost),".2f")
                else:
                    costStr = "+£"+format(cost,".2f")

                trade[2] = format(trade[2], ".2f")  
                ## Format all costs to 2dp
                trade.insert(3, costStr)
                formatted.append(trade)
                count += 2

            if (stockTrack < 0):
                stockStr = "-£"+format(abs(stockTrack),".2f")
            else:
                stockStr = "+£"+format(stockTrack,".2f")
            formatted.append(["","","","Total:",stockStr])
            formatted.append(["","","","",""])
            formatted.insert(0,["Stock Name", "Quantity", "Price", "Profit", "Timestamp"])
            profits[nameTrack] = round(stockTrack, 2)

            totalProfit = 0
            for key in profits:
                totalProfit += profits[key]
            if(totalProfit < 0):
                totalStr = "-£"+format(abs(totalProfit),".2f")
                formatted.append(["","","","Total Loss:",totalStr])
            else:
                totalStr = "£"+format(totalProfit,".2f")
                formatted.append(["","","","Total Profit:",totalStr])

            doc = SimpleDocTemplate("documents/reports/"+str(date)[:10]+"_report.pdf", title = "Monthly_Report")
            elements = []

            pStyle = ParagraphStyle("Heading",
                                    fontName = "Cambria",
                                    fontSize = 20,
                                    alignment = 1,
                                    spaceAfter = 30)

            heading = Paragraph("Report of all trades in the past month", pStyle)
            elements.append(heading)

            table = Table(formatted)
            tStyle = TableStyle([("FONTNAME",(0,0),(-1,-1),"Cambria"),
                                ("FONTNAME",(0,0),(4,0), "CambriaBd"),
                                ("FONTSIZE",(0,0),(-1,-1),11.5),
                                ("BACKGROUND",(0,0),(-1,-1),colors.lightgrey)])

            for row, trade in enumerate(formatted):
                if (trade[1] == "" and trade[4] != ""):
                    tStyle.add("FONTNAME",(0,row),(4,row), "CambriaBd")
                    if (trade[4][0] == "-"):
                        tStyle.add("TEXTCOLOR", (4,row), (4,row), colors.red)
                    else:
                        tStyle.add("TEXTCOLOR", (4,row), (4,row), colors.green)

            table.setStyle(tStyle)
            elements.append(table)

            doc.build(elements)

            oldDate = date
            date = date + relativedelta(months = 1)

def receipt(ticker, name, quantity, price, date):
    date = str(date)[:16]
    cost = (-1) * quantity * price

    if (cost < 0):
        costStr = "-£"+format(abs(cost),".2f")
    else:
        costStr = "+£"+format(cost,".2f")

    information = [["Traded Stock", "Quantity", "Total Price", "Timestamp"]]
    information.append([name, quantity, costStr, date])
    
    file = "documents/receipts/"+ ticker + "_" + date[:10] + "_receipt.pdf"
    doc = SimpleDocTemplate(file, title = "Receipt", pagesize = (6*inch, 4*inch))
    elements = []

    pStyle = ParagraphStyle("Heading",
                            fontName = "Cambria",
                            fontSize = 20,
                            alignment = 1,
                            spaceAfter = 30)


    if quantity < 0 :
        heading = Paragraph(name + " sale receipt", pStyle)
    else:
        heading = Paragraph(name + " purhcase receipt", pStyle)
    elements.append(heading)

    table = Table(information)
    tStyle = TableStyle([("FONTNAME",(0,0),(-1,-1),"Cambria"),
                        ("FONTNAME",(0,0),(4,0), "CambriaBd"),
                        ("FONTSIZE",(0,0),(-1,-1),11.5),
                        ("BACKGROUND",(0,0),(-1,-1),colors.lightgrey)])
    
    table.setStyle(tStyle)
    elements.append(table)

    doc.build(elements)