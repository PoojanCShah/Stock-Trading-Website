import os
from time import sleep
from datetime import datetime
import yfinance as yf
import pandas as pd
import jugaad_data.nse.live as live
def main():
    while True:
        last_modified = os.path.getmtime("stock_data.csv")
        now = datetime.now()
        if now.day != datetime.fromtimestamp(last_modified).day:
            update_data()
        sleep(60 * 60 * 24)
def update_data():
    df = pd.read_csv("ind_nifty50list.csv")
    useful_cols = [
        "currentPrice",
        "dayHigh",
        "dayLow",
        "previousClose",
        "trailingPE",
        "volume",
    ]
    better_name = [
        "Current Price",
        "Day High",
        "Day Low",
        "Previous Close",
        "P/E Ratio",
        "Volume",
    ]
    to_store = []
    obj = live.NSELive()
    for index, row in df.iterrows():
        stock = row["Symbol"] + ".NS"
        print(stock)
        ticker = yf.Ticker(stock)
        live_data = obj.stock_quote(row["Symbol"])["priceInfo"]
        stock_info = ticker.info
        data = {}
        data["Symbol"] = row["Symbol"]
        data["Percentage Change"] = round(live_data["pChange"], 2)
        for bet, col in zip(better_name, useful_cols):
            try:
                data[bet] = round(stock_info[col],3)
            except KeyError:
                if col == "trailingPE":
                    data[bet] = 0
                else:
                    raise KeyError
        to_store.append(data)

    df = pd.DataFrame(to_store)
    df.to_csv("stock_data.csv", index=False)

