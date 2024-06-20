import requests
from datetime import datetime, timedelta
from functools import lru_cache


url_main = "https://www.nseindia.com/"
url_template = "https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={from_date}&to={to_date}"


def init_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    session.get(url_main)
    return session

@lru_cache(maxsize=None)
def get_data(session, symbol, days):
    to_date = datetime.now().strftime("%d-%m-%Y")
    from_date = (datetime.now() - timedelta(days=days)).strftime("%d-%m-%Y")
    url = url_template.format(symbol=symbol, from_date=from_date, to_date=to_date)
    response = session.get(url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        return []


