import yfinance as yf

START_DATE = "2010-01-01"

def _load(symbol):
    df = yf.download(symbol, start=START_DATE, progress=False)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    return df


def load_gold():
    return _load("GC=F")        # Gold Futures


def load_silver():
    return _load("SI=F")        # Silver Futures


def load_gas():
    return _load("NG=F")        # Natural Gas Futures


def load_copper():
    return _load("HG=F")        # Copper Futures (COMEX)
